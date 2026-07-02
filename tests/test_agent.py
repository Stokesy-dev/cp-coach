import pytest
import math
from unittest.mock import patch, MagicMock
from src.agent import (
    weak_area_analysis_node,
    search_node,
    recommend_node,
    process_feedback_node,
    router,
    feedback_branch,
    AgentState
)

# --- 1. Weakness Score Formula Tests ---

def test_weakness_score_formula_dp():
    # DP worked example in README: 10 attempts, 2 solves
    # R = 2 / 10 = 0.2
    # W = (1 - 0.2) * ln(1 + 10) = 0.8 * ln(11) ≈ 1.918
    submissions = []
    # 2 solved problems
    for i in range(2):
        submissions.append({
            "problem_id": f"DP_SOLVED_{i}",
            "tags": ["dp"],
            "rating": 1200,
            "verdict": "OK",
            "timestamp": 0
        })
    # 8 unsolved/failed attempts (unique problems)
    for i in range(8):
        submissions.append({
            "problem_id": f"DP_FAILED_{i}",
            "tags": ["dp"],
            "rating": 1200,
            "verdict": "FAILED",
            "timestamp": 0
        })

    state: AgentState = {
        "handle": "TestUser",
        "csv_path": None,
        "force_offline": True,
        "submissions": submissions,
        "weak_tags": [],
        "target_ratings": {},
        "current_tag": None,
        "current_problem": None,
        "recommendation_rationale": None,
        "feedback": None,
        "history": [],
        "logs": [],
        "api_key": None
    }

    result = weak_area_analysis_node(state)
    weak_tags = dict(result["weak_tags"])
    
    assert "dp" in weak_tags
    expected_score = 0.8 * math.log(11)
    assert weak_tags["dp"] == pytest.approx(expected_score, abs=1e-5)
    assert weak_tags["dp"] == pytest.approx(1.918, abs=1e-3)


def test_weakness_score_formula_math():
    # Math worked example in README: 1 attempt, 0 solves
    # R = 0 / 1 = 0
    # W = (1 - 0) * ln(1 + 1) = 1.0 * ln(2) ≈ 0.693
    submissions = [
        {
            "problem_id": "MATH_FAILED_0",
            "tags": ["math"],
            "rating": 1200,
            "verdict": "FAILED",
            "timestamp": 0
        }
    ]

    state: AgentState = {
        "handle": "TestUser",
        "csv_path": None,
        "force_offline": True,
        "submissions": submissions,
        "weak_tags": [],
        "target_ratings": {},
        "current_tag": None,
        "current_problem": None,
        "recommendation_rationale": None,
        "feedback": None,
        "history": [],
        "logs": [],
        "api_key": None
    }

    result = weak_area_analysis_node(state)
    weak_tags = dict(result["weak_tags"])
    
    assert "math" in weak_tags
    expected_score = 1.0 * math.log(2)
    assert weak_tags["math"] == pytest.approx(expected_score, abs=1e-5)
    assert weak_tags["math"] == pytest.approx(0.693, abs=1e-3)


# --- 2. Rating Target Calculation Tests ---

@patch("src.agent.get_problems")
def test_rating_target_tag_specific_average(mock_get_problems):
    # Case 1: Tag-specific solved average (rounds to nearest 100, target is baseline + 100)
    mock_get_problems.return_value = [
        {"contestId": 1, "index": "A", "name": "P1", "rating": 1300, "tags": ["dp"]}
    ]
    submissions = [
        {"problem_id": "DP1", "tags": ["dp"], "rating": 1200, "verdict": "OK", "timestamp": 0},
        {"problem_id": "DP2", "tags": ["dp"], "rating": 1400, "verdict": "OK", "timestamp": 0},
    ]
    # Average: 1250 -> rounded to nearest 100 is 1300 -> target: 1300 + 100 = 1400

    state: AgentState = {
        "handle": "TestUser",
        "csv_path": None,
        "force_offline": True,
        "submissions": submissions,
        "weak_tags": [("dp", 1.0)],
        "target_ratings": {},
        "current_tag": "dp",
        "current_problem": None,
        "recommendation_rationale": None,
        "feedback": None,
        "history": [],
        "logs": [],
        "api_key": None
    }

    result = search_node(state)
    assert result["target_ratings"]["dp"] == 1400


