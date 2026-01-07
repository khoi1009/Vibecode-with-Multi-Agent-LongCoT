"""
Package Management Tools for ReAct Capabilities
Tools for npm and pip package operations.
"""

import subprocess
import sys
import shlex
from pathlib import Path
from typing import Dict, Any, List

from tool_base import Tool, ToolResult, ToolSchema, ToolCategory


class NpmInstallTool(Tool):
    """Install npm package(s)"""

    def __init__(self):
        super().__init__(
            name="npm_install",
            description="Install npm package(s)",
            version="1.0.0",
            category=ToolCategory.PACKAGE,
            tags=["npm", "install", "package", "javascript"]
        )

    def get_schema(self) -> ToolSchema:
        return ToolSchema(description="Install npm packages")\
            .add_string("package", required=False,
                       description="Package name(s) to install (space-separated)")\
            .add_string("version", required=False,
                       description="Specific version to install")\
            .add_string("global", required=False,
                       description="Install globally (true/false)")\
            .add_string("save", required=False,
                       description="Save to dependencies (true/false, default: true)")

    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute npm install"""
        workspace = context.get("workspace") if context else None
        if not workspace:
            return ToolResult(success=False, error="Workspace not provided in context")

        package = input_data.get("package", "")
        version = input_data.get("version", "")
        global_install = input_data.get("global", "false").lower() == "true"
        save = input_data.get("save", "true").lower() == "true"

        # Security: Validate package name
        if package and not self._validate_package_name(package):
            return ToolResult(success=False, error="Invalid package name")

        cmd = ["npm", "install"]

        if package:
            pkg_spec = package
            if version:
                pkg_spec = f"{package}@{version}"
            cmd.append(pkg_spec)
        else:
            # Install all dependencies
            pass  # npm install without args installs all deps

        if global_install:
            cmd.append("-g")

        if not save and not global_install:
            cmd.append("--no-save")

        try:
            result = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=300  # 5 min timeout for install
            )

            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    data={
                        "status": "success",
                        "package": package or "all dependencies",
                        "version": version,
                        "global": global_install,
                        "output": result.stdout
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error=result.stderr if result.stderr else "npm install failed"
                )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="npm install timed out (>5min)")
        except Exception as e:
            return ToolResult(success=False, error=f"Error executing npm install: {str(e)}")

    def _validate_package_name(self, package_name: str) -> bool:
        """Validate package name for security"""
        # Check for command injection patterns
        dangerous_chars = [";", "&", "|", "$", "`", ">", "<", "*", "?", "!", "~"]
        return not any(char in package_name for char in dangerous_chars)


class PipInstallTool(Tool):
    """Install Python package(s)"""

    def __init__(self):
        super().__init__(
            name="pip_install",
            description="Install Python package(s)",
            version="1.0.0",
            category=ToolCategory.PACKAGE,
            tags=["pip", "install", "package", "python"]
        )

    def get_schema(self) -> ToolSchema:
        return ToolSchema(description="Install Python packages")\
            .add_string("package", required=True,
                       description="Package name(s) to install")\
            .add_string("version", required=False,
                       description="Specific version to install")\
            .add_string("index_url", required=False,
                       description="Base URL of Python Package Index")\
            .add_string("user", required=False,
                       description="Install to user site-packages (true/false)")

    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute pip install"""
        workspace = context.get("workspace") if context else None
        if not workspace:
            return ToolResult(success=False, error="Workspace not provided in context")

        package = input_data.get("package", "")
        version = input_data.get("version", "")
        index_url = input_data.get("index_url", "")
        user = input_data.get("user", "false").lower() == "true"

        if not package:
            return ToolResult(success=False, error="Package name is required")

        if not self._validate_package_name(package):
            return ToolResult(success=False, error="Invalid package name")

        cmd = [sys.executable, "-m", "pip", "install"]

        pkg_spec = package
        if version:
            pkg_spec = f"{package}=={version}"
        cmd.append(pkg_spec)

        if index_url:
            cmd.extend(["--index-url", index_url])

        if user:
            cmd.append("--user")

        try:
            result = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    data={
                        "status": "success",
                        "package": package,
                        "version": version,
                        "output": result.stdout
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error=result.stderr if result.stderr else "pip install failed"
                )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="pip install timed out (>5min)")
        except Exception as e:
            return ToolResult(success=False, error=f"Error executing pip install: {str(e)}")

    def _validate_package_name(self, package_name: str) -> bool:
        """Validate package name for security"""
        # Check for command injection patterns
        dangerous_chars = [";", "&", "|", "$", "`", ">", "<", "*", "?", "!", "~"]
        return not any(char in package_name for char in dangerous_chars)


class NpmRunTool(Tool):
    """Run npm script"""

    def __init__(self):
        super().__init__(
            name="npm_run",
            description="Run npm script",
            version="1.0.0",
            category=ToolCategory.PACKAGE,
            tags=["npm", "run", "script", "build"]
        )

    def get_schema(self) -> ToolSchema:
        return ToolSchema(description="Run npm script")\
            .add_string("script", required=True,
                       description="Script name from package.json")\
            .add_string("args", required=False,
                       description="Additional arguments to pass to script")

    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute npm run"""
        workspace = context.get("workspace") if context else None
        if not workspace:
            return ToolResult(success=False, error="Workspace not provided in context")

        script = input_data.get("script", "")
        args = input_data.get("args", "")

        if not script:
            return ToolResult(success=False, error="Script name is required")

        # Whitelist common scripts for security
        allowed_scripts = ["build", "test", "lint", "start", "dev", "format", "typecheck"]
        if script not in allowed_scripts:
            return ToolResult(
                success=False,
                error=f"Script '{script}' not in allowed list: {', '.join(allowed_scripts)}"
            )

        # Security: Validate and sanitize args to prevent injection
        if args:
            if not self._validate_script_args(args):
                return ToolResult(
                    success=False,
                    error="Invalid arguments. Only alphanumeric, spaces, hyphens, and underscores allowed"
                )

        cmd = ["npm", "run", script]
        if args:
            # Use shlex to safely split arguments
            import shlex
            cmd.extend(shlex.split(args))

        try:
            result = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=300
            )

            return ToolResult(
                success=result.returncode == 0,
                data={
                    "status": "success" if result.returncode == 0 else "failed",
                    "script": script,
                    "args": args,
                    "output": result.stdout,
                    "error": result.stderr if result.stderr else None
                } if result.returncode == 0 else None,
                error=None if result.returncode == 0 else (result.stderr or "Script execution failed")
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="npm run timed out (>5min)")
        except Exception as e:
            return ToolResult(success=False, error=f"Error executing npm run: {str(e)}")

    def _validate_script_args(self, args: str) -> bool:
        """Validate script arguments to prevent injection"""
        # Allow only alphanumeric, spaces, hyphens, underscores, equals, and colons
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_=:.,]+$', args):
            return False
        return True

