# Autonomous Development Testing Guide

Complete guide for testing Vibecode's autonomous development capabilities.

---

## 🎯 Overview

This test suite validates the complete **Option 4** workflow:
1. **Phase 1:** Agent 01 creates architecture plan
2. **Approval Gate:** User reviews and approves plan
3. **Phase 2:** Agent 02 executes via ReasoningEngine
4. **Verification:** Automated checks for quality

---

## 🚀 Quick Start

### Method 1: Automated Test Suite (Recommended)

```powershell
# Run predefined test cases
python test_autonomous_dev.py

# Select from menu:
#   1. Simple Todo App
#   2. Blog Platform
#   3. Analytics Dashboard
#   c. Custom project
```

### Method 2: PowerShell Quick Test

```powershell
# One-click test (uses default blog app)
.\quick_test.ps1
```

### Method 3: Headless Mode with Autonomy Flags

```powershell
# Autonomous execution with confidence threshold
python vibecode_studio.py --prompt "Build a todo app" --auto --confidence-threshold 0.8

# With custom audit log location
python vibecode_studio.py --prompt "Build a blog" --auto --audit-log C:\logs\autonomy.log

# Manual approval mode (requires human confirmation)
python vibecode_studio.py --prompt "Build a dashboard" --confidence-threshold 0.75
```

### Method 4: Manual Interactive Testing

```powershell
# Interactive mode
python vibecode_studio.py

# Select Option 4
# Enter project details
# Approve plan when prompted
# Wait for completion
```

---

## 📋 Test Cases Included

### Test Case 1: Simple Todo App
```yaml
Name: test-todo-app
Description: A simple todo app with Next.js. Add a homepage with list of todos, 
             ability to add new todos, mark as complete, and delete. 
             Use Tailwind CSS for styling.
Expected Time: 3-4 minutes
Complexity: Low
```

### Test Case 2: Blog Platform
```yaml
Name: test-blog-platform
Description: A blog platform with Next.js 14. Include homepage listing posts, 
             individual post pages, about page, and contact form. 
             Use Tailwind CSS and add dark mode toggle.
Expected Time: 4-5 minutes
Complexity: Medium
```

### Test Case 3: Analytics Dashboard
```yaml
Name: test-dashboard
Description: A real-time analytics dashboard with Next.js. Include sales chart, 
             user stats, live notifications, and sidebar navigation. 
             Use Recharts for charts and Tailwind for styling.
Expected Time: 5-6 minutes
Complexity: High
```

---

## 🔍 What Gets Tested

### Automated Checks

| Check | Description | Pass Criteria |
|-------|-------------|---------------|
| **Planning Phase** | Agent 01 generates plan | `vibecode_plan.md` created |
| **Execution Phase** | Agent 02 runs ReasoningEngine | Build log shows iterations |
| **Project Structure** | Correct file/folder layout | Essential files exist |
| **Dependencies** | Packages installed | `node_modules/` present |
| **Files Generated** | Source code created | > 10 files in project |
| **Runnable** | Dev server starts | `npm run dev` works |

### Manual Verification

After automated tests, manually check:
1. **Code Quality:** Review generated files for best practices
2. **Type Safety:** Check for TypeScript usage
3. **Styling:** Verify Tailwind CSS is configured
4. **Functionality:** Test features in browser

---

## 📊 Understanding Test Results

### Perfect Score (100%)
```
Status: ✓ ALL TESTS PASSED
Score: 6/6 (100%)

Test Results:
  ✓ Planning Phase
  ✓ Execution Phase
  ✓ Project Structure
  ✓ Dependencies Installed
  ✓ Files Generated
  ✓ Dev Server Runnable
```

### Partial Success (70-99%)
```
Status: ⚠ MOSTLY WORKING
Score: 5/6 (83%)

Test Results:
  ✓ Planning Phase
  ✓ Execution Phase
  ✓ Project Structure
  ✓ Dependencies Installed
  ✓ Files Generated
  ✗ Dev Server Runnable  ← Issue here

Errors Encountered:
  1. Dev server crashed: Port 3000 already in use
```

**Fix:** Kill process on port 3000 or change port

