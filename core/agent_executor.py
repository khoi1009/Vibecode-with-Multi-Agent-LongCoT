"""
Agent Executor Module
Base classes and contracts for agent execution logic
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from pathlib import Path


@dataclass
class Artifact:
    type: str  # "file", "plan", "report", "test"
    path: str
    content: str


@dataclass
class AgentResult:
    agent_id: str
    status: str  # "success", "partial", "failed"
    artifacts: List[Artifact]
    insights: List[str]
    next_recommended_agent: Optional[str]
    confidence: float


class AgentExecutor(ABC):
    """Base class for agent execution logic"""

    def __init__(self, workspace: Path, ai_provider=None, skill_loader=None):
        self.workspace = workspace
        self.ai_provider = ai_provider
        self.skill_loader = skill_loader

    @abstractmethod
    def execute(self, query: str, context: Dict, **kwargs) -> AgentResult:
        """Execute agent's primary function"""
        pass

    def has_ai(self) -> bool:
        """Check if AI provider is available and configured"""
        return self.ai_provider and self.ai_provider.is_configured()
