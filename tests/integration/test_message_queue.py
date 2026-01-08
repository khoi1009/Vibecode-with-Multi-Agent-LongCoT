"""
Integration tests for AgentMessageQueue.

Tests thread-safety, message routing, and queue operations.
"""

import pytest
import threading
from pathlib import Path
from datetime import datetime

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.message_queue import AgentMessageQueue
from core.messages import AgentMessage, MessageType


class TestAgentMessageQueue:
    """Integration test suite for AgentMessageQueue."""

    @pytest.mark.integration
    def test_basic_push_pop(self):
        """Test basic message push and pop operations."""
        queue = AgentMessageQueue()

        # Create test message
        message = AgentMessage(
            id="test-1",
            from_agent="agent-01",
            to_agent="agent-02",
            message_type=MessageType.PLAN,
            payload={"plan": "test plan"}
        )

        # Push message
        queue.push(message)

        # Pop message
        messages = queue.pop_for_agent("agent-02")

        assert len(messages) == 1
        assert messages[0].id == "test-1"
        assert messages[0].from_agent == "agent-01"

    @pytest.mark.integration
    def test_multiple_agents(self):
        """Test message routing to multiple agents."""
        queue = AgentMessageQueue()

        # Send messages to different agents
        msg1 = AgentMessage("1", "orchestrator", "agent-01", MessageType.PLAN, {})
        msg2 = AgentMessage("2", "orchestrator", "agent-02", MessageType.CODE, {})
        msg3 = AgentMessage("3", "agent-01", "agent-03", MessageType.REVIEW, {})

        queue.push(msg1)
        queue.push(msg2)
        queue.push(msg3)

        # Pop messages for each agent
        agent1_msgs = queue.pop_for_agent("agent-01")
        agent2_msgs = queue.pop_for_agent("agent-02")
        agent3_msgs = queue.pop_for_agent("agent-03")

        assert len(agent1_msgs) == 1
        assert len(agent2_msgs) == 1
        assert len(agent3_msgs) == 1
        assert agent1_msgs[0].id == "1"
        assert agent2_msgs[0].id == "2"
        assert agent3_msgs[0].id == "3"

    @pytest.mark.integration
    def test_broadcast_messages(self):
        """Test handling of broadcast messages (to_agent=None)."""
        queue = AgentMessageQueue()

        # Broadcast message
        broadcast_msg = AgentMessage(
            id="broadcast-1",
            from_agent="orchestrator",
            to_agent=None,
            message_type=MessageType.INSIGHT,
            payload={"insight": "test"}
        )

        queue.push(broadcast_msg)

        # Should not be in any agent-specific queue
        agent_msgs = queue.pop_for_agent("agent-01")
        assert len(agent_msgs) == 0

        # But should be in main queue
        all_msgs = queue.get_all_messages()
        assert len(all_msgs) == 1

    @pytest.mark.integration
    def test_get_latest_by_type(self):
        """Test retrieving latest message by type."""
        queue = AgentMessageQueue()

        # Add multiple messages of different types
        queue.push(AgentMessage("1", "a", "b", MessageType.PLAN, {}))
        queue.push(AgentMessage("2", "a", "b", MessageType.CODE, {}))
        queue.push(AgentMessage("3", "a", "b", MessageType.PLAN, {}))

        # Get latest PLAN message
        latest_plan = queue.get_latest_by_type(MessageType.PLAN)
        assert latest_plan is not None
        assert latest_plan.id == "3"  # Last PLAN message

        # Get latest CODE message
        latest_code = queue.get_latest_by_type(MessageType.CODE)
        assert latest_code is not None
        assert latest_code.id == "2"

    @pytest.mark.integration
    def test_get_artifacts(self):
        """Test retrieving artifact paths from messages."""
        queue = AgentMessageQueue()

        # Add messages with artifacts
        queue.push(AgentMessage(
            "1", "a", "b", MessageType.PLAN, {},
            artifacts=["file1.py", "file2.py"]
        ))
        queue.push(AgentMessage(
            "2", "a", "b", MessageType.CODE, {},
            artifacts=["file3.py", "file1.py"]  # Duplicate
        ))

        artifacts = queue.get_artifacts()
        assert len(artifacts) == 3
        assert "file1.py" in artifacts
        assert "file2.py" in artifacts
        assert "file3.py" in artifacts

    @pytest.mark.integration
    def test_message_count(self):
        """Test message count tracking."""
        queue = AgentMessageQueue()

        assert queue.get_message_count() == 0

        queue.push(AgentMessage("1", "a", "b", MessageType.PLAN, {}))
        assert queue.get_message_count() == 1

        queue.push(AgentMessage("2", "a", "b", MessageType.CODE, {}))
        assert queue.get_message_count() == 2

    @pytest.mark.integration
    def test_clear_queue(self):
        """Test queue clearing."""
        queue = AgentMessageQueue()

        queue.push(AgentMessage("1", "a", "b", MessageType.PLAN, {}))
        queue.push(AgentMessage("2", "a", "b", MessageType.CODE, {}))

        assert queue.get_message_count() == 2

        queue.clear()

        assert queue.get_message_count() == 0
        assert len(queue.get_all_messages()) == 0

    @pytest.mark.integration
    def test_max_size_limit(self):
        """Test queue respects max_size."""
        max_size = 5
        queue = AgentMessageQueue(max_size=max_size)

        # Add messages up to max_size
        for i in range(max_size):
            queue.push(AgentMessage(str(i), "a", "b", MessageType.PLAN, {}))

        assert queue.get_message_count() == max_size

        # Add one more (should not exceed max_size due to deque maxlen)
        queue.push(AgentMessage(str(max_size), "a", "b", MessageType.PLAN, {}))

        # Deque with maxlen will maintain size
        assert queue.get_message_count() == max_size

    @pytest.mark.integration
    def test_thread_safety_push_pop(self):
        """Test thread safety of push/pop operations."""
        queue = AgentMessageQueue()
        num_threads = 10
        messages_per_thread = 10
        errors = []

        def push_messages(thread_id):
            try:
                for i in range(messages_per_thread):
                    msg = AgentMessage(
                        f"{thread_id}-{i}",
                        f"agent-{thread_id}",
                        "agent-00",
                        MessageType.PLAN,
                        {"thread": thread_id, "index": i}
                    )
                    queue.push(msg)
            except Exception as e:
                errors.append(e)

        def pop_messages(thread_id):
            try:
                for i in range(messages_per_thread):
                    msgs = queue.pop_for_agent(f"agent-{thread_id}")
                    if msgs:
                        assert len(msgs) == messages_per_thread
            except Exception as e:
                errors.append(e)

        # Start push threads
        push_threads = [
            threading.Thread(target=push_messages, args=(i,))
            for i in range(num_threads)
        ]

        # Start pop threads
        pop_threads = [
            threading.Thread(target=pop_messages, args=(i,))
            for i in range(num_threads)
        ]

        # Run all threads
        for t in push_threads + pop_threads:
            t.start()

        # Wait for completion
        for t in push_threads + pop_threads:
            t.join()

        # Should be no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

    @pytest.mark.integration
    def test_thread_safety_get_latest(self):
        """Test thread safety of get_latest_by_type."""
        queue = AgentMessageQueue()
        errors = []
        num_threads = 10

        def producer(thread_id):
            try:
                for i in range(100):
                    queue.push(AgentMessage(
                        f"{thread_id}-{i}",
                        "a",
                        "b",
                        MessageType.PLAN if i % 2 == 0 else MessageType.CODE,
                        {}
                    ))
            except Exception as e:
                errors.append(e)

        def consumer(thread_id):
            try:
                for i in range(50):
                    latest_plan = queue.get_latest_by_type(MessageType.PLAN)
                    latest_code = queue.get_latest_by_type(MessageType.CODE)
                    # Should not crash
                    assert latest_plan is None or isinstance(latest_plan, AgentMessage)
                    assert latest_code is None or isinstance(latest_code, AgentMessage)
            except Exception as e:
                errors.append(e)

        # Start threads
        threads = [
            threading.Thread(target=producer if i % 2 == 0 else consumer, args=(i,))
            for i in range(num_threads)
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors occurred: {errors}"

    @pytest.mark.integration
    def test_empty_pop(self):
        """Test popping from empty agent queue."""
        queue = AgentMessageQueue()

        # Pop from non-existent agent
        messages = queue.pop_for_agent("non-existent-agent")

        assert len(messages) == 0

    @pytest.mark.integration
    def test_multiple_pops_same_agent(self):
        """Test multiple pops for the same agent."""
        queue = AgentMessageQueue()

        # Add two messages for same agent
        queue.push(AgentMessage("1", "a", "agent-01", MessageType.PLAN, {}))
        queue.push(AgentMessage("2", "a", "agent-01", MessageType.CODE, {}))

        # First pop should get both
        messages1 = queue.pop_for_agent("agent-01")
        assert len(messages1) == 2

        # Second pop should be empty
        messages2 = queue.pop_for_agent("agent-01")
        assert len(messages2) == 0

    @pytest.mark.integration
    def test_message_ordering(self):
        """Test that messages maintain FIFO order."""
        queue = AgentMessageQueue()

        # Add messages in order
        for i in range(5):
            queue.push(AgentMessage(
                str(i), "a", "agent-01", MessageType.PLAN, {"index": i}
            ))

        # Pop and verify order
        messages = queue.pop_for_agent("agent-01")
        assert len(messages) == 5

        # Check they are in order (FIFO)
        for i, msg in enumerate(messages):
            assert msg.id == str(i)
            assert msg.payload["index"] == i

    @pytest.mark.integration
    def test_get_all_messages(self):
        """Test retrieving all messages."""
        queue = AgentMessageQueue()

        # Add messages to different agents
        queue.push(AgentMessage("1", "a", "agent-01", MessageType.PLAN, {}))
        queue.push(AgentMessage("2", "a", "agent-02", MessageType.CODE, {}))
        queue.push(AgentMessage("3", "a", None, MessageType.INSIGHT, {}))

        all_msgs = queue.get_all_messages()
        assert len(all_msgs) == 3

        # Verify all messages are present
        msg_ids = [msg.id for msg in all_msgs]
        assert "1" in msg_ids
        assert "2" in msg_ids
        assert "3" in msg_ids

    @pytest.mark.integration
    def test_priority_messages(self):
        """Test message priority handling."""
        queue = AgentMessageQueue()

        # Add messages with different priorities
        queue.push(AgentMessage("1", "a", "b", MessageType.PLAN, {}, priority=1))
        queue.push(AgentMessage("2", "a", "b", MessageType.PLAN, {}, priority=5))
        queue.push(AgentMessage("3", "a", "b", MessageType.PLAN, {}, priority=3))

        # Get all messages
        all_msgs = queue.get_all_messages()
        assert len(all_msgs) == 3

        # Verify priorities are maintained
        priorities = [msg.priority for msg in all_msgs]
        assert 1 in priorities
        assert 3 in priorities
        assert 5 in priorities

    @pytest.mark.integration
    def test_timestamp_preservation(self):
        """Test that timestamps are preserved."""
        queue = AgentMessageQueue()

        # Add message with known timestamp
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        message = AgentMessage(
            "1", "a", "b", MessageType.PLAN, {}, timestamp=timestamp
        )
        queue.push(message)

        # Retrieve and verify
        retrieved = queue.get_all_messages()[0]
        assert retrieved.timestamp == timestamp