### Failure (<70%)
```
Status: ✗ FAILED
Score: 2/6 (33%)

Errors Encountered:
  1. Gemini API key not configured
  2. Project directory missing
  3. npm install failed
```

**Fix:** Configure API key, check disk space, verify Node.js installation

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. API Key Not Configured
**Symptom:** Planning phase fails immediately

**Fix:**
```powershell
python vibecode_studio.py
# Select Option 9 (Settings)
# Enter your Gemini API key
```

#### 2. Node.js Not Installed
**Symptom:** "npm not found" error

**Fix:**
```powershell
# Download from https://nodejs.org/
# Or use winget:
winget install OpenJS.NodeJS
```

#### 3. Port Already in Use
**Symptom:** Dev server test fails

**Fix:**
```powershell
# Kill process on port 3000
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process

# Or use different port in test
```

#### 4. Timeout Errors
**Symptom:** Test fails after 5 minutes

**Fix:**
```python
# Edit test_autonomous_dev.py, line ~80:
stdout, stderr = process.communicate(input=automated_input, timeout=600)  # Increase to 10 min
```

#### 5. Planning Approval Hangs
**Symptom:** Test waits forever at approval step

**Fix:**
```python
# Automated input already includes 'y' for approval
# If hanging, check that vibecode_studio.py is reading stdin correctly
```

---

## 📈 Benchmarking

### Expected Performance

| Project Complexity | Planning Time | Execution Time | Total Time |
|-------------------|---------------|----------------|------------|
| Simple (Todo) | 20-30s | 2-3 min | ~3-4 min |
| Medium (Blog) | 30-40s | 3-4 min | ~4-5 min |
| Complex (Dashboard) | 40-60s | 4-5 min | ~5-6 min |

### Quality Metrics

**Good Results:**
- ✅ 100% test pass rate
- ✅ < 5 minute total time
- ✅ No errors in build log
- ✅ TypeScript used throughout
- ✅ Tailwind properly configured

**Acceptable Results:**
- ⚠️ 83% test pass rate (1 minor issue)
- ⚠️ 5-7 minute total time
- ⚠️ Minor warnings in build log
- ⚠️ Some JavaScript files (not critical)

**Poor Results:**
- ❌ < 70% test pass rate
- ❌ > 10 minute total time
- ❌ Build errors present
- ❌ Project doesn't run

---

## 🔧 Advanced Testing

### Custom Test Case

```python
# In test_autonomous_dev.py, add to test_cases list:
{
    "name": "my-custom-app",
    "description": """
    Build a real-time chat application with Next.js 14.
    Features:
    - User authentication (JWT)
    - Real-time messaging (Socket.io)
    - Message history (Prisma + SQLite)
    - Emoji support
    - Typing indicators
    - Online status
    Use Tailwind CSS for styling.
    """
}
```

### Stress Test

```powershell
# Run multiple tests in sequence
foreach ($i in 1..5) {
    Write-Host "Test iteration $i"
    python test_autonomous_dev.py
}
```

### Integration with CI/CD

```yaml
# .github/workflows/test-autonomous-dev.yml
name: Autonomous Dev Test
on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run autonomous dev test
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python test_autonomous_dev.py
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: |
            test-*/**
            *_build_log.txt
```

---

## 📝 Test Logs

### Build Log Location
```
{workspace}/{project-name}_build_log.txt
```

### What's in the Log

**Successful build log contains:**
1. Phase 1 markers: "Architecture Planning", "Agent 01"
2. Phase 2 markers: "Autonomous Execution", "Reasoning Engine", "Step N/15"
3. Tool executions: "Action: write_file", "Action: run_command"
4. Success indicators: "Success:", "✓", "completed"

**Failed build log contains:**
5. Error markers: "ERROR", "FAIL", "Exception"
6. Stack traces
7. npm error output

