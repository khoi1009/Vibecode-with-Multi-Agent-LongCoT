"""
Agent Message Queue
Thread-safe FIFO queue for agent-to-agent communication
"""

from collections import deque
from typing import Dict, List, Optional
from threading import Lock
from .messages import AgentMessage, MessageType


class AgentMessageQueue:
    """Thread-safe message queue for agent communication"""

    def __init__(self, max_size: int = 100):
        self._queue: deque = deque(maxlen=max_size)
        self._by_agent: Dict[str, List[AgentMessage]] = {}
        self._lock = Lock()

    def push(self, message: AgentMessage) -> None:
        """Add message to queue"""
        with self._lock:
            self._queue.append(message)
            # Index by target agent
            if message.to_agent:
                if message.to_agent not in self._by_agent:
                    self._by_agent[message.to_agent] = []
                self._by_agent[message.to_agent].append(message)

    def pop_for_agent(self, agent_id: str) -> List[AgentMessage]:
        """Get all pending messages for an agent"""
        with self._lock:
            messages = self._by_agent.pop(agent_id, [])
            return messages

    def get_latest_by_type(self, message_type: MessageType) -> Optional[AgentMessage]:
        """Get most recent message of a type"""
        with self._lock:
            for msg in reversed(self._queue):
                if msg.message_type == message_type:
                    return msg
            return None

    def get_artifacts(self) -> List[str]:
        """Get all artifact paths from messages"""
        with self._lock:
            artifacts = []
            for msg in self._queue:
                artifacts.extend(msg.artifacts)
            return list(set(artifacts))

    def get_all_messages(self) -> List[AgentMessage]:
        """Get all messages in queue"""
        with self._lock:
            return list(self._queue)

    def get_message_count(self) -> int:
        """Get total message count"""
        with self._lock:
            return len(self._queue)

    def clear(self) -> None:
        """Clear queue (e.g., on pipeline completion)"""
        with self._lock:
            self._queue.clear()
            self._by_agent.clear()
