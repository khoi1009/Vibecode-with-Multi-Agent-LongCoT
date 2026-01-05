"""
Diagnostician Module
-------------------
The "Eyes" of the self-healing system.
Responsible for analyzing stack traces and classifying errors.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json

from utils.ai_providers import GeminiProvider, Colors

class ErrorType(Enum):
    SYNTAX = "SYNTAX"           # Typos, indentation, missing colons
    LOGIC = "LOGIC"             # Wrong math, null pointers, infinite loops
    ENVIRONMENT = "ENVIRONMENT" # Missing pip packages, ports in use
    RUNTIME = "RUNTIME"         # Crashes during execution (generic)
    UNKNOWN = "UNKNOWN"

@dataclass
class ErrorDiagnosis:
    error_type: ErrorType
    summary: str
    file_path: Optional[str]
    line_number: Optional[int]
    root_cause: str
    suggested_fix: str

class Diagnostician:
    def __init__(self, ai_provider: GeminiProvider):
        self.ai_provider = ai_provider

    def analyze_error(self, stderr: str, context: str = "") -> ErrorDiagnosis:
        """
        Analyze a stack trace using Gemini to understand the root cause.
        """
        print(f"   {Colors.CYAN}[Diagnostician] Analyzing stack trace...{Colors.ENDC}")
        
        prompt = f"""
        ACT AS: Expert Python Debugger.
        
        TASK: Analyze the following error log/stack trace.
        
        CONTEXT:
        {context}
        
        ERROR LOG:
        {stderr}
        
        OUTPUT FORMAT:
        Return ONLY a JSON object with this structure (no markdown):
        {{
            "error_type": "SYNTAX" | "LOGIC" | "ENVIRONMENT" | "RUNTIME",
            "summary": "Short 1-line description of what broke",
            "file_path": "Path to the file causing the crash (or null)",
            "line_number": 123 (or null),
            "root_cause": "Detailed explanation of why this happened",
            "suggested_fix": "Description of the code change needed"
        }}
        """
        
        try:
            response = self.ai_provider.generate(prompt)
            # Robust cleanup: find the first { and last }
            start = response.find("{")
            end = response.rfind("}") + 1
            
            if start != -1 and end != 0:
                cleaned_response = response[start:end]
                data = json.loads(cleaned_response)
            else:
                raise ValueError("No JSON object found in response")
            
            return ErrorDiagnosis(
                error_type=ErrorType(data.get("error_type", "UNKNOWN")),
                summary=data.get("summary", "Unknown error"),
                file_path=data.get("file_path"),
                line_number=data.get("line_number"),
                root_cause=data.get("root_cause", ""),
                suggested_fix=data.get("suggested_fix", "")
            )
            
        except Exception as e:
            print(f"   {Colors.RED}[Diagnostician] Analysis failed: {e}{Colors.ENDC}")
            print(f"   {Colors.YELLOW}[DEBUG] Raw Response:\n{response if 'response' in locals() else 'None'}{Colors.ENDC}")
            return ErrorDiagnosis(
                error_type=ErrorType.UNKNOWN,
                summary="AI Analysis Failed",
                file_path=None,
                line_number=None,
                root_cause=str(e),
                suggested_fix="Manual intervention required"
            )
