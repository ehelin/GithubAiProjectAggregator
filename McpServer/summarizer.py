# Import the shared model core
from ModelCore import get_model_instance

model_core = None
model_core = get_model_instance()

def get_core():
    global model_core
    if model_core is None:
        print("Initializing AI Model...")
        model_core = get_model_instance()
    return model_core

# orchestrates repository analysis by using ModelCore to generate focused 
# summaries for a project’s README, commits, issues, and pull requests.
class Summarizer:
   
    # Summarizer methods
    def summarize_repo_readme(self):
        print("sumarize_repo_readme()");
        
        message = "What is 1 + 2?"
        response = get_core().generate_response(message)
        print(f"Response - {response}")
        
    def summarize_commits(self):
        print("summarize_commits()");
        
        message = "What is 1 + 3?"
        response = get_core().generate_response(message)
        print(f"Response - {response}")
        
    def summarize_issues(self):
        print("summarize_issues()");
        
        message = "What is 1 + 4?"
        response = get_core().generate_response(message)
        print(f"Response - {response}")
        
    def summarize_pull_requests(self):
        print("summarize_pull_requests()");
        
        message = "What is 1 + 5?"
        response = get_core().generate_response(message)
        print(f"Response - {response}")

if __name__ == "__main__":
    print("🧠 Starting local Summarizer test (safe mode ON)\n")
    print("Type your prompt and press Enter. Type 'exit' or 'quit' to stop.\n")

    s = Summarizer()

    s.summarize_repo_readme();
    s.summarize_commits();
    s.summarize_issues();
    s.summarize_pull_requests();

    end = 1;


# 2. summarizer.py
# Role: Wraps the Phi-3 Mini model (local inference).
# What it does:
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
