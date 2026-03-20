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
            # Proactive Rate Limit Check
            rate_limit = self.gh.get_rate_limit().rate
            if rate_limit.remaining < 50:
                raise GithubException(403, {"message": f"GitHub Rate Limit critically low ({rate_limit.remaining} remaining). Please wait until {rate_limit.reset}."}, {})

            user = self.gh.get_user(username)
            # Fetch top 30 by recency first (metadata only)
            repos_paged = user.get_repos(type="owner", sort="updated", direction="desc")
            all_repos = []
            for r in repos_paged[:30]:
                all_repos.append(r)
            
            # Blended Sort: Sort by Stars (Impact) first, then Updated (Recency)
            # This handles the "0 stars" case by falling back to most recent work.
            all_repos.sort(key=lambda x: (x.stargazers_count, x.updated_at), reverse=True)
            
            top_repos = all_repos[:10]
            result["repos_analyzed"] = len(top_repos)

            for repo in top_repos:
                repo_data = {
                    "name": repo.name,
                    "description": repo.description or "No description",
                    "languages": [],
                    "stars": repo.stargazers_count,
                    "commits": 0,
                    "recent_commit_messages": []
                }

                try:
                    # Deep language analysis
                    repo_langs = repo.get_languages()
                    repo_data["languages"] = list(repo_langs.keys())
                    for lang, bytes_count in repo_langs.items():
                        result["languages"][lang] = result["languages"].get(lang, 0) + bytes_count

                    # Optimized commit fetch
                    commits = repo.get_commits()
                    repo_data["commits"] = commits.totalCount
                    result["total_commits"] += repo_data["commits"]
                    
                    # Grab top 3 commit messages
                    for c in commits[:3]:
                        msg = c.commit.message.split('\n')[0]
                        repo_data["recent_commit_messages"].append(msg)
                except GithubException:
                    pass

                result["raw_repos"].append(repo_data)

            # Compile structured text summary
            # Start with Global Polyglot Profile
            sorted_langs = sorted(result["languages"].items(), key=lambda x: x[1], reverse=True)
            global_langs_str = ", ".join([f"{l[0]}" for l in sorted_langs[:5]])
            
            summary_lines = [
                f"Candidate: {username}",
                f"Global Tech Stack (Top 5): {global_langs_str}",
                f"Total Repos Analyzed: {len(top_repos)}"
            ]
            
            for r in result["raw_repos"]:
                langs_str = ", ".join(r['languages'])
                summary_lines.append(
                    f"Repo: {r['name']} | Languages: {langs_str} | Stars: {r['stars']} | Commits: {r['commits']}"
                )
                summary_lines.append(f"Description: {r['description']}")
                if r.get("recent_commit_messages"):
                    summary_lines.append(f"Recent Commits: {', '.join(r['recent_commit_messages'])}")
            
            result["summary_text"] = "\n".join(summary_lines)

        except GithubException as e:
            print(f"GitHub API Error: {e}")
            result["error"] = str(e.data.get('message', e)) if hasattr(e, 'data') else str(e)

        return result
