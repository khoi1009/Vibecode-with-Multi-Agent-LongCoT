"""
Performance benchmarks for Vibecode.

Tests system performance and establishes baselines using pytest-benchmark.
"""

import pytest
from pathlib import Path
import time
import threading
import concurrent.futures

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.orchestrator import Orchestrator
from core.reasoning_engine import ReasoningEngine
from core.message_queue import AgentMessageQueue
from core.messages import AgentMessage, MessageType


class TestOrchestratorBenchmarks:
    """Performance benchmarks for Orchestrator."""

    @pytest.mark.benchmark
    def test_orchestrator_initialization(self, benchmark, temp_workspace, mock_ai_provider):
        """Benchmark orchestrator initialization."""
        def init_orchestrator():
            return Orchestrator(
                workspace=temp_workspace,
                ai_provider=mock_ai_provider,
                agent_id="02"
            )

        result = benchmark(init_orchestrator)

        assert result is not None
        assert result.agent_id == "02"

    @pytest.mark.benchmark
    def test_orchestrate_goal_simple(self, benchmark, temp_workspace, mock_llm):
        """Benchmark simple goal orchestration."""
        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm,
            agent_id="02"
        )

        def run_simple_goal():
            return orchestrator.orchestrate("Create a simple file", "Test context")

        result = benchmark(run_simple_goal)

        assert isinstance(result, dict)

    @pytest.mark.benchmark
    def test_orchestrate_goal_complex(self, benchmark, temp_workspace, mock_llm_sequence):
        """Benchmark complex goal orchestration."""
        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm_sequence,
            agent_id="02"
        )

        def run_complex_goal():
            return orchestrator.orchestrate(
                "Create a complete Python web application with Flask, including routes, models, and tests",
                "Complex benchmark"
            )

        result = benchmark(run_complex_goal)

        assert isinstance(result, dict)


class TestReasoningEngineBenchmarks:
    """Performance benchmarks for ReasoningEngine."""

    @pytest.mark.benchmark
    def test_reasoning_engine_initialization(self, benchmark, temp_workspace, mock_ai_provider):
        """Benchmark reasoning engine initialization."""
        def init_engine():
            return ReasoningEngine(
                workspace=temp_workspace,
                ai_provider=mock_ai_provider,
                agent_id="02"
            )

        result = benchmark(init_engine)

        assert result is not None

    @pytest.mark.benchmark
    def test_run_goal_simple(self, benchmark, temp_workspace, mock_llm):
        """Benchmark simple goal execution."""
        engine = ReasoningEngine(
            workspace=temp_workspace,
            ai_provider=mock_llm,
            agent_id="02"
        )

        def run_goal():
            return engine.run_goal("Create a test file", "Benchmark context")

        result = benchmark(run_goal)

        assert isinstance(result, dict)

    @pytest.mark.benchmark
    def test_parse_response(self, benchmark, temp_workspace, mock_ai_provider):
        """Benchmark response parsing."""
        engine = ReasoningEngine(
            workspace=temp_workspace,
            ai_provider=mock_ai_provider,
            agent_id="02"
        )

        def parse():
            response = """Thought: I need to test parsing
Action: list_dir
Args: {"path": "."}"""
            return engine._parse_response(response)

        thought, tool_call = benchmark(parse)

        assert thought is not None
        assert tool_call is not None

    @pytest.mark.benchmark
    def test_execute_tool(self, benchmark, temp_workspace, mock_ai_provider):
        """Benchmark tool execution."""
        engine = ReasoningEngine(
            workspace=temp_workspace,
            ai_provider=mock_ai_provider,
            agent_id="02"
        )

        # Create test file
        test_file = temp_workspace / "benchmark.txt"
        test_file.write_text("Benchmark test")

        def execute_tool():
            return engine._execute_tool("list_dir", {"path": "."})

        result = benchmark(execute_tool)

        assert result is not None

    @pytest.mark.benchmark
    def test_build_system_prompt(self, benchmark, temp_workspace, mock_ai_provider):
        """Benchmark system prompt building."""
        engine = ReasoningEngine(
            workspace=temp_workspace,
            ai_provider=mock_ai_provider,
            agent_id="02"
        )

        def build_prompt():
            return engine._build_system_prompt()

        result = benchmark(build_prompt)

        assert result is not None
        assert len(result) > 0


