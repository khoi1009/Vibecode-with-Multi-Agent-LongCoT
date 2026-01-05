#!/usr/bin/env python3
"""
Vibecode Studio - Your AI Development Team in a Box
Main entry point for the Vibecode multi-agent system
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import codecs
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

from core.orchestrator import Orchestrator
from utils.ai_providers import GeminiProvider

# Version
VERSION = "1.0.0"
PRODUCT_NAME = "Vibecode Studio"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def print_banner():
    """Display Vibecode Studio banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
========================================================
    VIBECODE STUDIO - AI Development Team
========================================================
{Colors.ENDC}
{Colors.DIM}Your AI Development Team in a Box{Colors.ENDC}
{Colors.DIM}Version {VERSION}{Colors.ENDC}
{Colors.DIM}--------------------------------------------------------{Colors.ENDC}
"""
    print(banner)

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}\n")

def print_section(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}▶ {text}{Colors.ENDC}")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.DIM}{text}{Colors.ENDC}")


class VibecodeSudio:
    """
    Main Vibecode Studio application
    Coordinates agents, skills, and user interaction
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.workspace = Path.cwd()
        self.vibecode_dir = self.workspace / ".vibecode"
        self.state_file = self.vibecode_dir / "state.json"
        self.context_file = self.vibecode_dir / "project_context.md"
        
        # Load state
        self.state = self.load_state()
        
        # Initialize components
        self.agents_available = self.detect_agents()
        self.skills_available = self.detect_skills()
        self.ai_provider = GeminiProvider(self.workspace)
    
    def detect_agents(self) -> List[Dict]:
        """Detect available agents"""
        agents_dir = self.base_dir / "agents"
        if not agents_dir.exists():
            return []
        
        agents = []
        for agent_file in agents_dir.glob("agent_*.py"):
            agent_name = agent_file.stem.replace("agent_", "")
            agents.append({
                "name": agent_name,
                "file": agent_file,
                "available": True
            })
        
        return agents
    
    def detect_skills(self) -> List[Dict]:
        """Detect available skills"""
        skills_dir = self.base_dir / "skills"
        if not skills_dir.exists():
            return []
        
        skills = []
        for category_dir in skills_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('_'):
                for skill_dir in category_dir.iterdir():
                    if skill_dir.is_dir():
                        skill_md = skill_dir / "SKILL.md"
                        if skill_md.exists():
                            skills.append({
                                "name": skill_dir.name,
                                "category": category_dir.name,
                                "path": skill_dir,
                                "available": True
                            })
        
        return skills
    
    def load_state(self) -> Dict:
        """Load current state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "initialized": False,
            "project_scanned": False,
            "current_phase": "IDLE",
            "active_agents": []
        }
    
    def save_state(self):
        """Save current state"""
        self.vibecode_dir.mkdir(exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def show_main_menu(self):
        """Display main menu"""
        print_header("MAIN MENU")
        print(f"{Colors.BOLD}What would you like to do?{Colors.ENDC}\n")
        
        menu_items = [
            ("1", "🔍 Scan Project", "Analyze current project structure"),
            ("2", "🏗️  Build Feature", "Create new feature with agents"),
            ("3", "🐛 Fix Bug", "Diagnose and fix issues"),
            ("4", "🚀 New Fullstack App", "Scaffold a new project from scratch"),
            ("5", "✅ Run Tests", "Generate and run tests"),
            ("6", "📦 Ship Release", "Prepare for deployment"),
            ("7", "🤖 List Agents", "Show all available agents"),
            ("8", "🔧 List Skills", "Show all available skills"),
            ("9", "⚙️  Settings", "Configure Vibecode"),
            ("0", "❌ Exit", "Quit Vibecode Studio"),
        ]
        
        for num, title, desc in menu_items:
            print(f"  {Colors.BOLD}{num}.{Colors.ENDC} {title}")
            print(f"     {Colors.DIM}{desc}{Colors.ENDC}\n")
        
        choice = input(f"{Colors.BOLD}Enter your choice (0-9): {Colors.ENDC}")
        return choice
    
    def cmd_scan_project(self):
        """Scan current project"""
        print_header("🔍 SCANNING PROJECT")
        
        print_info("Invoking Agent 00 (Forensic)...")
        print_section("Analyzing project structure...")
        
        # Import and run the scan from CLI tool
        from core.scanner import ProjectScanner
        
        scanner = ProjectScanner(self.workspace)
        results = scanner.scan_deep()
        
        print_success("Project scan complete!")
        print_info(f"Results saved to {self.vibecode_dir / 'audit_report.md'}")
        
        self.state["project_scanned"] = True
        self.save_state()
        
        # Show summary
        print_section("Summary")
        print(f"  Tech Stack: {', '.join(results.get('tech_stack', {}).get('languages', []))}")
        print(f"  Total Files: {results.get('file_analysis', {}).get('total_files', 0):,}")
        print(f"  Total Lines: {results.get('file_analysis', {}).get('total_lines', 0):,}")
        
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
    
    def cmd_build_feature(self):
        """Build a new feature using agents"""
        print_header("🏗️  BUILD FEATURE")
        
        # Check if project is scanned
        if not self.state.get("project_scanned"):
            print_warning("Project not scanned yet. Scanning now...")
            self.cmd_scan_project()
        
        print(f"\n{Colors.BOLD}What feature would you like to build?{Colors.ENDC}")
        feature_desc = input("Description: ")
        
        if not feature_desc.strip():
            print_error("Feature description cannot be empty")
            return
        
        print_section("Orchestrating agents...")
        
        print_section("Orchestrating agents...")
        
        # Initialize Orchestrator
        orchestrator = Orchestrator(self.workspace)
        
        # Execute via Orchestrator (force build context)
        # We prepend '/build' to ensure the intent parser routes it correctly if the description is vague
        command = f"/build {feature_desc}"
        orchestrator.process_user_request(command, auto_approve=False)
        
        print_success("\nFeature pipeline complete!")
        print_info("Review the changes and commit when ready.")
        
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
    
    def cmd_new_project(self):
        """Create a new fullstack project"""
        print_header("🚀 NEW FULLSTACK APP")
        
        print(f"\n{Colors.BOLD}Project Details:{Colors.ENDC}")
        name = input("Project Name (e.g., 'nebula-board'): ").strip()
        desc = input("Description (e.g., 'A Kanban board with Next.js and Python'): ").strip()
        
        if not name or not desc:
            print_error("Name and description are required.")
            return

        # === PHASE 1: PLANNING (Agent 01) ===
        print_section("Phase 1: Architecture Planning (Agent 01)...")
        
        from core.skill_loader import SkillLoader
        from agents import load_all_agents
        
        agents_dir = Path(__file__).parent / "agents"
        agents = load_all_agents(agents_dir)
        skills_dir = self.workspace / "skills"
        skill_loader = SkillLoader(skills_dir)
        
        # Load Agent 01 (Planner)
        agent_01 = agents.get("01")
        if not agent_01:
            print_error("Agent 01 (Planner) not found. Skipping planning phase.")
            return
        
        # Select skills for planning
        planning_skills_with_score = skill_loader.select_skills(desc, agent_id="01", max_skills=3)
        planning_skills_context = skill_loader.build_skills_context([s for s, _ in planning_skills_with_score])
        
        if planning_skills_with_score:
            print_info(f"   + Planning Skills: {', '.join([s.name for s, _ in planning_skills_with_score])}")
        
        # Build planning context
        planning_context = f"""
{agent_01.instructions}

