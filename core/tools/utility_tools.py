"""
Utility Tools for ReAct Capabilities
General purpose tools for searching, environment variables, and file operations.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List

from tool_base import Tool, ToolResult, ToolSchema, ToolCategory


class SearchCodebaseTool(Tool):
    """Search for pattern in codebase (grep-like)"""

    def __init__(self):
        super().__init__(
            name="search_codebase",
            description="Search for pattern in codebase (grep-like)",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            tags=["search", "grep", "codebase"]
        )

    def get_schema(self) -> ToolSchema:
        return ToolSchema(description="Search for pattern in codebase")\
            .add_string("pattern", required=True,
                       description="Search pattern (regex supported)")\
            .add_string("file_type", required=False,
                       description="File extension filter (e.g., py, js)")\
            .add_string("path", required=False,
                       description="Path to search in (default: workspace root)")\
            .add_string("case_sensitive", required=False,
                       description="Case sensitive search (true/false, default: false)")\
            .add_integer("max_results", required=False,
                        description="Maximum number of results (default: 100)")

    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute codebase search"""
        workspace = context.get("workspace") if context else None
        if not workspace:
            return ToolResult(success=False, error="Workspace not provided in context")

        pattern = input_data.get("pattern", "")
        file_type = input_data.get("file_type", "")
        search_path = input_data.get("path", "")
        case_sensitive = input_data.get("case_sensitive", "false").lower() == "true"
        max_results = input_data.get("max_results", 100)

        if not pattern:
            return ToolResult(success=False, error="Pattern is required")

        # Use git grep if in repo, else fallback to grep/findstr
        use_git = self._is_git_repo(workspace)

        try:
            if use_git:
                result = self._git_grep(workspace, pattern, file_type, case_sensitive, max_results, search_path)
            else:
                result = self._fallback_grep(workspace, pattern, file_type, case_sensitive, max_results, search_path)

            return result
        except Exception as e:
            return ToolResult(success=False, error=f"Error searching codebase: {str(e)}")

    def _is_git_repo(self, workspace: Path) -> bool:
        """Check if directory is a git repository"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=workspace,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def _git_grep(self, workspace: Path, pattern: str, file_type: str,
                  case_sensitive: bool, max_results: int, search_path: str) -> ToolResult:
        """Search using git grep"""
        cmd = ["git", "grep", "-n"]

        if not case_sensitive:
            cmd.append("-i")

        if file_type:
            cmd.extend(["--", f"*.{file_type}"])

        if search_path:
            cmd.append(search_path)

        cmd.append(pattern)

        try:
            result = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout
            if output:
                lines = output.split("\n")
                if len(lines) > max_results:
                    output = "\n".join(lines[:max_results]) + f"\n... ({len(lines) - max_results} more matches)"

            return ToolResult(
                success=True,
                data={
                    "status": "success",
                    "pattern": pattern,
                    "file_type": file_type,
                    "case_sensitive": case_sensitive,
                    "results_count": len(output.split("\n")) if output else 0,
                    "output": output if output else "No matches found"
                }
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Search timed out")
        except Exception as e:
            return ToolResult(success=False, error=f"Git grep failed: {str(e)}")

    def _fallback_grep(self, workspace: Path, pattern: str, file_type: str,
                      case_sensitive: bool, max_results: int, search_path: str) -> ToolResult:
        """Fallback to system grep/findstr"""
        import platform

        system = platform.system()
        search_dir = workspace / search_path if search_path else workspace

        cmd = []
        if system == "Windows":
            cmd = ["findstr", "/R"]
            if not case_sensitive:
                cmd.append("/I")
            cmd.append(pattern)
            if file_type:
                cmd.append(f"*.{file_type}")
            cmd.append(str(search_dir))
        else:
            cmd = ["grep", "-rn"]
            if not case_sensitive:
                cmd.append("-i")
            if file_type:
                cmd.append(f"*.{file_type}")
            cmd.append(pattern)
            cmd.append(str(search_dir))

        try:
            result = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout
            if output:
                lines = output.split("\n")
                if len(lines) > max_results:
                    output = "\n".join(lines[:max_results]) + f"\n... ({len(lines) - max_results} more matches)"

            return ToolResult(
                success=True,
                data={
                    "status": "success",
                    "pattern": pattern,
                    "file_type": file_type,
                    "case_sensitive": case_sensitive,
                    "results_count": len(output.split("\n")) if output else 0,
                    "output": output if output else "No matches found"
                }
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Search timed out")
        except Exception as e:
            return ToolResult(success=False, error=f"Grep failed: {str(e)}")


class GetEnvVarTool(Tool):
    """Read environment variable (non-sensitive only)"""

    def __init__(self):
        super().__init__(
            name="get_env_var",
            description="Read environment variable (non-sensitive only)",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            tags=["environment", "variables", "config"]
        )

    def get_schema(self) -> ToolSchema:
        return ToolSchema(description="Get environment variable")\
            .add_string("name", required=True,
                       description="Environment variable name")

    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute get environment variable"""
        name = input_data.get("name", "").upper()

        if not name:
            return ToolResult(success=False, error="Variable name is required")

        # Security: Check for sensitive variable names
        sensitive_keywords = ["KEY", "SECRET", "PASSWORD", "TOKEN", "PRIVATE", "AUTH"]
        if any(keyword in name for keyword in sensitive_keywords):
            return ToolResult(
                success=False,
                error=f"Cannot read potentially sensitive variable: {name}"
            )

        value = os.environ.get(name)

        if value is None:
            return ToolResult(
                success=False,
                error=f"Environment variable not set: {name}"
            )

        return ToolResult(
            success=True,
            data={
                "status": "success",
                "name": name,
                "value": value,
                "length": len(value)
            }
        )