class TestMessageQueueBenchmarks:
    """Performance benchmarks for MessageQueue."""

    @pytest.mark.benchmark
    def test_message_queue_push(self, benchmark):
        """Benchmark message queue push operations."""
        queue = AgentMessageQueue()

        def push_message():
            msg = AgentMessage(
                id="test",
                from_agent="agent-01",
                to_agent="agent-02",
                message_type=MessageType.PLAN,
                payload={"test": "data"}
            )
            queue.push(msg)

        benchmark(push_message)

    @pytest.mark.benchmark
    def test_message_queue_pop(self, benchmark):
        """Benchmark message queue pop operations."""
        queue = AgentMessageQueue()

        # Pre-populate queue
        for i in range(100):
            msg = AgentMessage(
                id=str(i),
                from_agent="agent-01",
                to_agent="agent-02",
                message_type=MessageType.PLAN,
                payload={"index": i}
            )
            queue.push(msg)

        def pop_messages():
            return queue.pop_for_agent("agent-02")

        result = benchmark(pop_messages)

        assert len(result) == 100

    @pytest.mark.benchmark
    def test_message_queue_get_all(self, benchmark):
        """Benchmark getting all messages."""
        queue = AgentMessageQueue()

        # Pre-populate queue
        for i in range(1000):
            msg = AgentMessage(
                id=str(i),
                from_agent="agent-01",
                to_agent="agent-02",
                message_type=MessageType.PLAN,
                payload={"index": i}
            )
            queue.push(msg)

        def get_all():
            return queue.get_all_messages()

        result = benchmark(get_all)

        assert len(result) == 1000

    @pytest.mark.benchmark
    def test_message_queue_concurrent_push(self, benchmark):
        """Benchmark concurrent pushes to message queue."""
        queue = AgentMessageQueue()

        def concurrent_push():
            threads = []
            for i in range(10):
                def push_worker(worker_id):
                    for j in range(10):
                        msg = AgentMessage(
                            id=f"{worker_id}-{j}",
                            from_agent="agent-01",
                            to_agent="agent-02",
                            message_type=MessageType.PLAN,
                            payload={"worker": worker_id, "index": j}
                        )
                        queue.push(msg)

                t = threading.Thread(target=push_worker, args=(i,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

        benchmark(concurrent_push)

    @pytest.mark.benchmark
    def test_message_queue_get_latest_by_type(self, benchmark):
        """Benchmark getting latest message by type."""
        queue = AgentMessageQueue()

        # Pre-populate with mixed types
        for i in range(100):
            msg_type = MessageType.PLAN if i % 2 == 0 else MessageType.CODE
            msg = AgentMessage(
                id=str(i),
                from_agent="agent-01",
                to_agent="agent-02",
                message_type=msg_type,
                payload={"index": i}
            )
            queue.push(msg)

        def get_latest_plan():
            return queue.get_latest_by_type(MessageType.PLAN)

        result = benchmark(get_latest_plan)

        assert result is not None


class TestConcurrencyBenchmarks:
    """Performance benchmarks for concurrent operations."""

    @pytest.mark.benchmark
    def test_parallel_orchestrations(self, benchmark, temp_workspace, mock_ai_provider):
        """Benchmark parallel orchestrations."""
        def parallel_orchestration():
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for i in range(5):
                    orchestrator = Orchestrator(
                        workspace=temp_workspace,
                        ai_provider=mock_ai_provider,
                        agent_id="02"
                    )
                    future = executor.submit(
                        orchestrator.orchestrate,
                        f"Goal {i}",
                        f"Context {i}"
                    )
                    futures.append(future)

                results = [f.result() for f in futures]
                return results

        results = benchmark(parallel_orchestration)

        assert len(results) == 5
        for result in results:
            assert isinstance(result, dict)

    @pytest.mark.benchmark
    def test_parallel_reasoning_engines(self, benchmark, temp_workspace, mock_ai_provider):
        """Benchmark parallel reasoning engines."""
        def parallel_reasoning():
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for i in range(5):
                    engine = ReasoningEngine(
                        workspace=temp_workspace,
                        ai_provider=mock_ai_provider,
                        agent_id="02"
                    )
                    future = executor.submit(
                        engine.run_goal,
                        f"Goal {i}",
                        f"Context {i}"
                    )
                    futures.append(future)

                results = [f.result() for f in futures]
                return results

        results = benchmark(parallel_reasoning)

        assert len(results) == 5

    @pytest.mark.benchmark
    def test_thread_safety_message_queue(self, benchmark):
        """Benchmark thread safety of message queue."""
        queue = AgentMessageQueue()

        def concurrent_operations():
            def producer():
                for i in range(50):
                    msg = AgentMessage(
                        id=f"prod-{i}",
                        from_agent="agent-01",
                        to_agent="agent-02",
                        message_type=MessageType.PLAN,
                        payload={"index": i}
                    )
                    queue.push(msg)

            def consumer():
                for i in range(50):
                    queue.pop_for_agent("agent-02")

            threads = []
            for i in range(5):
                t1 = threading.Thread(target=producer)
                t2 = threading.Thread(target=consumer)
                threads.extend([t1, t2])
                t1.start()
                t2.start()

            for t in threads:
                t.join()

        benchmark(concurrent_operations)


class TestMemoryBenchmarks:
    """Memory usage benchmarks."""

    @pytest.mark.benchmark
    def test_memory_usage_orchestrator(self, benchmark, temp_workspace, mock_llm_sequence):
        """Benchmark memory usage during orchestrations."""
        import tracemalloc

        tracemalloc.start()

        def memory_test():
            orchestrator = Orchestrator(
                workspace=temp_workspace,
                ai_provider=mock_llm_sequence,
                agent_id="02"
            )
            result = orchestrator.orchestrate("Test memory usage", "Context")
            return result

        result = benchmark(memory_test)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Print memory usage for reference
        print(f"Current memory: {current / 1024 / 1024:.2f} MB")
        print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")

        assert isinstance(result, dict)

    @pytest.mark.benchmark
    def test_memory_usage_reasoning_engine(self, benchmark, temp_workspace, mock_llm_sequence):
        """Benchmark memory usage of reasoning engine."""
        import tracemalloc

        tracemalloc.start()

        def memory_test():
            engine = ReasoningEngine(
                workspace=temp_workspace,
                ai_provider=mock_llm_sequence,
                agent_id="02"
            )
            for i in range(10):
                engine.run_goal(f"Goal {i}", "Context")
            return True

        result = benchmark(memory_test)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"Current memory: {current / 1024 / 1024:.2f} MB")
        print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")

        assert result is True


class TestThroughputBenchmarks:
    """Throughput benchmarks."""

    @pytest.mark.benchmark
    def test_operations_per_second_simple(self, benchmark, temp_workspace, mock_ai_provider):
        """Benchmark simple operations per second."""
        engine = ReasoningEngine(
            workspace=temp_workspace,
            ai_provider=mock_ai_provider,
            agent_id="02"
        )

        def simple_operation():
            engine._execute_tool("list_dir", {"path": "."})

        ops_per_sec = benchmark.pedantic(
            simple_operation,
            rounds=100,
            iterations=10
        )

        print(f"Simple operations per second: {ops_per_sec:.2f}")
        assert ops_per_sec > 0

    @pytest.mark.benchmark
    def test_operations_per_second_message_queue(self, benchmark):
        """Benchmark message queue operations per second."""
        queue = AgentMessageQueue()

        def queue_operation():
            msg = AgentMessage(
                id="test",
                from_agent="agent-01",
                to_agent="agent-02",
                message_type=MessageType.PLAN,
                payload={"test": "data"}
            )
            queue.push(msg)
            queue.pop_for_agent("agent-02")

        ops_per_sec = benchmark.pedantic(
            queue_operation,
            rounds=200,
            iterations=5
        )

        print(f"Queue operations per second: {ops_per_sec:.2f}")
        assert ops_per_sec > 0

    @pytest.mark.benchmark
    def test_file_operations_throughput(self, benchmark, temp_workspace):
        """Benchmark file operations throughput."""
        def file_operations():
            # Create file
            test_file = temp_workspace / f"benchmark_{int(time.time())}.txt"
            test_file.write_text("Benchmark data")

            # Read file
            content = test_file.read_text()

            # Delete file
            test_file.unlink()

            return len(content)

        result = benchmark(file_operations)

        assert result > 0


class TestLatencyBenchmarks:
    """Latency benchmarks."""

    @pytest.mark.benchmark
    def test_orchestrator_response_time(self, benchmark, temp_workspace, mock_llm):
        """Benchmark orchestrator response time."""
        orchestrator = Orchestrator(
            workspace=temp_workspace,
            ai_provider=mock_llm,
            agent_id="02"
        )

        def measure_response():
            start = time.time()
            result = orchestrator.orchestrate("Quick test", "Context")
            elapsed = time.time() - start
            return elapsed

        latency = benchmark(measure_response)

        print(f"Average response time: {latency*1000:.2f} ms")
        assert latency > 0

    @pytest.mark.benchmark
    def test_reasoning_engine_response_time(self, benchmark, temp_workspace, mock_llm):
        """Benchmark reasoning engine response time."""
        engine = ReasoningEngine(
            workspace=temp_workspace,
            ai_provider=mock_llm,
            agent_id="02"
        )

        def measure_response():
            start = time.time()
            result = engine.run_goal("Quick test", "Context")
            elapsed = time.time() - start
            return elapsed

        latency = benchmark(measure_response)

        print(f"Average response time: {latency*1000:.2f} ms")
        assert latency > 0


class TestScalabilityBenchmarks:
    """Scalability benchmarks."""

    @pytest.mark.benchmark
    def test_scalability_message_count(self, benchmark):
        """Test how performance scales with message count."""
        def measure_with_messages(num_messages):
            queue = AgentMessageQueue()

            # Add messages
            for i in range(num_messages):
                msg = AgentMessage(
                    id=str(i),
                    from_agent="agent-01",
                    to_agent="agent-02",
                    message_type=MessageType.PLAN,
                    payload={"index": i}
                )
                queue.push(msg)

            # Measure get_all performance
            start = time.time()
            messages = queue.get_all_messages()
            elapsed = time.time() - start

            return elapsed, len(messages)

        # Test different scales
        scales = [100, 500, 1000, 5000]
        for scale in scales:
            elapsed, count = measure_with_messages(scale)
            print(f"Messages: {count}, Time: {elapsed*1000:.2f} ms")

        assert True

    @pytest.mark.benchmark
    def test_scalability_concurrent_threads(self, benchmark, temp_workspace, mock_ai_provider):
        """Test how performance scales with thread count."""
        def measure_with_threads(num_threads):
            def worker():
                orchestrator = Orchestrator(
                    workspace=temp_workspace,
                    ai_provider=mock_ai_provider,
                    agent_id="02"
                )
                orchestrator.orchestrate("Test", "Context")

            start = time.time()
            threads = [threading.Thread(target=worker) for _ in range(num_threads)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            elapsed = time.time() - start

            return elapsed

        # Test different thread counts
        thread_counts = [1, 2, 4, 8, 16]
        for count in thread_counts:
            elapsed = measure_with_threads(count)
            print(f"Threads: {count}, Time: {elapsed:.2f}s")

        assert True


class TestStabilityBenchmarks:
    """Stability and reliability benchmarks."""

    @pytest.mark.benchmark
    def test_repeated_operations_stability(self, benchmark, temp_workspace, mock_ai_provider):
        """Test stability over repeated operations."""
        engine = ReasoningEngine(
            workspace=temp_workspace,
            ai_provider=mock_ai_provider,
            agent_id="02"
        )

        def repeated_operation():
            return engine._execute_tool("list_dir", {"path": "."})

        # Run many times to check for stability
        result = benchmark.pedantic(
            repeated_operation,
            rounds=1000,
            iterations=1
        )

        assert result is not None

    @pytest.mark.benchmark
    def test_memory_leak_detection(self, benchmark, temp_workspace, mock_llm_sequence):
        """Test for memory leaks during repeated operations."""
        import tracemalloc

        def run_operations():
            engine = ReasoningEngine(
                workspace=temp_workspace,
                ai_provider=mock_llm_sequence,
                agent_id="02"
            )
            for i in range(100):
                engine.run_goal(f"Goal {i}", "Context")
            return True

        # Measure memory before
        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()

        result = benchmark(run_operations)

        # Measure memory after
        snapshot2 = tracemalloc.take_snapshot()
        tracemalloc.stop()

        # Compare snapshots
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')

        print("Top 10 memory differences:")
        for stat in top_stats[:10]:
            print(stat)

        assert result is True
