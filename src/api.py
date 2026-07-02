import requests
import pandas as pd
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Curated offline fallback database of ~60 common Codeforces problems
OFFLINE_PROBLEMS = [
    # DP Problems
    {"contestId": 1182, "index": "A", "name": "Filling Shapes", "rating": 1000, "tags": ["dp", "math"]},
    {"contestId": 327, "index": "A", "name": "Flipping Game", "rating": 1200, "tags": ["dp", "brute force"]},
    {"contestId": 189, "index": "A", "name": "Cut Ribbon", "rating": 1300, "tags": ["dp"]},
    {"contestId": 706, "index": "C", "name": "Hard Process", "rating": 1400, "tags": ["dp", "strings"]},
    {"contestId": 455, "index": "A", "name": "Boredom", "rating": 1500, "tags": ["dp"]},
    {"contestId": 166, "index": "E", "name": "Tetrahedron", "rating": 1500, "tags": ["dp", "math"]},
    {"contestId": 1633, "index": "D", "name": "Make Them Equal", "rating": 1600, "tags": ["dp", "greedy"]},
    {"contestId": 1676, "index": "H2", "name": "Maximum Crossings (Hard)", "rating": 1500, "tags": ["dp", "data structures"]},
    {"contestId": 977, "index": "F", "name": "Consecutive Subsequence", "rating": 1700, "tags": ["dp"]},
    {"contestId": 1385, "index": "D", "name": "a-Good String", "rating": 1350, "tags": ["dp", "divide and conquer"]},
    {"contestId": 180, "index": "E", "name": "Cubes", "rating": 1900, "tags": ["dp", "two pointers"]},

    # Graph Problems
    {"contestId": 115, "index": "A", "name": "Party", "rating": 900, "tags": ["graphs", "trees"]},
    {"contestId": 1020, "index": "B", "name": "Badge", "rating": 1000, "tags": ["graphs", "dfs and similar"]},
    {"contestId": 1433, "index": "D", "name": "Districts Connection", "rating": 1000, "tags": ["graphs"]},
    {"contestId": 1676, "index": "G", "name": "White-Black Balanced Subtrees", "rating": 1100, "tags": ["graphs", "dfs and similar", "trees"]},
    {"contestId": 520, "index": "B", "name": "Two Buttons", "rating": 1000, "tags": ["graphs", "math"]},
    {"contestId": 580, "index": "C", "name": "Kefa and Park", "rating": 1500, "tags": ["graphs", "dfs and similar", "trees"]},
    {"contestId": 977, "index": "D", "name": "Divide by three, multiply by two", "rating": 1100, "tags": ["graphs", "dfs and similar"]},
    {"contestId": 20, "index": "C", "name": "Dijkstra?", "rating": 1900, "tags": ["graphs", "shortest paths"]},
    {"contestId": 1385, "index": "E", "name": "Directing Edges", "rating": 1900, "tags": ["graphs", "dfs and similar"]},
    {"contestId": 161, "index": "D", "name": "Distance in Tree", "rating": 1800, "tags": ["graphs", "dp", "trees"]},
    {"contestId": 103, "index": "B", "name": "Cthulhu", "rating": 1600, "tags": ["graphs", "dfs and similar"]},

    # Math Problems
    {"contestId": 1335, "index": "A", "name": "Candies and Two Sisters", "rating": 800, "tags": ["math"]},
    {"contestId": 1343, "index": "B", "name": "Balanced Array", "rating": 800, "tags": ["math"]},
    {"contestId": 1328, "index": "A", "name": "Divisibility Problem", "rating": 800, "tags": ["math"]},
    {"contestId": 1353, "index": "B", "name": "Two Arrays And Swaps", "rating": 800, "tags": ["math", "greedy"]},
    {"contestId": 1374, "index": "A", "name": "Required Remainder", "rating": 800, "tags": ["math"]},
    {"contestId": 472, "index": "A", "name": "Design Tutorial: Learn from Math", "rating": 800, "tags": ["math", "number theory"]},
    {"contestId": 617, "index": "A", "name": "Elephant", "rating": 800, "tags": ["math"]},
    {"contestId": 148, "index": "A", "name": "Insomnia cure", "rating": 800, "tags": ["math", "constructive algorithms"]},
    {"contestId": 1542, "index": "A", "name": "Odd Set", "rating": 800, "tags": ["math"]},
    {"contestId": 1742, "index": "A", "name": "Sum", "rating": 800, "tags": ["math"]},
    {"contestId": 1850, "index": "A", "name": "To My Critics", "rating": 800, "tags": ["math"]},
    {"contestId": 230, "index": "B", "name": "T-primes", "rating": 1300, "tags": ["math", "number theory"]},
    {"contestId": 1338, "index": "A", "name": "Sorted Adjacent Differences", "rating": 1200, "tags": ["math", "greedy"]},
    {"contestId": 1500, "index": "A", "name": "Cool Folders", "rating": 1500, "tags": ["math"]},
    {"contestId": 1850, "index": "F", "name": "We Were Both Children", "rating": 1300, "tags": ["math", "number theory"]},
    {"contestId": 1613, "index": "C", "name": "Poisoned Dagger", "rating": 1100, "tags": ["math", "binary search"]},

    # Greedy Problems
    {"contestId": 1582, "index": "A", "name": "Luntik and Concerts", "rating": 800, "tags": ["greedy", "math"]},
    {"contestId": 1624, "index": "A", "name": "Plus One on the Subset", "rating": 800, "tags": ["greedy"]},
    {"contestId": 1692, "index": "A", "name": "Marathon", "rating": 800, "tags": ["greedy"]},
    {"contestId": 1703, "index": "A", "name": "YES or YES?", "rating": 800, "tags": ["greedy"]},
    {"contestId": 1722, "index": "A", "name": "Spell Check", "rating": 800, "tags": ["greedy"]},
    {"contestId": 1742, "index": "B", "name": "Increasing", "rating": 800, "tags": ["greedy"]},
    {"contestId": 1760, "index": "A", "name": "Medium Number", "rating": 800, "tags": ["greedy"]},
    {"contestId": 1791, "index": "A", "name": "Codeforces Checking", "rating": 800, "tags": ["greedy"]},
    {"contestId": 1807, "index": "A", "name": "Plus or Minus", "rating": 800, "tags": ["greedy"]},
    {"contestId": 1829, "index": "A", "name": "Love Story", "rating": 800, "tags": ["greedy"]},
    {"contestId": 1669, "index": "F", "name": "Eating Candies", "rating": 1000, "tags": ["greedy", "two pointers"]},
    {"contestId": 1669, "index": "H", "name": "Maximal AND", "rating": 1100, "tags": ["greedy", "math"]},
    {"contestId": 1624, "index": "D", "name": "Palindromes Coloring", "rating": 1400, "tags": ["greedy"]},
    {"contestId": 1742, "index": "F", "name": "Smaller", "rating": 1300, "tags": ["greedy"]},
    {"contestId": 158, "index": "A", "name": "Next Round", "rating": 800, "tags": ["greedy", "special"]}
]

