#!/usr/bin/env python3
"""
Simple test using headless mode with --prompt flag
"""

import subprocess
import sys
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def main():
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" * 60)
    print("  SIMPLE VIBECODE TEST - HEADLESS MODE")
    print("=" * 60)
    print(f"{Colors.ENDC}\n")
    
    # Test configuration
    project_name = "test-simple-app"
    description = "Create a simple Next.js blog app with homepage, about page, and post listing. Use Tailwind CSS."
    
    print(f"{Colors.BLUE}Project: {project_name}{Colors.ENDC}")
    print(f"{Colors.BLUE}Description: {description[:80]}...{Colors.ENDC}\n")
    
    # Build command using --prompt flag (headless mode)
    prompt = f"Create a new project called '{project_name}'. {description}"
    
    print(f"{Colors.YELLOW}Starting Vibecode in autonomous mode...{Colors.ENDC}\n")
    
    start_time = time.time()
    
    try:
        # Use --prompt and --auto flags for fully autonomous execution
        result = subprocess.run(
            [sys.executable, "vibecode_studio.py", "--prompt", prompt, "--auto"],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes
            cwd=Path.cwd()
        )
        
        elapsed = time.time() - start_time
        
        # Save output
        log_file = Path(f"{project_name}_output.txt")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=== STDOUT ===\n")
            f.write(result.stdout)
            f.write("\n\n=== STDERR ===\n")
            f.write(result.stderr)
        
        print(f"\n{Colors.GREEN}Build completed in {elapsed:.1f} seconds{Colors.ENDC}")
        print(f"{Colors.BLUE}Log saved to: {log_file}{Colors.ENDC}\n")
        
        # Check results
        project_dir = Path(project_name)
        
        print(f"{Colors.BOLD}Verification:{Colors.ENDC}")
        
        if project_dir.exists():
            print(f"{Colors.GREEN}✓ Project directory exists{Colors.ENDC}")
            
            # Count files
            files = list(project_dir.rglob("*"))
            file_count = len([f for f in files if f.is_file()])
            print(f"{Colors.GREEN}✓ Files generated: {file_count}{Colors.ENDC}")
            
            # Check for key files
            if (project_dir / "package.json").exists():
                print(f"{Colors.GREEN}✓ package.json exists{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}⚠ package.json missing{Colors.ENDC}")
            
            if (project_dir / "docs" / "vibecode_plan.md").exists():
                print(f"{Colors.GREEN}✓ Architecture plan exists{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}⚠ Plan missing (expected with headless mode){Colors.ENDC}")
            
            # Check node_modules
            if (project_dir / "node_modules").exists():
                print(f"{Colors.GREEN}✓ Dependencies installed{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}⚠ Dependencies not installed{Colors.ENDC}")
                print(f"{Colors.BLUE}  Run: cd {project_name} && npm install{Colors.ENDC}")
        
        else:
            print(f"{Colors.RED}✗ Project directory not found{Colors.ENDC}")
            print(f"{Colors.YELLOW}Check log for errors: cat {log_file}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}Next steps:{Colors.ENDC}")
        print(f"  1. Review log: {Colors.CYAN}cat {log_file}{Colors.ENDC}")
        if project_dir.exists():
            print(f"  2. Install deps: {Colors.CYAN}cd {project_name} && npm install{Colors.ENDC}")
            print(f"  3. Run project: {Colors.CYAN}npm run dev{Colors.ENDC}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"\n{Colors.RED}✗ Build timed out after 5 minutes{Colors.ENDC}")
        return False
    except Exception as e:
        print(f"\n{Colors.RED}✗ Error: {e}{Colors.ENDC}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
