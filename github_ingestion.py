import os
from github import Github
from github.GithubException import GithubException
from typing import Dict, Any

class GitHubParser:
    """
    A robust class that authenticates via a Personal Access Token (GITHUB_TOKEN)
    to parse a candidate's GitHub profile including commit quality.
    """
    def __init__(self):
        token = os.environ.get("GITHUB_TOKEN")
        self.gh = Github(token) if token else Github()

    def fetch_user_data(self, username: str) -> Dict[str, Any]:
        result = {
            "username": username,
            "repos_analyzed": 0,
            "total_commits": 0,
            "languages": {},
            "summary_text": "",
            "raw_repos": [],
            "error": None
        }

        try:
            user = self.gh.get_user(username)
            repos = list(user.get_repos(type="owner", sort="updated", direction="desc"))
            
            top_repos = repos[:6]
            result["repos_analyzed"] = len(top_repos)

            for repo in top_repos:
                repo_data = {
                    "name": repo.name,
                    "description": repo.description or "No description",
                    "language": repo.language or "Unknown",
                    "stars": repo.stargazers_count,
                    "commits": 0,
                    "recent_commit_messages": []
                }

                try:
                    commits = repo.get_commits()
                    commitsCount = commits.totalCount
                    repo_data["commits"] = commitsCount
                    result["total_commits"] += commitsCount
                    
                    # Grab top 3 commit messages for quality assessment
                    for c in commits[:3]:
                        msg = c.commit.message.split('\\n')[0]
                        repo_data["recent_commit_messages"].append(msg)
                except GithubException:
                    pass

                lang = repo_data["language"]
                if lang != "Unknown":
                    result["languages"][lang] = result["languages"].get(lang, 0) + 1

                result["raw_repos"].append(repo_data)

            # Compile structured text summary
            summary_lines = [f"Candidate: {username}", f"Total Repos Analyzed: {len(top_repos)}"]
            for r in result["raw_repos"]:
                summary_lines.append(
                    f"Repo: {r['name']} | Language: {r['language']} | Stars: {r['stars']} | Commits: {r['commits']}"
                )
                summary_lines.append(f"Description: {r['description']}")
                if r.get("recent_commit_messages"):
                    summary_lines.append(f"Recent Commits: {', '.join(r['recent_commit_messages'])}")
            
            result["summary_text"] = "\\n".join(summary_lines)

        except GithubException as e:
            print(f"GitHub API Error: {e}. Using fallback data for {username}.")
            result["error"] = str(e)
            result = self._get_fallback_data(username)

        return result

    def _get_fallback_data(self, username: str) -> Dict[str, Any]:
        """
        Fallback mock data with commit messages for demos.
        """
        dummy_repos = [
            {"name": "awesome-project", "description": "A scalable microservices architecture", "language": "Python", "stars": 42, "commits": 150, "recent_commit_messages": ["Refactor authentication layer", "Add unit tests"]},
            {"name": "react-frontend-app", "description": "Interactive UI dashboard using React and Tailwind", "language": "TypeScript", "stars": 15, "commits": 85, "recent_commit_messages": ["Fix responsive layout bug", "Update dependencies"]},
        ]
        
        summary_lines = [f"Candidate: {username} (MOCK DATA)", "Total Repos Analyzed: 2"]
        langs = {}
        commits = 0
        for r in dummy_repos:
            summary_lines.append(f"Repo: {r['name']} | Language: {r['language']} | Stars: {r['stars']} | Commits: {r['commits']}")
            summary_lines.append(f"Description: {r['description']}")
            summary_lines.append(f"Recent Commits: {', '.join(r['recent_commit_messages'])}")
            langs[r["language"]] = langs.get(r["language"], 0) + 1
            commits += r["commits"]

        return {
            "username": username,
            "repos_analyzed": len(dummy_repos),
            "total_commits": commits,
            "languages": langs,
            "summary_text": "\\n".join(summary_lines),
            "raw_repos": dummy_repos,
            "error": "Rate limited or User Not Found. Showing Mock Data."
        }
