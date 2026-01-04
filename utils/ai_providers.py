"""
AI Provider Module
Handles communication with Google Gemini API
"""
import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import google.generativeai as genai

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class KeyManager:
    """Manages secure storage of API keys"""
    def __init__(self, workspace: Path):
        self.config_dir = workspace / ".vibecode"
        self.config_dir.mkdir(exist_ok=True)
        self.key_file = self.config_dir / "api.key"
        
    def save_key(self, key: str):
        """Save API key to disk"""
        self.key_file.write_text(key.strip(), encoding="utf-8")
        
    def load_key(self) -> Optional[str]:
        """Load API key from disk or environment"""
        # 1. Check environment
        env_key = os.getenv("GOOGLE_API_KEY")
        if env_key:
            return env_key
            
        # 2. Check file
        if self.key_file.exists():
            return self.key_file.read_text(encoding="utf-8").strip()
            
        return None

class GeminiProvider:
    """Interface for Google Gemini API"""
    
    def __init__(self, workspace: Path):
        self.key_manager = KeyManager(workspace)
        self.api_key = self.key_manager.load_key()
        self.model = None
        
        if self.api_key:
            self.configure(self.api_key)
            
    def configure(self, api_key: str):
        """Configure the Gemini client"""
        self.api_key = api_key
        try:
            genai.configure(api_key=api_key)
            # Use gemini-1.5-flash as it is free and reliable
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.key_manager.save_key(api_key)
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ Config failed: {e}{Colors.ENDC}")
            return False
            
    def is_configured(self) -> bool:
        return self.api_key is not None and self.model is not None

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate content using Gemini
        
        Args:
            prompt: Full context prompt
            temperature: Creativity (0.0 - 1.0)
            
        Returns:
            Generated text response
        """
        if not self.is_configured():
            return "Error: Gemini API not configured. Please run setup."

        try:
            # Add safety settings to prevent blocking legitimate code generation
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=8192,
                ),
                safety_settings=safety_settings
            )
            
            return response.text
            
        except Exception as e:
            error_msg = f"Gemini API Error: {str(e)}"
            return error_msg
