
import json         # for test load_method()
import os           # for test load_method()

from ModelCore import get_model_instance
from DAL.Summary_Repository import SummaryRepository
from GithubApi import get_readme, get_commits, get_issues, get_pull_requests, get_repo_metadata
from DAL.GithubRepositoriesList_Repository import get_repositories

# Import the shared model core
model_core = None
model_core = get_model_instance()

def get_core():
    global model_core
    if model_core is None:
        print("Initializing AI Model...", flush=True)
        model_core = get_model_instance()
    return model_core

# orchestrates repository analysis by using ModelCore to generate focused 
# summaries for a project’s README, commits, issues, and pull requests.
class Summarizer:
    def __init__(self, repo_name="unknown-repo"):
        self.repo_name = repo_name  # format "owner/repo"
        self.repo = SummaryRepository()
        self.model = get_model_instance()        

        # self.owner, self.repo_short = self._split_repo()
        # self.metadata = get_repo_metadata(self.owner, self.repo_short)
               
    # =======================================================================
    # For provided github repository, summarize readme file
    # =======================================================================
    def summarize_repo_readme(self, owner: str, repo: str) -> str:
        print("", flush=True);
        print("sumarize_repo_readme()", flush=True);
        
        print("Pulling data...", flush=True);
        self.repo_name = f"{owner}/{repo}"  
        readme_content = get_readme(owner, repo)
        metadata = get_repo_metadata(owner, repo)
        
        print("Setting up model request and sending...", flush=True);
        system_prompt = (
            "You are an expert software analyst. Your goal is to evaluate a GitHub repository and determine "
            "whether it is valuable to a potential user or contributor. Do NOT copy the README content. "
            "Provide thoughtful analysis, not just description."
        )
        user_prompt = (
            f"The repository has the following metadata:\n"
            f"- Stars: {metadata.get('stars', 'N/A')}\n"
            f"- Forks: {metadata.get('forks', 'N/A')}\n"
            f"- Open Issues: {metadata.get('open_issues', 'N/A')}\n"
            f"- Main Language: {metadata.get('language', 'N/A')}\n"
            f"- License: {metadata.get('license', 'N/A')}\n"
            f"- Last Updated: {metadata.get('updated_at', 'N/A')}\n\n"

            "Here is the README content:\n"
            f"{readme_content}\n\n"

            "📌 Using this information, provide a structured analysis:\n"
            "## ✅ What Problem This Solves\n"
            "- Explain the purpose of the project and why it exists.\n\n"
            "## 🚀 Strengths / Why It’s Valuable\n"
            "- Key advantages, features, or innovations.\n\n"
            "## ⚠️ Limitations or Weaknesses\n"
            "- Missing features, risks, complexity, required skills, etc.\n\n"
            "## 👥 Ideal Users / Use Cases\n"
            "- Who should use this? In what scenario?\n\n"
            "## ⭐ Final Verdict (1–10 Usefulness Score)\n"
            "- Justify your score briefly.\n"
        )
        full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n<|assistant|>"
        response = self.model.generate_response(prompt=full_prompt, max_new_tokens=400, temperature=0.3)
        
        print("Saving response...", flush=True);
        self.repo.save_summary(self.repo_name, "readme", {
            "metadata": metadata,
            "summary": response
        })
        
        print("Returning response!", flush=True);
        return response
                
    # =======================================================================
    # For provided github repository, summarize latest commits
    # =======================================================================
    def summarize_commits(self, owner: str, repo: str) -> str:
        print("", flush=True);
        print("summarize_commits()", flush=True);
        
        print("Pulling data...", flush=True);     
        self.repo_name = f"{owner}/{repo}"     
        commits = get_commits(owner, repo)
        metadata = get_repo_metadata(owner, repo)

        if not commits:
            print("⚠️ No commit data available to summarize.", flush=True);
            response = "No commit data available to summarize."
            self.repo.save_summary(self.repo_name, "commits", response)
            return response
        
        print("Setting up model request and sending...", flush=True);
        formatted_commits = "\n".join([f"- {msg}" for msg in commits])
        system_prompt = (
            "You are a technical AI that summarizes GitHub repository activity clearly and accurately."
        )
        user_prompt = f"""
            You will be given a list of recent commit messages for the repository **{self.repo_name}**.

            Please analyze them and provide a structured summary using the following format:

            ### ✅ Summary of Recent Development Activity

            **1. 🚀 New Features or Enhancements**
            - What new capabilities or improvements were added?

            **2. 🐛 Bug Fixes**
            - What problems or defects were addressed?

            **3. 🛠 Refactoring / Code Improvements**
            - Any improvements to architecture, performance, or readability?

            **4. ✨ Notable Technical Changes**
            - Dependencies updated? Major API changes? Breaking updates?

            **5. 📌 Overall Impact**
            - How do these changes contribute to the project direction or stability?

            Here are the commits to analyze:
            {formatted_commits}
            """
        full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n<|assistant|>"
        response = self.model.generate_response(prompt=full_prompt, max_new_tokens=400, temperature=0.3)
        
        print("Saving response...", flush=True);
        # self.repo.save_summary(self.repo_name, "commits", response)
        self.repo.save_summary(self.repo_name, "commits", {
            "metadata": metadata,
            "summary": response
        })
        
        print("Returning response!", flush=True);
        return response
        
    # =======================================================================
    # For provided github repository, summarize latest issues
    # =======================================================================
    def summarize_issues(self, owner: str, repo: str) -> str:
        print("", flush=True);
        print("summarize_issues()", flush=True);
        
        print("Pulling data...", flush=True);
        self.repo_name = f"{owner}/{repo}"  
        issues = get_issues(owner, repo)
        metadata = get_repo_metadata(owner, repo)

        if not issues:
            print("⚠️ No issues found for this repository.", flush=True);
            response = "⚠️ No issues found for this repository."
            self.repo.save_summary(self.repo_name, "issues", response)
            return response        
        
        print("Setting up model request and sending...", flush=True);
        formatted_issues = "\n".join([f"- {issue}" for issue in issues])
        system_prompt = (
            "You are a helpful AI system that analyzes GitHub issues "
            "and summarizes user pain points and feature requests."
        )
        user_prompt = f"""
            You are given **recent GitHub issues** from the repository **{self.repo_name}**.

            Summarize them using the format below:

            ### 🛑 User Issues & Problem Summary

            **1. 🐞 Common Bugs or Errors Reported**
            - What problems or technical issues are users facing?

            **2. 💡 Feature Requests or Improvements**
            - What new features or enhancements are users asking for?

            **3. 🎯 Recurring Themes or Root Causes**
            - Are there repeated complaints or related problems?

            **4. ⚠ Severity & Impact**
            - Are these issues minor annoyances or major blockers?

            **5. 📌 Overall Insight**
            - Summarize in 2–3 sentences what the issues suggest about the project's health.

            Here are the issues:
            {formatted_issues}
            """
        full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n<|assistant|>"
        response = self.model.generate_response(prompt=full_prompt, max_new_tokens=400, temperature=0.3)
        
        print("Saving response...", flush=True);
        # self.repo.save_summary(self.repo_name, "issues", response)
        self.repo.save_summary(self.repo_name, "issues", {
            "metadata": metadata,
            "summary": response
        })
    
        print("Returning response!", flush=True);
        return response
        
    # =======================================================================
    # For provided github repository, summarize latest pull requests
    # =======================================================================
    def summarize_pull_requests(self, owner: str, repo: str) -> str:
        print("", flush=True);
        print("summarize_pull_requests()", flush=True);
                
        print("Pulling data...", flush=True);
        self.repo_name = f"{owner}/{repo}"  
        pull_requests = get_pull_requests(owner, repo)
        metadata = get_repo_metadata(owner, repo)

        if not pull_requests:
            print("⚠️ No pull requests found for this repository.", flush=True);
            response = "⚠️ No pull requests found for this repository."
            self.repo.save_summary(self.repo_name, "pull_requests", response)
            return response
        
        print("Setting up model request and sending...", flush=True);
        formatted_prs = "\n".join([f"- {pr}" for pr in pull_requests])
        system_prompt = (
            "You are an expert AI that summarizes GitHub pull requests "
            "for developers, project maintainers, and stakeholders."
        )
        user_prompt = f"""
            You are given a list of **open or recent pull requests** from the repository **{self.repo_name}**.

            Summarize them using the format below:

            ### 🔄 Pull Request Summary

            **1. 🎯 Purpose of Changes**
            - What is each pull request trying to accomplish?

            **2. 🛠 Key Technical Changes**
            - Are they adding new features, fixing bugs, refactoring code, or updating documentation?

            **3. ⚠ Risks or Breaking Changes**
            - Could these PRs introduce side effects, large refactoring, or failure points?

            **4. ✅ Current Status or Review Notes**
            - Are PRs approved, under review, or blocked?

            **5. 📌 Overall Insight**
            - Provide a short summary of the development direction.

            Here are the PRs to analyze:
            {formatted_prs}
            """
        full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n<|assistant|>"
        response = self.model.generate_response(prompt=full_prompt, max_new_tokens=400, temperature=0.3)
        
        print("Saving response...", flush=True);
        # self.repo.save_summary(self.repo_name, "pull_requests", response)
        self.repo.save_summary(self.repo_name, "pull_requests", {
            "metadata": metadata,
            "summary": response
        })
        
        print("Returning response!", flush=True);
        return response
    
    # =======================================================================
    # Local load method to write out summaries (test only)
    # =======================================================================
    def load_summary(self, repo_name, summary_type):
        file_path = os.path.join("summaries", repo_name, f"{summary_type}_summary.json")

        if not os.path.exists(file_path):
            return None  # or return {} if you want an empty object instead

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        summary_text = data.get("summary", None)
        print("\n======= SUMMARY TEXT =======\n", flush=True)
        print(summary_text if summary_text else "⚠️ No summary text available")
        print("\n============================\n", flush=True)

        return summary_text  # Optional — remove this if you don’t want to return anything

# local test run entry point
if __name__ == "__main__":
    print("🧠 Starting Summarizer", flush=True)

    repos = get_repositories()
    for repo_name in repos:
        print(f"\n🚀 Processing {repo_name}\n", flush=True)
        s = Summarizer(repo_name)

        s.summarize_repo_readme()
        s.load_summary("microsoft/vscode", "readme")
        s.summarize_commits()
        s.load_summary("microsoft/vscode", "commits")
        s.summarize_issues()
        s.load_summary("microsoft/vscode", "issues")
        s.summarize_pull_requests()
        s.load_summary("microsoft/vscode", "pull_requests")

    
