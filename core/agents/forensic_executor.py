"""
Forensic Scanner Executor
Agent 00: Security audit & pattern analysis
"""

from pathlib import Path
from typing import Dict, List
from core.agent_executor import AgentExecutor, AgentResult, Artifact


class ForensicExecutor(AgentExecutor):
    """Agent 00: Forensic Scanner - Security audit & pattern analysis"""

    def execute(self, query: str, context: Dict, **kwargs) -> AgentResult:
        """Execute forensic scanning (security audit & pattern analysis)"""
        insights = []
        artifacts = []

        # Security scan (no AI required)
        security_issues = self._scan_security()
        pattern_analysis = self._analyze_patterns()

        # Generate report
        report_content = self._generate_report(security_issues, pattern_analysis)
        artifacts.append(Artifact(
            type="report",
            path=".vibecode/security_audit.md",
            content=report_content
        ))

        if security_issues:
            insights.append(f"Found {len(security_issues)} security issue(s)")

        return AgentResult(
            agent_id="00",
            status="success",
            artifacts=artifacts,
            insights=insights,
            next_recommended_agent="01" if security_issues else None,
            confidence=0.9
        )

    def _scan_security(self) -> List[Dict]:
        """Scan for security issues (rule-based)"""
        issues = []
        workspace_path = Path(self.workspace)

        # Security patterns to check
        security_patterns = {
            "env_files": ["*.env", ".env*"],
            "api_keys": ["api_key", "apikey", "api-key"],
            "secrets": ["secret", "password", "passwd", "pwd"],
            "credentials": ["credentials", "auth_token", "token"]
        }

        # Scan Python files for security issues
        for py_file in workspace_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Check for hardcoded secrets
                for category, patterns in security_patterns.items():
                    for pattern in patterns:
                        if pattern in content.lower():
                            # Simple heuristic: check if it's a variable assignment
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if pattern in line.lower() and ('=' in line or '==' in line):
                                    issues.append({
                                        "file": str(py_file.relative_to(workspace_path)),
                                        "line": i,
                                        "type": category,
                                        "pattern": pattern,
                                        "severity": "medium"
                                    })
            except Exception:
                # Skip files that can't be read
                pass

        return issues

    def _analyze_patterns(self) -> Dict:
        """Analyze code patterns (no AI needed)"""
        patterns = {
            "total_files": 0,
            "python_files": 0,
            "test_files": 0,
            "config_files": 0
        }

        workspace_path = Path(self.workspace)

        # Count file types
        for file_path in workspace_path.rglob("*"):
            if file_path.is_file():
                patterns["total_files"] += 1
                if file_path.suffix == ".py":
                    patterns["python_files"] += 1
                    if "test" in file_path.name.lower():
                        patterns["test_files"] += 1
                elif file_path.suffix in [".json", ".yaml", ".yml", ".cfg", ".ini"]:
                    patterns["config_files"] += 1

        return patterns

    def _generate_report(self, security_issues: List[Dict], pattern_analysis: Dict) -> str:
        """Generate security audit report"""
        report = ["# Security Audit Report\n"]

        # Summary
        report.append("## Summary")
        report.append(f"- Total files scanned: {pattern_analysis.get('total_files', 0)}")
        report.append(f"- Python files: {pattern_analysis.get('python_files', 0)}")
        report.append(f"- Test files: {pattern_analysis.get('test_files', 0)}")
        report.append(f"- Security issues found: {len(security_issues)}")
        report.append("")

        # Security issues
        if security_issues:
            report.append("## Security Issues")
            for issue in security_issues:
                report.append(f"- **{issue['type']}** in `{issue['file']}:{issue['line']}`")
                report.append(f"  - Pattern: `{issue['pattern']}`")
                report.append(f"  - Severity: {issue['severity']}")
            report.append("")
        else:
            report.append("## Security Issues")
            report.append("No security issues detected.")
            report.append("")

        # Recommendations
        report.append("## Recommendations")
        if security_issues:
            report.append("- Remove hardcoded secrets from source code")
            report.append("- Use environment variables or secret management")
            report.append("- Review and rotate any exposed credentials")
        else:
            report.append("- Continue following security best practices")
            report.append("- Regular security audits recommended")

        return "\n".join(report)