@patch("src.agent.get_problems")
def test_rating_target_overall_average_fallback(mock_get_problems):
    # Case 2: No solved dp problems, fall back to overall solved average
    mock_get_problems.return_value = [
        {"contestId": 1, "index": "A", "name": "P1", "rating": 1300, "tags": ["dp"]}
    ]
    submissions = [
        {"problem_id": "MATH1", "tags": ["math"], "rating": 1100, "verdict": "OK", "timestamp": 0},
        {"problem_id": "GREEDY1", "tags": ["greedy"], "rating": 1300, "verdict": "OK", "timestamp": 0},
        {"problem_id": "DP_FAILED", "tags": ["dp"], "rating": 1000, "verdict": "FAILED", "timestamp": 0},
    ]
    # Overall solved average: (1100 + 1300)/2 = 1200 -> target: 1200 + 100 = 1300

    state: AgentState = {
        "handle": "TestUser",
        "csv_path": None,
        "force_offline": True,
        "submissions": submissions,
        "weak_tags": [("dp", 1.0)],
        "target_ratings": {},
        "current_tag": "dp",
        "current_problem": None,
        "recommendation_rationale": None,
        "feedback": None,
        "history": [],
        "logs": [],
        "api_key": None
    }

    result = search_node(state)
    assert result["target_ratings"]["dp"] == 1300


@patch("src.agent.get_problems")
def test_rating_target_global_default(mock_get_problems):
    # Case 3: No solved history at all -> baseline 800 -> target: 800 + 100 = 900
    mock_get_problems.return_value = [
        {"contestId": 1, "index": "A", "name": "P1", "rating": 900, "tags": ["dp"]}
    ]
    submissions = [
        {"problem_id": "DP_FAILED", "tags": ["dp"], "rating": 1000, "verdict": "FAILED", "timestamp": 0},
    ]

    state: AgentState = {
        "handle": "TestUser",
        "csv_path": None,
        "force_offline": True,
        "submissions": submissions,
        "weak_tags": [("dp", 1.0)],
        "target_ratings": {},
        "current_tag": "dp",
        "current_problem": None,
        "recommendation_rationale": None,
        "feedback": None,
        "history": [],
        "logs": [],
        "api_key": None
    }

    result = search_node(state)
    assert result["target_ratings"]["dp"] == 900


# --- 3. Difficulty Adjustment Tests ---

def test_difficulty_adjustment_pass():
    # Pass should increase rating target by 100
    state: AgentState = {
        "handle": "TestUser",
        "csv_path": None,
        "force_offline": True,
        "submissions": [],
        "weak_tags": [("dp", 1.0)],
        "target_ratings": {"dp": 1200},
        "current_tag": "dp",
        "current_problem": {"contestId": 1, "index": "A", "name": "P1", "rating": 1200, "tags": ["dp"]},
        "recommendation_rationale": "Motivation",
        "feedback": "pass",
        "history": [],
        "logs": [],
        "api_key": None
    }

    result = process_feedback_node(state)
    assert result["target_ratings"]["dp"] == 1300
    assert len(result["history"]) == 1
    assert result["history"][0]["verdict"] == "pass"


