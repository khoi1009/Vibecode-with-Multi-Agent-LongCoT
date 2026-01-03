# Vibecode System Handover Documentation (v2.0)

## 1. Project Overview
**Name**: Vibecode Studio (Anti-Gravity Edition)
**Goal**: An autonomous, skill-aware, multi-agent coding engine capable of creating, refactoring, optimizing, and self-healing software projects.
**Core Philosophy**: "Strict Protocol" - No random generation. Agents follow a defined chain of command (Architect -> Builder -> QA -> Supervisor).

## 2. Core Architecture Components

### A. Universal Generator (`core/universal_generator.py`)
The engine that adapts to user intent.
*   **Dynamic Complexity**:
    *   *Basic*: Single Python Scripts.
    *   *Intermediate*: Flask Apps with Auth.
    *   *Advanced*: Full-Stack (FastAPI + React) Distributed Systems.
*   **Zero-Dependency Frontend**: For Advanced projects, it generates a "No-Build" React architecture (using CDN-injected Babel/Tailwind) that runs immediately without Node.js.
*   **Name Sanitization**: Automatically strips quotes and stop-words ("refactor", "build", "optimize") to determine the correct project directory (e.g., "refactor modern_logistics" -> `modern_logistics`).

### B. Skill Synapse (`core/skill_loader.py`)
A plugin system that injects "Expert Knowledge" at runtime.
*   **Mechanism**: Scans `./skills` directory. Matches keywords in prompt (e.g., "secure" -> `better-auth`).
*   **Injection**:
    *   *Python*: Adds dependencies (`python-jose`) and middleware (`OAuth2PasswordBearer`).
    *   *React*: Adds libraries (`threejs`, `framer-motion`) and UI patterns.

### C. The Orchestrator (`core/orchestrator.py`)
The central brain managing agent pipelines.
*   **Universal Task Parsing**:
    1.  **New Build**: `Agent 01 (Plan) -> Agent 02 (Build) -> Agent 09 (Verify)`
    2.  **Refactor** (`/refactor`): `Agent 01 (Scan) -> Agent 04 (Review) -> Agent 02 (Fix)`
    3.  **Optimize** (`/optimize`): `Agent 00 (Profile) -> Agent 02 (Cache) -> Agent 09 (Benchmark)`
    4.  **Debug** (`/fix`): `Agent 00 (Forensic) -> Agent 02 (Patch) -> Agent 05 (Test)`
*   **Self-Healing Runtime (Agent 05)**:
    *   Launches the app via `subprocess`.
    *   Monitors `stderr` for crashes (e.g., `ModuleNotFoundError`).
    *   **Autofix Loop**: Identifies missing libs -> Installs them -> Restarts app automatically.

## 3. Key Workflows & Commands

### Interactive Autonomous Mode
`python vibecode_studio.py --prompt "<QUERY>" --auto`

**Examples:**
1.  **Create New Product**:
    ```bash
    python vibecode_studio.py --prompt "build a modern logistics platform" --auto
    ```
    *Result*: Generates backend/frontend in `modern_logistics`, launches server on port 8000.

2.  **Refactor Existing Code**:
    ```bash
    python vibecode_studio.py --prompt "refactor modern_logistics code" --auto
    ```
    *Result*: Analyzes `modern_logistics`, creates `refactor_plan.md`, applies changes.

3.  **Optimize Performance**:
    ```bash
    python vibecode_studio.py --prompt "optimize modern_logistics" --auto
    ```
    *Result*: Creates `performance_audit.log`, simulates caching patches.

## 4. Modified Files Manifest
*   **`vibecode_studio.py`**: Added `--auto` flag, integrated Orchestrator loop.
*   **`core/orchestrator.py`**:
    *   Implemented `_enact_agent_role` with branching logic for task types.
    *   Added `_run_with_healing` and `_autofix_error` methods.
*   **`core/universal_generator.py`**:
    *   Added `_generate_advanced` (Zero-Dependency + Skill Injection).
    *   Updated `_extract_project_name` with extended stop-word list.
*   **`demo_build.py`**: Initial proof-of-concept script.

## 5. Known Capabilities & Limits
*   **Frontend**: React runs via CDN (No `npm` needed). Ideal for demos.
*   **Skills**: Currently supports `better-auth`, `threejs`, `databases` (simulated injection).
*   **Healing**: Can fix missing modules and port conflicts.

**To resume work**: Provide this document to the AI assistant to instantly restore deep context of the system's capabilities.
