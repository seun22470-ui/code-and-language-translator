# CodeT5 Translation & Interpretation Engine
# Integrates Salesforce CodeT5+ models for Code-to-English and English-to-Code translation

from typing import Dict, Any, Optional

try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class CodeT5Translator:
    """
    Production CodeT5 translation engine supporting:
    - Code to English (Code summarization and explanation)
    - English to Code (Code generation from natural language)
    - Code Refinement and Defect detection
    """

    def __init__(self, model_checkpoint: str = 'Salesforce/codet5p-220m', device: Optional[str] = None):
        self.model_checkpoint = model_checkpoint
        self.device = device or ('cuda' if TRANSFORMERS_AVAILABLE and torch.cuda.is_available() else 'cpu')
        self.tokenizer = None
        self.model = None

    def load_model(self):
        if not TRANSFORMERS_AVAILABLE:
            raise RuntimeError('Transformers and PyTorch are required to run CodeT5 locally.')
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_checkpoint)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_checkpoint).to(self.device)

    def code_to_english(self, code_snippet: str, max_length: int = 256) -> str:
        """Translates code in any programming language into a natural English explanation."""
        if self.model is None:
            self.load_model()
        prompt = f'Summarize and explain this code: {code_snippet}'
        inputs = self.tokenizer(prompt, return_tensors='pt', truncation=True).to(self.device)
        outputs = self.model.generate(**inputs, max_length=max_length)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def english_to_code(self, english_description: str, language: str = 'python', max_length: int = 512) -> str:
        """Translates natural English prompt into code in the requested programming language."""
        if self.model is None:
            self.load_model()
        prompt = f'Generate {language} code for: {english_description}'
        inputs = self.tokenizer(prompt, return_tensors='pt', truncation=True).to(self.device)
        outputs = self.model.generate(**inputs, max_length=max_length)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
