"""
Unit tests for AutonomyConfig module.

Tests autonomous decision-making thresholds and audit logging.
"""

import pytest
from pathlib import Path
import json
import tempfile
import shutil

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.autonomy_config import AutonomyConfig


class TestAutonomyConfig:
    """Test suite for AutonomyConfig class."""

    @pytest.mark.unit
    def test_init_default(self):
        """Test initialization with default values."""
        config = AutonomyConfig()
        assert config.confidence_threshold == 0.8
        assert config.auto_approve is False
        assert config.audit_log_path == ".vibecode/autonomy_audit.log"

    @pytest.mark.unit
    def test_init_custom(self):
        """Test initialization with custom values."""
        config = AutonomyConfig(
            confidence_threshold=0.9,
            auto_approve=True,
            audit_log_path="/tmp/test.log"
        )
        assert config.confidence_threshold == 0.9
        assert config.auto_approve is True
        assert config.audit_log_path == "/tmp/test.log"

    @pytest.mark.unit
    def test_should_auto_approve_high_confidence(self):
        """Test auto-approval with high confidence."""
        config = AutonomyConfig(confidence_threshold=0.8)

        should_proceed, reason = config.should_auto_approve(
            confidence=0.9,
            is_destructive=True
        )

        assert should_proceed is True
        assert "High confidence" in reason
        assert "90.0%" in reason or "90%" in reason

    @pytest.mark.unit
    def test_should_auto_approve_exact_threshold(self):
        """Test auto-approval at exact threshold."""
        config = AutonomyConfig(confidence_threshold=0.8)

        should_proceed, reason = config.should_auto_approve(
            confidence=0.8,
            is_destructive=False
        )

        assert should_proceed is True

    @pytest.mark.unit
    def test_should_auto_approve_below_threshold(self):
        """Test rejection below threshold."""
        config = AutonomyConfig(confidence_threshold=0.8)

        should_proceed, reason = config.should_auto_approve(
            confidence=0.7,
            is_destructive=False
        )

        assert should_proceed is False
        assert "below threshold" in reason

    @pytest.mark.unit
    def test_should_auto_approve_low_confidence_destructive(self):
        """Test rejection of low confidence + destructive operation."""
        config = AutonomyConfig(confidence_threshold=0.8)

        should_proceed, reason = config.should_auto_approve(
            confidence=0.4,
            is_destructive=True
        )

        assert should_proceed is False
        assert "Low confidence" in reason
        assert "destructive" in reason

    @pytest.mark.unit
    def test_should_auto_approve_low_confidence_non_destructive(self):
        """Test medium confidence with auto-approve enabled."""
        config = AutonomyConfig(confidence_threshold=0.8, auto_approve=True)

        should_proceed, reason = config.should_auto_approve(
            confidence=0.5,
            is_destructive=False
        )

        # Should approve because auto_approve flag is set
        assert should_proceed is True
        assert "Auto-approve flag enabled" in reason

    @pytest.mark.unit
    def test_should_auto_approve_low_confidence_non_destructive_no_flag(self):
        """Test medium confidence without auto-approve flag."""
        config = AutonomyConfig(confidence_threshold=0.8, auto_approve=False)

        should_proceed, reason = config.should_auto_approve(
            confidence=0.5,
            is_destructive=False
        )

        # Should reject because below threshold and no auto-approve flag
        assert should_proceed is False

    @pytest.mark.unit
    def test_confidence_boundary_values(self):
        """Test boundary values for confidence."""
        config = AutonomyConfig(confidence_threshold=0.8)

        # Test exact boundaries
        assert config.should_auto_approve(1.0, False)[0] is True
        assert config.should_auto_approve(0.0, False)[0] is False

    @pytest.mark.unit
    def test_destructive_flag_true(self):
        """Test behavior with destructive flag set to True."""
        config = AutonomyConfig()

        # High confidence + destructive = approve
        assert config.should_auto_approve(0.9, True)[0] is True

        # Low confidence + destructive = reject
        assert config.should_auto_approve(0.4, True)[0] is False

    @pytest.mark.unit
    def test_destructive_flag_false(self):
        """Test behavior with destructive flag set to False."""
        config = AutonomyConfig()

        # High confidence + non-destructive = approve
        assert config.should_auto_approve(0.9, False)[0] is True

        # Medium confidence + non-destructive + auto-approve = approve
        config.auto_approve = True
        assert config.should_auto_approve(0.5, False)[0] is True

    @pytest.mark.unit
    def test_log_decision(self, temp_workspace):
        """Test logging decisions to audit trail."""
        log_path = temp_workspace / "audit.log"
        config = AutonomyConfig()

        config.log_decision(
            log_path=log_path,
            task_type="code_generation",
            confidence=0.85,
            approved=True,
            reason="High confidence"
        )

        # Verify log file was created
        assert log_path.exists()

        # Verify log content
        with open(log_path, 'r') as f:
            entry = json.loads(f.readline())
            assert entry["timestamp"] is not None
            assert entry["task_type"] == "code_generation"
            assert entry["confidence"] == 0.85
            assert entry["approved"] is True
            assert entry["reason"] == "High confidence"

    @pytest.mark.unit
    def test_log_decision_multiple_entries(self, temp_workspace):
        """Test logging multiple decisions."""
        log_path = temp_workspace / "audit.log"
        config = AutonomyConfig()

        # Log multiple entries
        for i in range(5):
            config.log_decision(
                log_path=log_path,
                task_type=f"task_{i}",
                confidence=0.5 + i * 0.1,
                approved=i % 2 == 0,
                reason=f"Reason {i}"
            )

        # Verify all entries were logged
        with open(log_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 5

            # Verify each entry
            for i, line in enumerate(lines):
                entry = json.loads(line)
                assert entry["task_type"] == f"task_{i}"
                assert entry["confidence"] == 0.5 + i * 0.1

    @pytest.mark.unit
    def test_log_decision_creates_parent_directory(self, temp_workspace):
        """Test that log decision creates parent directories if needed."""
        log_path = temp_workspace / ".vibecode" / "audit.log"
        config = AutonomyConfig()

        # Parent directory doesn't exist yet
        assert not log_path.parent.exists()

        config.log_decision(
            log_path=log_path,
            task_type="test",
            confidence=0.9,
            approved=True,
            reason="Test"
        )

        # Verify parent directory was created
        assert log_path.parent.exists()
        assert log_path.exists()

    @pytest.mark.unit
    def test_log_decision_json_format(self, temp_workspace):
        """Test that logged entries are valid JSON."""
        log_path = temp_workspace / "audit.log"
        config = AutonomyConfig()

        config.log_decision(
            log_path=log_path,
            task_type="test_task",
            confidence=0.75,
            approved=False,
            reason="Test reason"
        )

        # Verify valid JSON
        with open(log_path, 'r') as f:
            entry = json.loads(f.readline())
            assert isinstance(entry, dict)

    @pytest.mark.unit
    def test_confidence_threshold_edge_cases(self):
        """Test edge cases for confidence threshold."""
        # Very high threshold
        config = AutonomyConfig(confidence_threshold=0.99)
        assert config.should_auto_approve(0.999, False)[0] is True
        assert config.should_auto_approve(0.98, False)[0] is False

        # Very low threshold
        config = AutonomyConfig(confidence_threshold=0.1)
        assert config.should_auto_approve(0.2, False)[0] is True

        # Zero threshold
        config = AutonomyConfig(confidence_threshold=0.0)
        assert config.should_auto_approve(0.0, False)[0] is True

    @pytest.mark.unit
    def test_auto_approve_override(self):
        """Test that auto_approve flag overrides threshold for non-destructive."""
        config = AutonomyConfig(
            confidence_threshold=0.9,
            auto_approve=True
        )

        # Low confidence + non-destructive + auto_approve = approve
        should_proceed, reason = config.should_auto_approve(
            confidence=0.3,
            is_destructive=False
        )

        assert should_proceed is True
        assert "Auto-approve flag enabled" in reason

    @pytest.mark.unit
    def test_destructive_operation_detection(self):
        """Test detection of destructive vs non-destructive operations."""
        config = AutonomyConfig(confidence_threshold=0.8)

        # Same confidence, different destructive flags
        should_proceed_high, _ = config.should_auto_approve(0.9, True)
        should_proceed_non_destructive, _ = config.should_auto_approve(0.9, False)

        # Both should approve for high confidence
        assert should_proceed_high is True
        assert should_proceed_non_destructive is True

        # Low confidence + destructive should reject
        should_proceed_destructive, _ = config.should_auto_approve(0.4, True)
        should_proceed_non_destructive, _ = config.should_auto_approve(0.4, False)

        assert should_proceed_destructive is False
        # Low confidence + non-destructive depends on auto_approve flag
        config.auto_approve = True
        should_proceed_non_destructive, _ = config.should_auto_approve(0.4, False)
        assert should_proceed_non_destructive is True

    @pytest.mark.unit
    def test_reason_message_format(self):
        """Test that reason messages are properly formatted."""
        config = AutonomyConfig(confidence_threshold=0.8)

        # Test high confidence reason
        _, reason = config.should_auto_approve(0.95, False)
        assert "High confidence" in reason
        assert "%" in reason  # Should include percentage

        # Test below threshold reason
        _, reason = config.should_auto_approve(0.6, False)
        assert "below threshold" in reason

        # Test destructive operation reason
        _, reason = config.should_auto_approve(0.3, True)
        assert "Low confidence" in reason
        assert "destructive" in reason

    @pytest.mark.unit
    def test_multiple_config_instances(self):
        """Test that multiple config instances don't interfere."""
        config1 = AutonomyConfig(confidence_threshold=0.7)
        config2 = AutonomyConfig(confidence_threshold=0.9)

        # Verify they're independent
        assert config1.confidence_threshold != config2.confidence_threshold

        # Test with same input, different results
        should_proceed1, _ = config1.should_auto_approve(0.8, False)
        should_proceed2, _ = config2.should_auto_approve(0.8, False)

        assert should_proceed1 is True  # Above 0.7
        assert should_proceed2 is False  # Below 0.9
