# DAL/Summary_Repository.py

import os
import json
from datetime import datetime

class SummaryRepository:
    """
    Handles saving and loading AI-generated summaries for repositories.
    Files are stored under:
        summaries/<repo_name>/<summary_type>_summary.json
    """

    def __init__(self, base_dir="summaries"):
        self.base_dir = base_dir

    def _get_file_path(self, repo_name: str, summary_type: str) -> str:
        """
        Internal helper to build the JSON file path.
        """
        folder_path = os.path.join(self.base_dir, repo_name)
        os.makedirs(folder_path, exist_ok=True)
        return os.path.join(folder_path, f"{summary_type}_summary.json")

    def save_summary(self, repo_name, summary_type, data):
        """
        data should now be a dict:
        {
            "metadata": {},
            "summary": "..."
        }
        """
        folder_path = os.path.join("summaries", repo_name)
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, f"{summary_type}_summary.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_summary(self, repo_name: str, summary_type: str):
        """
        Loads a summary from disk.
        Returns None if the file does not exist.
        """
        file_path = self._get_file_path(repo_name, summary_type)

        if not os.path.exists(file_path):
            print(f"⚠️ No {summary_type} summary found for repo '{repo_name}'.")
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
