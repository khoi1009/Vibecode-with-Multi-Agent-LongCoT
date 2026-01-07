"""
Test Execution Tools for ReAct Capabilities
Tools for running tests and getting coverage reports.
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

from tool_base import Tool, ToolResult, ToolSchema, ToolCategory


class RunTestsTool(Tool):
    """Execute test suite"""

    def __init__(self):
        super().__init__(
            name="run_tests",
            description="Execute test suite",
            version="1.0.0",
            category=ToolCategory.TEST,
            tags=["test", "pytest", "jest", "testing"]
        )

    def get_schema(self) -> ToolSchema:
        return ToolSchema(description="Execute test suite")\
            .add_string("pattern", required=False,
                       description="Test file pattern (optional)")\
            .add_string("framework", required=False,
                       description="Testing framework (pytest or jest, default: pytest)")\
            .add_string("verbose", required=False,
                       description="Verbose output (true/false, default: true)")\
            .add_string("coverage", required=False,
                       description="Generate coverage report (true/false, default: false)")

    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute test suite"""
        workspace = context.get("workspace") if context else None
        if not workspace:
            return ToolResult(success=False, error="Workspace not provided in context")

        framework = input_data.get("framework", "pytest").lower()
        pattern = input_data.get("pattern", "")
        verbose = input_data.get("verbose", "true").lower() == "true"
        generate_coverage = input_data.get("coverage", "false").lower() == "true"

        cmd = []
        success = False
        output = ""
        error = None

        if framework == "pytest":
            cmd = [sys.executable, "-m", "pytest"]
            if verbose:
                cmd.append("-v")
            if generate_coverage:
                cmd.extend(["--cov=.=", "--cov-report=term-missing"])
            if pattern:
                cmd.append(pattern)
        elif framework == "jest":
            cmd = ["npx", "jest"]
            if verbose:
                cmd.append("--verbose")
            if pattern:
                cmd.extend(["--testMatch", pattern])
        else:
            return ToolResult(success=False, error=f"Unknown framework: {framework}")

        try:
            result = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=600  # 10 min timeout for tests
            )

            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr

            # Parse results
            success = result.returncode == 0

            # Summarize output if too long
            if len(output) > 3000:
                lines = output.split("\n")
                output = "\n".join(lines[:50]) + "\n...\n" + "\n".join(lines[-50:])

            # Try to parse test summary
            test_summary = self._parse_test_summary(output, framework)

            if success:
                return ToolResult(
                    success=True,
                    data={
                        "status": "success",
                        "framework": framework,
                        "pattern": pattern,
                        "tests_run": test_summary.get("tests", 0),
                        "passed": test_summary.get("passed", 0),
                        "failed": test_summary.get("failed", 0),
                        "skipped": test_summary.get("skipped", 0),
                        "output": output
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    data={
                        "status": "failed",
                        "framework": framework,
                        "pattern": pattern,
                        "tests_run": test_summary.get("tests", 0),
                        "passed": test_summary.get("passed", 0),
                        "failed": test_summary.get("failed", 0),
                        "output": output
                    },
                    error="Tests failed"
                )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Tests timed out (>10min)")
        except Exception as e:
            return ToolResult(success=False, error=f"Error executing tests: {str(e)}")

    def _parse_test_summary(self, output: str, framework: str) -> Dict[str, int]:
        """Parse test summary from output"""
        summary = {"tests": 0, "passed": 0, "failed": 0, "skipped": 0}

        if framework == "pytest":
            # Parse pytest output
            # Look for patterns like "5 passed, 2 failed in 10s"
            import re
            match = re.search(r"(\d+) passed(?:, (\d+) failed)?(?:, (\d+) skipped)?", output)
            if match:
                summary["passed"] = int(match.group(1))
                summary["failed"] = int(match.group(2)) if match.group(2) else 0
                summary["skipped"] = int(match.group(3)) if match.group(3) else 0
                summary["tests"] = summary["passed"] + summary["failed"] + summary["skipped"]
        elif framework == "jest":
            # Parse jest output
            # Look for "Tests: 5 passed, 2 failed"
            import re
            match = re.search(r"Tests:\s+(\d+)\s+passed(?:,\s+(\d+)\s+failed)?", output)
            if match:
                summary["passed"] = int(match.group(1))
                summary["failed"] = int(match.group(2)) if match.group(2) else 0
                summary["tests"] = summary["passed"] + summary["failed"]

        return summary


class GetCoverageTool(Tool):
    """Get test coverage report"""

    def __init__(self):
        super().__init__(
            name="get_test_coverage",
            description="Get test coverage report",
            version="1.0.0",
            category=ToolCategory.TEST,
            tags=["test", "coverage", "pytest"]
        )

    def get_schema(self) -> ToolSchema:
        return ToolSchema(description="Get test coverage report")\
            .add_string("format", required=False,
                       description="Coverage format (term, json, html)")\
            .add_string("source", required=False,
                       description="Source directory to measure coverage for")\
            .add_string("fail_under", required=False,
                       description="Fail if coverage is below this percentage")

    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute coverage report"""
        workspace = context.get("workspace") if context else None
        if not workspace:
            return ToolResult(success=False, error="Workspace not provided in context")

        format_type = input_data.get("format", "term").lower()
        source = input_data.get("source", "")
        fail_under = input_data.get("fail_under", "")

        cmd = [sys.executable, "-m", "pytest"]

        if format_type == "term":
            cmd.extend(["--cov=" + (source if source else "."), "--cov-report=term-missing"])
        elif format_type == "json":
            cmd.extend(["--cov=" + (source if source else "."), "--cov-report=json"])
        elif format_type == "html":
            cmd.extend(["--cov=" + (source if source else "."), "--cov-report=html"])
        else:
            return ToolResult(success=False, error=f"Unknown format: {format_type}")

        if fail_under:
            cmd.extend(["--cov-fail-under=" + fail_under])

        cmd.extend(["-v", "--tb=short"])

        try:
            result = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=600
            )

            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr

            # Parse coverage percentage
            coverage_pct = self._parse_coverage_percentage(output)

            if result.returncode == 0 or "FAILED" in output:
                # Coverage can show failures but still have valid results
                return ToolResult(
                    success=True,
                    data={
                        "status": "success",
                        "format": format_type,
                        "source": source or ".",
                        "coverage_percentage": coverage_pct,
                        "output": output
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error=result.stderr if result.stderr else "Coverage report failed",
                    data={
                        "status": "failed",
                        "format": format_type,
                        "output": output
                    }
                )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Coverage report timed out (>10min)")
        except Exception as e:
            return ToolResult(success=False, error=f"Error generating coverage: {str(e)}")

    def _parse_coverage_percentage(self, output: str) -> float:
        """Parse coverage percentage from pytest output"""
        import re
        # Look for "TOTAL X%"
        match = re.search(r"TOTAL\s+(\d+)%", output)
        if match:
            return float(match.group(1))
        return 0.0
