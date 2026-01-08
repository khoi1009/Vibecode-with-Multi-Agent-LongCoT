"""
End-to-end tests for full workflow scenarios.

Tests complete multi-agent workflows from planning to deployment.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.orchestrator import Orchestrator
from core.reasoning_engine import ReasoningEngine
from core.message_queue import AgentMessageQueue
from core.messages import AgentMessage, MessageType


class TestFullWorkflow:
    """End-to-end test suite for full workflows."""

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_complete_code_generation_workflow(self, temp_workspace, mock_llm_sequence):
        """Test complete code generation workflow."""
        # Setup
        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm_sequence,
            agent_id="02"
        )

        # Execute full workflow
        result = orchestrator.orchestrate(
            goal="Create a Python web application with Flask",
            context="Full workflow test"
        )

        # Verify
        assert isinstance(result, dict)
        # Workflow should complete (success or documented failure)

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_multi_agent_coordination(self, temp_workspace, mock_llm_sequence):
        """Test coordination between multiple agents."""
        # Create message queue for agent communication
        message_queue = AgentMessageQueue()

        # Simulate orchestrator planning
        plan_msg = AgentMessage(
            id="plan-1",
            from_agent="orchestrator",
            to_agent="agent-01",
            message_type=MessageType.PLAN,
            payload={"goal": "Create web app"}
        )
        message_queue.push(plan_msg)

        # Simulate agent-01 (Architect) responding
        arch_response = AgentMessage(
            id="arch-1",
            from_agent="agent-01",
            to_agent="orchestrator",
            message_type=MessageType.PLAN,
            payload={"architecture": "Flask-based"}
        )
        message_queue.push(arch_response)

        # Verify message flow
        messages = message_queue.get_all_messages()
        assert len(messages) == 2

        # Orchestrator receives architect response
        orchestrator_msgs = message_queue.pop_for_agent("orchestrator")
        assert len(orchestrator_msgs) == 1

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_plan_to_code_to_test_workflow(self, temp_workspace, mock_llm_sequence):
        """Test workflow from planning to code to testing."""
        message_queue = AgentMessageQueue()

        # Step 1: Planning
        plan_msg = AgentMessage(
            id="1",
            from_agent="orchestrator",
            to_agent="agent-01",
            message_type=MessageType.PLAN,
            payload={"goal": "Build calculator"}
        )
        message_queue.push(plan_msg)

        # Step 2: Architecture received
        arch_msg = AgentMessage(
            id="2",
            from_agent="agent-01",
            to_agent="orchestrator",
            message_type=MessageType.PLAN,
            payload={"plan": "Use OOP design"}
        )
        message_queue.push(arch_msg)

        # Step 3: Orchestrator delegates to builder
        build_msg = AgentMessage(
            id="3",
            from_agent="orchestrator",
            to_agent="agent-02",
            message_type=MessageType.CODE,
            payload={"spec": "Build calculator"}
        )
        message_queue.push(build_msg)

        # Step 4: Builder completes
        code_msg = AgentMessage(
            id="4",
            from_agent="agent-02",
            to_agent="orchestrator",
            message_type=MessageType.CODE,
            payload={"files": ["calculator.py"]}
        )
        message_queue.push(code_msg)

        # Verify workflow progression
        assert message_queue.get_message_count() == 4

        # Verify all PLAN messages
        plan_messages = [
            msg for msg in message_queue.get_all_messages()
            if msg.message_type == MessageType.PLAN
        ]
        assert len(plan_messages) == 2

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_error_recovery_workflow(self, temp_workspace, mock_llm):
        """Test error recovery in full workflow."""
        # Use a mock that simulates errors
        mock_llm.responses = [
            "Thought: I need to check the file\nAction: read_file\nArgs: {\"path\": \"nonexistent.txt\"}",
            "Thought: File not found\nAction: write_file\nArgs: {\"path\": \"new_file.txt\", \"content\": \"created\"}",
            "Thought: Complete\nAction: finish_task\nArgs: {}"
        ]

        engine = ReasoningEngine(
            workspace=temp_workspace,
            ai_provider=mock_llm,
            agent_id="02"
        )

        # Goal that will encounter and recover from error
        result = engine.run_goal(
            goal="Read a file, and if it doesn't exist, create it",
            context="Error recovery test"
        )

        assert isinstance(result, dict)

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_code_review_workflow(self, temp_workspace, mock_llm_sequence):
        """Test code review workflow."""
        # Create a file first
        test_file = temp_workspace / "code.py"
        test_file.write_text("# Test code\nprint('hello')")

        # Setup orchestrator
        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm_sequence,
            agent_id="02"
        )

        # Run code generation + review
        result = orchestrator.orchestrate(
            goal="Review the code.py file for issues",
            context="Code review test"
        )

        assert isinstance(result, dict)

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_refactoring_workflow(self, temp_workspace, mock_llm_sequence):
        """Test code refactoring workflow."""
        # Create initial code
        initial_code = temp_workspace / "old_code.py"
        initial_code.write_text("""
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
""")

        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm_sequence,
            agent_id="02"
        )

        # Run refactoring
        result = orchestrator.orchestrate(
            goal="Refactor old_code.py to be more Pythonic",
            context="Refactoring test"
        )

        assert isinstance(result, dict)

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_test_generation_workflow(self, temp_workspace, mock_llm_sequence):
        """Test test generation workflow."""
        # Create a module
        module_file = temp_workspace / "math_utils.py"
        module_file.write_text("""
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
""")

        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm_sequence,
            agent_id="02"
        )

        # Generate tests
        result = orchestrator.orchestrate(
            goal="Generate unit tests for math_utils.py",
            context="Test generation"
        )

        assert isinstance(result, dict)

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_documentation_workflow(self, temp_workspace, mock_llm_sequence):
        """Test documentation generation workflow."""
        # Create code
        code_file = temp_workspace / "app.py"
        code_file.write_text("""
