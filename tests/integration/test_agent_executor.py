"""
Integration tests for AgentExecutor.

Tests agent execution, AI integration, and artifact handling.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, Mock

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.agent_executor import AgentExecutor, AgentResult, Artifact


class TestAgentExecutor:
    """Integration test suite for AgentExecutor."""

    def test_artifact_creation(self):
        """Test Artifact dataclass creation."""
        artifact = Artifact(
            type="file",
            path="test.py",
            content="print('test')"
        )

        assert artifact.type == "file"
        assert artifact.path == "test.py"
        assert artifact.content == "print('test')"

    def test_agent_result_creation(self):
        """Test AgentResult dataclass creation."""
        artifact = Artifact(type="file", path="test.py", content="test")
        result = AgentResult(
            agent_id="agent-01",
            status="success",
            artifacts=[artifact],
            insights=["Insight 1"],
            next_recommended_agent="agent-02",
            confidence=0.95
        )

        assert result.agent_id == "agent-01"
        assert result.status == "success"
        assert len(result.artifacts) == 1
        assert result.artifacts[0].path == "test.py"
        assert len(result.insights) == 1
        assert result.next_recommended_agent == "agent-02"
        assert result.confidence == 0.95

    def test_agent_result_partial_status(self):
        """Test AgentResult with partial status."""
        result = AgentResult(
            agent_id="agent-01",
            status="partial",
            artifacts=[],
            insights=[],
            next_recommended_agent=None,
            confidence=0.5
        )

        assert result.status == "partial"
        assert result.confidence == 0.5

    def test_agent_result_failed_status(self):
        """Test AgentResult with failed status."""
        result = AgentResult(
            agent_id="agent-01",
            status="failed",
            artifacts=[],
            insights=["Error: something went wrong"],
            next_recommended_agent=None,
            confidence=0.1
        )

        assert result.status == "failed"
        assert len(result.insights) == 1
        assert "Error" in result.insights[0]

    @pytest.mark.integration
    def test_agent_executor_abstract_class(self):
        """Test that AgentExecutor is abstract and cannot be instantiated directly."""
        workspace = Path("/tmp/test")

        with pytest.raises(TypeError):
            # Should not be able to instantiate abstract class
            executor = AgentExecutor(workspace)

    @pytest.mark.integration
    def test_concrete_executor_implementation(self, temp_workspace):
        """Test a concrete implementation of AgentExecutor."""

        class TestExecutor(AgentExecutor):
            def execute(self, query: str, context: dict, **kwargs) -> AgentResult:
                return AgentResult(
                    agent_id="test-agent",
                    status="success",
                    artifacts=[
                        Artifact(type="file", path="output.txt", content="test content")
                    ],
                    insights=["Task completed"],
                    next_recommended_agent=None,
                    confidence=0.9
                )

        executor = TestExecutor(temp_workspace)
        result = executor.execute("test query", {})

        assert result.agent_id == "test-agent"
        assert result.status == "success"
        assert len(result.artifacts) == 1
        assert result.artifacts[0].path == "output.txt"
        assert result.confidence == 0.9

    @pytest.mark.integration
    def test_executor_with_ai_provider(self, temp_workspace):
        """Test executor with AI provider."""

        class AIExecutor(AgentExecutor):
            def execute(self, query: str, context: dict, **kwargs) -> AgentResult:
                if not self.has_ai():
                    return AgentResult(
                        agent_id="ai-executor",
                        status="failed",
                        artifacts=[],
                        insights=["AI not available"],
                        next_recommended_agent=None,
                        confidence=0.0
                    )

                # Simulate AI-powered execution
                return AgentResult(
                    agent_id="ai-executor",
                    status="success",
                    artifacts=[],
                    insights=[f"Processed: {query}"],
                    next_recommended_agent=None,
                    confidence=0.85
                )

        # Test without AI
        executor = AIExecutor(temp_workspace)
        result = executor.execute("test", {})
        assert result.status == "failed"

        # Test with mock AI provider
        mock_ai = MagicMock()
        mock_ai.is_configured.return_value = True
        executor = AIExecutor(temp_workspace, ai_provider=mock_ai)
        result = executor.execute("test", {})
        assert result.status == "success"
        assert result.confidence == 0.85

    @pytest.mark.integration
    def test_executor_with_skill_loader(self, temp_workspace):
        """Test executor with skill loader."""

        class SkillExecutor(AgentExecutor):
            def execute(self, query: str, context: dict, **kwargs) -> AgentResult:
                # Check if skill loader is available
                if self.skill_loader:
                    return AgentResult(
                        agent_id="skill-executor",
                        status="success",
                        artifacts=[],
                        insights=["Skills loaded"],
                        next_recommended_agent=None,
                        confidence=0.9
                    )
                else:
                    return AgentResult(
                        agent_id="skill-executor",
                        status="failed",
                        artifacts=[],
                        insights=["No skill loader"],
                        next_recommended_agent=None,
                        confidence=0.0
                    )

        # Test without skill loader
        executor = SkillExecutor(temp_workspace)
        result = executor.execute("test", {})
        assert result.status == "failed"

        # Test with mock skill loader
        mock_skills = MagicMock()
        executor = SkillExecutor(temp_workspace, skill_loader=mock_skills)
        result = executor.execute("test", {})
        assert result.status == "success"

    @pytest.mark.integration
    def test_executor_multiple_artifacts(self, temp_workspace):
        """Test executor returning multiple artifacts."""

        class MultiArtifactExecutor(AgentExecutor):
            def execute(self, query: str, context: dict, **kwargs) -> AgentResult:
                artifacts = [
                    Artifact(type="file", path="file1.py", content="# File 1"),
                    Artifact(type="file", path="file2.py", content="# File 2"),
                    Artifact(type="plan", path="plan.md", content="# Plan"),
                    Artifact(type="report", path="report.txt", content="Report content"),
                ]

                return AgentResult(
                    agent_id="multi-artifact",
                    status="success",
                    artifacts=artifacts,
                    insights=["Generated multiple artifacts"],
                    next_recommended_agent="agent-02",
                    confidence=0.88
                )

        executor = MultiArtifactExecutor(temp_workspace)
        result = executor.execute("test", {})

        assert len(result.artifacts) == 4
        assert result.artifacts[0].type == "file"
        assert result.artifacts[2].type == "plan"
        assert result.artifacts[3].type == "report"
        assert result.next_recommended_agent == "agent-02"

    @pytest.mark.integration
    def test_executor_context_passing(self, temp_workspace):
        """Test that context is properly passed to executor."""

        class ContextExecutor(AgentExecutor):
            def execute(self, query: str, context: dict, **kwargs) -> AgentResult:
                # Verify context was passed
                context_keys = list(context.keys()) if context else []

                insights = [
                    f"Query: {query}",
                    f"Context keys: {', '.join(context_keys)}",
                    f"Extra kwargs: {list(kwargs.keys())}"
                ]

                return AgentResult(
                    agent_id="context-executor",
                    status="success",
                    artifacts=[],
                    insights=insights,
                    next_recommended_agent=None,
                    confidence=0.8
                )

        executor = ContextExecutor(temp_workspace)
        test_context = {"key1": "value1", "key2": "value2"}
        result = executor.execute("test query", test_context)

        assert "Query: test query" in result.insights
        assert "key1" in result.insights[1]
        assert "key2" in result.insights[1]

    @pytest.mark.integration
    def test_executor_error_handling(self, temp_workspace):
        """Test executor error handling."""

        class ErrorExecutor(AgentExecutor):
            def execute(self, query: str, context: dict, **kwargs) -> AgentResult:
                # Simulate an error
                if "error" in query.lower():
                    return AgentResult(
                        agent_id="error-executor",
                        status="failed",
                        artifacts=[],
                        insights=[f"Error processing query: {query}"],
                        next_recommended_agent=None,
                        confidence=0.0
                    )

                return AgentResult(
                    agent_id="error-executor",
                    status="success",
                    artifacts=[],
                    insights=["Processed successfully"],
                    next_recommended_agent=None,
                    confidence=0.9
                )

        executor = ErrorExecutor(temp_workspace)

        # Test normal case
        result = executor.execute("normal query", {})
        assert result.status == "success"

        # Test error case
        result = executor.execute("error query", {})
        assert result.status == "failed"
        assert "Error" in result.insights[0]

    @pytest.mark.integration
    def test_executor_workspace_access(self, temp_workspace):
        """Test that executor can access workspace."""

        class WorkspaceExecutor(AgentExecutor):
            def execute(self, query: str, context: dict, **kwargs) -> AgentResult:
                # Create a file in workspace
                test_file = self.workspace / "test_output.txt"
                test_file.write_text("Executor output")

                # Verify workspace path
                assert self.workspace.exists()
                assert self.workspace.is_absolute()

                return AgentResult(
                    agent_id="workspace-executor",
                    status="success",
                    artifacts=[
                        Artifact(type="file", path=str(test_file), content="Executor output")
                    ],
                    insights=[f"Workspace: {self.workspace}"],
                    next_recommended_agent=None,
                    confidence=0.95
                )

        executor = WorkspaceExecutor(temp_workspace)
        result = executor.execute("create file", {})

        assert result.status == "success"
        assert (temp_workspace / "test_output.txt").exists()
        assert result.artifacts[0].path.endswith("test_output.txt")

    @pytest.mark.integration
    def test_confidence_scoring(self, temp_workspace):
        """Test confidence scoring in different scenarios."""

        class ConfidenceExecutor(AgentExecutor):
            def execute(self, query: str, context: dict, **kwargs) -> AgentResult:
                # Simulate varying confidence based on query
                if "simple" in query:
                    confidence = 0.95
                    status = "success"
                elif "complex" in query:
                    confidence = 0.6
                    status = "partial"
                else:
                    confidence = 0.3
                    status = "failed"

                return AgentResult(
                    agent_id="confidence-executor",
                    status=status,
                    artifacts=[],
                    insights=[f"Confidence: {confidence}"],
                    next_recommended_agent=None,
                    confidence=confidence
                )

        executor = ConfidenceExecutor(temp_workspace)

        # Test high confidence
        result = executor.execute("simple task", {})
        assert result.confidence == 0.95
        assert result.status == "success"

        # Test medium confidence
        result = executor.execute("complex task", {})
        assert result.confidence == 0.6
        assert result.status == "partial"

        # Test low confidence
        result = executor.execute("unknown task", {})
        assert result.confidence == 0.3
        assert result.status == "failed"

    @pytest.mark.integration
    def test_next_agent_recommendation(self, temp_workspace):
        """Test next agent recommendation logic."""

        class RecommendationExecutor(AgentExecutor):
            def execute(self, query: str, context: dict, **kwargs) -> AgentResult:
                # Recommend different agents based on query
                if "plan" in query:
                    next_agent = "agent-02"  # Builder
                elif "review" in query:
                    next_agent = "agent-04"  # Forensic
                elif "test" in query:
                    next_agent = "agent-09"  # QA
                else:
                    next_agent = None

                return AgentResult(
                    agent_id="recommendation-executor",
                    status="success",
                    artifacts=[],
                    insights=[f"Recommended next agent: {next_agent}"],
                    next_recommended_agent=next_agent,
                    confidence=0.8
                )

        executor = RecommendationExecutor(temp_workspace)

        # Test plan recommendation
        result = executor.execute("need plan", {})
        assert result.next_recommended_agent == "agent-02"

        # Test review recommendation
        result = executor.execute("need review", {})
        assert result.next_recommended_agent == "agent-04"

        # Test no recommendation
        result = executor.execute("generic task", {})
        assert result.next_recommended_agent is None

    @pytest.mark.integration
    def test_executor_initialization_variants(self, temp_workspace):
        """Test different ways of initializing executor."""

        # Test with only workspace
        executor1 = TestExecutor(temp_workspace)
        assert executor1.workspace == temp_workspace
        assert executor1.ai_provider is None
        assert executor1.skill_loader is None

        # Test with AI provider
        mock_ai = MagicMock()
        executor2 = TestExecutor(temp_workspace, ai_provider=mock_ai)
        assert executor2.ai_provider == mock_ai

        # Test with skill loader
        mock_skills = MagicMock()
        executor3 = TestExecutor(temp_workspace, skill_loader=mock_skills)
        assert executor3.skill_loader == mock_skills

        # Test with both
        executor4 = TestExecutor(temp_workspace, ai_provider=mock_ai, skill_loader=mock_skills)
        assert executor4.ai_provider == mock_ai
        assert executor4.skill_loader == mock_skills


# Helper class for testing
class TestExecutor(AgentExecutor):
    """Concrete implementation for testing."""
    def execute(self, query: str, context: dict, **kwargs) -> AgentResult:
        return AgentResult(
            agent_id="test-executor",
            status="success",
            artifacts=[],
            insights=["Test execution"],
            next_recommended_agent=None,
            confidence=0.9
        )
