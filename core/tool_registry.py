"""
Tool Registry for ReAct Capabilities
Central registry for all available tools with agent-specific permissions.
"""

from typing import Dict, List, Type, Optional, Any
from pathlib import Path
import sys

# Ensure the tools directory is in the path
_tools_dir = Path(__file__).parent / 'tools'
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))

# Import tool modules
from tool_base import (
    Tool,
    ToolResult,
    ToolSchema,
    ToolParameter,
    ToolCategory,
    RateLimiter,
    ToolRestrictionChecker,
    AgentType,
    AGENT_TOOL_PERMISSIONS
)
from git_tools import (
    GitStatusTool,
    GitCommitTool,
    GitDiffTool,
    GitBranchTool
)
from package_tools import (
    NpmInstallTool,
    PipInstallTool,
    NpmRunTool
)
from test_tools import (
    RunTestsTool,
    GetCoverageTool
)
from utility_tools import (
    SearchCodebaseTool,
    GetEnvVarTool,
    CreateDirectoryTool
)




class ToolRegistry:
    """
    Central registry for all available tools.

    Manages:
    - Tool registration and instantiation
    - Agent-specific tool permissions
    - Rate limiting configuration
    - Tool discovery and lookup
    """

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self._tools: Dict[str, Tool] = {}
        self._restriction_checker = ToolRestrictionChecker()
        self._rate_limiter = RateLimiter(default_calls_per_minute=60)

        # Configure default rate limits for specific tools
        self._setup_default_rate_limits()

        # Register all tools
        self._register_all_tools()

    def _setup_default_rate_limits(self) -> None:
        """Configure default rate limits for various tools"""
        # Conservative defaults
        self._rate_limiter.set_limit("npm_install", 10)  # 10 installs per minute
        self._rate_limiter.set_limit("pip_install", 10)  # 10 installs per minute
        self._rate_limiter.set_limit("git_commit", 5)   # 5 commits per minute
        self._rate_limiter.set_limit("run_tests", 3)    # 3 test runs per minute
        self._rate_limiter.set_limit("search_codebase", 30)  # 30 searches per minute

    def _register_all_tools(self) -> None:
        """Register all available tools"""
        tool_classes = [
            # Git tools
            GitStatusTool,
            GitCommitTool,
            GitDiffTool,
            GitBranchTool,
            # Package tools
            NpmInstallTool,
            PipInstallTool,
            NpmRunTool,
            # Test tools
            RunTestsTool,
            GetCoverageTool,
            # Utility tools
            SearchCodebaseTool,
            GetEnvVarTool,
            CreateDirectoryTool,
        ]

        for cls in tool_classes:
            try:
                tool = cls()
                tool._workspace = self.workspace  # Set workspace
                self._tools[tool.name] = tool
            except Exception as e:
                print(f"Warning: Failed to register tool {cls.__name__}: {e}")

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self._tools.get(name)

    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools"""
        return list(self._tools.values())

    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Get tools by category"""
        return [tool for tool in self._tools.values()
                if tool.category.value == category]

    def can_agent_use_tool(self, agent_id: str, tool_name: str,
                          agent_type: AgentType = AgentType.ALL) -> bool:
        """Check if an agent can use a specific tool"""
        return self._restriction_checker.can_use_tool(
            agent_id, tool_name, agent_type
        )

    def get_tools_for_agent(self, agent_id: str,
                           agent_type: AgentType = AgentType.ALL) -> List[str]:
        """Get list of tool names allowed for an agent"""
        allowed_tools = self._restriction_checker.get_allowed_tools(agent_type)

        # If empty list, agent has access to all tools
        if not allowed_tools:
            return list(self._tools.keys())

        # Filter to only include registered tools
        return [name for name in allowed_tools if name in self._tools]

    def get_tool_descriptions(self, tool_names: Optional[List[str]] = None) -> str:
        """
        Generate tool descriptions for system prompt.

        Args:
            tool_names: Specific tools to describe. If None, describes all tools.

        Returns:
            Formatted string with tool descriptions
        """
        if tool_names is None:
            tools = list(self._tools.values())
        else:
            tools = [self._tools[name] for name in tool_names
                     if name in self._tools]

        descriptions = []
        for tool in sorted(tools, key=lambda t: t.name):
            schema = tool.get_schema()
            param_str = ", ".join(
                f"{param.name}: {param.description}"
                for param in schema.parameters.values()
            )
            param_str = f"({param_str})" if param_str else "()"

            descriptions.append(
                f"- **{tool.name}**{param_str}: {tool.description}\n"
                f"  Category: {tool.category.value}\n"
                f"  Version: {tool.version}"
            )

        return "\n\n".join(descriptions)

    def get_tool_summary(self, tool_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get detailed tool information for documentation or API responses.

        Args:
            tool_names: Specific tools to include. If None, includes all tools.

        Returns:
            Dictionary with tool metadata
        """
        if tool_names is None:
            tools = list(self._tools.values())
        else:
            tools = [self._tools[name] for name in tool_names
                     if name in self._tools]

        return {
            tool.name: {
                "name": tool.name,
                "description": tool.description,
                "version": tool.version,
                "category": tool.category.value,
                "tags": tool.tags,
                "schema": tool.get_schema().get_summary()
            }
            for tool in tools
        }

    def execute_tool(self, tool_name: str, input_data: Dict[str, Any],
                    agent_id: str, agent_type: AgentType = AgentType.ALL,
                    context: Dict[str, Any] = None) -> Any:
        """
        Execute a tool with full validation and error handling.

        Args:
            tool_name: Name of the tool to execute
            input_data: Input parameters for the tool
            agent_id: ID of the agent executing the tool
            agent_type: Type of the agent
            context: Additional context (workspace, etc.)

        Returns:
            ToolResult from the executed tool
        """
        # Check permissions
        if not self.can_agent_use_tool(agent_id, tool_name, agent_type):
            return type('ToolResult', (), {
                'success': False,
                'error': f"Agent '{agent_id}' not allowed to use tool '{tool_name}'",
                'data': None
            })()

        # Get tool
        tool = self.get_tool(tool_name)
        if not tool:
            return type('ToolResult', (), {
                'success': False,
                'error': f"Tool '{tool_name}' not found",
                'data': None
            })()

        # Add workspace to context
        if context is None:
            context = {}
        context["workspace"] = self.workspace

        # Execute with validation, rate limiting, and error handling
        return tool.run(
            input_data=input_data,
            context=context,
            rate_limiter=self._rate_limiter,
            agent_id=agent_id
        )

    def get_rate_limit_status(self, tool_name: str) -> Dict[str, Any]:
        """Get current rate limit status for a tool"""
        return {
            "tool": tool_name,
            "limit": self._rate_limiter.get_limit(tool_name),
            "remaining": self._rate_limiter.get_remaining(tool_name),
            "allowed": self._rate_limiter.is_allowed(tool_name)
        }

    def reset_rate_limits(self, tool_name: Optional[str] = None) -> None:
        """Reset rate limit history"""
        self._rate_limiter.reset(tool_name)

    def list_categories(self) -> List[str]:
        """Get list of all tool categories"""
        return sorted(set(tool.category.value for tool in self._tools.values()))

    def get_tools_in_category(self, category: str) -> List[str]:
        """Get names of tools in a specific category"""
        return [tool.name for tool in self.get_tools_by_category(category)]

    def search_tools(self, query: str) -> List[Tool]:
        """
        Search for tools by name or description.

        Args:
            query: Search query (case-insensitive)

        Returns:
            List of matching tools
        """
        query = query.lower()
        return [
            tool for tool in self._tools.values()
            if query in tool.name.lower() or query in tool.description.lower()
        ]
