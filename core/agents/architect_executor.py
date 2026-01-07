"""
Architect Executor
Agent 01: System design & planning
"""

from pathlib import Path
from typing import Dict, List, Optional
from core.agent_executor import AgentExecutor, AgentResult, Artifact


class ArchitectExecutor(AgentExecutor):
    """Agent 01: Architect - System design & planning"""

    def execute(self, query: str, context: Dict, **kwargs) -> AgentResult:
        """Execute architectural planning"""
        if self.has_ai():
            return self._execute_with_ai(query, context)
        return self._execute_fallback(query, context)

    def _execute_with_ai(self, query: str, context: Dict) -> AgentResult:
        """Execute with AI for creative planning"""
        # Build prompt for AI
        prompt = self._build_prompt(query, context)

        # Generate plan using AI
        try:
            ai_response = self.ai_provider.generate(prompt)
            plan_content = self._format_ai_response(ai_response)

            # Save plan
            artifacts = [Artifact(
                type="plan",
                path="docs/implementation_plan.md",
                content=plan_content
            )]

            insights = self._extract_insights(plan_content)

            return AgentResult(
                agent_id="01",
                status="success",
                artifacts=artifacts,
                insights=insights,
                next_recommended_agent="02",
                confidence=0.85
            )
        except Exception as e:
            # Fallback on AI error
            return self._execute_fallback(query, context, error=str(e))

    def _execute_fallback(self, query: str, context: Dict, error: Optional[str] = None) -> AgentResult:
        """Template-based planning fallback"""
        # Load template based on task type
        task_type = context.get("task_type", "").value if hasattr(context.get("task_type", ""), "value") else str(context.get("task_type", ""))

        template = self._load_template(task_type)
        plan = self._fill_template(template, query, context, error)

        artifacts = [Artifact(
            type="plan",
            path="docs/implementation_plan.md",
            content=plan
        )]

        insights = ["Generated from template (no AI)"]
        if error:
            insights.append(f"AI unavailable: {error}")

        return AgentResult(
            agent_id="01",
            status="partial",  # Indicates fallback was used
            artifacts=artifacts,
            insights=insights,
            next_recommended_agent="02",
            confidence=0.6
        )

    def _build_prompt(self, query: str, context: Dict) -> str:
        """Build prompt for AI planning"""
        prompt_parts = [
            "# Architectural Planning Request",
            "",
            f"Task: {query}",
            "",
            "## Context",
            f"Task Type: {context.get('task_type', 'unknown')}",
            f"Parameters: {context.get('params', {})}",
            "",
            "## Instructions",
            "Create a detailed implementation plan including:",
            "1. System architecture overview",
            "2. Component breakdown",
            "3. Technology recommendations",
            "4. Implementation steps",
            "5. Potential challenges and solutions",
            "",
            "Format as a structured markdown document.",
            "",
            "Be specific, actionable, and aligned with modern best practices."
        ]

        return "\n".join(prompt_parts)

    def _format_ai_response(self, ai_response: str) -> str:
        """Format AI response as plan"""
        # AI should already return markdown, just ensure it's properly formatted
        return f"# Implementation Plan\n\n{ai_response}"

    def _extract_insights(self, plan_content: str) -> List[str]:
        """Extract key insights from plan"""
        insights = []

        # Simple heuristic: look for section headers
        lines = plan_content.split('\n')
        for line in lines:
            if line.strip().startswith('##'):
                insights.append(line.strip().replace('##', '').strip())

        # Limit to first 5 insights
        return insights[:5]

    def _load_template(self, task_type: str) -> str:
        """Load planning template based on task type"""
        templates = {
            "build_feature": "# Implementation Plan: Build Feature\n\n## Overview\n{query}\n\n## Architecture\n\n## Components\n\n## Implementation Steps\n1. Setup\n2. Core functionality\n3. Testing\n4. Documentation\n\n## Technologies\n\n## Potential Challenges",
            "fix_bug": "# Implementation Plan: Bug Fix\n\n## Issue\n{query}\n\n## Root Cause Analysis\n\n## Solution Approach\n\n## Implementation\n1. Reproduce issue\n2. Implement fix\n3. Verify solution\n\n## Testing Strategy",
            "refactor_code": "# Implementation Plan: Code Refactoring\n\n## Target\n{query}\n\n## Current State\n\n## Target State\n\n## Refactoring Steps\n1. Analyze dependencies\n2. Plan changes\n3. Implement incrementally\n4. Test thoroughly\n\n## Risk Assessment",
            "default": "# Implementation Plan\n\n## Request\n{query}\n\n## Analysis\n\n## Plan\n\n## Next Steps"
        }

        return templates.get(task_type.lower(), templates["default"])

    def _fill_template(self, template: str, query: str, context: Dict, error: Optional[str] = None) -> str:
        """Fill template with context"""
        filled = template.format(query=query)

        # Add error note if fallback due to AI error
        if error:
            filled += f"\n\n## Note\nAI was unavailable, used template-based planning.\nError: {error}"

        return filled
