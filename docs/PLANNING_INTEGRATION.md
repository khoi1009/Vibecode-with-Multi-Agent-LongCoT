# Planning with Files Integration

## Overview

Integrated Manus-style planning pattern into Vibecode based on [planning-with-files](https://github.com/OthmanAdi/planning-with-files).

**Why:** Manus (acquired by Meta for $2B) proved that persistent file-based planning prevents goal drift in long-running agent tasks.

## Changes Made

### 1. Agent 01 (Planner) - Updated ✅

**File:** `agents/01_planner.md`

**Added Section 0:** "Planning with Files (Manus Pattern) - MANDATORY"

**Key Changes:**
- MUST create `task_plan.md` before any planning work
- Read `task_plan.md` before architecture decisions
- Log all errors with timestamps
- Use 3-file pattern for all complex tasks

### 2. Created Skill ✅

**File:** `skills/planning-with-files/SKILL.md`

**Purpose:** 
- Auto-activates for complex tasks
- Provides templates for task_plan.md and notes.md
- Enforces Manus principles across all agents

### 3. Skill Loader - Already Compatible ✅

**File:** `core/skill_loader.py`

**Status:** Already has `planning` skill affinity for Agent 01
- Will auto-load planning-with-files for Agent 01
- Other agents can reference via skill system

## The 3-File Pattern

Every complex task now creates:

```
task_plan.md      → Phases, decisions, errors, progress
notes.md          → Research, findings, architecture notes
[deliverable].md  → Final output (blueprint, contract, etc.)
```

## Integration Points

### Agent 00 (Auditor)
- Reviews `task_plan.md` for completeness
- Checks error logging consistency

### Agent 01 (Planner) ✅ UPDATED
- **MUST** create `task_plan.md` first
- Updates phases after each step
- Logs architecture decisions

### Agent 02 (Coder)
- Reads `task_plan.md` for implementation guidance
- Can reference `notes.md` for context

### Agent 07 (Autofix)
- Logs errors to `task_plan.md`
- Tracks resolution attempts

### All Agents
- Read `task_plan.md` before major decisions
- Prevents "lost in the middle" after 50+ tool calls

## Benefits

### 1. Prevents Goal Drift
After 50+ tool calls, agents forget original goals. Reading `task_plan.md` keeps goals in attention window.

### 2. Error Persistence
Agents learn from past mistakes logged in task_plan.md:
```markdown
## Errors Encountered
- [2026-01-07] AuthStrategyConflict: JWT + Session → Chose JWT
- [2026-01-07] DBMismatch: PostgreSQL + MongoDB → Standardized on PostgreSQL
```

### 3. Agent Communication
All agents can read shared `task_plan.md` to understand project state.

### 4. Audit Trail
Every decision and error is logged with rationale.

## Testing

To test integration:

```bash
# Agent 01 should auto-create task_plan.md
python vibecode_studio.py --prompt "Build a SaaS app with user authentication" --agent 01

# Check for task_plan.md creation
cat task_plan.md

# Verify phases tracked with checkboxes
grep "\[x\]" task_plan.md
```

## Example task_plan.md

```markdown
# Task Plan: SaaS Authentication System

## Goal
Design authentication architecture for multi-tenant SaaS application.

## Phases
- [x] Phase 1: Requirements Intake ✓
- [x] Phase 2: Tech Stack Selection ✓
- [ ] Phase 3: Architecture Blueprint (CURRENT)
- [ ] Phase 4: Security Review
- [ ] Phase 5: Contract Handoff to Agent 02

## Key Questions
1. Multi-tenancy model? → Decided: Schema-per-tenant
2. Auth provider? → Decided: Supabase Auth
3. Session management? → Decided: JWT with refresh tokens

## Decisions Made
- **Tech Stack**: Next.js 14 + Supabase + PostgreSQL
  - Rationale: Built-in auth, RLS for multi-tenancy
- **Architecture**: Clean Architecture with Repository Pattern
  - Rationale: Testability and separation of concerns

## Errors Encountered
- [2026-01-07 14:32] User didn't specify tenant isolation → Asked for clarification
- [2026-01-07 14:45] Considered Clerk vs Supabase → Chose Supabase for cost

## Status
**Currently in Phase 3** - Designing auth flow diagrams
```

## Comparison: Before vs After

### Before (In-Memory Planning)
```
Agent 01: [Thinks] "I'll use Next.js"
[50 tool calls later]
Agent 01: [Forgets] "What was the stack again?"
```

### After (File-Based Planning)
```
Agent 01: Creates task_plan.md
[50 tool calls later]
Agent 01: Reads task_plan.md → "Stack is Next.js + Supabase"
```

## Manus Principles Applied

| Principle | Implementation |
|-----------|----------------|
| Filesystem as memory | task_plan.md stores state |
| Attention manipulation | Re-read before decisions |
| Error persistence | Log in "Errors Encountered" |
| Append-only context | Never modify history |
| Goal tracking | Checkboxes show progress |

## Next Steps

1. **Update Other Agents**: Add task_plan.md reading to Agent 02, 04, 07
2. **Templates**: Create project-specific templates (e.g., task_plan_web_app.md)
3. **Automation**: Auto-generate task_plan.md from LongCoT reasoning
4. **Validation**: Agent 00 checks task_plan.md completeness

## References

- Original Skill: https://github.com/OthmanAdi/planning-with-files
- Manus Blog: https://manus.im/de/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- Meta Acquisition: https://techcrunch.com/2025/12/29/meta-just-bought-manus

---

**Integration Date:** 2026-01-07  
**Status:** ✅ Agent 01 Updated, Skill Created, Ready for Testing
