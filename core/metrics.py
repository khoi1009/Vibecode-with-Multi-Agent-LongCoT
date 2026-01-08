"""
Metrics Module for VibeCode

Collects and persists performance metrics for pipelines and operations.
"""

import time
import json
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional


@dataclass
class PipelineMetrics:
    """Metrics for a single pipeline execution."""
    pipeline_id: str
    start_time: float
    end_time: Optional[float] = None
    agents_executed: int = 0
    total_tokens: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    files_read: int = 0
    files_written: int = 0
    errors: int = 0

    @property
    def duration_seconds(self) -> float:
        """Get pipeline duration in seconds."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    @property
    def cache_hit_rate(self) -> float:
        """Get cache hit rate as 0-1 fraction."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


class MetricsCollector:
    """Collect and persist performance metrics."""

    def __init__(self, workspace: Path):
        self.workspace = Path(workspace)
        self.metrics_file = self.workspace / ".vibecode" / "metrics.jsonl"
        self._current: Optional[PipelineMetrics] = None

    def start_pipeline(self, pipeline_id: str) -> PipelineMetrics:
        """Start tracking a new pipeline."""
        self._current = PipelineMetrics(
            pipeline_id=pipeline_id,
            start_time=time.time()
        )
        return self._current

    def end_pipeline(self) -> Optional[PipelineMetrics]:
        """End tracking current pipeline and persist."""
        if not self._current:
            return None

        self._current.end_time = time.time()
        self._persist()
        finished = self._current
        self._current = None
        return finished

    def record_tokens(self, count: int) -> None:
        """Record token usage."""
        if self._current:
            self._current.total_tokens += count

    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        if self._current:
            self._current.cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        if self._current:
            self._current.cache_misses += 1

    def record_file_read(self) -> None:
        """Record a file read operation."""
        if self._current:
            self._current.files_read += 1

    def record_file_write(self) -> None:
        """Record a file write operation."""
        if self._current:
            self._current.files_written += 1

    def record_agent_executed(self) -> None:
        """Record an agent execution."""
        if self._current:
            self._current.agents_executed += 1

    def record_error(self) -> None:
        """Record an error."""
        if self._current:
            self._current.errors += 1

    def _persist(self) -> None:
        """Persist current metrics to file."""
        if not self._current:
            return

        self.metrics_file.parent.mkdir(exist_ok=True)
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(self._current.to_dict()) + "\n")

    def get_summary(self, last_n: int = 10) -> Dict:
        """Get summary of recent pipelines."""
        if not self.metrics_file.exists():
            return {"count": 0, "message": "No metrics recorded"}

        try:
            lines = self.metrics_file.read_text().strip().split("\n")[-last_n:]
            metrics = [json.loads(line) for line in lines if line and line.strip()]
        except (IOError, json.JSONDecodeError):
            return {"count": 0, "message": "Error reading metrics"}

        if not metrics:
            return {"count": 0, "message": "No valid metrics"}

        # Calculate averages
        durations = [m.get("end_time", 0) - m["start_time"] for m in metrics if "end_time" in m]
        total_tokens = [m.get("total_tokens", 0) for m in metrics]
        cache_hits = [m.get("cache_hits", 0) for m in metrics]
        cache_misses = [m.get("cache_misses", 0) for m in metrics]

        total_cache = [h + m for h, m in zip(cache_hits, cache_misses)]
        avg_cache_hit = sum(cache_hits) / sum(total_cache) if sum(total_cache) > 0 else 0

        return {
            "count": len(metrics),
            "avg_duration_sec": sum(durations) / len(durations) if durations else 0,
            "avg_tokens": sum(total_tokens) / len(total_tokens),
            "avg_cache_hit_rate": avg_cache_hit,
            "total_errors": sum(m.get("errors", 0) for m in metrics)
        }

    def get_recent_pipelines(self, n: int = 5) -> List[Dict]:
        """Get recent pipeline metrics."""
        if not self.metrics_file.exists():
            return []

        try:
            lines = self.metrics_file.read_text().strip().split("\n")[-n:]
            return [json.loads(line) for line in lines if line and line.strip()]
        except (IOError, json.JSONDecodeError):
            return []

    def clear(self) -> None:
        """Clear all metrics (delete file)."""
        if self.metrics_file.exists():
            self.metrics_file.unlink()
        self._current = None


# Singleton collector factory
_collectors: Dict[str, MetricsCollector] = {}


def get_metrics_collector(workspace: Path) -> MetricsCollector:
    """Get or create metrics collector for workspace."""
    workspace_str = str(workspace)
    if workspace_str not in _collectors:
        _collectors[workspace_str] = MetricsCollector(workspace)
    return _collectors[workspace_str]
