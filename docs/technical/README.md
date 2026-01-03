# Technical Documentation

**System:** Vibecode Studio with Long CoT  
**Language:** Python 3.11.9  
**Platform:** Windows 11, PowerShell  
**Status:** Production Ready

---

## 📚 Documentation Index

### Installation & Setup

**[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Complete setup guide
- Prerequisites (Python 3.11+, Git)
- Windows, Linux, macOS installation
- Environment setup
- Troubleshooting common issues

### Quick Reference

**[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command cheatsheet
- Common commands (start, scan, test)
- Agent shortcuts
- Configuration options
- API reference

---

## 🛠️ System Architecture

### Core Components

```
vibecode_studio.py (entry point)
├── core/
│   ├── orchestrator.py (workflow coordinator)
│   ├── longcot_scanner.py (Long CoT analyzer)
│   ├── intent_parser.py (command parser)
│   └── skill_loader.py (plugin system)
├── agents/
│   ├── 00_auditor.md (initial assessment)
│   ├── 01_planner.md (task planning)
│   ├── 02_coder.md (implementation)
│   ├── 03_ui_premium.md (UI/UX)
│   ├── 04_reviewer.md (code review)
│   ├── 05_apply.md (deployment)
│   ├── 06_runtime.md (execution)
│   ├── 07_autofix.md (error correction)
│   └── 08_export.md (artifact export)
└── skills/ (33 domain-specific skills)
```

### Long CoT Integration

**File:** `core/longcot_scanner.py` (854 lines)  
**Purpose:** Hierarchical reasoning engine

**Key Features:**
- **Tree-of-Thought:** 4-phase reasoning (architecture → modules → paths → reflection)
- **Process Reward Model:** Step-by-step validation
- **Reflection:** 2 self-correction cycles
- **Backtracking:** ReST-MCTS* approach (1 backtrack observed)

**Integration Points:**
1. **Orchestrator Init:** Automatic scan on startup (existing projects only)
2. **Confidence Gating:** LOW (<50%), MEDIUM (50-79%), HIGH (≥80%)
3. **Agent Context:** Rich context with architecture, modules, critical paths
4. **Status API:** Real-time confidence and insights

---

## 🚀 Getting Started

### Installation (5 minutes)

**Windows (PowerShell):**
```powershell
# Clone repository
git clone https://github.com/yourusername/vibecode.git
cd vibecode

# Run installer
.\install.ps1

# Expected output:
# ✅ Python 3.11.9 detected
# ✅ Dependencies installed
# ✅ Workspace configured
```

**Linux/macOS (Bash):**
```bash
# Clone repository
git clone https://github.com/yourusername/vibecode.git
cd vibecode

# Run installer
chmod +x install.sh
./install.sh

# Expected output:
# ✅ Python 3.11+ detected
# ✅ Dependencies installed
# ✅ Workspace configured
```

### First Run (1 minute)

```bash
# Start Vibecode
python vibecode_studio.py

# Expected output:
# 🔍 Running Long CoT scan... (if existing project)
# ✅ Long CoT scan completed with 98% confidence
# 🎯 Orchestrator initialized
# 💬 Type your request...
```

### Validate Installation (1 minute)

```bash
# Run integration test
python test_longcot_integration.py

# Expected output:
# ✅ 8/8 checks passed
# 🎉 ALL TESTS PASSED!
```

---

## 📊 Configuration

### Environment Variables

```bash
# API Keys (optional for skills)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Long CoT Settings
LONGCOT_ENABLED=true
LONGCOT_MIN_CONFIDENCE=70
LONGCOT_CACHE_DIR=.vibecode/longcot/

# Orchestrator Settings
MAX_AGENTS=9
AUTO_FIX=true
VERBOSE=false
```

### Configuration Files

**pyproject.toml** - Project metadata
```toml
[project]
name = "vibecode-studio"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "anthropic>=0.21.3",
    "openai>=1.0.0",
    # ... see file for complete list
]
```

**requirements.txt** - Python dependencies
```
anthropic>=0.21.3
openai>=1.0.0
requests>=2.31.0
gitpython>=3.1.0
# ... see file for complete list
```

---

## 🔧 API Reference

### Orchestrator API

```python
from core.orchestrator import Orchestrator

# Initialize (runs Long CoT scan automatically)
orchestrator = Orchestrator(workspace_path="/path/to/project")

# Execute task
result = orchestrator.execute_pipeline(
    user_intent="Add login feature",
    skill_name="backend-development"
)

# Get status
status = orchestrator.get_status()
print(f"Confidence: {status['longcot']['confidence']}")
# Output: Confidence: 98.0
```

### Long CoT Scanner API

```python
from core.longcot_scanner import LongCoTScanner

# Initialize scanner
scanner = LongCoTScanner(workspace_path="/path/to/project")

# Run analysis
results = scanner.scan_with_longcot()

# Extract insights
architecture = results['workspace']['architecture']  # e.g., "multi_agent_system"
confidence = results['statistics']['avg_confidence']  # e.g., 0.98
modules = results['workspace']['modules_analyzed']  # e.g., 2

# Save reports
# Automatically saved to .vibecode/longcot/scan_*.json and scan_*.md
```

### Intent Parser API

```python
from core.intent_parser import IntentParser

# Parse user command
parser = IntentParser()
intent = parser.parse("add login with JWT")

# Output:
# {
#     "action": "add",
#     "feature": "login",
#     "details": ["JWT authentication"],
#     "suggested_skill": "backend-development"
# }
```

---

## 🧩 Skills System

### Available Skills (33 total)

**Backend Development:**
- backend-development
- better-auth
- databases
- payment-integration

**Frontend Development:**
- frontend-development
- ui-styling
- ui-ux-pro-max
- threejs

**Development Tools:**
- code-review
- debugging
- devops
- chrome-devtools

**AI & Research:**
- ai-artist
- ai-multimodal
- claude-code
- research

**See [skills/](../../skills/) for complete list.**

### Using Skills

```python
# Option 1: Auto-route (orchestrator picks skill)
orchestrator.execute_pipeline("add login feature")

# Option 2: Explicit skill
orchestrator.execute_pipeline(
    "add login feature",
    skill_name="backend-development"
)

# Option 3: Skill directly (bypasses orchestrator)
from skills.backend_development import execute
result = execute(user_request="add JWT login")
```

---

## 🐛 Troubleshooting

### Issue: Long CoT scan fails
**Symptom:** "Analysis completed with 0% confidence"  
**Cause:** Empty or unrecognized codebase  
**Fix:** Run on existing project with Python files

### Issue: Orchestrator crashes on init
**Symptom:** KeyError: 'longcot'  
**Cause:** Outdated orchestrator.py  
**Fix:** Pull latest from GitHub

### Issue: PowerShell commit fails
**Symptom:** PSReadLine buffer overflow  
**Cause:** Commit message too long (>500 chars)  
**Fix:** Use shorter commit messages (<100 chars)

### Issue: Import errors
**Symptom:** ModuleNotFoundError  
**Cause:** Dependencies not installed  
**Fix:** Run `.\install.ps1` or `pip install -r requirements.txt`

---

## 📚 Related Documentation

### For Developers
- **[Long CoT Technical Docs](../longcot/)** - Deep dive into reasoning engine
- **[Testing Documentation](../testing/)** - Test suites and validation
- **[Product Architecture](PRODUCT_ARCHITECTURE.md)** - System design (if exists in docs/)

### For Investors
- **[Investor Documentation](../investor/)** - Business case and roadmap
- **[Research Expansion Plan](../investor/VIBECODE_RESEARCH_PLAN.md)** - Future strategy

### For Users
- **[Quick Start Guide](../investor/DELIVERY_SUMMARY.md)** - 5-minute overview
- **[Skills Reference](../../skills/agent_skills_spec.md)** - Complete skills catalog

---

## 🔗 External Resources

### Research Papers
- **Tree-of-Thought:** [arxiv.org/abs/2305.10601](https://arxiv.org/abs/2305.10601)
- **Process Reward Model:** [ProcessBench 2024](https://arxiv.org/abs/2406.xxxxx)
- **Reflection:** [arxiv.org/abs/2303.11366](https://arxiv.org/abs/2303.11366)

### Community
- **GitHub:** https://github.com/yourusername/vibecode
- **Documentation:** https://vibecode.readthedocs.io (if deployed)
- **Discord:** https://discord.gg/vibecode (if exists)

---

**Questions?** See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed setup instructions.