def test_difficulty_adjustment_fail():
    # Fail should decrease rating target by 100
    state: AgentState = {
        "handle": "TestUser",
        "csv_path": None,
        "force_offline": True,
        "submissions": [],
        "weak_tags": [("dp", 1.0)],
        "target_ratings": {"dp": 1200},
        "current_tag": "dp",
        "current_problem": {"contestId": 1, "index": "A", "name": "P1", "rating": 1200, "tags": ["dp"]},
        "recommendation_rationale": "Motivation",
        "feedback": "fail",
        "history": [],
        "logs": [],
        "api_key": None
    }

    result = process_feedback_node(state)
    assert result["target_ratings"]["dp"] == 1100
    assert len(result["history"]) == 1
    assert result["history"][0]["verdict"] == "fail"


def test_difficulty_adjustment_fail_clamped():
    # Fail should decrease rating target but be clamped at 800 minimum
    state: AgentState = {
        "handle": "TestUser",
        "csv_path": None,
        "force_offline": True,
        "submissions": [],
        "weak_tags": [("dp", 1.0)],
        "target_ratings": {"dp": 800},
        "current_tag": "dp",
        "current_problem": {"contestId": 1, "index": "A", "name": "P1", "rating": 800, "tags": ["dp"]},
        "recommendation_rationale": "Motivation",
        "feedback": "fail",
        "history": [],
        "logs": [],
        "api_key": None
    }

    result = process_feedback_node(state)
    assert result["target_ratings"]["dp"] == 800  # remains 800


# --- 4. Rating Band Widening & Fallback Tests ---

@patch("src.agent.get_problems")
def test_rating_band_widening_exact_match(mock_get_problems):
    # Returns problem matching exact target rating (offset = 0)
    mock_get_problems.return_value = [
        {"contestId": 1, "index": "A", "name": "Exact", "rating": 1200, "tags": ["graphs"]}
    ]
    state: AgentState = {
        "handle": "TestUser",
        "csv_path": None,
        "force_offline": True,
        "submissions": [],
        "weak_tags": [("graphs", 1.0)],
        "target_ratings": {"graphs": 1200},
        "current_tag": "graphs",
        "current_problem": None,
        "recommendation_rationale": None,
        "feedback": None,
        "history": [],
        "logs": [],
        "api_key": None
    }
    
    result = search_node(state)
    assert result["current_problem"]["name"] == "Exact"
    any_offset_log = any("Found 1 problems in rating band [1200, 1200]" in log for log in result["logs"])
    assert any_offset_log


@patch("src.agent.get_problems")
def test_rating_band_widening_offset_100(mock_get_problems):
    # Returns problem requiring ±100 offset widening
    mock_get_problems.return_value = [
        {"contestId": 1, "index": "A", "name": "Offset100", "rating": 1300, "tags": ["graphs"]}
    ]
    state: AgentState = {
        "handle": "TestUser",
        "csv_path": None,
        "force_offline": True,
        "submissions": [],
        "weak_tags": [("graphs", 1.0)],
        "target_ratings": {"graphs": 1200},
        "current_tag": "graphs",
        "current_problem": None,
        "recommendation_rationale": None,
        "feedback": None,
        "history": [],
        "logs": [],
        "api_key": None
    }
    
    result = search_node(state)
    assert result["current_problem"]["name"] == "Offset100"
    any_offset_log = any("Found 1 problems in rating band [1100, 1300]" in log for log in result["logs"])
    assert any_offset_log


@patch("src.agent.get_problems")
def test_rating_band_widening_offset_1000(mock_get_problems):
    # Returns problem requiring ±1000 offset widening
    mock_get_problems.return_value = [
        {"contestId": 1, "index": "A", "name": "Offset1000", "rating": 2200, "tags": ["graphs"]}
    ]
    state: AgentState = {
        "handle": "TestUser",
        "csv_path": None,
        "force_offline": True,
        "submissions": [],
        "weak_tags": [("graphs", 1.0)],
        "target_ratings": {"graphs": 1200},
        "current_tag": "graphs",
        "current_problem": None,
        "recommendation_rationale": None,
        "feedback": None,
        "history": [],
        "logs": [],
        "api_key": None
    }
    
    result = search_node(state)
    assert result["current_problem"]["name"] == "Offset1000"
    any_offset_log = any("Found 1 problems in rating band [800, 2200]" in log for log in result["logs"])
    assert any_offset_log


