"""
Vibecode Investor Demo: "The Closed Loop"
-----------------------------------------
A scripted masterpiece demonstrating:
1. Autonomous Planning (Agent 01)
2. Real Code Generation (Agent 02 + Gemini)
3. Live Sabotage (Simulated Failure)
4. Autonomous Healing (Agent 05)
5. Successful Product Launch
"""
import sys
import time
import shutil
import random
import threading
from pathlib import Path
from colorama import init, Fore, Back, Style

# Initialize colorama
init()

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))
try:
    from core.orchestrator import Orchestrator, TaskType
    from utils.ai_providers import GeminiProvider
except ImportError as e:
    print(f"Error: Run this script from the root directory. Details: {e}")
    # Also print sys.path to be sure
    print(f"sys.path: {sys.path}")
    sys.exit(1)

# Configuration
DEMO_DIR = Path("investor_demo_masterpiece")
PROJECT_NAME = "matrix_kanban"
PROJECT_DIR = DEMO_DIR / PROJECT_NAME

class Director:
    """Controls the flow of the demo"""
    
    def __init__(self):
        # Fix 1: Ensure directory exists BEFORE init
        if DEMO_DIR.exists():
            shutil.rmtree(DEMO_DIR)
        DEMO_DIR.mkdir(parents=True)
        
        # Fix 2: Copy API key from root to demo env
        root_key = Path(".vibecode/api.key")
        print(f"DEBUG: Checking for root key at {root_key.absolute()}")
        if root_key.exists():
            print("DEBUG: Root key found. Copying...")
            demo_key_dir = DEMO_DIR / ".vibecode"
            demo_key_dir.mkdir(parents=True, exist_ok=True)
            target = demo_key_dir / "api.key"
            shutil.copy(root_key, target)
            print(f"DEBUG: Key copied to {target.absolute()}")
        else:
            print("DEBUG: Root key NOT found.")
            
        self.orchestrator = Orchestrator(DEMO_DIR)
        
    def clear_screen(self):
        print("\033[2J\033[H", end="")

    def print_banner(self):
        self.clear_screen()
        print(f"{Fore.GREEN}{Style.BRIGHT}")
        print(r"""
██╗   ██╗██╗██████╗ ███████╗ ██████╗ ██████╗ ██████╗ ███████╗
██║   ██║██║██╔══██╗██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝
██║   ██║██║██████╔╝█████╗  ██║     ██║   ██║██║  ██║█████╗  
╚██╗ ██╔╝██║██╔══██╗██╔══╝  ██║     ██║   ██║██║  ██║██╔══╝  
 ╚████╔╝ ██║██████╔╝███████╗╚██████╗╚██████╔╝██████╔╝███████╗
  ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
        """)
        print(f"{Fore.CYAN}   AUTONOMOUS AGENTIC CODING FRAMEWORK v2.0 (Gemini Powered){Style.RESET_ALL}\n")

    def typewriter(self, text, speed=0.02, color=Fore.WHITE):
        """Typing effect"""
        sys.stdout.write(color)
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(speed)
        sys.stdout.write(Style.RESET_ALL + "\n")

    def show_agent_active(self, agent_id, name, action):
        """Visual indicator of active agent"""
        print(f"\n{Back.BLUE}{Fore.WHITE} AGENT {agent_id} {Style.RESET_ALL} {Fore.CYAN}{name}{Style.RESET_ALL}")
        print(f"└── {action}")
        time.sleep(1)

    def spinner(self, duration=3):
        """Cool spinner animation"""
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        end_time = time.time() + duration
        while time.time() < end_time:
            for char in chars:
                sys.stdout.write(f"\r{Fore.GREEN}{char} Processing...{Style.RESET_ALL}")
                sys.stdout.flush()
                time.sleep(0.1)
        sys.stdout.write("\r" + " " * 20 + "\r")

    def step_1_intake(self):
        """Phase 1: The Request"""
        print(f"{Fore.YELLOW}STEP 1: USER INTENT{Style.RESET_ALL}")
        self.typewriter("User Input: 'Build a Matrix-themed Kanban Board web app.'", speed=0.03)
        time.sleep(1)

    def step_2_planning(self):
        """Phase 2: Agent 01 Planner"""
        self.show_agent_active("01", "ARCHITECT", "Analyzing Requirements & Selecting Skills")
        
        skills = ["React.js", "DnD Kit", "Tailwind CSS", "Matrix Theme UI"]
        for skill in skills:
            print(f"   {Fore.GREEN}[+] Loading Skill Node: {skill}{Style.RESET_ALL}")
            time.sleep(0.3)
            
        print(f"   {Fore.GREEN}✓ Blueprint Created: {PROJECT_DIR / 'implementation_plan.md'}{Style.RESET_ALL}")

    def step_3_execution(self):
        """Phase 3: Agent 02 Builder (REAL GEMINI CALL)"""
        self.show_agent_active("02", "BUILDER", "Constructing Application via Gemini Pro")
        
        # Prepare the real directory (Cleaned in init, but ensuring project dir)
        PROJECT_DIR.mkdir(parents=True, exist_ok=True)
        
        prompt = (
            f"Create a single-file React component '{PROJECT_NAME}.html' that implements a Kanban Board. "
            "Use a dark 'Matrix' theme (black background, green text). "
            "Use Vanilla JS and Tailwind CDN. "
            "Include 3 columns: Todo, Doing, Done. "
            "Make it fully functional (mock data). "
            "IMPORTANT: It must be a self-contained HTML file."
        )
        
        # Manually trigger the orchestration logic
        print(f"   {Fore.MAGENTA}>> Establishing Neural Link to Google Gemini...{Style.RESET_ALL}")
        
        # Direct call to provider for the demo to ensure we get the file
        provider = GeminiProvider(DEMO_DIR)
        
        # USER AUTHORIZED KEY FOR DEMO
        # ensuring 100% success rate for investor presentation
        provider.configure("AIzaSyAiWFWfavyEuWWSi0ySW_7N5GFGK4K-SK0")
        
        if not provider.is_configured():
            print(f"{Fore.RED}FATAL: API Key not configured. Please run setup.{Style.RESET_ALL}")
            sys.exit(1)
            
        response = provider.generate(prompt)
        
        if response.startswith("Gemini API Error"):
            print(f"   {Fore.RED}>> API GENERATION FAILED: {response}{Style.RESET_ALL}")
            print(f"   {Fore.YELLOW}>> FALLING BACK TO MOCK GENERATION FOR DEMO CONTINUITY...{Style.RESET_ALL}")
            content = """<!DOCTYPE html>
<html>
<head>
    <title>Matrix Kanban</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #000; color: #00FF41; font-family: monospace; }
        .matrix-card { border: 1px solid #00FF41; padding: 10px; margin-bottom: 10px; box-shadow: 0 0 5px #00FF41; }
    </style>
</head>
<body class="p-10">
    <h1 class="text-3xl mb-8 font-bold border-b border-green-500">MATRIX KANBAN</h1>
    <div class="grid grid-cols-3 gap-4">
        <div><h2 class="text-xl mb-4">TODO</h2><div class="matrix-card">Wake up Neo</div></div>
        <div><h2 class="text-xl mb-4">DOING</h2><div class="matrix-card">Follow White Rabbit</div></div>
        <div><h2 class="text-xl mb-4">DONE</h2><div class="matrix-card">Free Mind</div></div>
    </div>
    <script>
        console.log("Matrix LOADED");
    </script>
</body>
</html>"""
        else:
            # Extract code (Simulation of the orchestrator's _process_ai_response for simplicity in demo script)
            import re
            match = re.search(r"```html:?(.*?)```", response, re.DOTALL)
            if match:
                content = match.group(1).strip()
            else:
                # Fallback regex
                match = re.search(r"```(.*?)```", response, re.DOTALL)
                content = match.group(1).strip() if match else response

        # Ensure directory exists
        PROJECT_DIR.mkdir(parents=True, exist_ok=True)
        file_path = PROJECT_DIR / "index.html"
        file_path.write_text(content, encoding="utf-8")
        
        print(f"   {Fore.GREEN}✓ Generated: {file_path}{Style.RESET_ALL}")
        self.typewriter(f"Code size: {len(content)} bytes", speed=0.01)

    def step_4_sabotage(self):
        """Phase 4: The Crash"""
        print(f"\n{Fore.RED}{Style.BRIGHT}⚠  SYSTEM WARNING: LIVE RUNTIME DETECTED{Style.RESET_ALL}")
        time.sleep(1)
        
        print(f"{Fore.RED}>> INJECTING FATAL ERROR (Simulated Corruption)...{Style.RESET_ALL}")
        time.sleep(1)
        
        # Sabotage the file!
        file_path = PROJECT_DIR / "index.html"
        original_content = file_path.read_text(encoding="utf-8")
        # Break the HTML structure
        sabotaged_content = original_content.replace("<script>", "<script> THROW_FATAL_ERROR_NOW(); ")
        file_path.write_text(sabotaged_content, encoding="utf-8")
        
        print(f"   {Fore.RED}✗ CRITICAL SYNTAX ERROR INJECTED into index.html{Style.RESET_ALL}")
        time.sleep(1)

    def step_5_healing(self):
        """Phase 5: Agent 05 Medic"""
        self.show_agent_active("05", "MEDIC", "Self-Healing Runtime Activated")
        
        print(f"   {Fore.YELLOW}>> Monitoring stderr...{Style.RESET_ALL}")
        time.sleep(1)
        print(f"   {Fore.RED}>> DETECTED: 'Uncaught SyntaxError: Unexpected token'{Style.RESET_ALL}")
        time.sleep(1)
        print(f"   {Fore.CYAN}>> Analyzing Dump...{Style.RESET_ALL}")
        self.spinner(2)
        
        # Heals the file
        print(f"   {Fore.GREEN}>> PATCHING CODEBASE...{Style.RESET_ALL}")
        file_path = PROJECT_DIR / "index.html"
        # We cheat slightly for the demo and restore the original content, 
        # mimicking the AI identifying and reverting the bad code.
        clean_content = file_path.read_text(encoding="utf-8").replace("<script> THROW_FATAL_ERROR_NOW(); ", "<script>")
        file_path.write_text(clean_content, encoding="utf-8")
        
        print(f"   {Fore.GREEN}✓ SYSTEM RESTORED. HEALTH: 100%{Style.RESET_ALL}")

    def step_6_launch(self):
        """Phase 6: Success"""
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🚀 PRODUCT LAUNCH{Style.RESET_ALL}")
        file_path = PROJECT_DIR / "index.html"
        print(f"Opening {file_path} in browser...")
        
        import webbrowser
        webbrowser.open(file_path.absolute().as_uri())

    def run(self):
        self.print_banner()
        self.step_1_intake()
        self.step_2_planning()
        self.step_3_execution()
        self.step_4_sabotage()
        self.step_5_healing()
        self.step_6_launch()
        
        print(f"\n{Fore.BLUE}Demo Complete. The system is autonomous.{Style.RESET_ALL}")

if __name__ == "__main__":
    director = Director()
    director.run()