EXPERT KNOWLEDGE (SKILLS):
{planning_skills_context}

TASK: Create architecture plan and contract for new project.
Project Name: {name}
Description: {desc}

Execute your THREE-PHASE PROTOCOL:
1. INTAKE: Gather requirements (ask clarifying questions if needed, but provide sensible defaults)
2. BLUEPRINT: Design the architecture
3. CONTRACT: Create detailed implementation plan

Output the complete contract in markdown format with:
- Executive Summary
- Type Definitions (interfaces/schemas)
- Component Architecture (file paths, responsibilities)
- Implementation Checklist (sequential steps)
- Dependencies to install
"""
        
        # Generate plan using AI
        print_info("   + Generating architecture blueprint...")
        plan = self.ai_provider.generate(planning_context)
        
        # Save plan to workspace
        plan_file = self.workspace / name / "docs" / "vibecode_plan.md"
        plan_file.parent.mkdir(parents=True, exist_ok=True)
        plan_file.write_text(plan, encoding='utf-8')
        
        print_success(f"   + Plan saved to: {plan_file.relative_to(self.workspace)}")
        print_info("\n--- PLAN PREVIEW ---")
        print(Colors.DIM + plan[:500] + "..." + Colors.ENDC)
        print_info("--- END PREVIEW ---\n")
        
        # Ask for approval
        approval = input(f"{Colors.BOLD}Approve this plan and proceed to build? (y/n): {Colors.ENDC}")
        if approval.lower() != 'y':
            print_warning("Build cancelled. Plan saved for review.")
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
            return
        
        # === PHASE 2: EXECUTION (Agent 02 with ReasoningEngine) ===
        print_section("Phase 2: Autonomous Execution (Agent 02)...")
        
        from core.reasoning_engine import ReasoningEngine
        
        # Load Agent 02 (Builder)
        agent_02 = agents.get("02")
        agent_persona = agent_02.instructions if agent_02 else "You are an expert fullstack developer."
        
        # Load skills for execution
        execution_skills_with_score = skill_loader.select_skills(desc, agent_id="02", max_skills=3)
        execution_skills_context = skill_loader.build_skills_context([s for s, _ in execution_skills_with_score])
        
        if execution_skills_with_score:
            print_info(f"   + Execution Skills: {', '.join([s.name for s, _ in execution_skills_with_score])}")
        
        # Initialize ReasoningEngine with FULL capabilities
        engine = ReasoningEngine(self.workspace, self.ai_provider)
        
        # Build execution prompt with the plan
        prompt = f"""You are implementing the project '{name}' according to the approved architecture plan.

