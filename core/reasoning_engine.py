"""
Reasoning Engine Module
Implements the ReAct (Reason+Act) loop for autonomous tool usage.
"""

import json
import re
import subprocess
import platform
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

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

class ReasoningEngine:
    def __init__(self, workspace: Path, ai_provider, allowed_tools: Optional[List[str]] = None):
        self.workspace = workspace
        self.ai_provider = ai_provider
        self.max_steps = 30  # Increased from 15 to 30 for complex projects
        self.history = []
        self.allowed_tools = allowed_tools
        self.current_working_dir = workspace

    def run_goal(self, goal: str, context: str = "") -> Dict[str, Any]:
        """
        Executes the ReAct loop to achieve a goal.
        """
        print(f"\n{Colors.CYAN}🧠 Reasoning Engine Activated: {goal}{Colors.ENDC}")
        
        self.history = []
        system_prompt = self._build_system_prompt()
        
        step_count = 0
        while step_count < self.max_steps:
            step_count += 1
            progress_percent = (step_count / self.max_steps) * 100
            print(f"\n{Colors.BOLD}--- Step {step_count}/{self.max_steps} ({progress_percent:.0f}%) ---{Colors.ENDC}")
            
            # 1. THINK: Generate thought and action
            prompt = self._build_step_prompt(goal, context)
            response = self.ai_provider.generate(prompt)
            
            # Parse response
            thought, tool_call = self._parse_response(response)
            
            if thought:
                print(f"{Colors.BLUE}💭 Thought: {thought}{Colors.ENDC}")
            
            if not tool_call:
                if "FINAL ANSWER" in response:
                    print(f"{Colors.GREEN}🏁 Goal Completed.{Colors.ENDC}")
                    return {"success": True, "history": self.history}
                print(f"{Colors.YELLOW}🤔 No tool call detected. Retrying with feedback...{Colors.ENDC}")
                print(f"{Colors.RED}[DEBUG] Raw AI Response:\n{response}\n[DEBUG] End Response{Colors.ENDC}")
                self.history.append({"role": "assistant", "content": response})
                # [Antigravity Fix] Force the model to zero in on the format
                self.history.append({
                    "role": "user", 
                    "content": "SYSTEM ERROR: No valid 'Action:' or 'Args:' detected. You MUST use the strict format:\nThought: ...\nAction: ...\nArgs: { ... }"
                })
                continue

            # 2. ACT: Execute tool
            print(f"{Colors.YELLOW}🛠️  Action: {tool_call['tool']} ({tool_call['args']}){Colors.ENDC}")
            result = self._execute_tool(tool_call['tool'], tool_call['args'])
            
            # 3. OBSERVE: Record result
            observation = result[:500] + "..." if len(result) > 500 else result
            print(f"{Colors.DIM}👁️  Observation: {observation}{Colors.ENDC}")
            
            # Update history
            self.history.append({
                "role": "assistant",
                "content": response
            })
            self.history.append({
                "role": "user", 
                "content": f"Tool Output: {result}"
            })

            # Check for completion signal in tool output or if we are just listing things
            if tool_call['tool'] == "finish_task":
                 return {"success": True, "history": self.history}

        return {"success": False, "reason": "Max steps reached"}

    def _build_system_prompt(self) -> str:
        os_name = platform.system()
        return f"""
You are an autonomous coding agent. You have access to the user's filesystem and can execute commands.
Your goal is to complete the user's request by adhering to the ReAct loop:
1. THINK: Analyze the current state, what you know, and what you need to do next.
2. ACT: Select a tool to execute (read, write, list, command).
3. OBSERVE: Read the output of your action and refine your plan.

OPERATING SYSTEM CONSTRAINTS ({os_name}):
- WINDOWS: You MUST use DOUBLE QUOTES (") for paths with spaces. Single quotes (') will fail in cmd.exe.
- WINDOWS: Use '&&' to chain commands.
- ERROR HANDLING: If a directory already exists (Exit Code 1), do not panic. Just 'cd' into it.

COMMAND BEST PRACTICES:
- Use simple mkdir instead of complex scaffolding tools when possible
- For Next.js: Use 'npx create-next-app@latest <name> --typescript --tailwind --app'
- npx prompts are auto-confirmed, no need to worry about "Ok to proceed?" 
- Avoid outdated or deprecated flags
- If a command fails, try a simpler alternative

AVAILABLE TOOLS:
- list_dir(path): List files in a directory.
- read_file(path): Read the contents of a file.
- write_file(path, content): Write content to a file (overwrites).
- run_command(command): Run a shell command (e.g., 'npm install', 'mkdir').
- finish_task(summary): Call this when the goal is achieved.

RESPONSE FORMAT:
You must strictly follow this format for every turn. Do not output markdown code blocks for the Thought/Action.

Thought: <your reasoning here>
Action: <tool_name>
Args: <json_arguments>

Example:
Thought: I need to check if package.json exists.
Action: list_dir
Args: {{"path": "."}}

Example:
Thought: I need to create the main server file.
Action: write_file
Args: {{"path": "server.js", "content": "console.log('hello');"}}
"""

    def _build_step_prompt(self, goal: str, context: str) -> str:
        current_context = f"""
GOAL: {goal}
CONTEXT: {context}
GOAL: {goal}
CONTEXT: {context}
WORKING_DIR: {self.current_working_dir}
SYSTEM_OS: {platform.system()}
"""
        history_text = ""
        for item in self.history:
            if item['role'] == 'user':
                history_text += f"OBSERVATION: {item['content']}\n"
            else:
                history_text += f"{item['content']}\n"
        
        # [Antigravity Fix] Move Format Reminder to the END to prevent context loss
        format_reminder = """
IMPORTANT: You must output the response in this strict format:
Thought: <reasoning>
Action: <tool_name>
Args: <json_args>
"""
        return self._build_system_prompt() + "\n" + current_context + "\nHISTORY:\n" + history_text + "\n" + format_reminder + "\nNEXT STEP:"

    def _parse_response(self, response: str) -> tuple[Optional[str], Optional[Dict]]:
        thought = None
        tool_call = None
        
        # Extract Thought
        # Look for Thought: ... up to Action: or end of string
        thought_match = re.search(r"Thought:\s*(.+?)(?=\nAction:|\Z)", response, re.DOTALL | re.IGNORECASE)
        if thought_match:
            thought = thought_match.group(1).strip()
            
        # Extract Action and Args
        # More robust regex for Action (case insensitive, handle potential markdown bolding like **Action**)
        action_match = re.search(r"Action:\s*(\w+)", response, re.IGNORECASE)
        # Robust regex for Args: find the first { and the last }
        args_match = re.search(r"Args:\s*(\{.*\})", response, re.DOTALL | re.IGNORECASE)
        
        if action_match and args_match:
            try:
                tool_name = action_match.group(1).strip()
                args_str = args_match.group(1).strip()
                # Fix common JSON errors in LLM output (e.g. trailing commmas)
                import json
                args = json.loads(args_str)
                tool_call = {"tool": tool_name, "args": args}
            except Exception as e:
                print(f"{Colors.RED}❌ Error parsing tool args: {e}{Colors.ENDC}")
        
        return thought, tool_call

    def _execute_tool(self, tool_name: str, args: Dict) -> str:
        # Check against allowed tools if restriction is set
        if self.allowed_tools and tool_name not in self.allowed_tools:
            return f"Error: Tool '{tool_name}' is not allowed in this mode."

        try:
            if tool_name == "list_dir":
                # Use current_working_dir for relative paths
                path_arg = args.get("path", ".")
                if path_arg == "." or not Path(path_arg).is_absolute():
                    path = self.current_working_dir / path_arg
                else:
                    path = Path(path_arg)
                
                if not path.exists():
                    return f"Error: Path does not exist: {path}"
                items = [p.name + ("/" if p.is_dir() else "") for p in path.iterdir()]
                return "\n".join(items)
            
            elif tool_name == "read_file":
                # Use current_working_dir for relative paths
                path_arg = args.get("path")
                if not Path(path_arg).is_absolute():
                    path = self.current_working_dir / path_arg
                else:
                    path = Path(path_arg)
                
                if not path.exists():
                    return "Error: File not found."
                return path.read_text(encoding="utf-8")
            
            elif tool_name == "write_file":
                # Use current_working_dir for relative paths
                path_arg = args.get("path")
                if not Path(path_arg).is_absolute():
                    path = self.current_working_dir / path_arg
                else:
                    path = Path(path_arg)
                
                content = args.get("content")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
                return f"Success: Wrote to {path}"
            
            elif tool_name == "run_command":
                cmd = args.get("command")
                
                # [Antigravity Feature] Stateful Navigation
                # If the command is a simple directory change, update our internal state
                if cmd.strip().startswith("cd ") and "&&" not in cmd:
                    target = cmd.strip()[3:].strip().strip("'").strip('"')
                    new_path = (self.current_working_dir / target).resolve()
                    if new_path.exists() and new_path.is_dir():
                        self.current_working_dir = new_path
                        return f"Success: Changed directory to {self.current_working_dir}"
                    else:
                        return f"Error: Directory '{target}' not found."

                # Security check
                if any(x in cmd for x in ["rm -rf", "format", "del /s"]):
                    return "Error: Command blocked for safety."
                
                # Auto-confirm for npx and other prompts by piping "y"
                # This handles "Ok to proceed? (y)" prompts from npx
                if "npx" in cmd.lower() or "create-" in cmd.lower():
                    # Prepend with echo y to auto-confirm
                    if platform.system() == "Windows":
                        cmd = f'echo y | {cmd}'
                    else:
                        cmd = f'yes | {cmd}'
                
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    cwd=self.current_working_dir, 
                    capture_output=True, 
                    text=True,
                    timeout=180  # 3 minute timeout for long operations
                )
                output = result.stdout + result.stderr
                # Truncate very long output
                if len(output) > 2000:
                    output = output[:1000] + f"\n... (truncated {len(output) - 2000} chars) ...\n" + output[-1000:]
                return f"Exit Code: {result.returncode}\nOutput: {output}"
            
            elif tool_name == "finish_task":
                return "Task Completed."
            
            else:
                return f"Error: Unknown tool '{tool_name}'"
                
        except Exception as e:
            return f"Error executing tool: {str(e)}"