@patch("src.agent.get_problems")
def test_rating_band_widening_absolute_fallback(mock_get_problems):
    # If widening fails (target is 1200, but graphs problem has rating 2500 - outside range [200, 2200])
    # The search node must trigger absolute fallback and recommend the graphs problem anyway
    mock_get_problems.return_value = [
        {"contestId": 1, "index": "A", "name": "FallbackGraphs", "rating": 2500, "tags": ["graphs"]}
    ]
    state: AgentState = {
        "handle": "TestUser",
        "csv_path": None,
        "force_offline": True,
        "submissions": [],
        "weak_tags": [("graphs", 1.0)],
        "target_ratings": {"graphs": 1200},
        "current_tag": "graphs",
        "current_problem": None,
        "recommendation_rationale": None,
        "feedback": None,
        "history": [],
        "logs": [],
        "api_key": None
    }
    
    result = search_node(state)
    assert result["current_problem"]["name"] == "FallbackGraphs"
    any_fallback_log = any("Fallback: Widen search failed. Selected any unsolved problem for 'graphs'" in log for log in result["logs"])
    assert any_fallback_log


# --- 5. Router Logic Tests ---

def test_router_feedback_present():
    # Feedback is present -> process_feedback
    state = {"feedback": "pass", "submissions": []}
    assert router(state) == "process_feedback"

def test_router_empty_submissions():
    # Feedback is None, submissions is empty -> ingest
    state = {"feedback": None, "submissions": []}
    assert router(state) == "ingest"

def test_router_active_analysis():
    # Feedback is None, has submissions, no current_problem -> analyze
    state = {"feedback": None, "submissions": [{"problem_id": "1"}], "current_problem": None}
    assert router(state) == "analyze"

def test_router_end_state():
    # Feedback is None, has submissions, has current_problem -> END (waiting for user input)
    from langgraph.graph import END
    state = {"feedback": None, "submissions": [{"problem_id": "1"}], "current_problem": {"contestId": 1}}
    assert router(state) == END

def test_feedback_branch_pass():
    # History last verdict is pass -> clear_feedback_and_analyze
    state = {"history": [{"verdict": "pass"}]}
    assert feedback_branch(state) == "clear_feedback_and_analyze"

def test_feedback_branch_fail():
    # History last verdict is fail -> clear_feedback_and_search
    state = {"history": [{"verdict": "fail"}]}
    assert feedback_branch(state) == "clear_feedback_and_search"

def test_feedback_branch_default():
    # History is empty -> clear_feedback_and_analyze
    state = {"history": []}
    assert feedback_branch(state) == "clear_feedback_and_analyze"


# --- 6. Mocking API / LLM Calls ---

@patch("src.agent.Groq")
def test_recommend_node_mocks_llm(mock_groq_class):
    # Mocking Groq response to prevent network requests during LLM rationale generation
    mock_client = mock_groq_class.return_value
    mock_chat = mock_client.chat.completions.create.return_value
    mock_chat.choices = [
        MagicMock(message=MagicMock(content="Mocked LLM Rationale"))
    ]
    
    state: AgentState = {
        "handle": "TestUser",
        "csv_path": None,
        "force_offline": True,
        "submissions": [],
        "weak_tags": [("graphs", 1.0)],
        "target_ratings": {"graphs": 1200},
        "current_tag": "graphs",
        "current_problem": {"contestId": 1, "index": "A", "name": "P1", "rating": 1200, "tags": ["graphs"]},
        "recommendation_rationale": None,
        "feedback": None,
        "history": [],
        "logs": [],
        "api_key": "fake_api_key"
    }
    
    result = recommend_node(state)
    assert result["recommendation_rationale"] == "Mocked LLM Rationale"
    assert mock_groq_class.called
