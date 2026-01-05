#!/usr/bin/env python3
"""
Autonomous Development Test Script
Tests the complete Option 4 flow: Planning → Approval → Execution → Verification
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import codecs
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

# ANSI Colors
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class AutonomousDevTester:
    def __init__(self, project_name: str, description: str, workspace: Path = None):
        self.project_name = project_name
        self.description = description
        self.workspace = workspace or Path.cwd()
        self.project_dir = self.workspace / project_name
        self.test_results = {
            "planning_phase": False,
            "execution_phase": False,
            "project_structure": False,
            "dependencies_installed": False,
            "files_generated": False,
            "runnable": False,
            "errors": []
        }
    
    def print_header(self, text: str):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")
    
    def print_step(self, text: str):
        print(f"{Colors.BLUE}▶ {text}{Colors.ENDC}")
    
    def print_success(self, text: str):
        print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")
    
    def print_error(self, text: str):
        print(f"{Colors.RED}✗ {text}{Colors.ENDC}")
    
    def print_warning(self, text: str):
        print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")
    
    def run_vibecode_option4(self) -> bool:
        """
        Run Vibecode Studio Option 4 with automated input
        """
        self.print_header("STEP 1: Running Vibecode Studio (Option 4)")
        
        try:
            # Prepare automated input
            # Simulates: selecting option 4, entering name, entering description, approving plan
            automated_input = f"4\n{self.project_name}\n{self.description}\ny\n0\n"
            
            self.print_step("Launching Vibecode Studio with automated inputs...")
            self.print_step(f"Project Name: {self.project_name}")
            self.print_step(f"Description: {self.description[:100]}...")
            
            # Run vibecode_studio.py with input simulation
            process = subprocess.Popen(
                [sys.executable, "vibecode_studio.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.workspace
            )
            
            # Send automated input
            stdout, stderr = process.communicate(input=automated_input, timeout=300)
            
            # Save logs
            log_file = self.workspace / f"{self.project_name}_build_log.txt"
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("=== STDOUT ===\n")
                f.write(stdout)
                f.write("\n\n=== STDERR ===\n")
                f.write(stderr)
            
            self.print_success(f"Build log saved to: {log_file.name}")
            
            # Check for success indicators in output
            if "Phase 1: Architecture Planning" in stdout:
                self.test_results["planning_phase"] = True
                self.print_success("Phase 1 (Planning) detected")
            else:
                self.print_warning("Phase 1 (Planning) not detected in output")
            
            if "Phase 2: Autonomous Execution" in stdout or "Reasoning Engine" in stdout:
                self.test_results["execution_phase"] = True
                self.print_success("Phase 2 (Execution) detected")
            else:
                self.print_warning("Phase 2 (Execution) not detected in output")
            
            # Check for errors
            if "ERROR" in stderr or "FAIL" in stderr:
                self.test_results["errors"].append(f"Errors in stderr: {stderr[:200]}")
                self.print_error("Errors detected in stderr")
            
            return process.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.print_error("Build process timed out (>5 minutes)")
            self.test_results["errors"].append("Timeout after 300 seconds")
            return False
        except Exception as e:
            self.print_error(f"Failed to run Vibecode: {e}")
            self.test_results["errors"].append(str(e))
            return False
    
    def verify_project_structure(self) -> bool:
        """
        Verify that the project was created with proper structure
        """
        self.print_header("STEP 2: Verifying Project Structure")
        
        if not self.project_dir.exists():
            self.print_error(f"Project directory not found: {self.project_dir}")
            self.test_results["errors"].append("Project directory missing")
            return False
        
        self.print_success(f"Project directory exists: {self.project_dir}")
        
        # Check for essential files/folders
        essential_paths = [
            "docs/vibecode_plan.md",  # Planning artifact
            "package.json",           # Node project
            "src",                    # Source folder
        ]
        
        # Check for Next.js or React structure
        nextjs_indicators = ["app", "pages", "next.config.js"]
        react_indicators = ["src/App.tsx", "src/index.tsx", "public"]
        
        found_files = []
        missing_files = []
        
        for path_str in essential_paths:
            path = self.project_dir / path_str
            if path.exists():
                found_files.append(path_str)
                self.print_success(f"Found: {path_str}")
            else:
                missing_files.append(path_str)
                self.print_warning(f"Missing: {path_str}")
        
        # Check framework type
        is_nextjs = any((self.project_dir / p).exists() for p in nextjs_indicators)
        is_react = any((self.project_dir / p).exists() for p in react_indicators)
        
        if is_nextjs:
            self.print_success("Detected: Next.js project")
        elif is_react:
            self.print_success("Detected: React project")
        else:
            self.print_warning("Framework not clearly detected")
        
        # List all generated files
        all_files = list(self.project_dir.rglob("*"))
        file_count = len([f for f in all_files if f.is_file()])
        self.print_step(f"Total files generated: {file_count}")
        
        self.test_results["project_structure"] = len(found_files) >= 2
        self.test_results["files_generated"] = file_count > 0
        
        return self.test_results["project_structure"]
    
    def verify_dependencies(self) -> bool:
        """
        Check if dependencies were installed
        """
        self.print_header("STEP 3: Verifying Dependencies")
        
        package_json = self.project_dir / "package.json"
        node_modules = self.project_dir / "node_modules"
        
        if not package_json.exists():
            self.print_error("package.json not found")
            return False
        
        # Read package.json
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            deps = package_data.get("dependencies", {})
            dev_deps = package_data.get("devDependencies", {})
            
            self.print_step(f"Dependencies declared: {len(deps)}")
            self.print_step(f"Dev dependencies declared: {len(dev_deps)}")
            
            for dep, version in list(deps.items())[:5]:
                print(f"  • {dep}: {version}")
            
            if len(deps) > 5:
                print(f"  ... and {len(deps) - 5} more")
        
        except json.JSONDecodeError:
            self.print_error("package.json is malformed")
            return False
        
        # Check if node_modules exists
        if node_modules.exists():
            self.print_success("node_modules directory exists")
            installed_count = len(list(node_modules.iterdir()))
            self.print_step(f"Installed packages: ~{installed_count}")
            self.test_results["dependencies_installed"] = True
        else:
            self.print_warning("node_modules not found (dependencies not installed)")
            self.print_step("Attempting to install dependencies...")
            
            try:
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=180
                )
                
                if result.returncode == 0:
                    self.print_success("Dependencies installed successfully")
                    self.test_results["dependencies_installed"] = True
                else:
                    self.print_error(f"npm install failed: {result.stderr[:200]}")
                    self.test_results["errors"].append("npm install failed")
                    return False
            
            except subprocess.TimeoutExpired:
                self.print_error("npm install timed out")
                return False
            except FileNotFoundError:
                self.print_error("npm not found. Install Node.js first.")
                return False
        
        return self.test_results["dependencies_installed"]
    
    def verify_plan_contract(self) -> Dict:
        """
        Verify Agent 01's plan was created properly
        """
        self.print_header("STEP 4: Verifying Architecture Plan")
        
        plan_file = self.project_dir / "docs" / "vibecode_plan.md"
        
        if not plan_file.exists():
            self.print_error("Architecture plan not found!")
            return {"exists": False}
        
        self.print_success("Architecture plan exists")
        
        # Read and analyze plan
        plan_content = plan_file.read_text(encoding='utf-8')
        
        # Check for required sections
        required_sections = [
            "Blueprint:",
            "The Contract",
            "Component Architecture",
            "Implementation Checklist",
            "Dependencies"
        ]
        
        plan_analysis = {
            "exists": True,
            "size": len(plan_content),
            "sections_found": []
        }
        
        for section in required_sections:
            if section in plan_content:
                plan_analysis["sections_found"].append(section)
                self.print_success(f"Section found: {section}")
            else:
                self.print_warning(f"Section missing: {section}")
        
        # Extract checklist items
        checklist_items = plan_content.count("[ ]")
        self.print_step(f"Implementation checklist items: {checklist_items}")
        
        # Show preview
        preview = plan_content[:500]
        self.print_step("Plan preview:")
        print(f"{Colors.BLUE}{preview}...{Colors.ENDC}")
        
        return plan_analysis
    
    def test_run_dev_server(self) -> bool:
        """
        Attempt to start the dev server and verify it runs
        """
        self.print_header("STEP 5: Testing Development Server")
        
        # Check for dev script in package.json
        package_json = self.project_dir / "package.json"
        
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            scripts = package_data.get("scripts", {})
            
            if "dev" not in scripts:
                self.print_warning("No 'dev' script found in package.json")
                return False
            
            self.print_step(f"Dev command: {scripts['dev']}")
            self.print_step("Starting dev server (will run for 10 seconds)...")
            
            # Start dev server
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Let it run for 10 seconds
            time.sleep(10)
            
            # Check if still running
            if process.poll() is None:
                self.print_success("Dev server is running!")
                self.test_results["runnable"] = True
                
                # Try to read output
                # Note: This is non-blocking
                self.print_step("Server output sample:")
                # Kill the process
                process.terminate()
                process.wait(timeout=5)
            else:
                self.print_error("Dev server crashed immediately")
                stdout, stderr = process.communicate()
                self.print_error(f"Error: {stderr[:300]}")
                self.test_results["errors"].append(f"Dev server crashed: {stderr[:200]}")
                return False
            
            return True
        
        except Exception as e:
            self.print_error(f"Failed to test dev server: {e}")
            self.test_results["errors"].append(str(e))
            return False
    
    def generate_report(self) -> str:
        """
        Generate comprehensive test report
        """
        self.print_header("TEST REPORT")
        
        # Calculate score
        total_checks = 6
        passed_checks = sum([
            self.test_results["planning_phase"],
            self.test_results["execution_phase"],
            self.test_results["project_structure"],
            self.test_results["dependencies_installed"],
            self.test_results["files_generated"],
            self.test_results["runnable"]
        ])
        
        score_percent = (passed_checks / total_checks) * 100
        
        # Status indicator
        if score_percent == 100:
            status = f"{Colors.GREEN}✓ ALL TESTS PASSED{Colors.ENDC}"
        elif score_percent >= 70:
            status = f"{Colors.YELLOW}⚠ MOSTLY WORKING{Colors.ENDC}"
        else:
            status = f"{Colors.RED}✗ FAILED{Colors.ENDC}"
        
        print(f"{Colors.BOLD}Status: {status}{Colors.ENDC}")
        print(f"{Colors.BOLD}Score: {passed_checks}/{total_checks} ({score_percent:.0f}%){Colors.ENDC}\n")
        
        # Detailed results
        print(f"{Colors.BOLD}Test Results:{Colors.ENDC}")
        self._print_test_result("Planning Phase", self.test_results["planning_phase"])
        self._print_test_result("Execution Phase", self.test_results["execution_phase"])
        self._print_test_result("Project Structure", self.test_results["project_structure"])
        self._print_test_result("Dependencies Installed", self.test_results["dependencies_installed"])
        self._print_test_result("Files Generated", self.test_results["files_generated"])
        self._print_test_result("Dev Server Runnable", self.test_results["runnable"])
        
        # Errors
        if self.test_results["errors"]:
            print(f"\n{Colors.BOLD}Errors Encountered:{Colors.ENDC}")
            for i, error in enumerate(self.test_results["errors"], 1):
                print(f"{Colors.RED}  {i}. {error}{Colors.ENDC}")
        
        # Artifacts
        print(f"\n{Colors.BOLD}Generated Artifacts:{Colors.ENDC}")
        print(f"  • Project: {self.project_dir}")
        print(f"  • Plan: {self.project_dir}/docs/vibecode_plan.md")
        print(f"  • Build Log: {self.workspace}/{self.project_name}_build_log.txt")
        
        # Next steps
        print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
        print(f"  1. Review the plan: {Colors.CYAN}cat {self.project_dir}/docs/vibecode_plan.md{Colors.ENDC}")
        print(f"  2. Check build log: {Colors.CYAN}cat {self.project_name}_build_log.txt{Colors.ENDC}")
        print(f"  3. Run the project: {Colors.CYAN}cd {self.project_name} && npm run dev{Colors.ENDC}")
        
        return status
    
    def _print_test_result(self, name: str, passed: bool):
        icon = f"{Colors.GREEN}✓{Colors.ENDC}" if passed else f"{Colors.RED}✗{Colors.ENDC}"
        print(f"  {icon} {name}")
    
    def run_full_test(self) -> bool:
        """
        Run complete test suite
        """
        self.print_header(f"AUTONOMOUS DEVELOPMENT TEST: {self.project_name}")
        
        start_time = time.time()
        
        # Step 1: Run Vibecode
        step1 = self.run_vibecode_option4()
        
        # Step 2: Verify structure
        step2 = self.verify_project_structure()
        
        # Step 3: Verify dependencies
        step3 = self.verify_dependencies()
        
        # Step 4: Verify plan
        self.verify_plan_contract()
        
        # Step 5: Test dev server
        step5 = self.test_run_dev_server()
        
        # Generate report
        elapsed = time.time() - start_time
        print(f"\n{Colors.BOLD}Total Time: {elapsed:.1f} seconds{Colors.ENDC}")
        
        self.generate_report()
        
        return all([step1, step2, step3, step5])


def main():
    """
    Main entry point with predefined test cases
    """
    print(f"{Colors.BOLD}{Colors.MAGENTA}")
    print("============================================================")
    print("   VIBECODE AUTONOMOUS DEVELOPMENT TEST SUITE              ")
    print("   Tests: Planning -> Approval -> Execution -> Verification")
    print("============================================================")
    print(f"{Colors.ENDC}")
    
    # Test cases
    test_cases = [
        {
            "name": "test-todo-app",
            "description": "A simple todo app with Next.js. Add a homepage with a list of todos, ability to add new todos, mark as complete, and delete. Use Tailwind CSS for styling."
        },
        {
            "name": "test-blog-platform",
            "description": "A blog platform with Next.js 14. Include homepage listing posts, individual post pages, about page, and contact form. Use Tailwind CSS and add dark mode toggle."
        },
        {
            "name": "test-dashboard",
            "description": "A real-time analytics dashboard with Next.js. Include sales chart, user stats, live notifications, and sidebar navigation. Use Recharts for charts and Tailwind for styling."
        }
    ]
    
    print(f"{Colors.BOLD}Available Test Cases:{Colors.ENDC}")
    for i, tc in enumerate(test_cases, 1):
        print(f"  {i}. {tc['name']}")
        print(f"     {Colors.BLUE}{tc['description'][:80]}...{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Select test case (1-{len(test_cases)}) or 'c' for custom:{Colors.ENDC} ", end="")
    choice = input().strip()
    
    if choice == 'c':
        print(f"{Colors.BOLD}Project Name:{Colors.ENDC} ", end="")
        project_name = input().strip()
        print(f"{Colors.BOLD}Description:{Colors.ENDC} ", end="")
        description = input().strip()
    else:
        try:
            idx = int(choice) - 1
            test_case = test_cases[idx]
            project_name = test_case["name"]
            description = test_case["description"]
        except (ValueError, IndexError):
            print(f"{Colors.RED}Invalid choice. Using default test case.{Colors.ENDC}")
            test_case = test_cases[0]
            project_name = test_case["name"]
            description = test_case["description"]
    
    # Run test
    tester = AutonomousDevTester(project_name, description)
    success = tester.run_full_test()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
