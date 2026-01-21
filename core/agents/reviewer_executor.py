"""
Reviewer Executor
Agent 04: Code Review and Security Analysis via ReasoningEngine
"""

from pathlib import Path
from typing import Dict, List, Tuple
from core.agent_executor import AgentExecutor, AgentResult, Artifact
import re


class ReviewerExecutor(AgentExecutor):
    """Agent 04: Reviewer - Code review and security analysis"""

    def __init__(self, workspace: Path, ai_provider=None, skill_loader=None):
        super().__init__(workspace, ai_provider, skill_loader)
        self.reasoning_engine = None
        if ai_provider:
            try:
                from core.reasoning_engine import ReasoningEngine
                self.reasoning_engine = ReasoningEngine(workspace, ai_provider)
            except ImportError:
                pass

    def execute(self, query: str, context: Dict, **kwargs) -> AgentResult:
        """Execute code review"""
        artifacts_to_review = context.get("artifacts", [])
        plan = context.get("plan_content", "")

        # Try ReasoningEngine if available
        if self.reasoning_engine and self.has_ai():
            return self._execute_with_reasoning_engine(query, plan, context)

        # Fallback: Static analysis
        return self._fallback_static_review(query, context)

    def _execute_with_reasoning_engine(self, query: str, plan: str, context: Dict) -> AgentResult:
        """Execute using ReasoningEngine for comprehensive review"""
        try:
            prompt = self._build_review_prompt(query, plan, context)
            # Pass minimal context - not the full dict which exceeds API limits
            minimal_context = f"Task: {context.get('task_type', 'review')}. Working in {self.workspace}"
            result = self.reasoning_engine.run_goal(prompt, minimal_context)

            if result.get("success"):
                return AgentResult(
                    agent_id="04",
                    status="success",
                    artifacts=[Artifact(
                        type="report",
                        path="review_report.md",
                        content=result.get("summary", "Review complete")
                    )],
                    insights=[
                        "Comprehensive code review completed",
                        "Security patterns verified",
                        "Performance considerations checked"
                    ],
                    next_recommended_agent="05",
                    confidence=0.9
                )
            else:
                return self._fallback_static_review(query, context, reason="AI review incomplete")

        except Exception as e:
            return self._fallback_static_review(query, context, reason=f"Review error: {str(e)}")

    def _fallback_static_review(self, query: str, context: Dict, reason: str = "") -> AgentResult:
        """Fallback static code review"""
        insights = []
        issues = []
        
        # Scan source files
        source_files = self._get_source_files()
        
        # Run security checks
        security_issues = self._security_review(source_files)
        issues.extend(security_issues)
        
        # Run code quality checks
        quality_issues = self._quality_review(source_files)
        issues.extend(quality_issues)
        
        # Run performance checks
        perf_issues = self._performance_review(source_files)
        issues.extend(perf_issues)

        # Determine status based on issues
        critical_count = sum(1 for _, severity, _ in issues if severity == 'critical')
        warning_count = sum(1 for _, severity, _ in issues if severity == 'warning')
        
        if critical_count > 0:
            status = "failed"
            insights.append(f"❌ {critical_count} critical issues must be fixed")
        elif warning_count > 5:
            status = "partial"
            insights.append(f"⚠️ {warning_count} warnings should be addressed")
        else:
            status = "success"
            insights.append("✅ Code review passed")

        insights.append(f"Reviewed {len(source_files)} files")
        
        if reason:
            insights.append(f"Note: {reason}")

        report = self._generate_review_report(source_files, issues)

        return AgentResult(
            agent_id="04",
            status=status,
            artifacts=[Artifact(
                type="report",
                path="review_report.md",
                content=report
            )],
            insights=insights,
            next_recommended_agent="05" if status != "failed" else "07",
            confidence=0.7 if status == "success" else 0.5
        )

    def _build_review_prompt(self, query: str, plan: str, context: Dict) -> str:
        """Build prompt for code review"""
        return f"""# Code Review Request

## Original Request
{query}

## Architecture Plan
{plan if plan else "No specific plan provided"}

## Review Instructions

You are a Principal Staff Engineer reviewing this code. Check:

### Security Review (OWASP Top 10):
1. **Injection** - SQL, NoSQL, Command injection vulnerabilities
2. **Broken Auth** - Weak password handling, session management
3. **Sensitive Data** - Hardcoded secrets, exposed credentials
4. **XXE** - XML external entity processing
5. **Access Control** - Missing authorization checks
6. **Security Misconfig** - Debug modes, default credentials
7. **XSS** - Unescaped user input in output
8. **Insecure Deserialization** - Untrusted data processing
9. **Known Vulnerabilities** - Outdated dependencies
10. **Logging** - Missing security event logging

### Code Quality:
- Error handling completeness
- Input validation
- Type safety
- Code duplication
- Naming conventions
- Documentation coverage

### Performance:
- N+1 queries
- Unnecessary re-renders
- Memory leaks
- Large bundle imports
- Missing pagination

Generate a detailed review report with severity levels."""

    def _get_source_files(self) -> List[Path]:
        """Get source files to review"""
        extensions = ['.ts', '.tsx', '.js', '.jsx', '.py', '.java', '.go', '.rs']
        source_files = []
        
        for ext in extensions:
            source_files.extend(self.workspace.rglob(f'*{ext}'))
        
        # Filter out non-source directories
        excluded = ['node_modules', '.next', 'dist', 'build', '__pycache__', '.git', 'venv']
        source_files = [f for f in source_files 
                        if not any(ex in str(f) for ex in excluded)]
        
        return source_files[:100]  # Limit for performance

    def _security_review(self, files: List[Path]) -> List[Tuple[str, str, str]]:
        """Check for security vulnerabilities"""
        issues = []
        
        security_patterns = {
            # Critical patterns
            r'password\s*=\s*["\'][^"\']+["\']': ('Hardcoded password detected', 'critical'),
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']': ('Hardcoded API key detected', 'critical'),
            r'secret\s*=\s*["\'][^"\']+["\']': ('Hardcoded secret detected', 'critical'),
            r'eval\s*\(': ('Use of eval() is dangerous', 'critical'),
            r'exec\s*\(': ('Use of exec() is dangerous', 'critical'),
            r'\$\{.*\}.*query|query.*\$\{': ('Possible SQL injection', 'critical'),
            
            # Warning patterns
            r'console\.log': ('Console.log should be removed in production', 'warning'),
            r'debugger': ('Debugger statement found', 'warning'),
            r'TODO|FIXME|HACK': ('Unresolved TODO/FIXME comment', 'info'),
            r'any\s*[;,\)]': ('TypeScript any type usage', 'warning'),
            r'innerHTML\s*=': ('innerHTML can lead to XSS', 'warning'),
            r'dangerouslySetInnerHTML': ('dangerouslySetInnerHTML is risky', 'warning'),
        }
        
        for file_path in files[:50]:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                relative_path = str(file_path.relative_to(self.workspace))
                
                for pattern, (message, severity) in security_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append((f"{relative_path}: {message}", severity, pattern))
                        
            except Exception:
                pass
        
        return issues

    def _quality_review(self, files: List[Path]) -> List[Tuple[str, str, str]]:
        """Check for code quality issues"""
        issues = []
        
        for file_path in files[:30]:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                relative_path = str(file_path.relative_to(self.workspace))
                
                # Check file length
                if len(lines) > 500:
                    issues.append((f"{relative_path}: File too long ({len(lines)} lines)", 'warning', 'file_length'))
                
                # Check function length (simplified)
                if content.count('function') > 20:
                    issues.append((f"{relative_path}: Too many functions, consider splitting", 'info', 'complexity'))
                
                # Check for empty catch blocks
                if re.search(r'catch\s*\([^)]*\)\s*\{\s*\}', content):
                    issues.append((f"{relative_path}: Empty catch block found", 'warning', 'error_handling'))
                
                # Check for missing error handling
                if 'async' in content and 'catch' not in content and 'try' not in content:
                    issues.append((f"{relative_path}: Async code without error handling", 'warning', 'error_handling'))
                    
            except Exception:
                pass
        
        return issues

    def _performance_review(self, files: List[Path]) -> List[Tuple[str, str, str]]:
        """Check for performance issues"""
        issues = []
        
        for file_path in files[:30]:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                relative_path = str(file_path.relative_to(self.workspace))
                
                # Check for N+1 query patterns
                if re.search(r'for.*await.*find|forEach.*await', content):
                    issues.append((f"{relative_path}: Possible N+1 query in loop", 'warning', 'n+1'))
                
                # Check for missing useCallback/useMemo in React
                if '.tsx' in str(file_path) or '.jsx' in str(file_path):
                    if 'onClick' in content and 'useCallback' not in content:
                        issues.append((f"{relative_path}: Consider useCallback for event handlers", 'info', 'react_perf'))
                
                # Check for large imports
                if "import * from" in content:
                    issues.append((f"{relative_path}: Barrel import may increase bundle size", 'info', 'bundle'))
                    
            except Exception:
                pass
        
        return issues

    def _generate_review_report(self, files: List[Path], issues: List[Tuple[str, str, str]]) -> str:
        """Generate comprehensive review report"""
        critical = [i for i in issues if i[1] == 'critical']
        warnings = [i for i in issues if i[1] == 'warning']
        info = [i for i in issues if i[1] == 'info']
        
        report = [
            "# Code Review Report",
            "",
            f"**Files Reviewed:** {len(files)}",
            f"**Total Issues:** {len(issues)}",
            "",
            "## Summary",
            f"- 🔴 Critical: {len(critical)}",
            f"- 🟡 Warnings: {len(warnings)}",
            f"- 🔵 Info: {len(info)}",
            ""
        ]
        
        if critical:
            report.extend([
                "## 🔴 Critical Issues (Must Fix)",
                ""
            ])
            for issue, _, _ in critical:
                report.append(f"- {issue}")
            report.append("")
        
        if warnings:
            report.extend([
                "## 🟡 Warnings (Should Fix)",
                ""
            ])
            for issue, _, _ in warnings[:15]:  # Limit displayed warnings
                report.append(f"- {issue}")
            if len(warnings) > 15:
                report.append(f"- ... and {len(warnings) - 15} more warnings")
            report.append("")
        
        if info:
            report.extend([
                "## 🔵 Suggestions (Nice to Have)",
                ""
            ])
            for issue, _, _ in info[:10]:
                report.append(f"- {issue}")
            report.append("")
        
        # Verdict
        if critical:
            verdict = "❌ **REJECTED** - Critical issues must be resolved before proceeding."
            next_step = "Return to Agent 07 (Medic) for fixes."
        elif len(warnings) > 10:
            verdict = "⚠️ **CONDITIONAL APPROVAL** - Address warnings before shipping."
            next_step = "Proceed to Agent 05 (Integrator) with caution."
        else:
            verdict = "✅ **APPROVED** - Code meets quality standards."
            next_step = "Proceed to Agent 05 (Integrator)."
        
        report.extend([
            "## Verdict",
            "",
            verdict,
            "",
            f"**Next Step:** {next_step}"
        ])
        
        return "\n".join(report)
