---
name: planning-with-files
description: "Manus-style persistent planning with markdown files. Use for complex tasks, multi-step projects, when tracking progress, organizing work, or when tasks span 50+ tool calls. Creates task_plan.md for phases, notes.md for research, and deliverable files. Keywords: planning, organize, track progress, multi-step, complex task, research, architecture, design, phases, checklist."
---

# Planning with Files

Work like Manus ($2B Meta acquisition): Use persistent markdown files as your "working memory on disk."

## Quick Start

Before ANY complex task:

1. **Create `task_plan.md`** in the working directory
2. **Define phases** with checkboxes
3. **Update after each phase** - mark [x] and change status
4. **Read before deciding** - refresh goals in attention window

## The 3-File Pattern

For every non-trivial task, create THREE files:

| File | Purpose | When to Update |
|------|---------|----------------|
| `task_plan.md` | Track phases and progress | After each phase |
| `notes.md` | Store findings and research | During research |
| `[deliverable].md` | Final output | At completion |

## Core Workflow

```
Loop 1: Create task_plan.md with goal and phases
Loop 2: Research → save to notes.md → update task_plan.md
Loop 3: Read notes.md → create deliverable → update task_plan.md
Loop 4: Deliver final output
```

### The Loop in Detail

**Before each major action:**
```bash
Read task_plan.md  # Refresh goals in attention window
```

**After each phase:**
```bash
Edit task_plan.md  # Mark [x], update status
```

**When storing information:**
```bash
Write notes.md     # Don't stuff context, store in file
```

## task_plan.md Template

Create this file FIRST for any complex task:

```markdown
# Task Plan: [Brief Description]

## Goal
[One sentence describing the end state]

## Phases
- [ ] Phase 1: Plan and setup
- [ ] Phase 2: Research/gather information
- [ ] Phase 3: Execute/build
- [ ] Phase 4: Review and deliver

## Key Questions
1. [Question to answer]
2. [Question to answer]

## Decisions Made
- [Decision]: [Rationale]

## Errors Encountered
- [Error]: [Resolution]

## Status
**Currently in Phase X** - [What I'm doing now]
```

## notes.md Template

For research and findings:

```markdown
# Notes: [Topic]

## Sources

### Source 1: [Name]
- URL: [link]
- Key points:
  - [Finding]
  - [Finding]

## Synthesized Findings

### [Category]
- [Finding]
- [Finding]
```

## Critical Rules

### 1. ALWAYS Create Plan First
Never start a complex task without `task_plan.md`. This is non-negotiable.

### 2. Read Before Decide
Before any major decision, read the plan file. This keeps goals in your attention window.

### 3. Update After Act
After completing any phase, immediately update the plan file:
- Mark completed phases with [x]
- Update the Status section
- Log any errors encountered

### 4. Store, Don't Stuff
Large outputs go to files, not context. Keep only paths in working memory.

### 5. Log All Errors
Every error goes in the "Errors Encountered" section. This builds knowledge for future tasks.

## When to Use This Pattern

**Use 3-file pattern for:**
- Multi-step tasks (3+ steps)
- Research tasks
- Building/creating something
- Tasks spanning multiple tool calls
- Anything requiring organization

**Skip for:**
- Simple questions
- Single-file edits
- Quick lookups

## Anti-Patterns to Avoid

| Don't | Do Instead |
|-------|------------|
| Use TodoWrite for persistence | Create `task_plan.md` file |
| State goals once and forget | Re-read plan before each decision |
| Hide errors and retry | Log errors to plan file |
| Stuff everything in context | Store large content in files |
| Start executing immediately | Create plan file FIRST |

## The Manus Principles

This skill is based on Manus's context engineering (company acquired by Meta for $2B):

1. **Filesystem as External Memory** - Store in files, not context
2. **Attention Manipulation** - Re-read plan keeps goals visible
3. **Error Persistence** - Log failures for learning
4. **Append-Only Context** - Never modify history (KV-cache optimization)

## Integration with Vibecode

- **Agent 00 (Auditor)**: Reviews task_plan.md for completeness
- **Agent 01 (Planner)**: MUST use task_plan.md for all planning
- **Agent 02 (Coder)**: Reads task_plan.md for implementation guidance
- **Agent 07 (Autofix)**: Logs errors to task_plan.md
- **All Agents**: Read task_plan.md before major decisions

---

**Based on:** [Manus Context Engineering](https://manus.im/de/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
