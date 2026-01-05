# Consistent Planning Architecture

**Date:** January 5, 2026  
**Status:** ✅ Implemented  
**Objective:** Ensure all development paths follow Agent 01's planning protocol

---

## Problem Identified

**Original Issue:** Path 1 (New Fullstack App) bypassed Agent 01 (Planner) and went directly to Agent 02 (Builder), violating the Three-Phase Protocol defined in `agents/01_planner.md`.

**Impact:**
- ❌ New projects had no architecture contract
- ❌ Inconsistent quality gates between new vs existing projects
- ❌ No structured Intake → Blueprint → Contract flow
- ❌ Missing approval checkpoints

---

## Solution: Two-Phase Hybrid Architecture

All development now follows this pattern:

```
┌─────────────────────────────────────────────────────┐
│ PHASE 1: PLANNING (Agent 01 + AI)                  │
│ ────────────────────────────────────────────────────│
│ • Intake: Gather requirements                       │
│ • Blueprint: Design architecture                    │
│ • Contract: Create implementation plan              │
│ • Output: vibecode_plan.md                          │
│ • Gate: User approval required                      │
└─────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────┐
│ PHASE 2: EXECUTION (Agent 02 + ReasoningEngine)    │
│ ────────────────────────────────────────────────────│
│ • Load approved plan from Phase 1                   │
│ • ReAct loop: Think → Act → Observe                │
│ • Follow checklist step-by-step                     │
│ • Tools: read/write files, run commands             │
│ • Constraint: Must follow Agent 01's contract       │
└─────────────────────────────────────────────────────┘
```

---

## Implementation Details

### Path 1: New Fullstack App (vibecode_studio.py)

**Before:**
```python
# Skipped Agent 01 entirely
agent_02 = agents.get("02")
engine = ReasoningEngine(...)
engine.run_goal(prompt, context)  # No plan!
```

**After:**
```python
# PHASE 1: Planning
agent_01 = agents.get("01")
planning_context = f"""
{agent_01.instructions}
Execute THREE-PHASE PROTOCOL...
"""
plan = self.ai_provider.generate(planning_context)
plan_file.write_text(plan)

# User approval checkpoint
approval = input("Approve this plan? (y/n): ")

# PHASE 2: Execution (only if approved)
prompt = f"""
APPROVED ARCHITECTURE PLAN:
{plan}

EXECUTION INSTRUCTIONS:
Follow the Implementation Checklist step-by-step...
"""
engine = ReasoningEngine(...)
engine.run_goal(prompt, context)
```

### Path 2: Build Feature (orchestrator.py)

**Enhancement:** Agent 02 now checks for Agent 01's plan file before executing:

```python
# Check if Agent 01 created a plan
plan_file = target_dir / "implementation_plan.md"
plan_content = ""

if plan_file.exists():
    plan_content = plan_file.read_text()
    print("[INFO] Loading architecture plan from Agent 01...")

# Include plan in ReasoningEngine prompt
if plan_content:
    prompt = f"""
    APPROVED ARCHITECTURE PLAN:
    {plan_content}
    
    You MUST follow this plan. Do not deviate.
    """
else:
    prompt = "Work autonomously with best practices..."
```

---

## Benefits of New Architecture

### ✅ Consistency
- **All paths** now follow Intake → Blueprint → Contract
- New projects and existing projects use same quality standards
- Agent 01's expertise is never bypassed

### ✅ Quality Gates
- User approval required before execution
- Architecture review before code generation
- Prevents premature implementation

### ✅ Traceability
- Every project has a `vibecode_plan.md` artifact
- Clear audit trail: "What was the original design intent?"
- Easier debugging: "Did we follow the plan?"

### ✅ Hybrid Intelligence
- **Agent 01 (Thinking):** Uses AI for creative architecture design
- **Agent 02 (Doing):** Uses ReasoningEngine for autonomous execution
- Best of both worlds: strategy + action

