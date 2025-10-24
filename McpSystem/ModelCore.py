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

from typing import List

# Core class that wraps Phi-3 Model.
class ModelCore:
    def __init__(self, 
                model_name: str = "microsoft/Phi-3.5-mini-instruct",
                adapter_path: str = "./fine_tuned_phi_habits",
                device: str = "cpu",
                safe_mode = True,
                max_new_tokens: int = 300,
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

    # ModelCore.py  (replace your generate_response with this)
    def generate_response(self, prompt: str, max_new_tokens: int = 400, temperature: float = 0.3) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.05,
            eos_token_id=self.tokenizer.eos_token_id,
        )

        # ⚠️ Only decode the newly generated tokens (exclude the prompt)
        generated_ids = outputs[0][inputs.input_ids.shape[-1]:]
        text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        return text.strip()
    
# Singleton instance for shared use
_model_instance: ModelCore = None

def get_model_instance(**kwargs) -> ModelCore:
    global _model_instance
    if _model_instance is None:
       _model_instance = ModelCore(**kwargs)
    return _model_instance

def reset_model_instance():
    global _model_instance
    _model_instance = None  

# ------------------------------------------------
# Testing only code start
if __name__ == "__main__":
    print("🧠 Starting local Summarizer test (safe mode ON)\n")
    print("Type your prompt and press Enter. Type 'exit' or 'quit' to stop.\n")

    s = ModelCore(safe_mode=True)

    while True:
        try:
            user_input = input(">>> ").strip()
            if user_input.lower() in {"exit", "quit"}:
                print("Exiting Summarizer. Goodbye!")
                break
            if not user_input:
                continue  # skip empty input
            response = s.generate_response(prompt=user_input, max_new_tokens=400, temperature=0.3)
            print("\n--- Model Response ---\n")
            print(response)
            print("\n----------------------\n")
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting Summarizer.")
            break
        except Exception as e:
            print(f"\n[Error] {type(e).__name__}: {e}\n")            
# ------------------------------------------------
