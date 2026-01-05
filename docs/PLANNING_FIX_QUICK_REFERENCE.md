# Quick Reference: Consistent Planning Fix

## What Changed?

**Path 1 (New Fullstack App)** now includes Agent 01 planning phase before execution.

---

## Modified Files

1. **vibecode_studio.py** - `cmd_new_project()` method
2. **core/orchestrator.py** - `_enact_agent_role()` method for Agent 02

---

## New Workflow

### For Users:

**Before:**
```bash
python vibecode_studio.py
> Choose option 4: New Fullstack App
> Enter name and description
> [Builds immediately without plan]
```

**After:**
```bash
python vibecode_studio.py
> Choose option 4: New Fullstack App
> Enter name and description
> [Phase 1: Agent 01 creates plan]
> [Shows plan preview]
> Approve plan? (y/n): y
> [Phase 2: Agent 02 executes plan]
```

---

## For Developers:

### New Execution Flow

```python
# Phase 1: Planning
agent_01 = agents.get("01")
planning_context = f"{agent_01.instructions}\n\nTask: {desc}"
plan = ai_provider.generate(planning_context)
save_plan(plan)

# Approval gate
if not approved:
    return

# Phase 2: Execution
agent_02 = agents.get("02")
prompt = f"APPROVED PLAN:\n{plan}\n\nFollow checklist step-by-step"
engine = ReasoningEngine(workspace, ai_provider)
engine.run_goal(prompt, context)
```

---

## Benefits

✅ **All projects** now get architecture planning  
✅ **User approval** required before building  
✅ **Contract enforcement** - Agent 02 follows Agent 01's plan  
✅ **Traceability** - Plan saved in `project/docs/vibecode_plan.md`  

---

## Testing

```bash
# Test the new flow
python vibecode_studio.py

# Select option 4
# Enter: name="test-app", desc="Simple todo app"
# Verify: Plan is generated and shown
# Approve with 'y'
# Verify: Agent 02 follows the plan
# Check: test-app/docs/vibecode_plan.md exists
```

---

## Bypassing Approval (Automation)

```bash
# For CI/CD or automated workflows
python vibecode_studio.py --prompt "create blog app" --auto
# The --auto flag will automatically approve plans
```

---

## Architecture Compliance

Both paths now follow Agent 01's protocol from `agents/01_planner.md`:

1. ✅ **INTAKE** - Requirements gathering
2. ✅ **BLUEPRINT** - Architecture design  
3. ✅ **CONTRACT** - Implementation plan
4. ✅ **APPROVAL** - User gate
5. ✅ **EXECUTION** - Agent 02 follows contract

---

## Documentation

- Full details: [docs/CONSISTENT_PLANNING_ARCHITECTURE.md](CONSISTENT_PLANNING_ARCHITECTURE.md)
- Visual guide: [docs/PLANNING_ARCHITECTURE_VISUAL.md](PLANNING_ARCHITECTURE_VISUAL.md)
- Agent protocol: [agents/01_planner.md](../agents/01_planner.md)

---

## Rollback

If issues occur, revert these commits:
- `vibecode_studio.py` - Restore old `cmd_new_project()`
- `core/orchestrator.py` - Restore old `_enact_agent_role()` for Agent 02

---

**Implementation Date:** January 5, 2026  
**Status:** ✅ Production Ready
