#calls GitHub REST/GraphQL API.
class my_class(object):
    pass

# 4. github_api.py
# Role: Connects to GitHub REST/GraphQL API.
# What it does:
#   Authenticates with GitHub token.
#   Functions like:
#       get_repo_metadata(repo_name: str) -> dict
#       search_trending_repos(topic: str) -> list[dict]
#       get_recent_commits(repo_name: str) -> list[dict]
#   Handles pagination, rate limiting, retries.

# Think of it like: the “data source” layer.


