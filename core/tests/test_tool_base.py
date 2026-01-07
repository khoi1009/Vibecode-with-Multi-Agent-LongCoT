"""
Unit Tests for Tool Base Module
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from core.tools.tool_base import (
    Tool, ToolResult, ToolSchema, ToolParameter,
    ToolCategory, RateLimiter, ToolRestrictionChecker,
    AgentType, AGENT_TOOL_PERMISSIONS
)


class TestToolResult:
    """Tests for ToolResult dataclass"""

    def test_success_result(self):
        result = ToolResult(success=True, data="test data")
        assert result.success is True
        assert result.data == "test data"
        assert result.error is None
        assert result.is_error is False

    def test_error_result(self):
        result = ToolResult(success=False, error="Something went wrong")
        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.is_error is True

    def test_result_with_metadata(self):
        result = ToolResult(
            success=True,
            data={"key": "value"},
            metadata={"execution_time": 0.5}
        )
        assert result.metadata["execution_time"] == 0.5


class TestToolSchema:
    """Tests for ToolSchema validation"""

    def test_empty_schema(self):
        schema = ToolSchema(description="Test schema")
        assert schema.description == "Test schema"
        is_valid, _ = schema.validate({})
        assert is_valid is True

    def test_required_string_param(self):
        schema = ToolSchema()
        schema.add_string("name", required=True, min_length=1)

        # Should fail - missing required param
        is_valid, error = schema.validate({})
        assert is_valid is False
        assert "name" in error

        # Should fail - empty string
        is_valid, error = schema.validate({"name": ""})
        assert is_valid is False

        # Should pass
        is_valid, error = schema.validate({"name": "test"})
        assert is_valid is True

    def test_integer_param_with_range(self):
        schema = ToolSchema()
        schema.add_integer("count", required=True, min_value=0, max_value=100)

        # Should fail - below minimum
        is_valid, error = schema.validate({"count": -1})
        assert is_valid is False

        # Should fail - above maximum
        is_valid, error = schema.validate({"count": 101})
        assert is_valid is False

        # Should pass
        is_valid, error = schema.validate({"count": 50})
        assert is_valid is True

    def test_path_param(self):
        schema = ToolSchema()
        schema.add_path("filepath", required=True, must_exist=True, must_be_file=True)

        # Should fail - path doesn't exist
        is_valid, error = schema.validate({"filepath": "/nonexistent/path.txt"})
        assert is_valid is False

    def test_unknown_param(self):
        schema = ToolSchema()
        schema.add_string("name", required=True)

        is_valid, error = schema.validate({"name": "test", "extra": "value"})
        assert is_valid is False
        assert "extra" in error

    def test_get_summary(self):
        schema = ToolSchema(description="Test")
        schema.add_string("name", required=True, description="The name")
        schema.add_integer("count", required=False)

        summary = schema.get_summary()
        assert summary["description"] == "Test"
        assert "name" in summary["parameters"]
        assert "count" in summary["parameters"]
        assert summary["required"] == ["name"]


class TestRateLimiter:
    """Tests for RateLimiter"""

    def test_default_limit(self):
        limiter = RateLimiter(default_calls_per_minute=5)
        # First 5 calls should be allowed
        for i in range(5):
            assert limiter.is_allowed("test_tool") is True
            limiter.record_call("test_tool")

        # 6th call should be blocked
        assert limiter.is_allowed("test_tool") is False

    def test_custom_limit(self):
        limiter = RateLimiter()
        limiter.set_limit("special_tool", 2)

        assert limiter.is_allowed("special_tool") is True
        limiter.record_call("special_tool")
        assert limiter.is_allowed("special_tool") is True
        limiter.record_call("special_tool")
        assert limiter.is_allowed("special_tool") is False

    def test_get_remaining(self):
        limiter = RateLimiter(default_calls_per_minute=3)
        assert limiter.get_remaining("tool") == 3

        limiter.record_call("tool")
        assert limiter.get_remaining("tool") == 2

        limiter.record_call("tool")
        limiter.record_call("tool")
        assert limiter.get_remaining("tool") == 0

    def test_reset(self):
        limiter = RateLimiter(default_calls_per_minute=1)
        assert limiter.is_allowed("tool") is True
        limiter.record_call("tool")
        assert limiter.is_allowed("tool") is False

        limiter.reset("tool")
        assert limiter.is_allowed("tool") is True


class TestToolRestrictionChecker:
    """Tests for ToolRestrictionChecker"""

    def setup_method(self):
        self.checker = ToolRestrictionChecker()

    def test_unrestricted_agent(self):
        """ALL agent type should have access to all tools"""
        assert self.checker.can_use_tool("agent1", "any_tool", AgentType.ALL) is True
        assert self.checker.can_use_tool("agent1", "read_file", AgentType.ALL) is True

    def test_architect_restrictions(self):
        """Architect should have limited tool access"""
        assert self.checker.can_use_tool("01", "read_file", AgentType.ARCHITECT) is True
        assert self.checker.can_use_tool("01", "write_file", AgentType.ARCHITECT) is False

    def test_builder_permissions(self):
        """Builder should have file write permissions"""
        assert self.checker.can_use_tool("02", "write_file", AgentType.BUILDER) is True
        assert self.checker.can_use_tool("02", "run_command", AgentType.BUILDER) is True

    def test_custom_restriction(self):
        """Test adding custom tool restrictions"""
        self.checker.add_restriction("dangerous_tool", [AgentType.INTEGRATOR])

        assert self.checker.can_use_tool("02", "dangerous_tool", AgentType.BUILDER) is False
        assert self.checker.can_use_tool("05", "dangerous_tool", AgentType.INTEGRATOR) is True

    def test_get_allowed_tools(self):
        """Test getting allowed tools for agent type"""
        tools = self.checker.get_allowed_tools(AgentType.QA)
        assert "run_tests" in tools
        assert "read_file" in tools

    def test_get_allowed_tools_all(self):
        """ALL agent type should return empty list (all tools)"""
        tools = self.checker.get_allowed_tools(AgentType.ALL)
        assert tools == []


class TestToolBaseClass:
    """Tests for the abstract Tool base class"""

    def test_tool_creation(self):
        """Test basic tool creation"""
        class TestTool(Tool):
            def get_schema(self):
                return ToolSchema()

            def execute(self, input_data, context=None):
                return ToolResult(success=True, data="executed")

        tool = TestTool(
            name="test_tool",
            description="A test tool",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            tags=["test", "example"]
        )

        assert tool.name == "test_tool"
        assert tool.version == "1.0.0"
        assert tool.category == ToolCategory.UTILITY
        assert "test" in tool.tags

    def test_tool_metadata(self):
        class TestTool(Tool):
            def get_schema(self):
                return ToolSchema()

            def execute(self, input_data, context=None):
                return ToolResult(success=True)

        tool = TestTool(name="meta_test", description="Test")
        meta = tool.metadata

        assert meta["name"] == "meta_test"
        assert meta["category"] == "utility"
        assert "version" in meta

    def test_tool_run_method(self):
        """Test the run() method with validation and execution"""
        class TestTool(Tool):
            def get_schema(self):
                schema = ToolSchema()
                schema.add_string("message", required=True)
                return schema

            def execute(self, input_data, context=None):
                return ToolResult(success=True, data=input_data["message"])

        tool = TestTool(name="echo", description="Echo tool")

        # Should fail - missing required param
        result = tool.run({})
        assert result.success is False
        assert "message" in result.error

        # Should succeed
        result = tool.run({"message": "hello"})
        assert result.success is True
        assert result.data == "hello"

    def test_tool_run_with_rate_limit(self):
        """Test rate limiting in run() method"""
        class TestTool(Tool):
            def get_schema(self):
                return ToolSchema()

            def execute(self, input_data, context=None):
                return ToolResult(success=True)

        tool = TestTool(name="rate_limited", description="Rate limited")
        limiter = RateLimiter(default_calls_per_minute=1)

        # First call should succeed
        result = tool.run({}, rate_limiter=limiter)
        assert result.success is True

        # Second call should be rate limited
        result = tool.run({}, rate_limiter=limiter)
        assert result.success is False
        assert "Rate limit" in result.error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
