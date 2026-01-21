#!/usr/bin/env python3
"""
Vibecode Studio - Your AI Development Team in a Box
Main entry point for the Vibecode multi-agent system

Simplified single-prompt interface: Just provide your prompt and Vibecode handles the rest.
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
from core.autonomy_config import AutonomyConfig
from utils.ai_providers import GeminiProvider

# Version
VERSION = "2.0.0"
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
{Colors.DIM}Version {VERSION} - Single Prompt Interface{Colors.ENDC}
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


class VibecodeStudio:
    """
    Main Vibecode Studio application
    Simplified single-prompt interface that automatically routes tasks to appropriate agents.
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.workspace = Path.cwd()
        self.vibecode_dir = self.workspace / ".vibecode"
        self.state_file = self.vibecode_dir / "state.json"
        self.context_file = self.vibecode_dir / "project_context.md"
        
        # Ensure vibecode directory exists
        self.vibecode_dir.mkdir(exist_ok=True)
        
        # Load state
        self.state = self.load_state()
        
        # Get model selection from state or default to MiniMax M2.1
        model = self.state.get("ai_model", "minimax-m2.1")
        
        # Initialize AI provider
        self.ai_provider = GeminiProvider(self.workspace, model=model)
    
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
            "active_agents": [],
            "ai_model": "minimax-m2.1"
        }
    
    def save_state(self):
        """Save current state"""
        self.vibecode_dir.mkdir(exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def execute_prompt(self, prompt: str, auto_approve: bool = False, 
                       confidence_threshold: float = 0.8,
                       audit_log: str = '.vibecode/autonomy_audit.log') -> Dict:
        """
        Execute a user prompt through the Vibecode system.
        
        The orchestrator automatically:
        - Parses the intent (build, fix, scan, test, etc.)
        - Selects the appropriate agent pipeline
        - Executes the task with relevant skills
        
        Args:
            prompt: User's request in natural language or command format
            auto_approve: Whether to auto-approve destructive operations
            confidence_threshold: Minimum confidence for auto-approval (0.0-1.0)
            audit_log: Path for autonomy decision audit log
            
        Returns:
            Result dictionary with execution details
        """
        print_header("🚀 VIBECODE STUDIO - EXECUTING TASK")
        
        # Display prompt info
        print_section("Task Request")
        print(f"  {Colors.BOLD}Prompt:{Colors.ENDC} {prompt}")
        print(f"  {Colors.DIM}Auto-approve: {auto_approve}{Colors.ENDC}")
        print(f"  {Colors.DIM}Confidence threshold: {confidence_threshold:.0%}{Colors.ENDC}")
        
        # Check API configuration
        if not self.ai_provider.is_configured():
            print_warning("AI API Key not configured. Some features may be limited.")
            print_info("Set MINIMAX_API_KEY environment variable or configure via settings.")
        
        # Create autonomy configuration
        autonomy_config = AutonomyConfig(
            confidence_threshold=confidence_threshold,
            auto_approve=auto_approve,
            audit_log_path=audit_log
        )
        
        # Initialize Orchestrator
        print_section("Initializing Orchestrator")
        orchestrator = Orchestrator(self.workspace, autonomy_config=autonomy_config)
        
        # Process the request through the orchestrator
        # The orchestrator handles:
        # - Intent parsing (determines if it's a build, fix, scan, etc.)
        # - Agent pipeline selection
        # - Skill loading
        # - Execution
        print_section("Processing Request")
        result = orchestrator.process_user_request(prompt, auto_approve=auto_approve)
        
        # Display result summary
        print_section("Execution Complete")
        if result.get("success", False):
            print_success("Task completed successfully!")
        else:
            print_error(f"Task failed: {result.get('message', 'Unknown error')}")
        
        # Save state
        self.state["last_prompt"] = prompt
        self.state["last_result"] = "success" if result.get("success") else "failed"
        self.save_state()
        
        return result
    
    def run_interactive(self, auto_approve: bool = False,
                        confidence_threshold: float = 0.8,
                        audit_log: str = '.vibecode/autonomy_audit.log'):
        """
        Run in interactive mode - continuously accept prompts until exit.
        
        Args:
            auto_approve: Whether to auto-approve destructive operations
            confidence_threshold: Minimum confidence for auto-approval
            audit_log: Path for autonomy decision audit log
        """
        print_banner()
        
        # Show workspace info
        print_info(f"Workspace: {self.workspace}")
        print_info(f"AI Model: {self.state.get('ai_model', 'minimax-m2.1')}")
        
        if auto_approve:
            print_warning("Auto-approval mode ENABLED")
        
        # Check API configuration
        if not self.ai_provider.is_configured():
            print_warning("AI API Key not configured.")
            print_info("Set MINIMAX_API_KEY environment variable for full functionality.")
        
        print(f"\n{Colors.BOLD}Enter your prompt (or 'exit'/'quit' to stop):{Colors.ENDC}")
        print(f"{Colors.DIM}Examples:{Colors.ENDC}")
        print(f"  {Colors.DIM}• 'Build a todo app with React and Node.js'{Colors.ENDC}")
        print(f"  {Colors.DIM}• 'Fix the authentication bug in login.js'{Colors.ENDC}")
        print(f"  {Colors.DIM}• 'Scan the project and analyze the codebase'{Colors.ENDC}")
        print(f"  {Colors.DIM}• 'Add unit tests for the user service'{Colors.ENDC}")
        print(f"  {Colors.DIM}• '/build Add dark mode support'{Colors.ENDC}")
        print(f"  {Colors.DIM}• '/fix TypeError in payment processing'{Colors.ENDC}")
        print()
        
        while True:
            try:
                # Get user prompt
                prompt = input(f"{Colors.CYAN}vibecode>{Colors.ENDC} ").strip()
                
                # Check for exit commands
                if prompt.lower() in ['exit', 'quit', 'q', ':q', 'bye']:
                    print(f"\n{Colors.CYAN}Thanks for using Vibecode Studio! 👋{Colors.ENDC}\n")
                    break
                
                # Skip empty prompts
                if not prompt:
                    continue
                
                # Execute the prompt
                self.execute_prompt(
                    prompt=prompt,
                    auto_approve=auto_approve,
                    confidence_threshold=confidence_threshold,
                    audit_log=audit_log
                )
                
                print()  # Add spacing between prompts
                
            except KeyboardInterrupt:
                print(f"\n\n{Colors.CYAN}Thanks for using Vibecode Studio! 👋{Colors.ENDC}\n")
                break
            except Exception as e:
                import traceback
                print_error(f"An error occurred: {e}")
                print(f"{Colors.RED}{traceback.format_exc()}{Colors.ENDC}")


def main():
    """Entry point"""
    parser = argparse.ArgumentParser(
        description=f'{PRODUCT_NAME} - Your AI Development Team in a Box\n\n'
                    f'Simply provide a prompt and Vibecode handles the rest.\n'
                    f'The system automatically detects intent and routes to appropriate agents.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Build a REST API with Express and MongoDB"
  %(prog)s "Fix the login bug in auth.js"
  %(prog)s "Scan and analyze this codebase"
  %(prog)s --auto "Add user authentication feature"
  %(prog)s  # Interactive mode - enter prompts continuously
        """
    )
    
    parser.add_argument('prompt', nargs='?', type=str, default=None,
                        help='The task prompt to execute (natural language or command)')
    parser.add_argument('--version', action='version', version=f'{PRODUCT_NAME} v{VERSION}')
    parser.add_argument('--auto', action='store_true', 
                        help='Enable auto-approval mode (skip confirmations)')
    parser.add_argument('--confidence-threshold', type=float, default=0.8,
                        help='Minimum confidence for auto-approval (0.0-1.0, default: 0.8)')
    parser.add_argument('--audit-log', type=str, default='.vibecode/autonomy_audit.log',
                        help='Path for autonomy decision audit log')
    parser.add_argument('--verbose', action='store_true', 
                        help='Enable verbose output')

    args = parser.parse_args()

    # Initialize the application
    app = VibecodeStudio()

    if args.prompt:
        # Single prompt mode - execute and exit
        print_banner()
        app.execute_prompt(
            prompt=args.prompt,
            auto_approve=args.auto,
            confidence_threshold=args.confidence_threshold,
            audit_log=args.audit_log
        )
    else:
        # Interactive mode - continuous prompt input
        app.run_interactive(
            auto_approve=args.auto,
            confidence_threshold=args.confidence_threshold,
            audit_log=args.audit_log
        )


if __name__ == '__main__':
    main()
