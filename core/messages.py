"""
Message System for Agent Communication
Structured message types and contracts for agent-to-agent handoff
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    """Types of messages agents can send"""
    PLAN = "plan"           # Architecture plan from Agent 01
    CODE = "code"           # Generated code from Agent 02
    REVIEW = "review"       # Code review from Agent 04
    TEST_RESULT = "test"    # Test results from Agent 09
    DIAGNOSIS = "diagnosis" # Error analysis from Agent 07
    DEPLOYMENT = "deploy"   # Deployment config from Agent 08
    INSIGHT = "insight"     # General insights
    ARTIFACT = "artifact"   # File reference
    REPORT = "report"       # Reports and audits


@dataclass
class AgentMessage:
    """Structured message for agent-to-agent communication"""
    id: str
    from_agent: str
    to_agent: Optional[str]  # None = broadcast to orchestrator
    message_type: MessageType
    payload: Dict[str, Any]
    artifacts: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0  # Higher = more urgent

    def compact(self, max_chars: int = 1000) -> "AgentMessage":
        """Create compacted version for handoff"""
        compacted_payload = {}
        for key, value in self.payload.items():
            if isinstance(value, str) and len(value) > max_chars:
                compacted_payload[key] = value[:max_chars] + f"... (truncated {len(value) - max_chars} chars)"
            else:
                compacted_payload[key] = value
        return AgentMessage(
            id=self.id,
            from_agent=self.from_agent,
            to_agent=self.to_agent,
            message_type=self.message_type,
            payload=compacted_payload,
            artifacts=self.artifacts,
            timestamp=self.timestamp,
            priority=self.priority
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "artifacts": self.artifacts,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create from dictionary"""
        return cls(
            id=data["id"],
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            message_type=MessageType(data["message_type"]),
            payload=data["payload"],
            artifacts=data.get("artifacts", []),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            priority=data.get("priority", 0)
        )