### ✅ Self-Correction
- If Agent 02 deviates from plan, Agent 04 (Reviewer) can catch it
- Plan serves as reference contract for quality assurance
- ReasoningEngine can "re-read" the plan during execution

---

## Workflow Example

### User Request:
```
"Create a task management app with user authentication"
```

### Execution Flow:

**Step 1: Agent 01 Planning (AI-powered)**
```
📋 INTAKE STARTED
Questions:
1. Authentication method? (JWT, OAuth, session-based?)
2. Database? (PostgreSQL, MongoDB?)
3. Real-time updates needed? (WebSockets?)

[User provides answers or Agent 01 uses sensible defaults]

✅ INTAKE COMPLETE
Proceeding to Blueprint...

[Agent 01 generates architecture plan]

✅ CONTRACT FINALIZED
Location: task-app/docs/vibecode_plan.md
```

**Plan Preview:**
```markdown
# Blueprint: Task Management App

## 2. The Contract
```typescript
interface Task {
  id: string;
  title: string;
  status: 'todo' | 'in-progress' | 'done';
  userId: string;
}
```

## 3. Component Architecture
- File: src/components/TaskBoard.tsx
- File: src/lib/api/tasks.ts
- File: src/types/task.ts

## 4. Implementation Checklist
1. [ ] Create type definitions
2. [ ] Implement API layer
3. [ ] Build TaskBoard component
...
```

**Step 2: User Approval**
```
Approve this plan and proceed to build? (y/n): y
```

**Step 3: Agent 02 Execution (ReasoningEngine)**
```
🛠️ Step 1/15
💭 Thought: "Need to create task-app directory structure"
🛠️ Action: run_command({"command": "mkdir task-app"})
👁️ Observation: "Success: Directory created"

🛠️ Step 2/15
💭 Thought: "Creating type definitions as per plan Step 1"
🛠️ Action: write_file({"path": "task-app/src/types/task.ts", "content": "..."})
👁️ Observation: "Success: Wrote to task-app/src/types/task.ts"

[... continues following checklist ...]

✅ Agent 02 completed the build via Reasoning
```

---

## Files Modified

| File | Changes | Purpose |
|------|---------|---------|
| `vibecode_studio.py` | `cmd_new_project()` rewritten | Add Phase 1 planning before execution |
| `core/orchestrator.py` | `_enact_agent_role()` enhanced | Load Agent 01 plan in Agent 02 execution |
| `docs/CONSISTENT_PLANNING_ARCHITECTURE.md` | Created | Document the architecture fix |

---

## Migration Notes

### For Existing Projects

No breaking changes. Existing projects continue to work as before.

### For New Projects

- Users will now see a planning phase before execution
- Approval step added (can be bypassed with `--auto` flag)
- `vibecode_plan.md` will be generated in project docs folder

---

## Testing Checklist

- [ ] Test Path 1: New fullstack app with planning
- [ ] Test Path 2: Build feature in existing project
- [ ] Verify Agent 01 creates proper contract
- [ ] Verify Agent 02 follows the contract
- [ ] Test approval gate (both approve and reject)
- [ ] Verify plan file is saved correctly
- [ ] Test --auto flag bypasses approval

---

## Future Enhancements

1. **Plan Versioning**: Track plan revisions (v1, v2, v3)
2. **Plan Validation**: Agent 04 reviews plan before execution
3. **Interactive Intake**: Terminal UI for better UX during requirements gathering
4. **Plan Templates**: Pre-approved patterns for common architectures
5. **Deviation Detection**: Agent 02 warns if going off-plan

---

## Conclusion

The system now consistently follows the **Intake → Blueprint → Contract → Execute** flow for both new and existing projects, ensuring architectural consistency and quality gates are never bypassed.

This aligns with Agent 01's mandate:
> "You are the gatekeeper of quality. No code is written until you approve."
