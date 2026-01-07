"""
Agent Registry
Maps agent IDs to executor classes
"""

from typing import Dict, Type, Optional
from core.agent_executor import AgentExecutor
from core.agents.forensic_executor import ForensicExecutor
from core.agents.architect_executor import ArchitectExecutor
from core.agents.builder_executor import BuilderExecutor
from core.agents.qa_executor import QAExecutor


AGENT_REGISTRY: Dict[str, Type[AgentExecutor]] = {
    "00": ForensicExecutor,
    "01": ArchitectExecutor,
    "02": BuilderExecutor,
    "03": None,  # Designer - TODO
    "04": None,  # Reviewer - TODO
    "05": None,  # Integrator - TODO
    "06": None,  # Operator - TODO
    "07": None,  # Medic - Use existing Diagnostician
    "08": None,  # Shipper - TODO
    "09": QAExecutor,
}


def get_executor(agent_id: str, workspace, ai_provider, skill_loader) -> Optional[AgentExecutor]:
    """
    Get executor instance for agent ID

    Args:
        agent_id: Agent identifier (e.g., "00", "01", "02")
        workspace: Workspace directory path
        ai_provider: AI provider instance
        skill_loader: Skill loader instance

    Returns:
        AgentExecutor instance or None if not implemented
    """
    executor_class = AGENT_REGISTRY.get(agent_id)
    if executor_class:
        return executor_class(workspace, ai_provider, skill_loader)
    return None  # Fallback to simulation


def is_implemented(agent_id: str) -> bool:
    """Check if agent has real implementation"""
    return agent_id in AGENT_REGISTRY and AGENT_REGISTRY[agent_id] is not None


def list_implemented_agents() -> list[str]:
    """List all agent IDs that have implementations"""
    return [aid for aid, cls in AGENT_REGISTRY.items() if cls is not None]