### Example Log Snippet
```
Phase 1: Architecture Planning (Agent 01)...
   + Planning Skills: web-frameworks, frontend-development

--- PLAN PREVIEW ---
# Blueprint: test-blog-app
...

Approve this plan and proceed to build? (y/n): y

Phase 2: Autonomous Execution (Agent 02)...

🧠 Reasoning Engine Activated: Create test-blog-app

--- Step 1/15 ---
💭 Thought: Need to create project directory
🛠️ Action: run_command ({"command": "mkdir test-blog-app"})
👁️ Observation: Exit Code: 0

--- Step 2/15 ---
💭 Thought: Initialize Next.js project
...
```

---

## ✅ Success Checklist

Before considering a test successful, verify:

- [ ] Build log shows no errors
- [ ] `vibecode_plan.md` exists and is comprehensive
- [ ] Project structure matches framework (Next.js/React)
- [ ] `package.json` has correct dependencies
- [ ] `node_modules/` directory exists
- [ ] TypeScript files generated (`.ts`, `.tsx`)
- [ ] Tailwind CSS configured (`tailwind.config.ts`)
- [ ] Dev server starts without errors
- [ ] Browser shows working page at `localhost:3000`
- [ ] No console errors in browser
- [ ] All features from description work

---

## 🎓 Learning from Results

### What to Look For

**In the Plan (`vibecode_plan.md`):**
- Clear type definitions
- Proper component hierarchy
- Sequential implementation steps
- Dependency list with versions
- Risk mitigation strategies

**In the Generated Code:**
- TypeScript throughout
- Proper imports and exports
- React hooks used correctly
- Tailwind classes applied
- Comments explaining complex logic

**In the Execution:**
- Orderly step progression (1→2→3...)
- Smart reasoning ("I need X before Y")
- Error handling ("npm failed, retrying")
- Completion within step limit (< 15 steps)

---

## 🚀 Next Steps After Testing

1. **Review the Plan**
   ```powershell
   cat {project-name}/docs/vibecode_plan.md
   ```

2. **Run the Project**
   ```powershell
   cd {project-name}
   npm run dev
   # Open: http://localhost:3000
   ```

3. **Iterate**
   ```powershell
   # Use Option 2 to add features
   python vibecode_studio.py
   # Select: 2. Build Feature
   # Enter: "Add user authentication"
   ```

4. **Deploy**
   ```powershell
   # Push to GitHub
   git init
   git add .
   git commit -m "Initial commit by Vibecode"
   
   # Deploy to Vercel
   vercel deploy
   ```

---

## 📞 Support

**If tests fail consistently:**
1. Check `test_autonomous_dev.py` output for errors
2. Review `{project-name}_build_log.txt`
3. Verify prerequisites (Node.js, Python, API key)
4. Check disk space and permissions
5. Report issue with logs attached

**Test suite version:** 1.0
**Last updated:** January 5, 2026
**Compatible with:** Vibecode Studio v1.0.0

---

## 🤖 Phase 1: Autonomous Decision-Making (NEW)

### Overview

Vibecode now includes confidence-based autonomous approval for development tasks. The system evaluates task complexity, uses Long CoT analysis for decision confidence, and automatically approves/rejects without human intervention when conditions are met.

### CLI Flags

Three flags control autonomous behavior:

| Flag | Default | Purpose |
|------|---------|---------|
| `--auto` | disabled | Override ALL checks, proceed unconditionally |
| `--confidence-threshold` | 0.8 | Minimum confidence (0.0-1.0) for auto-approval |
| `--audit-log` | `.vibecode/autonomy_audit.log` | Path to decision audit trail |

### Decision Logic

```
IF confidence >= threshold (0.8)
   THEN auto-approve

ELSE IF confidence < 0.5 AND is_destructive_operation
   THEN auto-reject (safety fail-close)

ELSE IF --auto flag enabled
   THEN auto-approve (override)

ELSE
   THEN require manual approval
```

### Example Usage

**Scenario 1: High Confidence (Auto-Approve)**
```powershell
# LongCoT confidence: 0.95 (>= 0.8 threshold)
python vibecode_studio.py --prompt "Add a button component" --confidence-threshold 0.8
# Result: APPROVED automatically, audit logged
```

**Scenario 2: Low Confidence + Destructive (Auto-Reject)**
```powershell
# LongCoT confidence: 0.42, task: code refactoring (destructive)
python vibecode_studio.py --prompt "Refactor database schema"
# Result: REJECTED automatically, manual approval required
```

