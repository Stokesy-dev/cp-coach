import os
import random
import logging
import math
from typing import TypedDict, List, Dict, Any, Optional, Tuple
from groq import Groq
from langgraph.graph import StateGraph, START, END
from src.api import get_problems, fetch_user_submissions_api, load_user_submissions_csv

logger = logging.getLogger(__name__)

# Standard Topic Roadmap for beginners who have no active weaknesses
TOPIC_ROADMAP = [
    "Arrays & Strings",
    "Hashing",
    "Two Pointers",
    "Sliding Window",
    "Binary Search",
    "Stack & Queue",
    "Linked List",
    "Trees & BST",
    "Heap",
    "Backtracking",
    "Graphs",
    "Dynamic Programming",
    "Trie",
    "Union Find (DSU)",
    "Segment Tree (basic)",
    "Bit Manipulation"
]

ROADMAP_TO_CF = {
    "Arrays & Strings": ["strings", "implementation", "sortings"],
    "Hashing": ["hashing"],
    "Two Pointers": ["two pointers"],
    "Sliding Window": ["two pointers"],
    "Binary Search": ["binary search"],
    "Stack & Queue": ["data structures"],
    "Linked List": ["data structures"],
    "Trees & BST": ["trees"],
    "Heap": ["data structures"],
    "Backtracking": ["dfs and similar", "brute force"],
    "Graphs": ["graphs", "shortest paths"],
    "Dynamic Programming": ["dp"],
    "Trie": ["strings", "data structures"],
    "Union Find (DSU)": ["dsu"],
    "Segment Tree (basic)": ["data structures"],
    "Bit Manipulation": ["bitmasks", "math"]
}

# Reverse mapping for quick lookup
CF_TO_ROADMAP = {}
for r_tag, cf_tags in ROADMAP_TO_CF.items():
    for cf_tag in cf_tags:
        if cf_tag not in CF_TO_ROADMAP:
            CF_TO_ROADMAP[cf_tag] = []
        CF_TO_ROADMAP[cf_tag].append(r_tag)

# State definition
class AgentState(TypedDict):
    handle: str
    csv_path: Optional[str]
    force_offline: bool
    submissions: List[Dict[str, Any]]
    weak_tags: List[Tuple[str, float]]
    target_ratings: Dict[str, int]
    current_tag: Optional[str]
    current_problem: Optional[Dict[str, Any]]
    recommendation_rationale: Optional[str]
    feedback: Optional[str]  # "pass", "fail", or None
    history: List[Dict[str, Any]]
    logs: List[str]
    api_key: Optional[str]

def generate_rationale(
    tag: str, 
    rating: int, 
    name: str, 
    solve_rate: float, 
    attempts: int, 
    api_key: Optional[str]
) -> str:
    """Generate a short rationale using Groq LLM, with a fallback."""
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        return f"This problem is recommended because it focuses on '{tag}' at rating {rating}, which is currently your top weak area (solve rate: {solve_rate:.1f}% across {attempts} attempts)."
    
    try:
        client = Groq(api_key=key)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CPCoach, an expert competitive programming tutor. Write a short 1-2 sentence "
                        "motivating rationale explaining why this problem is recommended to target the user's weak area. "
                        "Keep it concise, professional, and under 220 characters. Do not use placeholders."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"User's weak tag is '{tag}' (solve rate: {solve_rate:.1f}% across {attempts} attempts). "
                        f"I am recommending problem '{name}' (rating: {rating}). Write a short rationale."
                    )
                }
            ],
            model="llama-3.1-8b-instant",
            max_tokens=80,
            temperature=0.7
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        return f"This problem is recommended because it focuses on '{tag}' at rating {rating}, which is currently your top weak area (solve rate: {solve_rate:.1f}% across {attempts} attempts)."

# Nodes
def ingest_node(state: AgentState) -> Dict[str, Any]:
    logs = list(state.get("logs", []))
    logs.append("[Node: Ingest] Starting ingestion.")
    
    submissions = []
    if state.get("csv_path"):
        try:
            submissions = load_user_submissions_csv(state["csv_path"])
            logs.append(f"[Node: Ingest] Loaded {len(submissions)} submissions from CSV: {state['csv_path']}")
        except Exception as e:
            logs.append(f"[Node: Ingest] CSV Load failed: {e}. Falling back to empty history.")
    else:
        try:
            submissions = fetch_user_submissions_api(state["handle"])
            logs.append(f"[Node: Ingest] Fetched {len(submissions)} submissions for handle: {state['handle']}")
        except Exception as e:
            logs.append(f"[Node: Ingest] API fetch failed: {e}. Falling back to empty history.")
            
    return {"submissions": submissions, "logs": logs}

