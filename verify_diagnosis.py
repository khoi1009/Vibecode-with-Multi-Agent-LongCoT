
import sys
from pathlib import Path

# Add root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.diagnostician import Diagnostician
from utils.ai_providers import GeminiProvider

def test_diagnosis():
    print("Initializing Diagnostician...")
    provider = GeminiProvider(Path.cwd())
    
    # Use the authorized demo key for verification
    provider.configure("AIzaSyAiWFWfavyEuWWSi0ySW_7N5GFGK4K-SK0")
    
    if not provider.is_configured():
        print("SKIPPING: No API Key available for diagnosis test.")
        return

    diagnostician = Diagnostician(provider)

    # Simulated Stack Trace (Division by Zero)
    sample_stderr = """
Traceback (most recent call last):
  File "calculator.py", line 10, in <module>
    result = divide_numbers(10, 0)
  File "calculator.py", line 5, in divide_numbers
    return a / b
ZeroDivisionError: division by zero
    """

    print("\nSimulating Crash: ZeroDivisionError")
    print("-" * 30)
    print(sample_stderr)
    print("-" * 30)

    diagnosis = diagnostician.analyze_error(sample_stderr, context="A simple calculator script.")

    print("\nDIAAGNOSIS RESULT:")
    print(f"Type: {diagnosis.error_type}")
    print(f"Summary: {diagnosis.summary}")
    print(f"Root Cause: {diagnosis.root_cause}")
    print(f"Suggested Fix: {diagnosis.suggested_fix}")

if __name__ == "__main__":
    test_diagnosis()