**Scenario 3: Override with --auto Flag**
```powershell
# LongCoT confidence: 0.55 (below threshold), --auto present
python vibecode_studio.py --prompt "Build dashboard" --auto --confidence-threshold 0.8
# Result: APPROVED despite low confidence (user override)
```

### Audit Log Format

Each decision logged to `.vibecode/autonomy_audit.log` (JSON lines):

```json
{
  "timestamp": "2026-01-07T12:14:30.123456",
  "task_type": "BUILD_FEATURE",
  "confidence": 0.87,
  "approved": true,
  "reason": "High confidence (87%)"
}

{
  "timestamp": "2026-01-07T12:15:45.654321",
  "task_type": "REFACTOR",
  "confidence": 0.42,
  "approved": false,
  "reason": "Low confidence (42%) + destructive op"
}

{
  "timestamp": "2026-01-07T12:16:20.111111",
  "task_type": "BUGFIX",
  "confidence": 0.65,
  "approved": true,
  "reason": "Auto-approve flag enabled"
}
```

### Analyzing Audit Logs

```powershell
# View recent decisions
Get-Content .vibecode/autonomy_audit.log -Tail 10

# Filter approved only
Get-Content .vibecode/autonomy_audit.log |
  ConvertFrom-Json |
  Where-Object { $_.approved -eq $true } |
  Select-Object timestamp, task_type, confidence

# Generate summary
$log = Get-Content .vibecode/autonomy_audit.log | ConvertFrom-Json
$approved_count = ($log | Where-Object { $_.approved }).Count
$total = $log.Count
Write-Host "Approval Rate: $($approved_count / $total * 100)%"
```

### Confidence Scoring

Long CoT evaluates confidence based on:

1. **Task Complexity** - Simple tasks score higher
2. **Codebase Clarity** - Well-structured code → higher confidence
3. **Plan Completeness** - Detailed plans → higher confidence
4. **Error Recovery** - Fewer errors in reasoning → higher confidence
5. **Precedent** - Similar tasks already completed → higher confidence

### Recommended Thresholds

| Use Case | Threshold | Notes |
|----------|-----------|-------|
| Development/Testing | 0.75-0.8 | Accept moderate risk |
| Production CI/CD | 0.85-0.9 | Conservative, minimal risk |
| Critical Infrastructure | 0.95+ | Extreme caution |
| Local Experimentation | 0.5-0.6 | Fast iteration |

### Disabling Autonomy

To require manual approval for all tasks:

```powershell
# Don't use --auto, set threshold to 1.0
python vibecode_studio.py --prompt "Build feature" --confidence-threshold 1.0
# Result: ALL tasks require manual confirmation
```

### Best Practices

1. **Start Conservative** - Use `--confidence-threshold 0.85` initially
2. **Monitor Audit Logs** - Review decisions regularly
3. **Adjust Threshold** - Lower for trusted tasks, raise for risky ones
4. **Use --auto Sparingly** - Override only when you're certain
5. **Archive Logs** - Keep audit trail for compliance

### Troubleshooting

**Q: Tasks always rejected despite high confidence?**
- Check if task is marked as "destructive" (code changes)
- Verify confidence score in audit log
- Try `--confidence-threshold 0.7` to lower bar

**Q: Too many approvals, want more control?**
- Remove `--auto` flag
- Increase `--confidence-threshold` to 0.9+
- Check audit logs for pattern

**Q: Audit log not being created?**
- Verify `.vibecode/` directory exists
- Check file permissions on directory
- Specify explicit `--audit-log` path

---

## 🔒 Safety Features

### Fail-Close Design

Low confidence + destructive operations ALWAYS rejected by default:
- No approval threshold override
- Prevents accidental data loss
- Requires manual review

### Audit Trail

Every decision logged immutably:
- Timestamp per decision
- Reason recorded
- Confidence score documented
- Enables compliance/review

### Reversibility

All autonomy flags affect ONLY approval logic:
- Generated code is identical
- Plans are the same
- Undo/rollback unchanged
- Safe to experiment with thresholds