def weak_area_analysis_node(state: AgentState) -> Dict[str, Any]:
    logs = list(state.get("logs", []))
    logs.append("[Node: Weak-Area Analysis] Analyzing submissions.")
    
    submissions = state.get("submissions", [])
    
    # Calculate unique attempts and solves per tag
    tag_attempts: Dict[str, set] = {}
    tag_solves: Dict[str, set] = {}
    
    for sub in submissions:
        prob_id = sub["problem_id"]
        verdict = sub["verdict"]
        tags = sub["tags"]
        
        # Map raw Codeforces tags to our custom Roadmap tags
        mapped_roadmap_tags = set()
        for tag in tags:
            if tag in TOPIC_ROADMAP:
                mapped_roadmap_tags.add(tag)
            elif tag in CF_TO_ROADMAP:
                for r_tag in CF_TO_ROADMAP[tag]:
                    mapped_roadmap_tags.add(r_tag)
                    
        for r_tag in mapped_roadmap_tags:
            if r_tag not in tag_attempts:
                tag_attempts[r_tag] = set()
                tag_solves[r_tag] = set()
            
            tag_attempts[r_tag].add(prob_id)
            if verdict == "OK":
                tag_solves[r_tag].add(prob_id)
                
    weak_tags_list = []
    for tag, attempts_set in tag_attempts.items():
        attempts_cnt = len(attempts_set)
        solves_cnt = len(tag_solves[tag])
        solve_rate = solves_cnt / attempts_cnt if attempts_cnt > 0 else 1.0
        
        # Weakness formula: W = (1 - R) * ln(1 + attempts)
        weakness_score = (1.0 - solve_rate) * math.log(1 + attempts_cnt)
        weak_tags_list.append((tag, weakness_score, solve_rate, attempts_cnt))
        
    # Sort descending by weakness score
    weak_tags_list.sort(key=lambda x: x[1], reverse=True)
    
    # Format for state
    state_weak_tags = [(item[0], item[1]) for item in weak_tags_list]
    
    # Filter weak tags to only those with a weakness score > 0
    actual_weak_tags = [wt for wt in weak_tags_list if wt[1] > 0]
    
    top_tag = None
    if actual_weak_tags:
        top_tag = actual_weak_tags[0][0]
        logs.append(f"[Node: Weak-Area Analysis] Identified weakest tag: '{top_tag}' (Weakness score: {actual_weak_tags[0][1]:.3f})")
    else:
        # User has no active weaknesses (empty history or solved all attempted problems)
        # We walk the TOPIC_ROADMAP and find the first unsolved topic
        solved_tag_names = set()
        for sub in submissions:
            if sub["verdict"] == "OK":
                for tag in sub["tags"]:
                    if tag in TOPIC_ROADMAP:
                        solved_tag_names.add(tag)
                    elif tag in CF_TO_ROADMAP:
                        for r_tag in CF_TO_ROADMAP[tag]:
                            solved_tag_names.add(r_tag)
                    
        roadmap_tag = None
        for tag in TOPIC_ROADMAP:
            if tag not in solved_tag_names:
                roadmap_tag = tag
                break
                
        if roadmap_tag:
            top_tag = roadmap_tag
            logs.append(f"[Node: Weak-Area Analysis] No active weaknesses. Following roadmap: next topic is '{top_tag}'.")
        else:
            # Fallback if they solved all roadmap topics
            top_tag = TOPIC_ROADMAP[0]
            logs.append(f"[Node: Weak-Area Analysis] All roadmap topics solved. Defaulting back to '{top_tag}'.")
        
    return {"weak_tags": state_weak_tags, "current_tag": top_tag, "logs": logs}

