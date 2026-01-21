"""
Integrator Executor
Agent 05: Safe File System Integration and Change Application
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from core.agent_executor import AgentExecutor, AgentResult, Artifact
from datetime import datetime
import json
import shutil


class IntegratorExecutor(AgentExecutor):
    """Agent 05: Integrator - Safe file system integration"""

    def __init__(self, workspace: Path, ai_provider=None, skill_loader=None):
        super().__init__(workspace, ai_provider, skill_loader)
        self.backup_dir = workspace / ".vibecode" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Safety limits
        self.max_file_size = 1024 * 1024  # 1MB
        self.forbidden_paths = [
            'C:\\Windows', 'C:\\Program Files', '/etc', '/usr', '/bin',
            '.env', '.env.local', '.env.production', 'secrets'
        ]

    def execute(self, query: str, context: Dict, **kwargs) -> AgentResult:
        """Execute file integration safely"""
        # Get approved changes from review
        changes = context.get("pending_changes", [])
        artifacts = context.get("artifacts", [])
        review_status = context.get("review_status", "unknown")

        # Validate review approval
        if review_status == "failed":
            return AgentResult(
                agent_id="05",
                status="failed",
                artifacts=[],
                insights=["Cannot integrate: Code review failed. Fix issues first."],
                next_recommended_agent="07",
                confidence=0.0
            )

        # Process artifacts as changes if no explicit changes
        if not changes and artifacts:
            changes = self._artifacts_to_changes(artifacts)

        if not changes:
            # No changes to apply, just validate workspace
            return self._validate_workspace(context)

        # Apply changes safely
        return self._apply_changes_safely(changes, context)

    def _artifacts_to_changes(self, artifacts: List) -> List[Dict]:
        """Convert artifacts to change operations"""
        changes = []
        for artifact in artifacts:
            if hasattr(artifact, 'path') and hasattr(artifact, 'content'):
                changes.append({
                    'path': artifact.path,
                    'content': artifact.content,
                    'operation': 'create' if not (self.workspace / artifact.path).exists() else 'update'
                })
            elif isinstance(artifact, dict):
                changes.append({
                    'path': artifact.get('path', ''),
                    'content': artifact.get('content', ''),
                    'operation': artifact.get('operation', 'create')
                })
        return changes

    def _validate_workspace(self, context: Dict) -> AgentResult:
        """Validate workspace when no changes to apply"""
        insights = []
        
        # Check workspace exists
        if not self.workspace.exists():
            return AgentResult(
                agent_id="05",
                status="failed",
                artifacts=[],
                insights=["Workspace directory does not exist"],
                next_recommended_agent="00",
                confidence=0.0
            )
        
        # Count files
        file_count = sum(1 for _ in self.workspace.rglob('*') if _.is_file())
        insights.append(f"Workspace validated: {file_count} files present")
        
        # Check for common project files
        has_package_json = (self.workspace / 'package.json').exists()
        has_requirements = (self.workspace / 'requirements.txt').exists()
        
        if has_package_json:
            insights.append("Node.js project structure detected")
        if has_requirements:
            insights.append("Python project structure detected")
        
        return AgentResult(
            agent_id="05",
            status="success",
            artifacts=[],
            insights=insights,
            next_recommended_agent="06",
            confidence=0.8
        )

    def _apply_changes_safely(self, changes: List[Dict], context: Dict) -> AgentResult:
        """Apply changes with safety checks and backups"""
        applied = []
        failed = []
        insights = []
        
        # Create backup session
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_backup = self.backup_dir / session_id
        session_backup.mkdir(exist_ok=True)
        
        for change in changes:
            path = change.get('path', '')
            content = change.get('content', '')
            operation = change.get('operation', 'create')
            
            # Safety checks
            safety_result = self._safety_check(path, content)
            if not safety_result[0]:
                failed.append({
                    'path': path,
                    'reason': safety_result[1]
                })
                continue
            
            try:
                # Resolve full path
                full_path = self._resolve_path(path)
                
                if full_path is None:
                    failed.append({'path': path, 'reason': 'Invalid path'})
                    continue
                
                # Backup existing file
                if full_path.exists():
                    self._backup_file(full_path, session_backup)
                
                # Apply the change
                if operation == 'delete':
                    if full_path.exists():
                        full_path.unlink()
                        applied.append({'path': path, 'operation': 'deleted'})
                else:
                    # Create parent directories
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write content
                    full_path.write_text(content, encoding='utf-8')
                    applied.append({'path': path, 'operation': operation})
                    
            except Exception as e:
                failed.append({
                    'path': path,
                    'reason': str(e)
                })
        
        # Generate result
        if not applied and failed:
            status = "failed"
            insights.append(f"Integration failed: {len(failed)} files could not be applied")
        elif failed:
            status = "partial"
            insights.append(f"Partial integration: {len(applied)} applied, {len(failed)} failed")
        else:
            status = "success"
            insights.append(f"Successfully integrated {len(applied)} files")
        
        insights.append(f"Backup created: {session_backup.name}")
        
        # Generate integration report
        report = self._generate_integration_report(applied, failed, session_id)
        
        return AgentResult(
            agent_id="05",
            status=status,
            artifacts=[Artifact(
                type="report",
                path="integration_report.md",
                content=report
            )],
            insights=insights,
            next_recommended_agent="06" if status != "failed" else "07",
            confidence=0.9 if status == "success" else 0.5
        )

    def _safety_check(self, path: str, content: str) -> Tuple[bool, str]:
        """Perform safety checks on a file operation"""
        # Check for path traversal
        if '..' in path:
            return False, "Path traversal detected (..)"
        
        # Check for forbidden paths
        for forbidden in self.forbidden_paths:
            if forbidden.lower() in path.lower():
                return False, f"Forbidden path pattern: {forbidden}"
        
        # Check for absolute paths (outside workspace)
        if path.startswith('/') and not path.startswith(str(self.workspace)):
            return False, "Absolute path outside workspace"
        if len(path) > 2 and path[1] == ':' and not path.startswith(str(self.workspace)):
            return False, "Absolute Windows path outside workspace"
        
        # Check content size
        if len(content) > self.max_file_size:
            return False, f"Content too large ({len(content)} bytes > {self.max_file_size})"
        
        # Check for potential secrets in content
        secret_patterns = ['password=', 'api_key=', 'secret=', 'token=']
        content_lower = content.lower()
        for pattern in secret_patterns:
            if pattern in content_lower:
                # Check if it's a real value (not a placeholder)
                import re
                real_secret = re.search(rf'{pattern}["\']?[a-zA-Z0-9]{{10,}}', content_lower)
                if real_secret:
                    return False, f"Potential hardcoded secret detected: {pattern}"
        
        return True, "OK"

    def _resolve_path(self, path: str) -> Optional[Path]:
        """Resolve path relative to workspace"""
        try:
            # Handle various path formats
            clean_path = path.replace('\\', '/').lstrip('/')
            
            # Remove any workspace prefix if present
            workspace_str = str(self.workspace).replace('\\', '/')
            if clean_path.startswith(workspace_str):
                clean_path = clean_path[len(workspace_str):].lstrip('/')
            
            full_path = self.workspace / clean_path
            
            # Verify it's within workspace (prevent path traversal)
            try:
                full_path.resolve().relative_to(self.workspace.resolve())
            except ValueError:
                return None
            
            return full_path
            
        except Exception:
            return None

    def _backup_file(self, file_path: Path, backup_dir: Path) -> None:
        """Backup a file before modification"""
        try:
            relative = file_path.relative_to(self.workspace)
            backup_path = backup_dir / relative
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
        except Exception:
            pass  # Best effort backup

    def _generate_integration_report(self, applied: List[Dict], failed: List[Dict], session_id: str) -> str:
        """Generate integration report"""
        report = [
            "# Integration Report",
            "",
            f"**Session ID:** {session_id}",
            f"**Timestamp:** {datetime.now().isoformat()}",
            "",
            "## Summary",
            f"- ✅ Applied: {len(applied)}",
            f"- ❌ Failed: {len(failed)}",
            ""
        ]
        
        if applied:
            report.extend([
                "## Applied Changes",
                ""
            ])
            for item in applied:
                report.append(f"- ✅ `{item['path']}` ({item['operation']})")
            report.append("")
        
        if failed:
            report.extend([
                "## Failed Changes",
                ""
            ])
            for item in failed:
                report.append(f"- ❌ `{item['path']}`: {item['reason']}")
            report.append("")
        
        report.extend([
            "## Rollback",
            "",
            f"To rollback this integration, restore from backup:",
            f"```",
            f".vibecode/backups/{session_id}/",
            f"```",
            "",
            "## Next Steps",
            "",
            "Proceed to Agent 06 (Runtime) for environment setup and testing."
        ])
        
        return "\n".join(report)

    def rollback(self, session_id: str) -> AgentResult:
        """Rollback changes from a specific session"""
        backup_dir = self.backup_dir / session_id
        
        if not backup_dir.exists():
            return AgentResult(
                agent_id="05",
                status="failed",
                artifacts=[],
                insights=[f"Backup session not found: {session_id}"],
                next_recommended_agent="07",
                confidence=0.0
            )
        
        restored = []
        for backup_file in backup_dir.rglob('*'):
            if backup_file.is_file():
                relative = backup_file.relative_to(backup_dir)
                target = self.workspace / relative
                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup_file, target)
                    restored.append(str(relative))
                except Exception:
                    pass
        
        return AgentResult(
            agent_id="05",
            status="success",
            artifacts=[],
            insights=[f"Restored {len(restored)} files from backup {session_id}"],
            next_recommended_agent="04",
            confidence=0.9
        )
