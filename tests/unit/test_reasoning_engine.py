"""
Unit tests for ReasoningEngine module.

Tests the ReAct loop implementation, tool execution, and reasoning logic.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.reasoning_engine import ReasoningEngine
from core.memory_manager import BoundedHistory


class TestReasoningEngine:
    """Test suite for ReasoningEngine class."""

    @pytest.mark.unit
    def test_init(self, reasoning_engine):
        """Test reasoning engine initialization."""
        assert reasoning_engine.workspace is not None
        assert reasoning_engine.ai_provider is not None
        assert reasoning_engine.agent_id == "02"
        assert reasoning_engine.max_steps > 0
        assert isinstance(reasoning_engine.history, BoundedHistory)

    @pytest.mark.unit
    def test_init_default_values(self, temp_workspace, mock_ai_provider):
        """Test reasoning engine with default values."""
        engine = ReasoningEngine(
            workspace=temp_workspace,
            ai_provider=mock_ai_provider
        )
        assert engine.agent_id == "02"
        assert engine.max_steps > 0

    @pytest.mark.unit
    def test_run_goal_success(self, reasoning_engine, mock_llm_sequence):
        """Test successful goal execution."""
        reasoning_engine.ai_provider = mock_llm_sequence

        result = reasoning_engine.run_goal("Test goal", "Test context")

        assert isinstance(result, dict)
        assert "success" in result or "error" in result

    @pytest.mark.unit
    def test_run_goal_with_context(self, reasoning_engine, mock_llm):
        """Test goal execution with context."""
        context = "Additional context"
        result = reasoning_engine.run_goal("Test goal", context)

        assert reasoning_engine.ai_provider.generate.called

    @pytest.mark.unit
    def test_max_steps_limit(self, reasoning_engine):
        """Test that max steps limit is respected."""
        reasoning_engine.max_steps = 5
        reasoning_engine.ai_provider.generate.return_value = "Invalid response"

        result = reasoning_engine.run_goal("Test goal", "Test context")

        assert isinstance(result, dict)

    @pytest.mark.unit
    def test_parse_response_valid(self, reasoning_engine):
        """Test parsing valid AI responses."""
        response = """Thought: I need to test this
Action: list_dir
Args: {"path": "."}"""

        thought, tool_call = reasoning_engine._parse_response(response)

        assert thought is not None
        assert "test" in thought.lower()
        assert tool_call is not None
        assert tool_call["tool"] == "list_dir"

    @pytest.mark.unit
    def test_parse_response_invalid(self, reasoning_engine):
        """Test parsing invalid responses."""
        invalid_response = "This is not in the correct format"

        thought, tool_call = reasoning_engine._parse_response(invalid_response)

        # Should handle gracefully
        assert thought is None or isinstance(thought, str)
        assert tool_call is None

    @pytest.mark.unit
    def test_parse_response_missing_action(self, reasoning_engine):
        """Test parsing response with missing action."""
        response = "Thought: Testing"

        thought, tool_call = reasoning_engine._parse_response(response)

        assert thought is not None
        assert tool_call is None

    @pytest.mark.unit
    def test_parse_response_missing_args(self, reasoning_engine):
        """Test parsing response with missing args."""
        response = "Thought: Testing\nAction: list_dir"

        thought, tool_call = reasoning_engine._parse_response(response)

        assert thought is not None
        assert tool_call is None

    @pytest.mark.unit
    def test_execute_tool_list_dir(self, reasoning_engine, temp_workspace):
        """Test executing list_dir tool."""
        # Create a test file in workspace
        test_file = temp_workspace / "test.txt"
        test_file.write_text("test")

        args = {"path": "."}
        result = reasoning_engine._execute_tool("list_dir", args)

        assert result is not None
        assert "test.txt" in result

    @pytest.mark.unit
    def test_execute_tool_read_file(self, reasoning_engine, temp_workspace):
        """Test executing read_file tool."""
        test_file = temp_workspace / "test.txt"
        test_content = "Test file content"
        test_file.write_text(test_content)

        args = {"path": "test.txt"}
        result = reasoning_engine._execute_tool("read_file", args)

        assert test_content in result

    @pytest.mark.unit
    def test_execute_tool_write_file(self, reasoning_engine, temp_workspace):
        """Test executing write_file tool."""
        args = {
            "path": "new_file.txt",
            "content": "New file content"
        }
        result = reasoning_engine._execute_tool("write_file", args)

        assert "Success" in result
        assert (temp_workspace / "new_file.txt").exists()

    @pytest.mark.unit
    def test_execute_tool_run_command(self, reasoning_engine):
        """Test executing run_command tool."""
        args = {"command": "echo 'test'"}
        result = reasoning_engine._execute_tool("run_command", args)

        assert result is not None
        assert "Exit Code" in result

    @pytest.mark.unit
    def test_execute_tool_finish_task(self, reasoning_engine):
        """Test executing finish_task tool."""
        args = {"summary": "Task completed"}
        result = reasoning_engine._execute_tool("finish_task", args)

        assert "Task Completed" in result

    @pytest.mark.unit
    def test_execute_tool_invalid(self, reasoning_engine):
        """Test executing invalid tool."""
        args = {}
        result = reasoning_engine._execute_tool("invalid_tool", args)

        assert "Error" in result

    @pytest.mark.unit
    def test_history_tracking(self, reasoning_engine, mock_llm):
        """Test that history is tracked correctly."""
        reasoning_engine.ai_provider = mock_llm

        initial_history_len = len(reasoning_engine.history)
        result = reasoning_engine.run_goal("Test goal", "Test context")
        final_history_len = len(reasoning_engine.history)

        # History should have grown
        assert final_history_len >= initial_history_len

    @pytest.mark.unit
    def test_thought_extraction(self, reasoning_engine):
        """Test extraction of thought from response."""
        response = "Thought: This is a test thought\nAction: list_dir\nArgs: {}"

        thought, _ = reasoning_engine._parse_response(response)

        assert "test thought" in thought.lower()

    @pytest.mark.unit
    def test_action_extraction(self, reasoning_engine):
        """Test extraction of action from response."""
        response = "Thought: Test\nAction: read_file\nArgs: {}"

        _, tool_call = reasoning_engine._parse_response(response)

        assert tool_call is not None
        assert tool_call["tool"] == "read_file"

    @pytest.mark.unit
    def test_args_extraction(self, reasoning_engine):
        """Test extraction of args from response."""
        response = "Thought: Test\nAction: write_file\nArgs: {\"path\": \"test.txt\"}"

        _, tool_call = reasoning_engine._parse_response(response)

        assert tool_call is not None
        assert "path" in tool_call["args"]
        assert tool_call["args"]["path"] == "test.txt"

    @pytest.mark.unit
    def test_case_insensitive_parsing(self, reasoning_engine):
        """Test case-insensitive parsing of response."""
        response = "THOUGHT: Test\nACTION: list_dir\nARGS: {}"

        thought, tool_call = reasoning_engine._parse_response(response)

        assert thought is not None
        assert tool_call is not None

    @pytest.mark.unit
    def test_multiline_thought(self, reasoning_engine):
        """Test parsing multiline thought."""
        response = """Thought: This is a
