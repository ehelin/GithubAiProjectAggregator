# GithubApi.py

import requests
import base64

# Optional: Add your token here or load from environment variable later
GITHUB_TOKEN = None  # or: os.getenv("GITHUB_TOKEN")

BASE_URL = "https://api.github.com"

def get_repo_metadata(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json()
    return {
        "full_name": data.get("full_name", ""),
        "description": data.get("description", ""),
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "open_issues": data.get("open_issues_count", 0),
        "language": data.get("language", ""),
        "license": data.get("license", {}).get("name", "Unknown") if data.get("license") else "Unknown",
        "updated_at": data.get("updated_at", ""),
        "watchers": data.get("subscribers_count", 0),
    }

def _make_request(endpoint: str):
    """
    Internal helper: makes an authenticated or anonymous HTTP request to GitHub API.
    """
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    if response.status_code != 200:
        raise Exception(f"GitHub API Error {response.status_code}: {response.text}")
    return response.json()


# ✅ 1. Get README.md content (decoded to plain text)
def get_readme(owner: str, repo: str) -> str:
    data = _make_request(f"/repos/{owner}/{repo}/readme")

    if "content" in data:
        return base64.b64decode(data["content"]).decode("utf-8")
    else:
        return "(No README found for this repository)"


# ✅ 2. Get latest commit messages
def get_commits(owner: str, repo: str, limit: int = 10) -> list[str]:
    data = _make_request(f"/repos/{owner}/{repo}/commits")

    commits = []
    for item in data[:limit]:
        message = item.get("commit", {}).get("message", "")
        commits.append(message)
    return commits


# ✅ 3. Get open issues (title + body)
def get_issues(owner: str, repo: str, limit: int = 10) -> list[str]:
    data = _make_request(f"/repos/{owner}/{repo}/issues")

    issues = []
    for item in data[:limit]:
        # Exclude pull requests (GitHub treats them as issues with "pull_request" key)
        if "pull_request" in item:
            continue
        title = item.get("title", "")
        body = item.get("body", "") or ""
        issues.append(f"{title} - {body[:100]}")  # Truncate body for prompt safety
    return issues


# ✅ 4. Get open pull requests (title + description)
def get_pull_requests(owner: str, repo: str, limit: int = 10) -> list[str]:
    data = _make_request(f"/repos/{owner}/{repo}/pulls")

    prs = []
    for item in data[:limit]:
        title = item.get("title", "")
        body = item.get("body", "") or ""
        prs.append(f"{title} - {body[:100]}")
    return prs
