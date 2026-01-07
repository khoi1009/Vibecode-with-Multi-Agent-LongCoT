"""
Artifact Registry
Track and manage artifacts created during pipeline execution
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json
import shutil
import hashlib
from threading import Lock


@dataclass
class ArtifactEntry:
    path: str
    agent_id: str
    artifact_type: str  # "file", "plan", "report", "test"
    created_at: datetime
    checksum: str
    size_bytes: int


class ArtifactRegistry:
    """Track and manage artifacts created during pipeline execution"""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.registry_dir = workspace / ".vibecode" / "artifacts"
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self._entries: Dict[str, ArtifactEntry] = {}
        self._run_id: Optional[str] = None
        self._lock = Lock()  # Thread safety for register operations

    def start_run(self, run_id: str) -> None:
        """Start new pipeline run"""
        self._run_id = run_id
        self._entries = {}
        run_dir = self.registry_dir / run_id
        run_dir.mkdir(exist_ok=True)

    def register(self, path: str, agent_id: str, artifact_type: str) -> None:
        """Register artifact created by agent (thread-safe)"""
        with self._lock:
            full_path = self.workspace / path
            if not full_path.exists():
                return

            checksum = hashlib.sha256(full_path.read_bytes()).hexdigest()

            entry = ArtifactEntry(
                path=path,
                agent_id=agent_id,
                artifact_type=artifact_type,
                created_at=datetime.now(),
                checksum=checksum,
                size_bytes=full_path.stat().st_size
            )
            self._entries[path] = entry

            # Copy to run archive
            if self._run_id:
                archive_path = self.registry_dir / self._run_id / path
                archive_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(full_path, archive_path)

    def get_by_agent(self, agent_id: str) -> List[ArtifactEntry]:
        """Get artifacts created by specific agent"""
        return [e for e in self._entries.values() if e.agent_id == agent_id]

    def get_by_type(self, artifact_type: str) -> List[ArtifactEntry]:
        """Get artifacts of specific type"""
        return [e for e in self._entries.values() if e.artifact_type == artifact_type]

    def rollback_run(self, run_id: str) -> bool:
        """Rollback artifacts from a run (delete created files)"""
        run_dir = self.registry_dir / run_id
        if not run_dir.exists():
            return False

        manifest = run_dir / "manifest.json"
        if manifest.exists():
            entries = json.loads(manifest.read_text())
            for entry in entries:
                target = self.workspace / entry["path"]
                if target.exists():
                    target.unlink()
            return True
        return False

    def save_manifest(self) -> None:
        """Save registry manifest"""
        if not self._run_id:
            return
        manifest_path = self.registry_dir / self._run_id / "manifest.json"
        manifest_data = [
            {
                "path": e.path,
                "agent_id": e.agent_id,
                "type": e.artifact_type,
                "checksum": e.checksum
            }
            for e in self._entries.values()
        ]
        manifest_path.write_text(json.dumps(manifest_data, indent=2))

    def get_all_artifacts(self) -> List[ArtifactEntry]:
        """Get all registered artifacts"""
        return list(self._entries.values())

    def get_run_id(self) -> Optional[str]:
        """Get current run ID"""
        return self._run_id
