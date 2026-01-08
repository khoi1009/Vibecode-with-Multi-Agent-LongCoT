"""
Global test fixtures for Vibecode test suite.

This module provides reusable fixtures for unit, integration, and end-to-end tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, Mock
from typing import Dict, Any, List

# Import core modules for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestrator import Orchestrator
from core.reasoning_engine import ReasoningEngine


# ============================================================================
# Workspace Fixtures
# ============================================================================

@pytest.fixture
def temp_workspace():
    """Create an isolated temporary directory for each test."""
    tmp_dir = tempfile.mkdtemp(prefix="vibecode_test_")
    yield Path(tmp_dir)
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture
def workspace_with_project(temp_workspace):
    """Create a workspace with a sample project structure."""
    # Create basic project structure
    (temp_workspace / "src").mkdir(parents=True)
    (temp_workspace / "tests").mkdir(parents=True)
    (temp_workspace / "docs").mkdir(parents=True)

    # Create sample files
    (temp_workspace / "README.md").write_text("# Test Project\n\nA sample project for testing.\n")
    (temp_workspace / "requirements.txt").write_text("requests>=2.28.0\nnumpy>=1.21.0\n")
    (temp_workspace / "setup.py").write_text("from setuptools import setup\n\nsetup(name='test', version='1.0')\n")
    (temp_workspace / "src" / "main.py").write_text("# Main module\nprint('Hello, World!')\n")

    return temp_workspace


# ============================================================================
# Mock AI/LLM Fixtures
# ============================================================================

class MockLLM:
    """Mock LLM provider with deterministic responses."""

    def __init__(self, responses: List[str] = None):
        self.responses = responses or ["Mock response"]
        self.call_count = 0

    def generate(self, prompt: str) -> str:
        """Generate a mock response."""
        if self.responses:
            response = self.responses[min(self.call_count, len(self.responses) - 1)]
            self.call_count += 1
            return response
        return "Mock response"


@pytest.fixture
def mock_llm():
    """Create a mock LLM with a single response."""
    return MockLLM(["Test response"])


@pytest.fixture
def mock_llm_sequence():
    """Create a mock LLM with a sequence of responses."""
    return MockLLM([
        "First response",
        "Second response",
        "Third response",
    ])


@pytest.fixture
def mock_ai_provider():
    """Create a mock AI provider."""
    mock = MagicMock()
    mock.generate = MagicMock(return_value="Mock AI response")
    return mock


# ============================================================================
# Core Component Fixtures
# ============================================================================

@pytest.fixture
def orchestrator(temp_workspace, mock_ai_provider):
    """Create a pre-configured orchestrator instance."""
    orch = Orchestrator(
        workspace=temp_workspace,
        ai_provider=mock_ai_provider,
        agent_id="02"
    )
    return orch


@pytest.fixture
def reasoning_engine(temp_workspace, mock_ai_provider):
    """Create a ReasoningEngine with mocked LLM."""
    engine = ReasoningEngine(
        workspace=temp_workspace,
        ai_provider=mock_ai_provider,
        agent_id="02"
    )
    return engine


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_code():
    """Provide sample code for testing."""
    return {
        "python": """
def calculate_sum(a, b):
    '''Calculate the sum of two numbers.'''
    return a + b

result = calculate_sum(5, 3)
print(f"Result: {result}")
""",
        "javascript": """
function calculateSum(a, b) {
    return a + b;
}

const result = calculateSum(5, 3);
console.log(`Result: ${result}`);
""",
        "markdown": """
# Test Document

This is a test document for testing purposes.

## Section 1

Some content here.

## Section 2

More content.
"""
    }


@pytest.fixture
def sample_plan():
    """Provide sample plan for testing."""
    return {
        "goal": "Create a simple web application",
        "tasks": [
            {
                "id": "1",
                "title": "Setup project structure",
                "status": "pending",
                "agent_id": "02"
            },
            {
                "id": "2",
                "title": "Implement core functionality",
                "status": "pending",
                "agent_id": "02"
            }
        ],
        "context": "Test project context"
    }


@pytest.fixture
def sample_project_structure():
    """Provide a complete sample project structure."""
    return {
        "name": "test_project",
        "files": {
            "README.md": "# Test Project\n\nTest description\n",
            "src/main.py": "# Main module\nprint('Hello')\n",
            "src/utils.py": "# Utility functions\ndef helper(): pass\n",
            "tests/test_main.py": "# Tests\nimport pytest\n\ndef test_example():\n    assert True\n",
            "requirements.txt": "pytest>=7.0.0\n",
        }
    }


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls."""
    mock = MagicMock()
    mock.run = MagicMock()
    return mock


@pytest.fixture
def mock_path_exists():
    """Mock pathlib.Path.exists() method."""
    with pytest.MonkeyPatch().context() as m:
        m.setattr(Path, 'exists', lambda self: True)
        yield m


# ============================================================================
# Test Configuration
# ============================================================================

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment (runs automatically for each test)."""
    # Set test environment variables
    import os
    os.environ['VIBECODE_TEST_MODE'] = 'true'
    os.environ['VIBECODE_NO_COLOR'] = 'true'

    yield

    # Cleanup after test
    if 'VIBECODE_TEST_MODE' in os.environ:
        del os.environ['VIBECODE_TEST_MODE']
    if 'VIBECODE_NO_COLOR' in os.environ:
        del os.environ['VIBECODE_NO_COLOR']


# ============================================================================
# Parametrization Helpers
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "benchmark: mark test as a performance benchmark"
    )


# ============================================================================
# Test Data Generators
# ============================================================================

@pytest.fixture
def sample_file_content():
    """Generate sample file content for various file types."""
    def _generate_content(file_type: str, size: str = "small"):
        sizes = {
            "small": 10,
            "medium": 100,
            "large": 1000
        }
        count = sizes.get(size, 10)

        if file_type == "python":
            lines = ["# Python file\n"] + [f"x_{i} = {i}\n" for i in range(count)]
        elif file_type == "javascript":
            lines = ["// JavaScript file\n"] + [f"const x_{i} = {i};\n" for i in range(count)]
        elif file_type == "markdown":
            lines = ["# Markdown File\n\n"] + [f"## Section {i}\n\nContent {i}\n\n" for i in range(count)]
        else:
            lines = [f"Line {i}\n" for i in range(count)]

        return "".join(lines)

    return _generate_content
