"""
Autonomy Configuration Module
Manages autonomous decision-making thresholds and audit logging
"""

from dataclasses import dataclass
from pathlib import Path
import json
from datetime import datetime
from typing import Tuple


@dataclass
class AutonomyConfig:
    """Configuration for autonomous decision-making"""
    confidence_threshold: float = 0.8
    auto_approve: bool = False
    audit_log_path: str = ".vibecode/autonomy_audit.log"

    def should_auto_approve(self, confidence: float, is_destructive: bool) -> Tuple[bool, str]:
        """
        Determine if task should auto-approve based on confidence.

        Args:
            confidence: Long CoT confidence score (0.0-1.0)
            is_destructive: Whether task involves code changes

        Returns:
            (should_proceed, reason) tuple
        """
        # High confidence: always approve
        if confidence >= self.confidence_threshold:
            return True, f"High confidence ({confidence:.1%})"

        # Low confidence + destructive: reject
        if confidence < 0.5 and is_destructive:
            return False, f"Low confidence ({confidence:.1%}) + destructive op"

        # Manual override via --auto flag
        if self.auto_approve:
            return True, "Auto-approve flag enabled"

        # Medium confidence: require manual approval
        return False, f"Confidence {confidence:.1%} below threshold {self.confidence_threshold:.0%}"

    def log_decision(self, log_path: Path, task_type: str, confidence: float,
                    approved: bool, reason: str) -> None:
        """
        Log autonomy decision to audit trail.

        Args:
            log_path: Path to audit log file
            task_type: Type of task being evaluated
            confidence: Confidence score
            approved: Whether task was approved
            reason: Reason for decision
        """
        log_path.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "confidence": round(confidence, 3),
            "approved": approved,
            "reason": reason
        }

        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
