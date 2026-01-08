# Agent Reference

## Agent Overview

| ID | Name | Role | Capabilities |
|----|------|------|--------------|
| 00 | Forensic | Security & Analysis | Read-only, pattern detection |
| 01 | Architect | Planning | System design, contracts |
| 02 | Builder | Implementation | Code generation, file ops |
| 03 | Designer | UI/UX | Visual design, CSS |
| 04 | Reviewer | Quality | Code review, static analysis |
| 05 | Integrator | Operations | Deployment, runtime |
| 06 | Operator | Runtime | Process management |
| 07 | Medic | Debugging | Error diagnosis, auto-fix |
| 08 | Shipper | Release | Packaging, publishing |
| 09 | QA | Testing | Test generation, execution |

## Agent Details

### Agent 00: Forensic Scanner

**Purpose**: Security audits, pattern analysis, codebase understanding

**Capabilities**:
- Security vulnerability scanning
- Dependency audit
- Code pattern recognition
- Architecture detection

**Tools Available**: `list_dir`, `read_file`, `search_codebase`

**Output**: Security report, pattern analysis

---

### Agent 01: Architect

**Purpose**: System design, architecture planning, contract creation

**Capabilities**:
- Requirements analysis
- Architecture design
- Interface contracts
- Implementation planning

**Tools Available**: `list_dir`, `read_file`, `write_file`, `search_codebase`

**Output**: Implementation plan (markdown), type definitions

---

### Agent 02: Builder

**Purpose**: Code implementation via ReasoningEngine

**Capabilities**:
- File creation/modification
- Dependency installation
- Command execution
- Git operations

**Tools Available**: All (git, npm, pip, file ops)

**Output**: Source code files, configuration

---

### Agent 09: QA Specialist

**Purpose**: Test generation and execution

**Capabilities**:
- Test file generation
- Test suite execution
- Coverage reporting
- Quality gates

**Tools Available**: `run_tests`, `get_test_coverage`, file ops

**Output**: Test files, QA report

## Agent Communication

Agents communicate through the orchestrator:
1. Output stored in message queue
2. Artifacts registered in registry
3. Next agent receives context
