"""
Unit tests for memory_manager module.

Tests bounded history, context compaction, and memory profiling.
"""

import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.memory_manager import BoundedHistory, ContextCompactor, MemoryProfiler


class TestBoundedHistory:
    """Test suite for BoundedHistory class."""

    @pytest.mark.unit
    def test_append_and_get_recent(self):
        """Test basic append and get_recent."""
        history = BoundedHistory(max_entries=10, max_chars=1000)
        history.append({"role": "user", "content": "test1"})
        history.append({"role": "assistant", "content": "test2"})

        recent = history.get_recent(2)
        assert len(recent) == 2

    @pytest.mark.unit
    def test_max_entries_enforced(self):
        """Test that max entries are enforced."""
        history = BoundedHistory(max_entries=3, max_chars=10000)
        for i in range(5):
            history.append({"entry": i})

        assert len(history) == 3

    @pytest.mark.unit
    def test_compaction(self):
        """Test history compaction."""
        history = BoundedHistory(max_entries=10, max_chars=1000)
        for i in range(8):
            history.append({"entry": i, "content": "x" * 100})  # Large entries

        summary = history.compact()
        assert "earlier steps summarized" in summary

    @pytest.mark.unit
    def test_clear(self):
        """Test history clearing."""
        history = BoundedHistory(max_entries=10, max_chars=1000)
        history.append({"entry": "test"})
        history.clear()

        assert len(history) == 0
        assert history.total_chars == 0

    @pytest.mark.unit
    def test_is_full(self):
        """Test is_full property."""
        history = BoundedHistory(max_entries=2, max_chars=10000)
        history.append({"entry": 1})
        assert not history.is_full
        history.append({"entry": 2})
        assert history.is_full

    @pytest.mark.unit
    def test_iteration(self):
        """Test history iteration."""
        history = BoundedHistory(max_entries=5, max_chars=1000)
        history.append({"a": 1})
        history.append({"b": 2})

        items = list(history)
        assert len(items) == 2
        assert items[0]["a"] == 1


class TestContextCompactor:
    """Test suite for ContextCompactor class."""

    @pytest.mark.unit
    def test_compact_under_limit(self):
        """Test that text under limit is not changed."""
        compactor = ContextCompactor(max_tokens=1000, reserve_tokens=100)
        text = "Short text"
        result = compactor.compact(text)
        assert result == text

    @pytest.mark.unit
    def test_compact_over_limit(self):
        """Test that text over limit is truncated."""
        compactor = ContextCompactor(max_tokens=10, reserve_tokens=2)
        # Create text longer than available tokens (8 chars max)
        text = "This is a very long text that should be truncated"
        result = compactor.compact(text)
        assert len(result) <= 32  # 8 tokens * 4 chars per token

    @pytest.mark.unit
    def test_priority_sections_preserved(self):
        """Test that priority sections are preserved."""
        compactor = ContextCompactor(max_tokens=20, reserve_tokens=5)
        priority = "## Priority Section"
        remaining = "A" * 100
        result = compactor.compact(priority + remaining, [priority])
        assert priority in result

    @pytest.mark.unit
    def test_estimate_tokens(self):
        """Test token estimation."""
        compactor = ContextCompactor()
        text = "1234"  # 4 chars = 1 token
        assert compactor.estimate_tokens(text) == 1


class TestMemoryProfiler:
    """Test suite for MemoryProfiler class."""

    @pytest.mark.unit
    def test_snapshot(self):
        """Test memory snapshot."""
        profiler = MemoryProfiler()
        snapshot = profiler.snapshot("test")

        # Snapshot should have current and peak MB
        assert snapshot is not None
        assert "current_mb" in snapshot
        assert "peak_mb" in snapshot

    @pytest.mark.unit
    def test_report(self):
        """Test memory report generation."""
        profiler = MemoryProfiler()
        profiler.snapshot("test1")
        profiler.snapshot("test2")

        report = profiler.report()
        assert "test1" in report
        assert "test2" in report

    @pytest.mark.unit
    def test_clear(self):
        """Test clearing snapshots."""
        profiler = MemoryProfiler()
        profiler.snapshot("test")
        profiler.clear()

        report = profiler.report()
        assert "No snapshots" in report

    @pytest.mark.unit
    def test_start_stop(self):
        """Test profiler start/stop."""
        profiler = MemoryProfiler()
        profiler.start()
        profiler.stop()
        assert not profiler.is_tracing
