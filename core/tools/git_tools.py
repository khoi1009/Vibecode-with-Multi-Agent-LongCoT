"""
Git Management Tools for ReAct Capabilities
Tools for git repository operations.
"""

import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from tool_base import Tool, ToolResult, ToolSchema, ToolCategory


class GitStatusTool(Tool):
    """Check current git repository status"""

    def __init__(self):
        super().__init__(
            name="git_status",
            description="Check current git repository status",
            version="1.0.0",
            category=ToolCategory.GIT,
            tags=["git", "status", "repository"]
        )

    def get_schema(self) -> ToolSchema:
        return ToolSchema(description="Check git repository status")\
            .add_string("porcelain", required=False,
                       description="Use porcelain format (true/false)")

    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute git status check"""
        workspace = context.get("workspace") if context else None
        if not workspace:
            return ToolResult(success=False, error="Workspace not provided in context")

        porcelain = input_data.get("porcelain", "true").lower() == "true"

        try:
            cmd = ["git", "status", "--porcelain"]
            if porcelain:
                cmd.append("-b")

            result = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                output = result.stdout if result.stdout else "No changes"
                return ToolResult(
                    success=True,
                    data={
                        "status": "success",
                        "output": output,
                        "branch": self._get_current_branch(workspace) if porcelain else None
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error=result.stderr if result.stderr else "Git status failed"
                )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Git status timed out")
        except Exception as e:
            return ToolResult(success=False, error=f"Error executing git status: {str(e)}")

    def _get_current_branch(self, workspace: Path) -> Optional[str]:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None


class GitCommitTool(Tool):
    """Create a git commit with specified message"""

    def __init__(self):
        super().__init__(
            name="git_commit",
            description="Create a git commit with specified message",
            version="1.0.0",
            category=ToolCategory.GIT,
            tags=["git", "commit", "version-control"]
        )

    def get_schema(self) -> ToolSchema:
        return ToolSchema(description="Create git commit")\
            .add_string("message", required=True,
                       description="Commit message",
                       min_length=1)

    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute git commit"""
        workspace = context.get("workspace") if context else None
        if not workspace:
            return ToolResult(success=False, error="Workspace not provided in context")

        message = input_data.get("message", "Auto-commit by Vibecode")

        try:
            # Stage all changes
            stage_result = subprocess.run(
                ["git", "add", "."],
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=30
            )

            if stage_result.returncode != 0:
                return ToolResult(
                    success=False,
                    error=f"Failed to stage changes: {stage_result.stderr}"
                )

            # Commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=30
            )

            if commit_result.returncode == 0:
                # Get commit hash
                hash_result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=workspace,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown"

                return ToolResult(
                    success=True,
                    data={
                        "status": "success",
                        "message": message,
                        "commit_hash": commit_hash,
                        "output": commit_result.stdout
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error=commit_result.stderr if commit_result.stderr else "Commit failed"
                )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Git commit timed out")
        except Exception as e:
            return ToolResult(success=False, error=f"Error executing git commit: {str(e)}")


class GitDiffTool(Tool):
    """Show changes in working directory"""

    def __init__(self):
        super().__init__(
            name="git_diff",
            description="Show changes in working directory",
            version="1.0.0",
            category=ToolCategory.GIT,
            tags=["git", "diff", "changes"]
        )

    def get_schema(self) -> ToolSchema:
        return ToolSchema(description="Show git diff")\
            .add_string("staged", required=False,
                       description="Show staged changes only (true/false)")\
            .add_string("file_path", required=False,
                       description="Show diff for specific file")\
            .add_integer("max_lines", required=False,
                        description="Maximum lines to return (default: 2000)")

    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute git diff"""
        workspace = context.get("workspace") if context else None
        if not workspace:
            return ToolResult(success=False, error="Workspace not provided in context")

        cmd = ["git", "diff"]
        staged = input_data.get("staged", "false").lower() == "true"
        file_path = input_data.get("file_path")
        max_lines = input_data.get("max_lines", 2000)

        if staged:
            cmd.append("--staged")

        if file_path:
            cmd.append("--")
            cmd.append(file_path)

        try:
            result = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout
            if output and len(output) > max_lines * 80:  # rough char estimate
                lines = output.split("\n")
                if len(lines) > max_lines:
                    output = "\n".join(lines[:max_lines // 2]) + \
                            f"\n... ({len(lines) - max_lines} more lines) ...\n" + \
                            "\n".join(lines[-max_lines // 2:])

            return ToolResult(
                success=True,
                data={
                    "status": "success",
                    "output": output if output else "No changes",
                    "staged": staged,
                    "file_path": file_path
                }
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Git diff timed out")
        except Exception as e:
            return ToolResult(success=False, error=f"Error executing git diff: {str(e)}")


class GitBranchTool(Tool):
    """Create or switch git branch"""

    def __init__(self):
        super().__init__(
            name="git_branch",
            description="Create or switch git branch",
            version="1.0.0",
            category=ToolCategory.GIT,
            tags=["git", "branch", "version-control"]
        )

    def get_schema(self) -> ToolSchema:
        return ToolSchema(description="Create or switch git branch")\
            .add_string("name", required=True,
                       description="Branch name",
                       min_length=1)\
            .add_string("create", required=False,
                       description="Create new branch (true/false)")\
            .add_string("delete", required=False,
                       description="Delete branch (true/false)")

    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute git branch operation"""
        workspace = context.get("workspace") if context else None
        if not workspace:
            return ToolResult(success=False, error="Workspace not provided in context")

        name = input_data.get("name")
        create = input_data.get("create", "false").lower() == "true"
        delete = input_data.get("delete", "false").lower() == "true"

        if not name:
            return ToolResult(success=False, error="Branch name is required")

        # Security: Sanitize branch name to prevent injection
        if not self._validate_branch_name(name):
            return ToolResult(
                success=False,
                error="Invalid branch name. Use alphanumeric, hyphens, underscores, and forward slashes only"
            )

        cmd = ["git"]
        operation = ""

        try:
            if delete:
                cmd.extend(["branch", "-d", name])
                operation = "delete"
            elif create:
                cmd.extend(["checkout", "-b", name])
                operation = "create"
            else:
                cmd.extend(["checkout", name])
                operation = "switch"

            result = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                current_branch = self._get_current_branch(workspace)
                return ToolResult(
                    success=True,
                    data={
                        "status": "success",
                        "operation": operation,
                        "branch_name": name,
                        "current_branch": current_branch,
                        "output": result.stdout if result.stdout else f"Switched to {name}"
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error=result.stderr if result.stderr else f"Git branch operation failed"
                )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Git branch operation timed out")
        except Exception as e:
            return ToolResult(success=False, error=f"Error executing git branch: {str(e)}")

    def _validate_branch_name(self, name: str) -> bool:
        """Validate branch name to prevent injection"""
        # Git reference validation - alphanumeric, -, ., _, /, \
        # Based on git check-ref-format rules
        if len(name) > 255:
            return False

        # Check for invalid characters
        # Git allows: alphanumeric, ., -, _, /, \
        # But disallows: space, :, ^, ~, ?, *, [, \
        invalid_pattern = re.compile(r'[\s:^~?*\[\\]|^\.|\.\.$|/\\|\.\./')
        return not bool(invalid_pattern.search(name))

    def _get_current_branch(self, workspace: Path) -> Optional[str]:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