def fetch_user_submissions_api(handle: str) -> List[Dict[str, Any]]:
    """Fetch user submissions from Codeforces API and normalize."""
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    logger.info(f"Querying Codeforces API for handle: {handle}")
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"Codeforces API error (HTTP {response.status_code}): {response.text}")
    
    data = response.json()
    if data.get("status") != "OK":
        raise RuntimeError(f"Codeforces API status failed: {data.get('comment', 'Unknown error')}")
    
    submissions = []
    for item in data.get("result", []):
        prob = item.get("problem", {})
        contest_id = prob.get("contestId")
        index = prob.get("index")
        if contest_id is None or index is None:
            continue
        
        problem_id = f"{contest_id}{index}"
        tags = prob.get("tags", [])
        rating = prob.get("rating", 800)
        verdict = "OK" if item.get("verdict") == "OK" else "FAILED"
        timestamp = item.get("creationTimeSeconds", 0)
        
        submissions.append({
            "problem_id": problem_id,
            "tags": tags,
            "rating": int(rating) if rating is not None else 800,
            "verdict": verdict,
            "timestamp": int(timestamp)
        })
    return submissions

def load_user_submissions_csv(csv_path: str) -> List[Dict[str, Any]]:
    """Load user submissions from fallback CSV and normalize."""
    logger.info(f"Loading user submissions from CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    
    submissions = []
    for _, row in df.iterrows():
        problem_id = str(row["problem_id"]).strip()
        tags_raw = row["tags"]
        if pd.isna(tags_raw):
            tags = []
        else:
            tags = [t.strip() for t in str(tags_raw).split(";") if t.strip()]
        
        rating = row["rating"]
        if pd.isna(rating):
            rating = 800
        else:
            rating = int(rating)
            
        verdict = "OK" if str(row["verdict"]).strip().upper() in ["OK", "SOLVED", "PASS"] else "FAILED"
        
        timestamp = row.get("timestamp", 0)
        if pd.isna(timestamp):
            timestamp = 0
        else:
            timestamp = int(timestamp)
            
        submissions.append({
            "problem_id": problem_id,
            "tags": tags,
            "rating": rating,
            "verdict": verdict,
            "timestamp": timestamp
        })
    return submissions

def fetch_problems_api() -> List[Dict[str, Any]]:
    """Fetch active problemset from Codeforces API."""
    url = "https://codeforces.com/api/problemset.problems"
    logger.info("Querying Codeforces API for all problems")
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"Codeforces API error (HTTP {response.status_code})")
        
    data = response.json()
    if data.get("status") != "OK":
        raise RuntimeError(f"Codeforces API status failed: {data.get('comment')}")
        
    problems = []
    for prob in data.get("result", {}).get("problems", []):
        contest_id = prob.get("contestId")
        index = prob.get("index")
        if contest_id is None or index is None:
            continue
            
        problem_id = f"{contest_id}{index}"
        name = prob.get("name", "Unknown Problem")
        rating = prob.get("rating")
        tags = prob.get("tags", [])
        
        # Filter out unrated or invalid problems
        if rating is None:
            continue
            
        problems.append({
            "contestId": int(contest_id),
            "index": index,
            "name": name,
            "rating": int(rating),
            "tags": tags
        })
    return problems

def get_problems(force_offline: bool = False) -> List[Dict[str, Any]]:
    """Get active problems list, falling back to offline db on failure."""
    if force_offline:
        logger.info("Using offline problems database by user request")
        return OFFLINE_PROBLEMS
        
    try:
        return fetch_problems_api()
    except Exception as e:
        logger.warning(f"Failed to fetch problems from Codeforces API: {e}. Falling back to offline database.")
        return OFFLINE_PROBLEMS
