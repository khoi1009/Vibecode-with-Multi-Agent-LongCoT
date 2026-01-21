"""
Agent Registry
Maps agent IDs to executor classes
"""

from typing import Dict, Type, Optional
from core.agent_executor import AgentExecutor
from core.agents.forensic_executor import ForensicExecutor
from core.agents.architect_executor import ArchitectExecutor
from core.agents.builder_executor import BuilderExecutor
from core.agents.designer_executor import DesignerExecutor
from core.agents.reviewer_executor import ReviewerExecutor
from core.agents.integrator_executor import IntegratorExecutor
from core.agents.operator_executor import OperatorExecutor
from core.agents.medic_executor import MedicExecutor
from core.agents.shipper_executor import ShipperExecutor
from core.agents.qa_executor import QAExecutor


AGENT_REGISTRY: Dict[str, Type[AgentExecutor]] = {
    "00": ForensicExecutor,     # Auditor - Forensic codebase analysis
    "01": ArchitectExecutor,    # Planner - Architecture and planning
    "02": BuilderExecutor,      # Coder - Code implementation
    "03": DesignerExecutor,     # Designer - UI/UX transformation
    "04": ReviewerExecutor,     # Reviewer - Code review and security
    "05": IntegratorExecutor,   # Integrator - Safe file integration
    "06": OperatorExecutor,     # Runtime - Environment management
    "07": MedicExecutor,        # Autofix - Bug fixing and recovery
    "08": ShipperExecutor,      # Export - Release engineering
    "09": QAExecutor,           # Testing - Automated QA
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
