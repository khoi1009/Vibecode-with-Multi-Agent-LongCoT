"""
Memory Manager Module for VibeCode

Provides bounded history, context compaction, and memory profiling.
"""

import sys
from typing import List, Dict, Any, Optional
from collections import deque


class BoundedHistory:
    """Bounded conversation history with automatic compaction."""

    def __init__(self, max_entries: int = 50, max_chars: int = 50000):
        self._history: deque = deque(maxlen=max_entries)
        self.max_chars = max_chars
        self._total_chars = 0

    def append(self, entry: Dict[str, Any]) -> None:
        """Add entry, automatically compacting if needed."""
        entry_size = len(str(entry))

        # Check if we need to compact before adding
        while self._total_chars + entry_size > self.max_chars and self._history:
            removed = self._history.popleft()
            self._total_chars -= len(str(removed))

        self._history.append(entry)
        self._total_chars += entry_size

    def get_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get n most recent entries."""
        return list(self._history)[-n:]

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all entries."""
        return list(self._history)

    def compact(self) -> str:
        """Compact history into summary and return the summary."""
        if len(self._history) <= 5:
            return ""

        # Keep first 2 and last 3, summarize middle
        first_entries = list(self._history)[:2]
        last_entries = list(self._history)[-3:]
        middle_count = len(self._history) - 5

        summary = f"[{middle_count} earlier steps summarized]"

        # Reset history with compacted version
        self._history.clear()
        for entry in first_entries:
            self._history.append(entry)
        self._history.append({"role": "system", "content": summary})
        for entry in last_entries:
            self._history.append(entry)

        self._total_chars = sum(len(str(e)) for e in self._history)
        return summary

    def clear(self) -> None:
        """Clear all history."""
        self._history.clear()
        self._total_chars = 0

    def __iter__(self):
        return iter(self._history)

    def __len__(self):
        return len(self._history)

    @property
    def total_chars(self) -> int:
        """Return total character count."""
        return self._total_chars

    @property
    def is_full(self) -> bool:
        """Check if history is at max capacity."""
        return len(self._history) >= self._history.maxlen


class ContextCompactor:
    """Compact context to stay within token limits."""

    def __init__(self, max_tokens: int = 6000, reserve_tokens: int = 1000):
        self.max_tokens = max_tokens
        self.reserve_tokens = reserve_tokens
        self.available_tokens = max_tokens - reserve_tokens

    def compact(self, context: str, priority_sections: List[str] = None) -> str:
        """
        Compact context to fit within token limit.
        Priority sections are kept intact if possible.
        """
        if priority_sections is None:
            priority_sections = []

        # Estimate token count (rough: 4 chars per token)
        current_tokens = len(context) // 4

        if current_tokens <= self.available_tokens:
            return context

        # Try to keep priority sections
        priority_text = ""
        remaining_text = context

        for section in priority_sections:
            if section in remaining_text:
                idx = remaining_text.find(section)
                if idx >= 0:
                    priority_text += remaining_text[idx:idx + len(section)]
                    remaining_text = remaining_text[:idx]

        # If still over limit, truncate remaining
        priority_tokens = len(priority_text) // 4
        remaining_available = self.available_tokens - priority_tokens

        if remaining_available <= 0:
            # Truncate priority sections proportionally
            return priority_text[:self.available_tokens * 4]

        # Take as much of remaining as fits
        remaining_tokens = len(remaining_text) // 4
        if remaining_tokens > remaining_available:
            keep_chars = remaining_available * 4
            remaining_text = remaining_text[:keep_chars]

        return priority_text + remaining_text

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        return len(text) // 4


class MemoryProfiler:
    """Simple memory profiler for debugging memory usage."""

    def __init__(self):
        self._snapshots: List[Dict] = []
        self._tracing = False

    def start(self) -> None:
        """Start memory tracing."""
        try:
            import tracemalloc
            tracemalloc.start()
            self._tracing = True
        except ImportError:
            pass

    def stop(self) -> None:
        """Stop memory tracing."""
        try:
            import tracemalloc
            if self._tracing:
                tracemalloc.stop()
                self._tracing = False
        except ImportError:
            pass

    def snapshot(self, label: str) -> Optional[Dict]:
        """Take memory snapshot. Returns None if tracing not available."""
        try:
            import tracemalloc

            if not self._tracing:
                self.start()

            current, peak = tracemalloc.get_traced_memory()
            snapshot = {
                "label": label,
                "current_mb": current / 1e6,
                "peak_mb": peak / 1e6,
                "current_bytes": current,
                "peak_bytes": peak
            }
            self._snapshots.append(snapshot)
            return snapshot
        except ImportError:
            return None

    def report(self) -> str:
        """Generate memory report."""
        if not self._snapshots:
            return "No snapshots recorded"

        lines = ["Memory Profile:"]
        for snap in self._snapshots:
            lines.append(
                f"  {snap['label']}: "
                f"{snap.get('current_mb', 0):.2f}MB "
                f"(peak: {snap.get('peak_mb', 0):.2f}MB)"
            )
        return "\n".join(lines)

    def get_top_allocations(self, n: int = 10) -> List[str]:
        """Get top memory allocations."""
        try:
            import tracemalloc

            if not self._tracing:
                return ["Tracing not started"]

            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')[:n]

            return [str(stat) for stat in top_stats]
        except ImportError:
            return ["tracemalloc not available"]

    def clear(self) -> None:
        """Clear all snapshots."""
        self._snapshots.clear()

    @property
    def is_tracing(self) -> bool:
        """Check if tracing is active."""
        return self._tracing