PROJECT PLAN (created by Agent 01):
{plan}

EXECUTION INSTRUCTIONS:
1. Follow the Implementation Checklist from the plan step-by-step
2. Create all files in the specified paths
3. Use the exact type definitions from the contract
4. Install all required dependencies
5. Ensure the project structure matches the plan

You are authorized to run all necessary commands (npm install, mkdir, etc.).
Begin implementation now."""
        
        # Build execution context
        context = f"""
ACT AS: Agent 02 (Builder).

YOUR PERSONA:
{agent_persona}

EXPERT KNOWLEDGE (SKILLS):
{execution_skills_context}

APPROVED ARCHITECTURE PLAN:
You MUST follow the plan created by Agent 01. Do not deviate from the contract.

MISSION:
Execute the implementation checklist to create '{name}'.
"""
        
        # Execute with ReasoningEngine
        print_info("   + Starting autonomous build process...")
        result = engine.run_goal(prompt, context)
        
        if result.get("success"):
            print_success(f"\n✅ Project '{name}' generated and configured!")
            print_info(f"   • Architecture Plan: {plan_file.relative_to(self.workspace)}")
            print_info(f"   • Project Location: {name}/")
        else:
            print_error(f"\n❌ Build encountered issues: {result.get('reason', 'Unknown')}")
        
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")

    def cmd_fix_bug(self):
        """Fix a bug using Agent 07 (Medic)"""
        print_header("🐛 FIX BUG")
        
        print(f"\n{Colors.BOLD}Describe the bug or paste error message:{Colors.ENDC}")
        bug_desc = input("Bug: ")
        
        if not bug_desc.strip():
            print_error("Bug description cannot be empty")
            return
        
        print_section("Invoking Agent 07 (Medic)...")
        
        # Initialize Orchestrator
        orchestrator = Orchestrator(self.workspace)
        
        # Execute via Orchestrator
        command = f"/fix {bug_desc}"
        orchestrator.process_user_request(command, auto_approve=False)
        
        print_success("\nBug fix generated!")
        print_info("Review the suggested changes.")
        
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
    
    def cmd_list_agents(self):
        """List all available agents"""
        print_header("🤖 AVAILABLE AGENTS")
        
        if not self.agents_available:
            print_warning("No agents found. Please install agents first.")
            return
        
        agents_info = [
            ("00", "Forensic", "Security audit & pattern analysis"),
            ("01", "Architect", "System design & planning"),
            ("02", "Builder", "Code implementation"),
            ("03", "Designer", "UI/UX design"),
            ("04", "Reviewer", "Quality assurance"),
            ("05", "Integrator", "File operations"),
            ("06", "Operator", "Runtime management"),
            ("07", "Medic", "Error recovery"),
            ("08", "Shipper", "Release management"),
            ("09", "Tester", "Test generation"),
        ]
        
        for agent_id, name, desc in agents_info:
            status = "✓" if any(a["name"] == f"{agent_id}_{name.lower()}" for a in self.agents_available) else "✗"
            print(f"{Colors.GREEN if status == '✓' else Colors.RED}{status}{Colors.ENDC} Agent {agent_id} - {Colors.BOLD}{name}{Colors.ENDC}")
            print(f"   {Colors.DIM}{desc}{Colors.ENDC}\n")
        
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
    
    def cmd_list_skills(self):
        """List all available skills"""
        print_header("🔧 AVAILABLE SKILLS")
        
        if not self.skills_available:
            print_warning("No skills found. Please install skills first.")
            return
        
        # Group by category
        skills_by_category = {}
        for skill in self.skills_available:
            category = skill["category"]
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(skill["name"])
        
        for category, skills in sorted(skills_by_category.items()):
            print(f"\n{Colors.BOLD}{Colors.CYAN}{category.upper()}{Colors.ENDC}")
            for skill in sorted(skills):
                print(f"  {Colors.GREEN}✓{Colors.ENDC} {skill}")
        
        print(f"\n{Colors.DIM}Total: {len(self.skills_available)} skills available{Colors.ENDC}")
        
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
    
    def run_headless(self, prompt: str, auto: bool = False):
        """Run in headless mode for automation"""
        print_banner()
        print_header("🤖 AUTONOMOUS MODE ACTIVE")
        print_info(f"Executing prompt: '{prompt}'")
        if auto:
            print_warning("Auto-approval ENABLED")
        
        # Initialize Orchestrator properly
        orchestrator = Orchestrator(self.workspace)
        
        # Execute
        orchestrator.process_user_request(prompt, auto_approve=auto)
        
        print_success("\nAutonomous execution complete.")
    
    def run(self):
        """Main application loop"""
        print_banner()
        
        # Check if in a project directory
        if not (self.workspace / "package.json").exists() and \
           not (self.workspace / "requirements.txt").exists() and \
           not (self.workspace / "Cargo.toml").exists():
            print_warning("You don't appear to be in a project directory.")
            print_info("Navigate to your project folder and run Vibecode Studio there.\n")
        
        # Show project info if scanned
        if self.state.get("project_scanned"):
            print_success("Project initialized and ready!")
        else:
            print_info("First time? Run 'Scan Project' to get started.")
            
        # Check API Key
        if not self.ai_provider.is_configured():
            print(f"\n{Colors.YELLOW}⚠ Gemini API Key missing.{Colors.ENDC}")
            print(f"{Colors.DIM}   Vibecode will run in simulation mode.{Colors.ENDC}")
            print(f"{Colors.DIM}   Go to Settings (9) to configure your AI Brain.{Colors.ENDC}\n")
        
        # Main loop
        while True:
            try:
                choice = self.show_main_menu()
                
                if choice == "0":
                    print(f"\n{Colors.CYAN}Thanks for using Vibecode Studio! 👋{Colors.ENDC}\n")
                    break
                elif choice == "1":
                    self.cmd_scan_project()
                elif choice == "2":
                    self.cmd_build_feature()
                elif choice == "3":
                    self.cmd_fix_bug()
                elif choice == "4":
                    self.cmd_new_project()
                elif choice == "5":
                    print_info("Test generation feature coming soon!")
                    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
                elif choice == "6":
                    print_info("Ship Release feature coming soon!")
                    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
                elif choice == "7":
                    self.cmd_list_agents()
                elif choice == "8":
                    self.cmd_list_skills()
                elif choice == "9":
                    self.cmd_settings()
                else:
                    print_error("Invalid choice. Please enter 0-9.")
                    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
            
            except KeyboardInterrupt:
                print(f"\n\n{Colors.CYAN}Thanks for using Vibecode Studio! 👋{Colors.ENDC}\n")
                break
            except Exception as e:
                import traceback
                print_error(f"An error occurred: {e}")
                print(f"{Colors.RED}{traceback.format_exc()}{Colors.ENDC}")
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")

    def cmd_settings(self):
        """Configure settings"""
        print_header("⚙️  SETTINGS")
        
        current_key = self.ai_provider.api_key
        status_color = Colors.GREEN if self.ai_provider.is_configured() else Colors.RED
        status_text = "Configured" if self.ai_provider.is_configured() else "Not Configured"
        
        print(f"Gemini API Status: {status_color}{status_text}{Colors.ENDC}")
        if current_key and len(current_key) > 8:
            masked = current_key[:4] + "*" * (len(current_key)-8) + current_key[-4:]
            print(f"Current Key: {masked}")
            
        print("\nOptions:")
        print("1. Update API Key")
        print("2. Back")
        
        choice = input(f"\n{Colors.BOLD}Enter choice: {Colors.ENDC}")
        
        if choice == "1":
            new_key = input("Enter Google Gemini API Key: ").strip()
            if new_key:
                if self.ai_provider.configure(new_key):
                    print_success("API Key updated successfully!")
                else:
                    print_error("Failed to update key")
        
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")


def main():
    """Entry point"""
    parser = argparse.ArgumentParser(
        description=f'{PRODUCT_NAME} - Your AI Development Team in a Box',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--version', action='version', version=f'{PRODUCT_NAME} v{VERSION}')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--prompt', type=str, help='Directly execute a prompt without menu')
    parser.add_argument('--auto', action='store_true', help='Autonomous mode (skip confirmations)')
    
    args = parser.parse_args()
    
    # Run the application
    app = VibecodeSudio()
    
    if args.prompt:
        app.run_headless(args.prompt, args.auto)
    else:
        app.run()


if __name__ == '__main__':
    main()
