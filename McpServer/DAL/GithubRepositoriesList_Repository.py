# GithubRepositoriesList_Repository.py

# List of GitHub repositories to analyze.
# Format: "owner/repo"
REPOSITORIES = [
    # 🔹 Popular, good-quality open-source projects to test on:
    "microsoft/vscode",          # Microsoft’s open-source code editor
    "torvalds/linux",            # Linux kernel (huge, good test for README parsing)
    "facebook/react",            # Popular JavaScript frontend library
    "pallets/flask",             # Lightweight Python web framework
    "django/django",             # Popular Python backend framework
    "numpy/numpy",               # Core Python library for scientific computing
    "huggingface/transformers",  # LLM/AI model library
    "fastapi/fastapi",           # Fast Python API framework (modern)
    "vercel/next.js",            # Full-stack React framework
    "nestjs/nest",               # Backend Node.js framework with TypeScript
]

def get_repositories():
    return REPOSITORIES
