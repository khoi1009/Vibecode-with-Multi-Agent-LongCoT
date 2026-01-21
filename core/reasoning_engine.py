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

# Import dependencies
from .tool_registry import ToolRegistry
from .memory_manager import BoundedHistory

# Import AgentType from tools (use absolute path with sys.path modification)
from pathlib import Path
_tools_dir = Path(__file__).parent / 'tools'
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))
from tool_base import AgentType

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
    def __init__(self, workspace: Path, ai_provider, agent_id: str = "02",
                 allowed_tools: Optional[List[str]] = None):
        self.workspace = workspace
        self.ai_provider = ai_provider
        self.max_steps = 15  # Reduced from 30 for better performance
        self.history = BoundedHistory(max_entries=30, max_chars=20000)  # Reduced for context efficiency
        self.allowed_tools = allowed_tools
        self.agent_id = agent_id
        self.current_working_dir = workspace

        # Initialize ToolRegistry for extended tool capabilities
        self.tool_registry = ToolRegistry(workspace)

        # Get tools available to this agent
        self.agent_type = self._determine_agent_type(agent_id)
        self.available_tools = self.tool_registry.get_tools_for_agent(
            agent_id, self.agent_type
        )

    def _determine_agent_type(self, agent_id: str) -> AgentType:
        """Determine agent type from ID for permission purposes"""
        agent_type_map = {
            "00": AgentType.FORENSIC,
            "01": AgentType.ARCHITECT,
            "02": AgentType.BUILDER,
            "03": AgentType.DESIGNER,
            "04": AgentType.FORENSIC,
            "05": AgentType.INTEGRATOR,
            "09": AgentType.QA,
        }
        return agent_type_map.get(agent_id, AgentType.ALL)

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
                # [Antigravity Fix] Force the model to zero in on the format with specific examples
                self.history.append({
                    "role": "user", 
                    "content": """SYSTEM ERROR: No valid 'Action:' or 'Args:' detected.

⚠️ STRICT FORMAT REQUIRED - Copy this EXACTLY:

Thought: [one short sentence]
Action: finish_task
Args: {"summary": "[what you accomplished]"}

RULES:
1. Output ONLY these 3 lines
2. NO text before Thought:
3. NO text after Args: {...}
4. JSON must be on ONE line
5. Use double quotes in JSON

Try again with the EXACT format above."""
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
            completion_tools = ["finish_task", "complete_task", "task_complete", "done", "complete", "end_task", "none", "no_action_required"]
            if tool_call['tool'] in completion_tools:
                 return {"success": True, "history": self.history}

        return {"success": False, "reason": "Max steps reached"}

    def _build_system_prompt(self) -> str:
        os_name = platform.system()

        # Get tool descriptions from the registry
        tool_docs = self.tool_registry.get_tool_descriptions(self.available_tools)

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

CORE TOOLS (Basic Operations):
- list_dir(path): List files in a directory.
- read_file(path): Read the contents of a file.
- write_file(path, content): Write content to a file (overwrites).
- run_command(command): Run a shell command (e.g., 'npm install', 'mkdir').
- finish_task(summary): **CRITICAL** - You MUST call this tool when done! This is the ONLY way to complete the task.

⚠️ IMPORTANT: When you have finished creating all files and the task is complete:
- You MUST use Action: finish_task
- Do NOT use: complete_task, task_complete, none, done, or any other name
- The ONLY valid completion tool is: finish_task

EXTENDED TOOLS (Enhanced Capabilities):
{tool_docs}

RESPONSE FORMAT:
You must strictly follow this format for every turn. Do not output markdown code blocks for the Thought/Action.

⚠️ CRITICAL RULE: Output EXACTLY ONE action per response!
- Do NOT output multiple Action/Args pairs
- Create ONE file, then wait for observation, then create the next
- If you need to create 5 files, that takes 5 separate steps

Thought: <your reasoning here>
Action: <tool_name>
Args: <json_arguments>

STOP AFTER Args! Do not add more text or another Action.

Example:
Thought: I need to check if package.json exists.
Action: list_dir
Args: {{"path": "."}}

Example:
Thought: I need to create the main server file.
Action: write_file
Args: {{"path": "server.js", "content": "console.log('hello');"}}

⚠️ COMPLETION EXAMPLE (IMPORTANT - use this EXACT format when done):
Thought: Task complete
Action: finish_task
Args: {{"summary": "Created server.js with Express API"}}

NOTE: After Args line, STOP. Do not write explanations or reasoning after the JSON.
"""

    def _build_step_prompt(self, goal: str, context: str) -> str:
        # Context window limit - reduced for better performance
        # MiniMax M2.1 has ~196K tokens, but we need headroom for skills + response
        MAX_PROMPT_CHARS = 100000  # Reduced from 200K for faster processing
        
        current_context = f"""
GOAL: {goal}
CONTEXT: {context}
WORKING_DIR: {self.current_working_dir}
SYSTEM_OS: {platform.system()}
"""
        
        # [Antigravity Fix] Move Format Reminder to the END to prevent context loss
        format_reminder = """
═══════════════════════════════════════════════════════
⚠️ CRITICAL: OUTPUT FORMAT (follow EXACTLY)
═══════════════════════════════════════════════════════
Thought: [brief reasoning - ONE sentence]
Action: [tool_name]
Args: {"key": "value"}

RULES:
• Output ONLY 3 lines (Thought, Action, Args)
• Args JSON must be on ONE line
• STOP immediately after Args - NO MORE TEXT

IF TASK IS DONE, use:
Thought: Task complete
Action: finish_task
Args: {"summary": "what you did"}
═══════════════════════════════════════════════════════
"""
        
        system_prompt = self._build_system_prompt()
        
        # Calculate fixed overhead (system + context + format reminder + buffer)
        fixed_overhead = len(system_prompt) + len(current_context) + len(format_reminder) + 5000  # Increased buffer
        
        # CRITICAL FIX: Ensure available space is never negative
        available_for_history = max(5000, MAX_PROMPT_CHARS - fixed_overhead)  # Minimum 5K chars for history
        available_for_history = MAX_PROMPT_CHARS - fixed_overhead
        
        # Build history, keeping most recent entries if we exceed limit
        history_text = ""
        for item in self.history:
            if item['role'] == 'user':
                history_text += f"OBSERVATION: {item['content']}\n"
            else:
                history_text += f"{item['content']}\n"
        
        # Compact history if it exceeds available space
        if len(history_text) > available_for_history:
            # Keep first entry (initial context) and most recent entries
            compacted_history = []
            total_chars = 0
            
            # Always keep first 2 entries for context
            first_entries = self.history[:2] if len(self.history) >= 2 else self.history[:]
            first_text = ""
            for item in first_entries:
                if item['role'] == 'user':
                    first_text += f"OBSERVATION: {item['content']}\n"
                else:
                    first_text += f"{item['content']}\n"
            
            # Calculate remaining space for recent history
            remaining_space = available_for_history - len(first_text) - 100  # 100 char buffer for separator
            
            # Build recent history from end, truncating if needed
            recent_text = ""
            for item in reversed(self.history[2:]):
                entry = ""
                if item['role'] == 'user':
                    entry = f"OBSERVATION: {item['content']}\n"
                else:
                    entry = f"{item['content']}\n"
                
                if len(recent_text) + len(entry) < remaining_space:
                    recent_text = entry + recent_text
                else:
                    break
            
            # Combine with compaction marker
            history_text = first_text + "\n... [Earlier steps compacted to fit context window] ...\n\n" + recent_text
            print(f"{Colors.YELLOW}⚠️  Context compacted: {len(self.history)} entries → fit in {available_for_history} chars{Colors.ENDC}")
        
        return system_prompt + "\n" + current_context + "\nHISTORY:\n" + history_text + "\n" + format_reminder + "\nNEXT STEP:"

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
        
        # Parse Args using balanced brace matching (stops at first complete JSON object)
        args_match = re.search(r"Args:\s*", response, re.IGNORECASE)
        
        if action_match and args_match:
            try:
                tool_name = action_match.group(1).strip()
                
                # Extract JSON by finding balanced braces (not greedy regex)
                args_start = args_match.end()
                json_str = self._extract_first_json_object(response[args_start:])
                
                if json_str:
                    import json
                    args = json.loads(json_str)
                    tool_call = {"tool": tool_name, "args": args}
                else:
                    print(f"{Colors.RED}❌ Could not find valid JSON object after Args:{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}❌ Error parsing tool args: {e}{Colors.ENDC}")
        
        return thought, tool_call
    
    def _extract_first_json_object(self, text: str) -> Optional[str]:
        """Extract the first complete JSON object using balanced brace matching.
        
        This prevents issues where the model outputs extra text after the JSON.
        """
        text = text.strip()
        if not text.startswith('{'):
            # Find the first {
            brace_pos = text.find('{')
            if brace_pos == -1:
                return None
            text = text[brace_pos:]
        
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i, char in enumerate(text):
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if in_string:
                continue
            
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Found complete JSON object
                    return text[:i+1]
        
        return None  # No complete JSON object found

    def _execute_tool(self, tool_name: str, args: Dict) -> str:
        # Check against allowed tools if restriction is set
        if self.allowed_tools and tool_name not in self.allowed_tools:
            return f"Error: Tool '{tool_name}' is not allowed in this mode."

        # Try to use tool registry for extended tools
        tool = self.tool_registry.get_tool(tool_name)
        if tool:
            try:
                # Use the tool registry's execute method with proper context
                result = self.tool_registry.execute_tool(
                    tool_name=tool_name,
                    input_data=args,
                    agent_id=self.agent_id,
                    agent_type=self.agent_type,
                    context={"workspace": self.workspace}
                )

                if result.success:
                    if hasattr(result, 'data') and result.data:
                        # Format the data nicely
                        if isinstance(result.data, dict):
                            return json.dumps(result.data, indent=2)
                        return str(result.data)
                    return "Success"
                else:
                    return f"Error: {result.error}"
            except Exception as e:
                return f"Error executing tool '{tool_name}': {str(e)}"

        # Fall back to legacy core tools
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
            
            # Add aliases for finish_task (models often try these variations)
            elif tool_name in ["complete_task", "task_complete", "done", "complete", "end_task", "none", "no_action_required"]:
                print(f"{Colors.YELLOW}⚠️  '{tool_name}' interpreted as 'finish_task'{Colors.ENDC}")
                return "Task Completed."
            
            else:
                return f"Error: Unknown tool '{tool_name}'"
                
        except Exception as e:
            return f"Error executing tool: {str(e)}"