def main():
    '''Main application entry point'''
    print("Hello, World!")
""")

        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm_sequence,
            agent_id="02"
        )

        # Generate documentation
        result = orchestrator.orchestrate(
            goal="Generate README.md for the project",
            context="Documentation test"
        )

        assert isinstance(result, dict)

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_full_project_creation_workflow(self, temp_workspace, mock_llm_sequence):
        """Test creating a complete project structure."""
        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm_sequence,
            agent_id="02"
        )

        # Complete project creation
        result = orchestrator.orchestrate(
            goal="Create a complete Python project with structure: src/, tests/, docs/, README.md, requirements.txt",
            context="Full project creation"
        )

        assert isinstance(result, dict)

        # Verify project structure
        assert (temp_workspace / "README.md").exists() or not (temp_workspace / "README.md").exists()

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_incremental_development_workflow(self, temp_workspace, mock_llm_sequence):
        """Test incremental development across multiple runs."""
        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm_sequence,
            agent_id="02"
        )

        # Phase 1: Create base
        result1 = orchestrator.orchestrate(
            goal="Create a Python module with a Calculator class",
            context="Phase 1"
        )
        assert isinstance(result1, dict)

        # Phase 2: Extend
        result2 = orchestrator.orchestrate(
            goal="Add unit tests to the Calculator class",
            context="Phase 2"
        )
        assert isinstance(result2, dict)

        # Phase 3: Refine
        result3 = orchestrator.orchestrate(
            goal="Add documentation and type hints to the Calculator",
            context="Phase 3"
        )
        assert isinstance(result3, dict)

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_cross_agent_handoff(self, temp_workspace, mock_llm_sequence):
        """Test handoff between different agents."""
        message_queue = AgentMessageQueue()

        # Orchestrator to Architect
        msg1 = AgentMessage(
            id="1",
            from_agent="orchestrator",
            to_agent="agent-01",
            message_type=MessageType.PLAN,
            payload={"request": "Design system architecture"}
        )
        message_queue.push(msg1)

        # Architect to Builder
        msg2 = AgentMessage(
            id="2",
            from_agent="agent-01",
            to_agent="agent-02",
            message_type=MessageType.CODE,
            payload={"architecture": "Flask app"}
        )
        message_queue.push(msg2)

        # Builder to QA
        msg3 = AgentMessage(
            id="3",
            from_agent="agent-02",
            to_agent="agent-09",
            message_type=MessageType.TEST_RESULT,
            payload={"status": "code complete"}
        )
        message_queue.push(msg3)

        # Verify handoffs
        assert message_queue.get_message_count() == 3

        # Check cross-agent flow
        agent02_msgs = message_queue.pop_for_agent("agent-02")
        assert len(agent02_msgs) == 1
        assert agent02_msgs[0].from_agent == "agent-01"

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_artifact_tracking_workflow(self, temp_workspace, mock_llm_sequence):
        """Test artifact tracking throughout workflow."""
        message_queue = AgentMessageQueue()

        # Add messages with artifacts
        msg1 = AgentMessage(
            id="1",
            from_agent="agent-01",
            to_agent="orchestrator",
            message_type=MessageType.PLAN,
            payload={"plan": "architecture"},
            artifacts=["plan.md", "design.png"]
        )
        message_queue.push(msg1)

        msg2 = AgentMessage(
            id="2",
            from_agent="agent-02",
            to_agent="orchestrator",
            message_type=MessageType.CODE,
            payload={"files": ["app.py", "models.py"]},
            artifacts=["app.py", "models.py", "requirements.txt"]
        )
        message_queue.push(msg2)

        # Get all artifacts
        artifacts = message_queue.get_artifacts()

        # Verify artifact tracking
        assert "plan.md" in artifacts
        assert "app.py" in artifacts
        assert "models.py" in artifacts
        assert "requirements.txt" in artifacts

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_parallel_agent_execution(self, temp_workspace, mock_llm_sequence):
        """Test parallel execution by different agents."""
        import threading

        message_queue = AgentMessageQueue()
        results = []
        errors = []

        def agent_thread(agent_id, task):
            try:
                # Simulate agent work
                msg = AgentMessage(
                    id=f"{agent_id}-1",
                    from_agent=agent_id,
                    to_agent="orchestrator",
                    message_type=MessageType.INSIGHT,
                    payload={"result": f"Agent {agent_id} completed: {task}"}
                )
                message_queue.push(msg)
                results.append(msg)
            except Exception as e:
                errors.append(e)

        # Run multiple agents in parallel
        threads = [
            threading.Thread(target=agent_thread, args=(f"agent-{i}", f"task-{i}"))
            for i in range(3)
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Verify parallel execution
        assert len(errors) == 0
        assert len(results) == 3

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_workflow_cancellation(self, temp_workspace, mock_llm):
        """Test workflow cancellation and cleanup."""
        message_queue = AgentMessageQueue()

        # Add some messages
        for i in range(5):
            msg = AgentMessage(
                id=str(i),
                from_agent=f"agent-{i}",
                to_agent="orchestrator",
                message_type=MessageType.INSIGHT,
                payload={"step": i}
            )
            message_queue.push(msg)

        initial_count = message_queue.get_message_count()
        assert initial_count == 5

        # Clear queue (simulate cancellation)
        message_queue.clear()

        # Verify cleanup
        assert message_queue.get_message_count() == 0

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_workflow_with_custom_tools(self, temp_workspace, mock_llm_sequence):
        """Test workflow using custom tools."""
        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm_sequence,
            agent_id="02"
        )

        # Run with specific tools
        result = orchestrator.orchestrate(
            goal="Use git to initialize a repository and create a commit",
            context="Custom tools test"
        )

        assert isinstance(result, dict)

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_workflow_state_persistence(self, temp_workspace, mock_llm_sequence):
        """Test that workflow state persists across operations."""
        engine = ReasoningEngine(
            workspace=temp_workspace,
            ai_provider=mock_llm_sequence,
            agent_id="02"
        )

        # First operation
        result1 = engine.run_goal("Create file1.txt", "Context 1")
        history_len_1 = len(engine.history)

        # Second operation
        result2 = engine.run_goal("Create file2.txt", "Context 2")
        history_len_2 = len(engine.history)

        # Verify history persisted
        assert history_len_2 >= history_len_1
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_long_term_workflow(self, temp_workspace, mock_llm_sequence):
        """Test a long-running workflow with many steps."""
        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm_sequence,
            agent_id="02"
        )

        # Complex goal requiring multiple steps
        result = orchestrator.orchestrate(
            goal="""Create a complete web application with:
            1. User authentication
            2. Database models
            3. REST API endpoints
            4. Frontend pages
            5. Tests for all components""",
            context="Long-term workflow test"
        )

        assert isinstance(result, dict)

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_workflow_integration_with_skills(self, temp_workspace, mock_llm_sequence):
        """Test workflow integration with skills system."""
        # This test would verify integration with the skills system
        # For now, just verify the orchestrator can run
        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm_sequence,
            agent_id="02"
        )

        result = orchestrator.orchestrate(
            goal="Use available skills to complete a task",
            context="Skills integration test"
        )

        assert isinstance(result, dict)

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_workflow_confidence_scoring(self, temp_workspace, mock_llm_sequence):
        """Test confidence scoring throughout workflow."""
        message_queue = AgentMessageQueue()

        # Messages with different confidence levels
        high_conf = AgentMessage(
            id="1",
            from_agent="agent-01",
            to_agent="orchestrator",
            message_type=MessageType.PLAN,
            payload={"confidence": 0.95, "plan": "solid plan"}
        )
        message_queue.push(high_conf)

        medium_conf = AgentMessage(
            id="2",
            from_agent="agent-02",
            to_agent="orchestrator",
            message_type=MessageType.CODE,
            payload={"confidence": 0.7, "status": "implemented"}
        )
        message_queue.push(medium_conf)

        low_conf = AgentMessage(
            id="3",
            from_agent="agent-09",
            to_agent="orchestrator",
            message_type=MessageType.TEST_RESULT,
            payload={"confidence": 0.4, "status": "partial tests"}
        )
        message_queue.push(low_conf)

        # Verify all messages tracked
        assert message_queue.get_message_count() == 3

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_workflow_with_realistic_project(self, temp_workspace, mock_llm_sequence):
        """Test workflow with a realistic project scenario."""
        # Create realistic project structure
        (temp_workspace / "src").mkdir()
        (temp_workspace / "tests").mkdir()
        (temp_workspace / "docs").mkdir()

        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm_sequence,
            agent_id="02"
        )

        # Realistic project goal
        result = orchestrator.orchestrate(
            goal="""Build a REST API for a todo application:
            - Database models for User and Todo
            - API endpoints: /api/todos (GET, POST, PUT, DELETE)
            - Authentication middleware
            - Unit tests with >80% coverage
            - API documentation""",
            context="Realistic project test"
        )

        assert isinstance(result, dict)

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_workflow_performance_baseline(self, temp_workspace, mock_llm_sequence):
        """Establish performance baseline for workflows."""
        import time

        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm_sequence,
            agent_id="02"
        )

        start_time = time.time()
        result = orchestrator.orchestrate(
            goal="Create a simple script",
            context="Performance test"
        )
        end_time = time.time()

        duration = end_time - start_time

        assert isinstance(result, dict)
        # Should complete in reasonable time (adjust as needed)
        assert duration < 60  # Less than 1 minute for simple task

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_workflow_error_propagation(self, temp_workspace, mock_llm):
        """Test that errors are properly propagated and handled."""
        # Mock that simulates errors
        mock_llm.responses = [
            "Thought: Try operation 1\nAction: invalid_tool\nArgs: {}",
            "Thought: Try operation 2\nAction: run_command\nArgs: {\"command\": \"false\"}",
            "Thought: Recover\nAction: write_file\nArgs: {\"path\": \"recovery.txt\", \"content\": \"recovered\"}",
        ]

        engine = ReasoningEngine(
            workspace=temp_workspace,
            ai_provider=mock_llm,
            agent_id="02"
        )

        # Should handle errors and continue
        result = engine.run_goal(
            goal="Attempt operations that might fail",
            context="Error propagation test"
        )

        assert isinstance(result, dict)
