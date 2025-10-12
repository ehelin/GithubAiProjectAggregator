import os
import warnings
import contextlib
import io
import torch
import time

from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import snapshot_download  # external Hugging Face utility

try:
    from peft import PeftModel
except ImportError:
    PeftModel = None


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
    def __init__(self, 
                model_name: str = "microsoft/Phi-3.5-mini-instruct",
                adapter_path: str = "./fine_tuned_phi_habits",
                device: str = "cpu",
                safe_mode = True,
                max_new_tokens: int = 100,
                temperature: float = 0.5,
                top_p: float = 0.9):
        
        self.model_name = model_name
        self.adapter_path = adapter_path
        self.device = device
        self.safe_mode = safe_mode
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """
        Load the Phi-3.5 Mini model safely.
        - Enforces safe-mode isolation (no remote code execution).
        - Downloads model files once if not present in local cache.
        - Loads tokenizer and model from disk.
        - Optionally loads local LoRA adapters if found.
        """

        start_time = time.time()
        print(f"\n🧠 Loading model: {self.model_name}")
        print(f"Safe mode: {'ON' if self.safe_mode else 'OFF'}")

        # --------------------------------------------
        # Safe-mode environment setup
        # --------------------------------------------
        if self.safe_mode:
            os.environ["TRANSFORMERS_OFFLINE"] = "1"
            os.environ["HF_HUB_OFFLINE"] = "1"
            trust_remote = False

            # Ensure a local cache directory exists for Hugging Face
            if not os.getenv("HF_HUB_CACHE"):
                Test = os.path.expanduser("~/.cache/huggingface")
                os.environ["HF_HUB_CACHE"] = os.path.expanduser("~/.cache/huggingface")
        else:
            trust_remote = True

        cache_dir = os.getenv("HF_HUB_CACHE", os.path.expanduser("~/.cache/huggingface"))
        model_dir = os.path.join(cache_dir, self.model_name.replace("/", "--"))

        # --------------------------------------------
        # Verify model integrity (whitelist)
        # --------------------------------------------
        allowed_models = ["microsoft/Phi-3.5-mini-instruct"]
        if self.model_name not in allowed_models:
            raise ValueError(f"Untrusted model repository: {self.model_name}")

        # --------------------------------------------
        # Ensure model exists locally (download if missing)
        # --------------------------------------------
        if not os.path.exists(model_dir):
            print(f"Model not found in local cache at: {model_dir}")
            print("Downloading verified model from Hugging Face (once)...")

            snapshot_download(
                repo_id=self.model_name,
                local_dir=model_dir,
                local_dir_use_symlinks=False,
                allow_patterns=["*.bin", "*.json", "*.safetensors", "*.model"],
                resume_download=True,
            )
            print("Model download completed.\n")
        else:
            print(f"✅ Model already cached at: {model_dir}\n")

        # --------------------------------------------
        # Load tokenizer and model
        # --------------------------------------------
        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_dir,
            trust_remote_code=trust_remote
        )

        print("Loading base model (this may take a moment)...")
        self.model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            trust_remote_code=trust_remote,
            torch_dtype=torch.float32,
            device_map=self.device,
            low_cpu_mem_usage=True
        )

        # --------------------------------------------
        # Safe local adapter load
        # --------------------------------------------
        if (
            PeftModel
            and os.path.exists(self.adapter_path)
            and self.adapter_path.startswith("./")
        ):
            print(f"Loading LoRA adapters from {self.adapter_path}...")
            self.model = PeftModel.from_pretrained(self.model, self.adapter_path)
            print("Adapters loaded successfully.")
        else:
            print("Skipping adapter load for safety or missing path.")

        elapsed = time.time() - start_time
        print(f"✅ Model ready (loaded in {elapsed:.2f} seconds)\n")

  
    def generate_response(self, input_text: str) -> str:
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded")

        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                do_sample=True,
            )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.strip()
    
    # Summarizer methods
    def summarize_repo_readme(self):
        print("sumarize_repo_readme()");
        
    def summarize_commits(self):
        print("summarize_commits()");
        
    def summarize_issues(self):
        print("summarize_issues()");
        
    def summarize_pull_requests(self):
        print("summarize_pull_requests()");

if __name__ == "__main__":
    print("🧠 Starting local Summarizer test (safe mode ON)\n")
    print("Type your prompt and press Enter. Type 'exit' or 'quit' to stop.\n")

    s = Summarizer(safe_mode=True)

    while True:
        try:
            user_input = input(">>> ").strip()
            if user_input.lower() in {"exit", "quit"}:
                print("Exiting Summarizer. Goodbye!")
                break
            if not user_input:
                continue  # skip empty input
            response = s.generate_response(user_input)
            print("\n--- Model Response ---\n")
            print(response)
            print("\n----------------------\n")
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting Summarizer.")
            break
        except Exception as e:
            print(f"\n[Error] {type(e).__name__}: {e}\n")
