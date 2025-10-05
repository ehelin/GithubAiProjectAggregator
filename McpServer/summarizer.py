# 2. summarizer.py
# Role: Wraps the Phi-3 Mini model (local inference).
# What it does:
#   Loads Phi-3 (from ONNX, GGUF, or local API).
#   Provides a function like summarize_repo(readme_text: str) -> str.
#   Encapsulates all model-specific details (tokenization, max length, truncation).
# Think of it like: a service class that abstracts away the model details.

# Example high-level logic:
# def summarize_repo(readme_text: str) -> str:
#     # Preprocess
#     prompt = f"Summarize this repository:\n{readme_text}"
#     # Call Phi-3 model
#     summary = phi3_model.generate(prompt, max_tokens=200)
#     return summary

from typing import List

# wraps Phi-3 Mini.
class Summarizer:
    """
    Summarizer class for handling different GitHub-related
    summarization tasks using the Phi-3 model.
    """

    def summarize_repo_readme(self, readme_text: str) -> str:
        """
        Summarize the README of a GitHub repository.
        """
        raise NotImplementedError("summarize_repo_readme is not implemented yet.")

    def summarize_commits(self, commits: List[str]) -> str:
        """
        Summarize a list of commit messages into a digest/changelog.
        """
        raise NotImplementedError("summarize_commits is not implemented yet.")

    def summarize_issues(self, issues: List[str]) -> str:
        """
        Summarize a set of GitHub issues into a single paragraph.
        """
        raise NotImplementedError("summarize_issues is not implemented yet.")

    def summarize_pull_requests(self, prs: List[str]) -> str:
        """
        Summarize open pull requests into a digest.
        """
        raise NotImplementedError("summarize_pull_requests is not implemented yet.")