def search_node(state: AgentState) -> Dict[str, Any]:
    logs = list(state.get("logs", []))
    tag = state.get("current_tag")
    target_ratings = dict(state.get("target_ratings", {}))
    submissions = state.get("submissions", [])
    history = state.get("history", [])
    
    logs.append(f"[Node: Search] Searching for unsolved problem for tag: '{tag}'")
    
    # 1. Determine baseline target rating if not initialized
    if tag not in target_ratings:
        # Get solved problems for this tag
        solved_ratings = []
        for sub in submissions:
            if sub["verdict"] == "OK":
                mapped_sub_tags = set()
                for t in sub["tags"]:
                    if t in TOPIC_ROADMAP:
                        mapped_sub_tags.add(t)
                    elif t in CF_TO_ROADMAP:
                        for r_t in CF_TO_ROADMAP[t]:
                            mapped_sub_tags.add(r_t)
                if tag in mapped_sub_tags:
                    solved_ratings.append(sub["rating"])
                
        if solved_ratings:
            avg_rating = sum(solved_ratings) / len(solved_ratings)
            baseline = int(round(avg_rating / 100.0) * 100.0)
            logs.append(f"[Node: Search] Baseline solved rating for '{tag}': {baseline}")
        else:
            # Check overall solved rating
            all_solved_ratings = [sub["rating"] for sub in submissions if sub["verdict"] == "OK"]
            if all_solved_ratings:
                baseline = int(round((sum(all_solved_ratings) / len(all_solved_ratings)) / 100.0) * 100.0)
                logs.append(f"[Node: Search] No solved history for '{tag}'. Using overall baseline rating: {baseline}")
            else:
                baseline = 800
                logs.append(f"[Node: Search] No solved history at all. Using default baseline rating: {baseline}")
                
        # Recommended initial target is baseline + 100
        target_ratings[tag] = max(800, baseline + 100)
        logs.append(f"[Node: Search] Initialized target rating for '{tag}' to: {target_ratings[tag]}")

    target_rating = target_ratings[tag]
    
    # 2. Get list of candidate problems
    all_problems = get_problems(force_offline=state.get("force_offline", False))
    
    # Set of solved problem IDs
    solved_ids = {sub["problem_id"] for sub in submissions if sub["verdict"] == "OK"}
    # Set of recommended problem IDs in this session
    recommended_ids = {str(hist["problem"]["contestId"]) + str(hist["problem"]["index"]) for hist in history if "problem" in hist}
    
    # 3. Dynamic search with band widening
    chosen_problem = None
    offset = 0
    while offset <= 1000:
        lower_bound = max(800, target_rating - offset)
        upper_bound = target_rating + offset
        
        target_cf_tags = ROADMAP_TO_CF.get(tag, [])
        candidates = []
        for prob in all_problems:
            prob_id = f"{prob['contestId']}{prob['index']}"
            if prob_id in solved_ids or prob_id in recommended_ids:
                continue
            has_tag = tag in prob["tags"] or any(cf_t in prob["tags"] for cf_t in target_cf_tags)
            if has_tag:
                if lower_bound <= prob["rating"] <= upper_bound:
                    candidates.append(prob)
                    
        if candidates:
            # Found candidates! Select one at random to avoid deterministic selection
            chosen_problem = random.choice(candidates)
            logs.append(
                f"[Node: Search] Found {len(candidates)} problems in rating band [{lower_bound}, {upper_bound}]. "
                f"Selected: {chosen_problem['contestId']}{chosen_problem['index']} - {chosen_problem['name']} (Rating: {chosen_problem['rating']})"
            )
            break
            
        offset += 100
        
    if not chosen_problem:
        # Fallback: ignore rating constraints entirely and find any unsolved problem for this tag
        target_cf_tags = ROADMAP_TO_CF.get(tag, [])
        candidates = []
        for prob in all_problems:
            prob_id = f"{prob['contestId']}{prob['index']}"
            if prob_id in solved_ids or prob_id in recommended_ids:
                continue
            has_tag = tag in prob["tags"] or any(cf_t in prob["tags"] for cf_t in target_cf_tags)
            if has_tag:
                candidates.append(prob)
        if candidates:
            chosen_problem = random.choice(candidates)
            logs.append(
                f"[Node: Search] Fallback: Widen search failed. Selected any unsolved problem for '{tag}' "
                f"without rating bounds: {chosen_problem['contestId']}{chosen_problem['index']} - {chosen_problem['name']} (Rating: {chosen_problem['rating']})"
            )
        else:
            logs.append(f"[Node: Search] WARNING: Absolutely no unsolved problems found for tag '{tag}' in dataset.")
            
    return {"current_problem": chosen_problem, "target_ratings": target_ratings, "logs": logs}

def recommend_node(state: AgentState) -> Dict[str, Any]:
    logs = list(state.get("logs", []))
    logs.append("[Node: Recommend] Generating rationale.")
    
    prob = state.get("current_problem")
    tag = state.get("current_tag")
    submissions = state.get("submissions", [])
    
    if not prob:
        logs.append("[Node: Recommend] No problem to recommend.")
        return {"recommendation_rationale": "No unsolved problems found. Try another tag or reset.", "logs": logs}
        
    # Calculate stats for prompt
    tag_subs = [s for s in submissions if tag in s["tags"]]
    attempts = len({s["problem_id"] for s in tag_subs})
    solves = len({s["problem_id"] for s in tag_subs if s["verdict"] == "OK"})
    solve_rate = (solves / attempts) * 100 if attempts > 0 else 0.0
    
    rationale = generate_rationale(
        tag=tag,
        rating=prob["rating"],
        name=prob["name"],
        solve_rate=solve_rate,
        attempts=attempts,
        api_key=state.get("api_key")
    )
    logs.append(f"[Node: Recommend] Recommendation ready: {prob['contestId']}{prob['index']}")
    
    return {"recommendation_rationale": rationale, "logs": logs}

