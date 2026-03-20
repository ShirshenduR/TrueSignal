import requests
from typing import Dict, Any

def fetch_leetcode_stats(username: str) -> Dict[str, Any]:
    """
    Fetches basic LeetCode stats using their unofficial GraphQL API.
    """
    if not username:
        return {}
        
    query = """
    query getUserProfile($username: String!) {
        matchedUser(username: $username) {
            submitStats: submitStatsGlobal {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
            profile {
                reputation
                ranking
            }
        }
    }
    """
    variables = {"username": username}
    url = "https://leetcode.com/graphql/"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            user_data = data.get('data', {}).get('matchedUser')
            if user_data:
                stats = user_data.get('submitStats', {}).get('acSubmissionNum', [])
                easy = next((s['count'] for s in stats if s['difficulty'] == 'Easy'), 0)
                medium = next((s['count'] for s in stats if s['difficulty'] == 'Medium'), 0)
                hard = next((s['count'] for s in stats if s['difficulty'] == 'Hard'), 0)
                total = next((s['count'] for s in stats if s['difficulty'] == 'All'), easy+medium+hard)
                return {
                    "platform": "LeetCode",
                    "total_solved": total,
                    "easy": easy,
                    "medium": medium,
                    "hard": hard,
                    "ranking": user_data.get('profile', {}).get('ranking', "N/A")
                }
    except Exception as e:
        print(f"LeetCode fetch error: {e}")
        
    return {"platform": "LeetCode", "total_solved": 0, "error": "Failed to fetch LeetCode data for Demo.", "mock": True}

def fetch_codeforces_stats(username: str) -> Dict[str, Any]:
    """
    Fetches Codeforces rating and max rating using their official API.
    """
    if not username:
        return {}
        
    url = f"https://codeforces.com/api/user.info?handles={username}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "OK" and len(data.get("result", [])) > 0:
                user = data["result"][0]
                return {
                    "platform": "Codeforces",
                    "rating": user.get("rating", 0),
                    "max_rating": user.get("maxRating", 0),
                    "rank": user.get("rank", "Unrated")
                }
    except Exception as e:
        print(f"Codeforces fetch error: {e}")
        
    return {"platform": "Codeforces", "rating": 0, "error": "Failed to fetch Codeforces data for Demo.", "mock": True}
