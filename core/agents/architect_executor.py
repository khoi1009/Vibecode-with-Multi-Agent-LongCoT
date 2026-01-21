"""
Architect Executor
Agent 01: System design & planning using ReasoningEngine
Implements the full INTAKE → BLUEPRINT → CONTRACT protocol from 01_planner.md
"""

from pathlib import Path
from typing import Dict, List, Optional
from core.agent_executor import AgentExecutor, AgentResult, Artifact


class ArchitectExecutor(AgentExecutor):
    """Agent 01: Architect - Principal Software Architect & Product Strategist
    
    Follows the 3-Phase Protocol:
    - Phase 0: INTAKE (Requirements Gathering)
    - Phase 1: BLUEPRINT (Architecture Design)  
    - Phase 2: CONTRACT (Finalization & Handoff)
    """
    
    def __init__(self, workspace: Path, ai_provider=None, skill_loader=None):
        super().__init__(workspace, ai_provider, skill_loader)
        self.reasoning_engine = None
        if ai_provider:
            try:
                from core.reasoning_engine import ReasoningEngine
                # Use agent_id "01" for proper tool permissions
                self.reasoning_engine = ReasoningEngine(workspace, ai_provider, agent_id="01")
            except ImportError:
                pass
        
        # Load the full agent instructions from 01_planner.md
        self.agent_instructions = self._load_agent_instructions()

    def _load_agent_instructions(self) -> str:
        """Load the full 01_planner.md as agent instructions"""
        planner_paths = [
            Path(__file__).parent.parent.parent / "agents" / "01_planner.md",
            self.workspace / "agents" / "01_planner.md",
        ]
        
        for path in planner_paths:
            if path.exists():
                try:
                    return path.read_text(encoding='utf-8')
                except:
                    pass
        
        # Fallback: embedded core instructions
        return self._get_embedded_instructions()

    def execute(self, query: str, context: Dict, **kwargs) -> AgentResult:
        """Execute architectural planning following the 3-Phase Protocol"""
        # Try ReasoningEngine first for intelligent planning
        if self.reasoning_engine and self.has_ai():
            return self._execute_with_reasoning_engine(query, context)
        elif self.has_ai():
            return self._execute_with_ai(query, context)
        return self._execute_fallback(query, context)
    
    def _execute_with_reasoning_engine(self, query: str, context: Dict) -> AgentResult:
        """Execute planning using ReasoningEngine for multi-step analysis"""
        try:
            # Build comprehensive planning prompt with full protocol
            prompt = self._build_planning_prompt(query, context)
            
            # Run reasoning engine
            result = self.reasoning_engine.run_goal(prompt, str(context))
            
            if result.get("success"):
                # Look for the contract file
                contract_file = self.workspace / "docs" / "vibecode_plan.md"
                plan_file = self.workspace / "implementation_plan.md"
                task_plan_file = self.workspace / "task_plan.md"
                
                # Read whichever plan file was created
                plan_content = ""
                for pf in [contract_file, plan_file, task_plan_file]:
                    if pf.exists():
                        plan_content = pf.read_text(encoding='utf-8')
                        break
                
                if not plan_content:
                    # Create a summary from the reasoning history
                    plan_content = self._extract_plan_from_history(result.get("history", []))
                    # Save it to disk for Agent 02
                    plan_file.write_text(plan_content, encoding='utf-8')
                
                # Also ensure implementation_plan.md exists for Agent 02
                if not plan_file.exists():
                    plan_file.write_text(plan_content, encoding='utf-8')
                
                artifacts = [Artifact(
                    type="plan",
                    path="implementation_plan.md",
                    content=plan_content
                )]
                
                insights = self._extract_insights(plan_content)
                
                return AgentResult(
                    agent_id="01",
                    status="success",
                    artifacts=artifacts,
                    insights=insights,
                    next_recommended_agent="02",
                    confidence=0.9
                )
            else:
                # Fallback if reasoning fails
                return self._execute_with_ai(query, context)
                
        except Exception as e:
            return self._execute_with_ai(query, context)
    
    def _load_relevant_skills(self, query: str) -> str:
        """
        Load relevant skills for planning tasks.
        Agent 01 has affinity for: planning, planning-with-files, sequential-thinking, problem-solving
        """
        if not self.skill_loader:
            return ""
        
        try:
            # Select skills with agent affinity (agent_id="01")
            selected = self.skill_loader.select_skills(
                query=query,
                agent_id="01",
                max_skills=3,
                min_score=0.1
            )
            
            if not selected:
                # Fallback: Always load planning skill for Agent 01
                planning_skill = self.skill_loader.get_skill("planning")
                if planning_skill:
                    selected = [(planning_skill, 1.0)]
            
            if selected:
                # Extract just the Skill objects from tuples
                skills = [s[0] if isinstance(s, tuple) else s for s in selected]
                skill_context = self.skill_loader.build_skills_context(
                    skills,
                    include_references=True,
                    include_scripts=True
                )
                print(f"   [+] Loaded {len(skills)} skills for Agent 01: {[s.name for s in skills]}")
                return skill_context
        except Exception as e:
            print(f"   [!] Skill loading error: {e}")
        
        return ""

    def _build_planning_prompt(self, query: str, context: Dict) -> str:
        """Build comprehensive planning prompt following 01_planner.md protocol"""
        task_type = context.get("task_type", "build_feature")
        if hasattr(task_type, 'value'):
            task_type = task_type.value
        
        # Load relevant skills from skills folder
        skills_context = self._load_relevant_skills(query)
        
        # Check for existing audit report
        audit_report = ""
        audit_path = self.workspace / "audit_report.md"
        if audit_path.exists():
            try:
                audit_report = audit_path.read_text(encoding='utf-8')[:5000]  # Limit size
            except:
                pass
            
        return f"""# Agent 01: Principal Software Architect

{skills_context}

You are Agent 01, the Principal Software Architect & Product Strategist.
Your mission: Lead the project from concept to blueprint through the systematic **Intake → Blueprint → Contract** process.

---

## YOUR CORE PROTOCOL

### Phase 0: INTAKE (Requirements Gathering)
- Analyze the user request
- Identify what's clear vs what's ambiguous
- For BUILD tasks: Determine tech stack, data models, key features

### Phase 1: BLUEPRINT (Architecture Design)  
- Design system architecture
- Define data models with TypeScript interfaces
- Plan component structure
- Identify dependencies

### Phase 2: CONTRACT (Finalization)
- Create the implementation contract
- Define atomic implementation steps
- Include gate checklist for Agent 04

---

## USER REQUEST
{query}

## TASK TYPE
{task_type}

## EXISTING AUDIT DATA
{audit_report if audit_report else "No audit_report.md found. Proceed with user-provided tech stack."}

---

## YOUR DELIVERABLES

You MUST create these files using write_file:

### 1. task_plan.md (Track your progress)
```markdown
# Task Plan: [Project Name]

## Goal
[One sentence: What we're building]

## Phases
- [x] Phase 0: Requirements Intake
- [ ] Phase 1: Architecture Blueprint  
- [ ] Phase 2: Technical Contract

## Decisions Made
- [Decision]: [Rationale]

## Status
Currently in Phase X
```

### 2. implementation_plan.md (The Contract for Agent 02)

Use this EXACT structure:

```markdown
# Blueprint: [Project Name]
**Status:** FINAL CONTRACT
**Architect:** Agent 01
**Estimated Complexity:** [Low/Medium/High]

---

## 1. Executive Summary
[What is being built and why - 1-2 sentences]

---

## 2. The Contract (Type Definitions)

CRITICAL: Agent 02 must use these EXACT interfaces.

```typescript
// Define all key data structures
interface IUser {{
  id: string;
  email: string;
  // ... other fields
}}

// API response type
type ApiResponse<T> = {{
  data: T;
  error: string | null;
  status: number;
}}
```

---

## 3. Component Architecture

### Module A: [Name]
- **File Path:** `src/path/to/file.ts`
- **Responsibility:** [What it does]
- **Props/Input:** [TypeScript interface]
- **Dependencies:** [Libraries needed]

### Module B: [Name]  
[Same structure]

---

## 4. Implementation Checklist (Sequential Steps)

Agent 02 must complete in this order:

1. [ ] **Step 1:** Create type definitions in `src/types/`
2. [ ] **Step 2:** Set up project structure
3. [ ] **Step 3:** Implement core backend/API
4. [ ] **Step 4:** Implement database schema
5. [ ] **Step 5:** Build frontend components
6. [ ] **Step 6:** Connect frontend to backend
7. [ ] **Step 7:** Add error handling
8. [ ] **Step 8:** Self-test all features

---

## 5. File Structure

```
project-name/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   └── types/
│   └── package.json
├── backend/
│   ├── src/
│   │   ├── routes/
│   │   ├── controllers/
│   │   └── middleware/
│   ├── prisma/
│   └── package.json
└── README.md
```

---

## 6. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/resource | List resources |
| POST | /api/resource | Create resource |

---

## 7. Database Schema

[Prisma schema or SQL tables]

---

## 8. Non-Functional Requirements

### Performance:
- API response time: <500ms
- Page load: <3s

### Security:
- Input validation on all endpoints
- JWT token expiration: 15min access, 7d refresh

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| [Risk 1] | [How to handle] |

---

## 10. Gate Checklist (For Agent 04 Review)

Agent 04 must verify:
- [ ] All interfaces from Section 2 are used
- [ ] All files from Section 5 exist
- [ ] All steps from Section 4 completed
- [ ] No `any` types in TypeScript
- [ ] Error handling in all async code

---

## 11. Dependencies to Install

```bash
# Frontend
npm install [packages]

# Backend  
npm install [packages]
```

---

**Status:** APPROVED FOR CONSTRUCTION
**Next:** Hand off to Agent 02 (Builder)
```

---

## EXECUTION INSTRUCTIONS

1. First, create `task_plan.md` to track your progress
2. Analyze the requirements thoroughly
3. Create `implementation_plan.md` with the FULL contract structure above
4. When done, call finish_task with summary

Remember: You are the GATEKEEPER OF QUALITY. No code is written until you approve.
Be specific, actionable, and create atomic steps that Agent 02 cannot misinterpret.
"""

    def _extract_plan_from_history(self, history: List) -> str:
        """Extract plan content from reasoning history if file wasn't created"""
        # Look for write_file operations in history
        for item in history:
            content = item.get("content", "")
            if "implementation_plan" in content.lower() and "```" in content:
                # Extract markdown content
                import re
                match = re.search(r"```markdown\n(.*?)```", content, re.DOTALL)
                if match:
                    return match.group(1)
        
        # Fallback: create basic plan
        return "# Implementation Plan\n\nPlan generation in progress. See Agent 02 for implementation."

    def _execute_with_ai(self, query: str, context: Dict) -> AgentResult:
        """Execute with AI for creative planning (simple single-call fallback)"""
        # Build prompt for AI
        prompt = self._build_prompt(query, context)

        # Generate plan using AI
        try:
            ai_response = self.ai_provider.generate(prompt)
            plan_content = self._format_ai_response(ai_response)

            # IMPORTANT: Save plan to disk so Agent 02 can read it
            plan_file = self.workspace / "implementation_plan.md"
            plan_file.write_text(plan_content, encoding='utf-8')
            print(f"   [+] Plan saved to: {plan_file}")

            # Save plan
            artifacts = [Artifact(
                type="plan",
                path="implementation_plan.md",
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

        # IMPORTANT: Save plan to disk so Agent 02 can read it
        plan_file = self.workspace / "implementation_plan.md"
        plan_file.write_text(plan, encoding='utf-8')
        print(f"   [+] Plan saved to: {plan_file}")

        artifacts = [Artifact(
            type="plan",
            path="implementation_plan.md",
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

    def _get_embedded_instructions(self) -> str:
        """
        Fallback embedded instructions when 01_planner.md cannot be loaded.
        Contains the essential protocol for Agent 01 - Principal Software Architect.
        """
        return '''
# Agent 01 - Principal Software Architect Protocol

## YOUR ROLE
You are the PRINCIPAL SOFTWARE ARCHITECT. Every successful project begins with YOUR blueprint.
You produce the CONTRACT that all other agents will follow.

## 3-PHASE PROTOCOL

### PHASE 1: INTAKE (Understanding)
1. Parse the user's request completely
2. Identify explicit and implicit requirements
3. Determine project scope and boundaries
4. Note any constraints (tech stack, performance, etc.)

### PHASE 2: BLUEPRINT (Design)
1. Define the system architecture
2. Design component interactions
3. Specify data models and TypeScript interfaces
4. Plan file structure and organization

### PHASE 3: CONTRACT (Documentation)
Create implementation_plan.md with these sections:

1. **Executive Summary** - One paragraph overview
2. **Type Definitions** - TypeScript interfaces for all data structures
3. **Component Architecture** - How components interact
4. **Implementation Checklist** - Atomic steps with checkboxes
5. **File Structure** - Complete project tree
6. **API Endpoints** - If applicable
7. **Database Schema** - If applicable
8. **Non-Functional Requirements** - Performance, security, accessibility
9. **Risk Mitigation** - Potential issues and solutions
10. **Gate Checklist for Agent 04** - What reviewer must verify
11. **Dependencies** - npm packages, pip packages to install

## CRITICAL RULES
- Every implementation step must be ATOMIC (one action)
- Include TypeScript interfaces for ALL data structures
- File paths must be EXPLICIT
- No ambiguous instructions
- Gate checklist is REQUIRED for Agent 04
'''

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
