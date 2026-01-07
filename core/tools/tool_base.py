"""
Tool Base Module for ReAct Capabilities
Abstract base class and utilities for all ReAct tools.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from threading import Lock
from time import time
import logging


class ToolCategory(Enum):
    """Categories for organizing tools"""
    GIT = "git"
    PACKAGE = "package"
    TEST = "test"
    API = "api"
    UTILITY = "utility"
    FILE = "file"
    SYSTEM = "system"


@dataclass
class ToolResult:
    """Result dataclass for tool execution"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_error(self) -> bool:
        return not self.success


@dataclass
class ToolParameter:
    """Schema definition for a single parameter"""
    name: str
    param_type: type
    required: bool = False
    description: str = ""
    default: Any = None
    validator: Optional[Callable[[Any], bool]] = None
    validator_error: Optional[str] = None


class ToolSchema:
    """JSON schema-like structure for input validation"""

    def __init__(self, description: str = ""):
        self.description = description
        self.parameters: Dict[str, ToolParameter] = {}
        self.required_params: List[str] = []

    def add_param(self, param: ToolParameter) -> "ToolSchema":
        """Add a parameter to the schema"""
        self.parameters[param.name] = param
        if param.required:
            self.required_params.append(param.name)
        return self

    def add_string(self, name: str, required: bool = False,
                   description: str = "", min_length: int = 0,
                   max_length: Optional[int] = None) -> "ToolSchema":
        """Add a string parameter with length validation"""
        def validate_string(value: Any) -> bool:
            if not isinstance(value, str):
                return False
            if len(value) < min_length:
                return False
            if max_length is not None and len(value) > max_length:
                return False
            return True

        error_msg = f"String must be {min_length}-{max_length or 'inf'} chars"
        param = ToolParameter(
            name=name,
            param_type=str,
            required=required,
            description=description,
            validator=validate_string,
            validator_error=error_msg
        )
        return self.add_param(param)

    def add_integer(self, name: str, required: bool = False,
                    description: str = "", min_value: Optional[int] = None,
                    max_value: Optional[int] = None) -> "ToolSchema":
        """Add an integer parameter with range validation"""
        def validate_int(value: Any) -> bool:
            if not isinstance(value, int):
                return False
            if min_value is not None and value < min_value:
                return False
            if max_value is not None and value > max_value:
                return False
            return True

        error_msg = f"Integer must be in range [{min_value or '-inf'}, {max_value or 'inf'}]"
        param = ToolParameter(
            name=name,
            param_type=int,
            required=required,
            description=description,
            validator=validate_int,
            validator_error=error_msg
        )
        return self.add_param(param)

    def add_path(self, name: str, required: bool = False,
                 description: str = "", must_exist: bool = False,
                 must_be_file: bool = False, must_be_dir: bool = False) -> "ToolSchema":
        """Add a path parameter with path validation"""
        def validate_path(value: Any) -> bool:
            if not isinstance(value, str):
                return False
            from pathlib import Path
            p = Path(value)
            if must_exist and not p.exists():
                return False
            if must_be_file and not p.is_file():
                return False
            if must_be_dir and not p.is_dir():
                return False
            return True

        error_parts = ["Path must be valid"]
        if must_exist:
            error_parts.append("exist")
        if must_be_file:
            error_parts.append("be a file")
        if must_be_dir:
            error_parts.append("be a directory")

        param = ToolParameter(
            name=name,
            param_type=str,
            required=required,
            description=description,
            validator=validate_path,
            validator_error=". ".join(error_parts)
        )
        return self.add_param(param)

    def validate(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input against schema.
        Returns (is_valid, error_message).
        """
        # Check required parameters
        for required_param in self.required_params:
            if required_param not in input_data:
                return False, f"Missing required parameter: '{required_param}'"

        # Validate each provided parameter
        for name, value in input_data.items():
            if name not in self.parameters:
                return False, f"Unknown parameter: '{name}'"

            param = self.parameters[name]
            if not isinstance(value, param.param_type):
                return False, f"Parameter '{name}' must be type {param.param_type.__name__}"

            if param.validator and not param.validator(value):
                return False, param.validator_error or f"Validation failed for '{name}'"

        return True, None

    def get_summary(self) -> Dict[str, Any]:
        """Get schema summary for documentation"""
        return {
            "description": self.description,
            "parameters": {
                name: {
                    "type": p.param_type.__name__,
                    "required": p.required,
                    "description": p.description
                }
                for name, p in self.parameters.items()
            },
            "required": self.required_params
        }


class RateLimiter:
    """
    Simple in-memory rate limiter.
    Thread-safe implementation tracking calls per tool per minute.
    """

    def __init__(self, default_calls_per_minute: int = 60):
        self.default_calls_per_minute = default_calls_per_minute
        self._tool_limits: Dict[str, int] = {}
        self._call_history: Dict[str, List[float]] = {}
        self._lock = Lock()

    def set_limit(self, tool_name: str, calls_per_minute: int) -> None:
        """Set rate limit for a specific tool"""
        with self._lock:
            self._tool_limits[tool_name] = calls_per_minute

    def get_limit(self, tool_name: str) -> int:
        """Get rate limit for a tool (uses default if not set)"""
        return self._tool_limits.get(tool_name, self.default_calls_per_minute)

    def is_allowed(self, tool_name: str) -> bool:
        """Check if a call to the tool is allowed under rate limits"""
        with self._lock:
            limit = self.get_limit(tool_name)
            now = time()

            # Initialize history if needed
            if tool_name not in self._call_history:
                self._call_history[tool_name] = []

            # Remove calls older than 1 minute
            self._call_history[tool_name] = [
                ts for ts in self._call_history[tool_name]
                if now - ts < 60
            ]

            # Check if under limit
            return len(self._call_history[tool_name]) < limit

    def record_call(self, tool_name: str) -> bool:
        """Record a tool call. Returns True if allowed, False if rate limited."""
        with self._lock:
            if not self.is_allowed(tool_name):
                return False

            self._call_history[tool_name].append(time())
            return True

    def get_remaining(self, tool_name: str) -> int:
        """Get remaining calls for a tool in current window"""
        with self._lock:
            limit = self.get_limit(tool_name)
            if tool_name not in self._call_history:
                return limit

            now = time()
            recent_calls = [
                ts for ts in self._call_history[tool_name]
                if now - ts < 60
            ]
            return max(0, limit - len(recent_calls))

    def reset(self, tool_name: Optional[str] = None) -> None:
        """Reset rate limit history. If tool_name is None, reset all."""
        with self._lock:
            if tool_name:
                self._call_history.pop(tool_name, None)
            else:
                self._call_history.clear()


# Agent ID constants for tool restrictions
class AgentType(Enum):
    """Agent types that can use tools"""
    ARCHITECT = "architect"
    BUILDER = "builder"
    DESIGNER = "designer"
    QA = "qa"
    INTEGRATOR = "integrator"
    FORENSIC = "forensic"
    ALL = "all"


# Predefined agent permission sets
AGENT_TOOL_PERMISSIONS: Dict[AgentType, List[str]] = {
    AgentType.ALL: [],  # Empty means all tools (default)
    AgentType.ARCHITECT: ["read_file", "list_dir", "git_status", "git_branch"],
    AgentType.BUILDER: ["read_file", "write_file", "list_dir", "run_command",
                        "npm_install", "pip_install", "create_directory"],
    AgentType.DESIGNER: ["read_file", "list_dir", "run_command", "npm_run"],
    AgentType.QA: ["read_file", "list_dir", "run_command", "run_tests",
                   "get_test_coverage", "git_status"],
    AgentType.INTEGRATOR: ["read_file", "write_file", "list_dir", "run_command",
                           "run_tests", "npm_run"],
    AgentType.FORENSIC: ["read_file", "list_dir", "search_codebase", "git_status",
                         "git_diff", "get_env_var"],
}


class ToolRestrictionChecker:
    """Check if agents are allowed to use specific tools"""

    def __init__(self):
        self._custom_restrictions: Dict[str, List[AgentType]] = {}

    def can_use_tool(self, agent_id: str, tool_name: str,
                     agent_type: AgentType = AgentType.ALL) -> bool:
        """Check if an agent can use a specific tool"""
        # Check custom restrictions first
        if tool_name in self._custom_restrictions:
            allowed_agents = self._custom_restrictions[tool_name]
            if agent_type not in allowed_agents and AgentType.ALL not in allowed_agents:
                return False

        # Get agent's allowed tools
        allowed_tools = AGENT_TOOL_PERMISSIONS.get(agent_type, [])

        # Empty list means all tools allowed
        if not allowed_tools:
            return True

        return tool_name in allowed_tools

    def add_restriction(self, tool_name: str, allowed_agents: List[AgentType]) -> None:
        """Add a custom restriction for a tool"""
        self._custom_restrictions[tool_name] = allowed_agents

    def get_allowed_tools(self, agent_type: AgentType) -> List[str]:
        """Get list of tools allowed for an agent type"""
        allowed_tools = AGENT_TOOL_PERMISSIONS.get(agent_type, [])
        # If empty, return all tools (indicates unrestricted)
        return allowed_tools


class Tool(ABC):
    """
    Abstract base class for all ReAct tools.

    Subclasses must implement:
    - execute(): Main tool logic
    - get_schema(): Return ToolSchema for input validation

    Optional overrides:
    - validate_input(): Custom validation before execute
    - get_metadata(): Return tool info for documentation
    """

    def __init__(self, name: str, description: str, version: str = "1.0.0",
                 category: ToolCategory = ToolCategory.UTILITY,
                 tags: List[str] = None):
        self.name = name
        self.description = description
        self.version = version
        self.category = category
        self.tags = tags or []
        self._logger = logging.getLogger(f"tool.{name}")

    @property
    def metadata(self) -> Dict[str, Any]:
        """Tool metadata for documentation and registration"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category.value,
            "tags": self.tags
        }

    @abstractmethod
    def get_schema(self) -> ToolSchema:
        """Return the input schema for this tool"""
        pass

    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input against schema.
        Override for custom validation logic.
        """
        schema = self.get_schema()
        return schema.validate(input_data)

    @abstractmethod
    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """
        Execute the tool's main functionality.

        Args:
            input_data: Validated input parameters
            context: Optional context (workspace, agent_id, etc.)

        Returns:
            ToolResult with success status and data/error
        """
        pass

    def run(self, input_data: Dict[str, Any], context: Dict[str, Any] = None,
            rate_limiter: RateLimiter = None, agent_id: str = "default") -> ToolResult:
        """
        Run the tool with full validation and error handling.

        This is the main entry point used by the ReasoningEngine.
        """
        # Check rate limit
        if rate_limiter and not rate_limiter.record_call(self.name):
            return ToolResult(
                success=False,
                error=f"Rate limit exceeded for tool '{self.name}'"
            )

        # Validate input
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            self._logger.warning(f"Validation failed for {self.name}: {error}")
            return ToolResult(success=False, error=error)

        # Execute tool
        try:
            result = self.execute(input_data, context)
            self._logger.info(f"Tool {self.name} executed successfully")
            return result
        except Exception as e:
            self._logger.error(f"Tool {self.name} failed: {str(e)}")
            return ToolResult(
                success=False,
                error=f"Execution error: {str(e)}"
            )

    def __repr__(self) -> str:
        return f"Tool(name={self.name}, version={self.version}, category={self.category.value})"