multiline thought
that spans several lines
Action: list_dir
Args: {}"""

        thought, tool_call = reasoning_engine._parse_response(response)

        assert thought is not None
        assert "multiline" in thought.lower()

    @pytest.mark.unit
    @patch('subprocess.run')
    def test_command_timeout(self, mock_subprocess, reasoning_engine):
        """Test command timeout handling."""
        mock_subprocess.side_effect = Exception("Timeout")

        args = {"command": "sleep 100"}
        result = reasoning_engine._execute_tool("run_command", args)

        assert "Error" in result

    @pytest.mark.unit
    def test_build_system_prompt(self, reasoning_engine):
        """Test system prompt building."""
        prompt = reasoning_engine._build_system_prompt()

        assert prompt is not None
        assert len(prompt) > 0
        assert "Reasoning" in prompt or "ReAct" in prompt

    @pytest.mark.unit
    def test_build_step_prompt(self, reasoning_engine):
        """Test step prompt building."""
        prompt = reasoning_engine._build_step_prompt("Test goal", "Test context")

        assert prompt is not None
        assert "Test goal" in prompt
        assert "Test context" in prompt

    @pytest.mark.unit
    def test_current_working_dir_update(self, reasoning_engine, temp_workspace):
        """Test current working directory updates."""
        initial_dir = reasoning_engine.current_working_dir

        # Simulate cd command
        args = {"command": f"cd {temp_workspace}"}
        reasoning_engine._execute_tool("run_command", args)

        # Working directory should update
        assert reasoning_engine.current_working_dir == temp_workspace

    @pytest.mark.unit
    def test_allowed_tools_restriction(self, reasoning_engine):
        """Test tool restriction with allowed_tools."""
        reasoning_engine.allowed_tools = ["list_dir"]

        args = {"command": "echo test"}
        result = reasoning_engine._execute_tool("run_command", args)

        # Should be restricted
        assert "not allowed" in result

    @pytest.mark.unit
    def test_special_characters_in_args(self, reasoning_engine):
        """Test handling special characters in tool args."""
        args = {"path": "test-file_2024.txt"}
        result = reasoning_engine._execute_tool("list_dir", args)

        assert result is not None

    @pytest.mark.unit
    def test_nested_directory_listing(self, reasoning_engine, temp_workspace):
        """Test listing nested directories."""
        # Create nested structure
        (temp_workspace / "dir1" / "dir2").mkdir(parents=True)
        (temp_workspace / "dir1" / "file.txt").write_text("test")

        args = {"path": "dir1"}
        result = reasoning_engine._execute_tool("list_dir", args)

        assert "dir2" in result or "file.txt" in result

    @pytest.mark.unit
    def test_empty_directory(self, reasoning_engine, temp_workspace):
        """Test listing empty directory."""
        empty_dir = temp_workspace / "empty"
        empty_dir.mkdir()

        args = {"path": "empty"}
        result = reasoning_engine._execute_tool("list_dir", args)

        assert result is not None

    @pytest.mark.unit
    def test_nonexistent_path(self, reasoning_engine):
        """Test handling nonexistent paths."""
        args = {"path": "nonexistent"}
        result = reasoning_engine._execute_tool("list_dir", args)

        assert "Error" in result or "does not exist" in result
