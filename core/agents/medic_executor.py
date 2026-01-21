"""
Medic Executor
Agent 07: Automated Bug Fixing and Error Recovery
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from core.agent_executor import AgentExecutor, AgentResult, Artifact
import re
import json
from datetime import datetime


class MedicExecutor(AgentExecutor):
    """Agent 07: Medic - Automated bug fixing and error recovery"""

    def __init__(self, workspace: Path, ai_provider=None, skill_loader=None):
        super().__init__(workspace, ai_provider, skill_loader)
        self.reasoning_engine = None
        if ai_provider:
            try:
                from core.reasoning_engine import ReasoningEngine
                self.reasoning_engine = ReasoningEngine(workspace, ai_provider)
            except ImportError:
                pass
        
        # Safety limits
        self.max_lines_per_fix = 50
        self.max_files_per_fix = 2
        self.max_attempts = 3
        self.attempt_history = []
        
        # State tracking
        self.state_file = workspace / ".vibecode" / "medic_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def execute(self, query: str, context: Dict, **kwargs) -> AgentResult:
        """Execute bug fixing"""
        # Load state
        self._load_state()
        
        # Check circuit breaker
        if self._check_circuit_breaker():
            return self._escalate("Circuit breaker triggered - too many failed attempts")
        
        # Parse error from context
        error_info = self._parse_error(query, context)
        
        if not error_info:
            return AgentResult(
                agent_id="07",
                status="partial",
                artifacts=[],
                insights=["No clear error to fix. Running diagnostic scan..."],
                next_recommended_agent="00",
                confidence=0.5
            )
        
        # Try to fix with ReasoningEngine
        if self.reasoning_engine and self.has_ai():
            return self._fix_with_reasoning_engine(error_info, context)
        
        # Fallback: Pattern-based fixes
        return self._apply_pattern_fix(error_info, context)

    def _load_state(self) -> None:
        """Load medic state"""
        try:
            if self.state_file.exists():
                state = json.loads(self.state_file.read_text(encoding='utf-8'))
                self.attempt_history = state.get('attempts', [])
        except Exception:
            self.attempt_history = []

    def _save_state(self) -> None:
        """Save medic state"""
        try:
            state = {
                'attempts': self.attempt_history[-10:],  # Keep last 10
                'last_updated': datetime.now().isoformat()
            }
            self.state_file.write_text(json.dumps(state, indent=2), encoding='utf-8')
        except Exception:
            pass

    def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker should trigger"""
        # Check total attempts in session
        if len(self.attempt_history) >= 5:
            recent = self.attempt_history[-5:]
            failed = sum(1 for a in recent if not a.get('success', False))
            if failed >= 4:
                return True
        
        # Check same error repeated
        if len(self.attempt_history) >= 3:
            recent_errors = [a.get('error_type') for a in self.attempt_history[-3:]]
            if len(set(recent_errors)) == 1 and recent_errors[0]:
                return True
        
        return False

    def _escalate(self, reason: str) -> AgentResult:
        """Escalate to human intervention"""
        report = [
            "# ⚠️ Medic Circuit Breaker Triggered",
            "",
            f"**Reason:** {reason}",
            "",
            "## Attempt History",
            ""
        ]
        
        for attempt in self.attempt_history[-5:]:
            status = "✅" if attempt.get('success') else "❌"
            report.append(f"- {status} {attempt.get('error_type', 'unknown')}: {attempt.get('description', 'N/A')}")
        
        report.extend([
            "",
            "## Recommendation",
            "",
            "Human intervention required. The automated fix system has reached its limits.",
            "",
            "Please review:",
            "1. The error messages in the attempt history",
            "2. The files involved",
            "3. Consider reverting recent changes",
            "",
            "After manual review, run Agent 00 (Auditor) to re-assess the codebase."
        ])
        
        return AgentResult(
            agent_id="07",
            status="failed",
            artifacts=[Artifact(
                type="report",
                path="medic_escalation.md",
                content="\n".join(report)
            )],
            insights=[reason, "Human intervention required"],
            next_recommended_agent=None,  # Human intervention
            confidence=0.0
        )

    def _parse_error(self, query: str, context: Dict) -> Optional[Dict]:
        """Parse error information from query and context"""
        error_info = {
            'type': None,
            'message': None,
            'file': None,
            'line': None,
            'stack': None
        }
        
        # Check context for error details
        if 'error' in context:
            error = context['error']
            if isinstance(error, dict):
                error_info.update(error)
            else:
                error_info['message'] = str(error)
        
        # Parse from query
        text = query + " " + str(context)
        
        # Common error patterns
        patterns = {
            'typescript': r"TS(\d+):\s*(.+?)(?:\n|$)",
            'eslint': r"error\s+(.+?)\s+(.+?)(?:\n|$)",
            'python': r"(\w+Error):\s*(.+?)(?:\n|$)",
            'node': r"Error:\s*(.+?)(?:\n|$)",
            'file_line': r"(?:at\s+)?([^\s:]+):(\d+)(?::(\d+))?",
        }
        
        # Try to extract error type
        for error_type, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if error_type == 'file_line':
                    error_info['file'] = match.group(1)
                    error_info['line'] = int(match.group(2))
                else:
                    error_info['type'] = error_type
                    error_info['message'] = match.group(0)
        
        # Check if we have enough info
        if error_info['message'] or error_info['type']:
            return error_info
        
        return None

    def _fix_with_reasoning_engine(self, error_info: Dict, context: Dict) -> AgentResult:
        """Fix using ReasoningEngine"""
        try:
            prompt = self._build_fix_prompt(error_info, context)
            # Pass minimal context - not the full dict which exceeds API limits
            minimal_context = f"Error: {error_info.get('type', 'unknown')}. Working in {self.workspace}"
            result = self.reasoning_engine.run_goal(prompt, minimal_context)
            
            # Record attempt
            self.attempt_history.append({
                'timestamp': datetime.now().isoformat(),
                'error_type': error_info.get('type'),
                'description': error_info.get('message', '')[:100],
                'success': result.get('success', False)
            })
            self._save_state()
            
            if result.get('success'):
                return AgentResult(
                    agent_id="07",
                    status="success",
                    artifacts=[],
                    insights=[
                        "Fix applied via ReasoningEngine",
                        f"Error type: {error_info.get('type', 'unknown')}"
                    ],
                    next_recommended_agent="04",  # Review the fix
                    confidence=0.8
                )
            else:
                return self._apply_pattern_fix(error_info, context)
                
        except Exception as e:
            return self._apply_pattern_fix(error_info, context, reason=str(e))

    def _apply_pattern_fix(self, error_info: Dict, context: Dict, reason: str = "") -> AgentResult:
        """Apply pattern-based fixes"""
        insights = []
        fixed = False
        
        # Try to locate the file
        file_path = self._locate_error_file(error_info)
        
        if file_path and file_path.exists():
            # Read the file
            try:
                content = file_path.read_text(encoding='utf-8')
                original_content = content
                
                # Apply known fixes
                error_type = error_info.get('type', '').lower()
                message = error_info.get('message', '').lower()
                
                # Fix: Missing import
                if 'not defined' in message or 'cannot find' in message:
                    fix_result = self._fix_missing_import(content, error_info)
                    if fix_result:
                        content = fix_result
                        fixed = True
                        insights.append("Added missing import")
                
                # Fix: Type errors
                elif 'type' in message and ('assignable' in message or 'compatible' in message):
                    fix_result = self._fix_type_error(content, error_info)
                    if fix_result:
                        content = fix_result
                        fixed = True
                        insights.append("Fixed type annotation")
                
                # Fix: Syntax errors
                elif 'syntax' in message or 'unexpected' in message:
                    fix_result = self._fix_syntax_error(content, error_info)
                    if fix_result:
                        content = fix_result
                        fixed = True
                        insights.append("Fixed syntax error")
                
                # Write back if fixed
                if fixed and content != original_content:
                    # Safety check: don't change too many lines
                    original_lines = original_content.count('\n')
                    new_lines = content.count('\n')
                    if abs(new_lines - original_lines) <= self.max_lines_per_fix:
                        file_path.write_text(content, encoding='utf-8')
                        insights.append(f"Modified {file_path.name}")
                    else:
                        fixed = False
                        insights.append("Fix would change too many lines - skipped for safety")
                        
            except Exception as e:
                insights.append(f"Could not apply fix: {str(e)}")
        else:
            insights.append("Could not locate error file")
        
        # Record attempt
        self.attempt_history.append({
            'timestamp': datetime.now().isoformat(),
            'error_type': error_info.get('type'),
            'description': error_info.get('message', '')[:100],
            'success': fixed
        })
        self._save_state()
        
        if reason:
            insights.append(f"Note: {reason}")
        
        return AgentResult(
            agent_id="07",
            status="success" if fixed else "partial",
            artifacts=[Artifact(
                type="report",
                path="medic_report.md",
                content=self._generate_medic_report(error_info, insights, fixed)
            )],
            insights=insights,
            next_recommended_agent="04" if fixed else "00",
            confidence=0.7 if fixed else 0.4
        )

    def _locate_error_file(self, error_info: Dict) -> Optional[Path]:
        """Locate the file with the error"""
        file_ref = error_info.get('file')
        
        if not file_ref:
            return None
        
        # Try direct path
        direct = self.workspace / file_ref
        if direct.exists():
            return direct
        
        # Try searching
        file_name = Path(file_ref).name
        matches = list(self.workspace.rglob(file_name))
        
        # Filter out node_modules, etc.
        matches = [m for m in matches if 'node_modules' not in str(m)]
        
        if matches:
            return matches[0]
        
        return None

    def _fix_missing_import(self, content: str, error_info: Dict) -> Optional[str]:
        """Try to fix missing import"""
        message = error_info.get('message', '')
        
        # Extract what's missing
        match = re.search(r"['\"](\w+)['\"].*(?:not defined|cannot find)", message, re.IGNORECASE)
        if match:
            missing = match.group(1)
            
            # Common auto-imports
            auto_imports = {
                'useState': "import { useState } from 'react';",
                'useEffect': "import { useEffect } from 'react';",
                'useCallback': "import { useCallback } from 'react';",
                'useMemo': "import { useMemo } from 'react';",
                'React': "import React from 'react';",
                'Path': "from pathlib import Path",
                'Dict': "from typing import Dict",
                'List': "from typing import List",
                'Optional': "from typing import Optional",
            }
            
            if missing in auto_imports:
                import_line = auto_imports[missing]
                if import_line not in content:
                    # Add import at the top
                    lines = content.split('\n')
                    # Find first non-comment, non-empty line
                    insert_pos = 0
                    for i, line in enumerate(lines):
                        if line.strip() and not line.strip().startswith(('#', '//', '/*', '*')):
                            if 'import' in line or 'from' in line:
                                insert_pos = i + 1
                            else:
                                insert_pos = i
                                break
                    
                    lines.insert(insert_pos, import_line)
                    return '\n'.join(lines)
        
        return None

    def _fix_type_error(self, content: str, error_info: Dict) -> Optional[str]:
        """Try to fix type errors"""
        line_num = error_info.get('line')
        
        if line_num:
            lines = content.split('\n')
            if 0 < line_num <= len(lines):
                line = lines[line_num - 1]
                
                # Add type assertion for common cases
                if ': any' not in line and '| undefined' not in line:
                    # This is a simplified fix - in reality would need more analysis
                    pass
        
        return None

    def _fix_syntax_error(self, content: str, error_info: Dict) -> Optional[str]:
        """Try to fix common syntax errors"""
        line_num = error_info.get('line')
        message = error_info.get('message', '').lower()
        
        if line_num:
            lines = content.split('\n')
            if 0 < line_num <= len(lines):
                line = lines[line_num - 1]
                
                # Missing semicolon
                if 'semicolon' in message and not line.rstrip().endswith(';'):
                    lines[line_num - 1] = line.rstrip() + ';'
                    return '\n'.join(lines)
                
                # Unclosed bracket
                if 'bracket' in message or 'brace' in message:
                    open_count = line.count('(') + line.count('{') + line.count('[')
                    close_count = line.count(')') + line.count('}') + line.count(']')
                    if open_count > close_count:
                        # Try to close
                        if line.count('(') > line.count(')'):
                            lines[line_num - 1] = line.rstrip() + ')'
                            return '\n'.join(lines)
        
        return None

    def _build_fix_prompt(self, error_info: Dict, context: Dict) -> str:
        """Build prompt for ReasoningEngine fix"""
        return f"""# Bug Fix Request

## Error Information
- **Type:** {error_info.get('type', 'unknown')}
- **Message:** {error_info.get('message', 'No message')}
- **File:** {error_info.get('file', 'Unknown')}
- **Line:** {error_info.get('line', 'Unknown')}

## Safety Rules (CRITICAL)
1. DO NOT delete any files
2. DO NOT replace more than {self.max_lines_per_fix} lines
3. DO NOT modify more than {self.max_files_per_fix} files
4. Always read the file BEFORE making changes
5. Make the SMALLEST possible fix

## Instructions
1. Read the error file
2. Identify the root cause
3. Apply a minimal, surgical fix
4. Verify the fix doesn't break other code

Report what you fixed and why."""

    def _generate_medic_report(self, error_info: Dict, insights: List[str], fixed: bool) -> str:
        """Generate medic report"""
        lines = [
            "# Medic Report",
            "",
            "## Error Analyzed",
            f"- **Type:** {error_info.get('type', 'unknown')}",
            f"- **File:** {error_info.get('file', 'unknown')}",
            f"- **Line:** {error_info.get('line', 'unknown')}",
            f"- **Message:** {error_info.get('message', 'No message')[:200]}",
            "",
            "## Actions Taken",
            ""
        ]
        
        for insight in insights:
            lines.append(f"- {insight}")
        
        lines.extend([
            "",
            "## Result",
            "",
            "✅ **Fix Applied**" if fixed else "⚠️ **Manual Review Required**",
            "",
            "## Next Steps",
            "",
            "- Run Agent 04 (Reviewer) to verify the fix" if fixed else "- Review error manually",
            "- Run Agent 09 (Testing) to ensure no regressions" if fixed else "- Provide more error context"
        ])
        
        return "\n".join(lines)
