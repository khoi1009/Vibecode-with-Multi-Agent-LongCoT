
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import Orchestrator
from utils.ai_providers import GeminiProvider

def run_healing_test():
    workspace = Path.cwd()
    
    # Configure provider explicitly for the test (just in case)
    provider = GeminiProvider(workspace)
    if not provider.is_configured():
        provider.configure("AIzaSyAiWFWfavyEuWWSi0ySW_7N5GFGK4K-SK0")
        
    orchestrator = Orchestrator(workspace)
    
    # Create valid project structure expectation
    target_dir = workspace / "sabotage_project"
    target_dir.mkdir(exist_ok=True)
    
    # Move the sabotage file into the project dir
    source = workspace / "sabotage_test.py"
    target = target_dir / "app.py"
    target.write_text(source.read_text())
    
    print("\n[TEST] Initiating Self-Healing Verification...")
    print(f"[TEST] Target: {target}")
    
    # Run the orchestrator's healing loop
    orchestrator._run_with_healing(target_dir)

if __name__ == "__main__":
    run_healing_test()