def process_feedback_node(state: AgentState) -> Dict[str, Any]:
    logs = list(state.get("logs", []))
    feedback = state.get("feedback")
    prob = state.get("current_problem")
    tag = state.get("current_tag")
    target_ratings = dict(state.get("target_ratings", {}))
    history = list(state.get("history", []))
    submissions = list(state.get("submissions", []))
    
    if not prob or not feedback:
        logs.append("[Node: Process Feedback] No active problem or feedback to process.")
        return {"feedback": None}
        
    prob_id = f"{prob['contestId']}{prob['index']}"
    logs.append(f"[Node: Process Feedback] User reported '{feedback}' on problem {prob_id} (rating {prob['rating']}).")
    
    # 1. Update history log
    history.append({
        "problem": prob,
        "tag": tag,
        "target_rating": target_ratings[tag],
        "verdict": feedback
    })
    
    # 2. Append to submissions list so agent knows user attempted/solved it
    submissions.append({
        "problem_id": prob_id,
        "tags": prob["tags"],
        "rating": prob["rating"],
        "verdict": "OK" if feedback == "pass" else "FAILED",
        "timestamp": 0  # mock timestamp for feedback
    })
    
    # 3. Adjust rating target
    old_rating = target_ratings[tag]
    if feedback == "pass":
        target_ratings[tag] = old_rating + 100
        logs.append(f"[Node: Process Feedback] Difficulty Adjustment: PASSED. Rating target for '{tag}' increased from {old_rating} to {target_ratings[tag]}.")
    else:
        target_ratings[tag] = max(800, old_rating - 100)
        logs.append(f"[Node: Process Feedback] Difficulty Adjustment: FAILED. Rating target for '{tag}' decreased from {old_rating} to {target_ratings[tag]}.")
        
    return {
        "history": history,
        "target_ratings": target_ratings,
        "submissions": submissions,
        "logs": logs
    }

def clear_feedback_and_analyze(state: AgentState) -> Dict[str, Any]:
    logs = list(state.get("logs", []))
    logs.append("[Transition] Clearing feedback and routing to Weak-Area Analysis.")
    return {"feedback": None, "current_problem": None, "logs": logs}

def clear_feedback_and_search(state: AgentState) -> Dict[str, Any]:
    logs = list(state.get("logs", []))
    logs.append("[Transition] Clearing feedback and routing directly to Search.")
    return {"feedback": None, "current_problem": None, "logs": logs}


# Routing logic
def router(state: AgentState) -> str:
    """Determine initial node based on state contents."""
    if state.get("feedback") is not None:
        return "process_feedback"
    if not state.get("submissions"):
        return "ingest"
    if not state.get("current_problem"):
        return "analyze"
    return END

def feedback_branch(state: AgentState) -> str:
    """Route after processing feedback based on verdict."""
    # We look at the last item in the history to find the verdict
    history = state.get("history", [])
    if history:
        last_verdict = history[-1].get("verdict")
        if last_verdict == "pass":
            return "clear_feedback_and_analyze"
        elif last_verdict == "fail":
            return "clear_feedback_and_search"
    return "clear_feedback_and_analyze"


# Graph Construction
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("ingest", ingest_node)
workflow.add_node("analyze", weak_area_analysis_node)
workflow.add_node("search", search_node)
workflow.add_node("recommend", recommend_node)
workflow.add_node("process_feedback", process_feedback_node)
workflow.add_node("clear_feedback_and_analyze", clear_feedback_and_analyze)
workflow.add_node("clear_feedback_and_search", clear_feedback_and_search)

# Router entry point
workflow.add_conditional_edges(START, router, {
    "ingest": "ingest",
    "analyze": "analyze",
    "process_feedback": "process_feedback",
    END: END
})

# Sequential edges
workflow.add_edge("ingest", "analyze")
workflow.add_edge("analyze", "search")
workflow.add_edge("search", "recommend")
workflow.add_edge("recommend", END)

# Feedback flow routing
workflow.add_conditional_edges("process_feedback", feedback_branch, {
    "clear_feedback_and_analyze": "clear_feedback_and_analyze",
    "clear_feedback_and_search": "clear_feedback_and_search"
})

workflow.add_edge("clear_feedback_and_analyze", "analyze")
workflow.add_edge("clear_feedback_and_search", "search")

# Compile app
app = workflow.compile()