class CreateDirectoryTool(Tool):
    """Create directory (with parents)"""

    def __init__(self):
        super().__init__(
            name="create_directory",
            description="Create directory (with parents)",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            tags=["directory", "mkdir", "file-system"]
        )

    def get_schema(self) -> ToolSchema:
        return ToolSchema(description="Create directory")\
            .add_string("path", required=True,
                       description="Directory path to create")\
            .add_string("parents", required=False,
                       description="Create parent directories (true/false, default: true)")

    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute create directory"""
        workspace = context.get("workspace") if context else None
        if not workspace:
            return ToolResult(success=False, error="Workspace not provided in context")

        path = input_data.get("path", "")
        parents = input_data.get("parents", "true").lower() == "true"

        if not path:
            return ToolResult(success=False, error="Directory path is required")

        # Security: Ensure path is under workspace using resolve() for proper path comparison
        try:
            full_path = (workspace / path).resolve()
            workspace_resolved = workspace.resolve()

            # Use is_relative_to() if available (Python 3.9+), otherwise use startswith
            if hasattr(full_path, 'is_relative_to'):
                if not full_path.is_relative_to(workspace_resolved):
                    return ToolResult(
                        success=False,
                        error="Path must be under workspace"
                    )
            else:
                # For older Python versions, use commonpath for robust comparison
                try:
                    import os.path
                    common = os.path.commonpath([str(full_path), str(workspace_resolved)])
                    if common != str(workspace_resolved):
                        return ToolResult(
                            success=False,
                            error="Path must be under workspace"
                        )
                except ValueError:
                    # Different drives on Windows
                    return ToolResult(
                        success=False,
                        error="Path must be under workspace"
                    )
        except (OSError, ValueError) as e:
            return ToolResult(
                success=False,
                error=f"Invalid path: {str(e)}"
            )

        try:
            already_existed = full_path.exists() and full_path.is_dir()
            
            if parents:
                full_path.mkdir(parents=True, exist_ok=True)
            else:
                if already_existed:
                    # Directory exists, return success (idempotent)
                    return ToolResult(
                        success=True,
                        data={
                            "status": "already_exists",
                            "message": f"Directory already exists: {path}",
                            "path": path,
                            "full_path": str(full_path),
                            "parents": parents
                        }
                    )
                full_path.mkdir(exist_ok=False)

            # Verify directory was created
            if full_path.exists() and full_path.is_dir():
                return ToolResult(
                    success=True,
                    data={
                        "status": "created" if not already_existed else "already_exists",
                        "message": f"Directory {'created' if not already_existed else 'already exists'}: {path}",
                        "path": path,
                        "full_path": str(full_path),
                        "parents": parents
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error="Failed to create directory"
                )
        except FileExistsError:
            # This shouldn't happen with exist_ok=True, but handle gracefully
            return ToolResult(
                success=True,  # Changed from False - directory exists is success
                data={
                    "status": "already_exists",
                    "message": f"Directory already exists: {path}",
                    "path": path,
                    "full_path": str(full_path)
                }
            )
        except PermissionError:
            return ToolResult(
                success=False,
                error=f"Permission denied: {path}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error creating directory: {str(e)}"
            )

