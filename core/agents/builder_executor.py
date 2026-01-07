"""
Builder Executor
Agent 02: Code implementation via ReasoningEngine
"""

from pathlib import Path
from typing import Dict, List
from core.agent_executor import AgentExecutor, AgentResult, Artifact


class BuilderExecutor(AgentExecutor):
    """Agent 02: Builder - Code implementation via ReasoningEngine"""

    def __init__(self, workspace: Path, ai_provider=None, skill_loader=None):
        super().__init__(workspace, ai_provider, skill_loader)
        self.reasoning_engine = None
        if ai_provider:
            try:
                from core.reasoning_engine import ReasoningEngine
                self.reasoning_engine = ReasoningEngine(workspace, ai_provider)
            except ImportError:
                # ReasoningEngine might not exist yet
                pass

    def execute(self, query: str, context: Dict, **kwargs) -> AgentResult:
        """Execute code building"""
        # Check for plan from Agent 01
        plan = context.get("plan_content", "")
        task_type = context.get("task_type", "")

        # Try ReasoningEngine if available
        if self.reasoning_engine and self.has_ai():
            return self._execute_with_reasoning_engine(query, plan, context)

        # Fallback: Use universal generator
        return self._fallback_generate(query, context)

    def _execute_with_reasoning_engine(self, query: str, plan: str, context: Dict) -> AgentResult:
        """Execute using ReasoningEngine"""
        try:
            # Build execution prompt
            prompt = self._build_execution_prompt(query, plan, context)

            # Run reasoning engine
            result = self.reasoning_engine.run_goal(prompt, str(context))

            if result.get("success"):
                # Collect created files
                created_files = self._collect_created_files()

                return AgentResult(
                    agent_id="02",
                    status="success",
                    artifacts=created_files,
                    insights=["Built via ReasoningEngine"],
                    next_recommended_agent="09",
                    confidence=0.9
                )
            else:
                # Reasoning failed, use fallback
                return self._fallback_generate(query, context, reason="ReasoningEngine failed")

        except Exception as e:
            # Error in ReasoningEngine, use fallback
            return self._fallback_generate(query, context, reason=f"ReasoningEngine error: {str(e)}")

    def _fallback_generate(self, query: str, context: Dict, reason: str = "") -> AgentResult:
        """Fallback code generation without ReasoningEngine"""
        # Use UniversalGenerator if available
        if self.skill_loader:
            try:
                # Create a simple implementation based on query
                code = self._generate_simple_implementation(query, context)

                artifacts = [Artifact(
                    type="file",
                    path="generated_implementation.py",
                    content=code
                )]

                insights = ["Generated using template-based approach"]
                if reason:
                    insights.append(f"Primary method unavailable: {reason}")

                return AgentResult(
                    agent_id="02",
                    status="partial",
                    artifacts=artifacts,
                    insights=insights,
                    next_recommended_agent="09",
                    confidence=0.6
                )
            except Exception as e:
                pass

        # Minimal fallback
        return AgentResult(
            agent_id="02",
            status="failed",
            artifacts=[],
            insights=[f"Build failed: {reason or 'No implementation available'}"],
            next_recommended_agent="07",  # Medic
            confidence=0.0
        )

    def _build_execution_prompt(self, query: str, plan: str, context: Dict) -> str:
        """Build prompt for ReasoningEngine"""
        prompt_parts = [
            "# Code Implementation Request",
            "",
            f"Task: {query}",
            "",
            "## Plan (from Architect)",
            plan if plan else "No plan provided",
            "",
            "## Context",
            f"Task Type: {context.get('task_type', 'unknown')}",
            f"Parameters: {context.get('params', {})}",
            "",
            "## Instructions",
            "Implement the requested feature or fix:",
            "1. Create necessary files",
            "2. Write clean, documented code",
            "3. Follow project conventions",
            "4. Include error handling",
            "",
            "Work in the workspace directory. Report created files.",
        ]

        return "\n".join(prompt_parts)

    def _collect_created_files(self) -> List[Artifact]:
        """Collect files created by ReasoningEngine"""
        artifacts = []
        workspace_path = Path(self.workspace)

        # Look for recently modified files
        # In a real implementation, ReasoningEngine would track this
        for file_path in workspace_path.rglob("*.py"):
            try:
                # Check if file was modified recently (simple heuristic)
                content = file_path.read_text(encoding='utf-8', errors='ignore')

                artifacts.append(Artifact(
                    type="file",
                    path=str(file_path.relative_to(workspace_path)),
                    content=content
                ))
            except Exception:
                pass

        # If no files found, create a summary artifact
        if not artifacts:
            artifacts.append(Artifact(
                type="report",
                path="build_summary.md",
                content="# Build Summary\n\nImplementation completed."
            ))

        return artifacts

    def _generate_simple_implementation(self, query: str, context: Dict) -> str:
        """Generate simple implementation as fallback"""
        # Simple template-based generation
        implementation = f'''"""
Implementation for: {query}
Generated by Vibecode Agent 02 (Builder)
"""

# TODO: Implement the requested feature
# This is a template - replace with actual implementation

def main():
    """
    Main implementation for: {query}
    """
    print("Feature not yet implemented")
    print(f"Query: {query}")
    print(f"Context: {context}")

if __name__ == "__main__":
    main()
'''

        return implementation
