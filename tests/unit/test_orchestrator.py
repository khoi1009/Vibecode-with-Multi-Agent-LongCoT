"""
Unit tests for Orchestrator module.

Tests the core orchestration logic, agent delegation, and workflow management.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.orchestrator import Orchestrator
from core.autonomy_config import AutonomyConfig


class TestOrchestrator:
    """Test suite for Orchestrator class."""

    @pytest.mark.unit
    def test_init(self, temp_workspace):
        """Test orchestrator initialization."""
        orch = Orchestrator(temp_workspace)
        assert orch.workspace is not None
        assert orch.vibecode_dir.exists()

    @pytest.mark.unit
    def test_init_with_autonomy_config(self, temp_workspace):
        """Test orchestrator with custom autonomy config."""
        config = AutonomyConfig(confidence_threshold=0.9, auto_approve=True)
        orch = Orchestrator(temp_workspace, autonomy_config=config)
        assert orch.autonomy_config.confidence_threshold == 0.9
        assert orch.autonomy_config.auto_approve is True

    @pytest.mark.unit
    def test_init_default_values(self, temp_workspace):
        """Test orchestrator with default values."""
        orch = Orchestrator(temp_workspace)
        assert orch.autonomy_config.confidence_threshold == 0.8
        assert orch.autonomy_config.auto_approve is False

    @pytest.mark.unit
    def test_validate_workspace(self, temp_workspace):
        """Test workspace validation."""
        orch = Orchestrator(temp_workspace)
        assert orch.workspace == temp_workspace

    @pytest.mark.unit
    def test_workspace_path_handling(self, temp_workspace):
        """Test that workspace paths are handled correctly."""
        orch = Orchestrator(temp_workspace)
        assert orch.workspace.is_absolute() or str(temp_workspace).startswith('.')

    @pytest.mark.unit
    def test_vibecode_directory_created(self, temp_workspace):
        """Test that .vibecode directory is created."""
        assert not (temp_workspace / ".vibecode").exists()
        orch = Orchestrator(temp_workspace)
        assert (temp_workspace / ".vibecode").exists()

    @pytest.mark.unit
    def test_state_file_attribute_set(self, temp_workspace):
        """Test that state file attribute is set correctly."""
        orch = Orchestrator(temp_workspace)
        assert ".vibecode" in str(orch.state_file)
        assert "state.json" in str(orch.state_file)

    @pytest.mark.unit
    def test_state_initial_idle(self, temp_workspace):
        """Test initial state is IDLE."""
        orch = Orchestrator(temp_workspace)
        assert orch.state.get("current_phase") == "IDLE"

    @pytest.mark.unit
    def test_existing_project_detection(self, workspace_with_project):
        """Test detection of existing project."""
        orch = Orchestrator(workspace_with_project)
        assert orch.is_existing_project is True

    @pytest.mark.unit
    def test_message_queue_initialized(self, temp_workspace):
        """Test message queue is initialized."""
        orch = Orchestrator(temp_workspace)
        assert orch.message_queue is not None

    @pytest.mark.unit
    def test_artifact_registry_initialized(self, temp_workspace):
        """Test artifact registry is initialized."""
        orch = Orchestrator(temp_workspace)
        assert orch.artifact_registry is not None

    @pytest.mark.unit
    def test_intent_parser_initialized(self, temp_workspace):
        """Test intent parser is initialized."""
        orch = Orchestrator(temp_workspace)
        assert orch.intent_parser is not None

    @pytest.mark.unit
    def test_longcot_scanner_initialized(self, temp_workspace):
        """Test LongCoT scanner is initialized."""
        orch = Orchestrator(temp_workspace)
        assert orch.longcot_scanner is not None

    @pytest.mark.unit
    def test_agents_loaded(self, temp_workspace):
        """Test agents are loaded."""
        orch = Orchestrator(temp_workspace)
        assert len(orch.agents) > 0

    @pytest.mark.unit
    def test_skill_loader_initialized(self, temp_workspace):
        """Test skill loader is initialized."""
        orch = Orchestrator(temp_workspace)
        assert orch.skill_loader is not None

    @pytest.mark.unit
    def test_should_auto_approve_high_confidence(self, temp_workspace):
        """Test auto-approve with high confidence."""
        orch = Orchestrator(temp_workspace)
        should_proceed, reason = orch.autonomy_config.should_auto_approve(0.9, False)
        assert should_proceed is True

    @pytest.mark.unit
    def test_should_auto_approve_low_confidence_rejects(self, temp_workspace):
        """Test auto-reject with low confidence."""
        orch = Orchestrator(temp_workspace)
        should_proceed, reason = orch.autonomy_config.should_auto_approve(0.3, False)
        assert should_proceed is False

    @pytest.mark.unit
    def test_should_auto_approve_destructive_low_rejects(self, temp_workspace):
        """Test auto-reject with low confidence + destructive."""
        orch = Orchestrator(temp_workspace)
        should_proceed, reason = orch.autonomy_config.should_auto_approve(0.3, True)
        assert should_proceed is False
        assert "destructive" in reason.lower()

    @pytest.mark.unit
    def test_set_max_iterations(self, temp_workspace):
        """Test setting max iterations."""
        orch = Orchestrator(temp_workspace)
        new_limit = 50
        orch.max_iterations = new_limit
        assert orch.max_iterations == new_limit

    @pytest.mark.unit
    def test_autonomy_audit_log_path(self, temp_workspace):
        """Test audit log path is set correctly."""
        orch = Orchestrator(temp_workspace)
        assert "autonomy_audit.log" in str(orch.autonomy_audit_log)
