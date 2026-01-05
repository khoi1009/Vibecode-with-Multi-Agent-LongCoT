# Vibecode System Handover Documentation (v2.2 - Antigravity Upgrade)

## 1. Project Overview
**Name**: Vibecode Studio (Anti-Gravity Edition)
**Goal**: An autonomous, skill-aware, multi-agent coding engine capable of creating, refactoring, optimizing, and self-healing software projects.
**Core Philosophy**: "Reason & Act" - No random generation or static templates. Agents use a cognitive loop (Think -> Act -> Observe) to interact with the filesystem dynamically.

## 2. Core Architecture Components

### A. Reasoning Engine (`core/reasoning_engine.py`) [NEW]
The new cognitive core of the system, replacing static templates.
*   **Mechanism**: Implements a ReAct (Reason+Act) Loop.
*   **Process**:
    1.  **Think**: Analyzes the current state and goal.
    2.  **Act**: Selects a tool (`read_file`, `write_file`, `run_command`, `list_dir`).
    3.  **Observe**: Reads tool output and refines the plan.
*   **Context Awareness**:
    *   **Agent Persona**: Adopts the specific identity (e.g., "Agent 02 Builder") including strict coding standards.
    *   **Skill Injection**: Automatically loads full content (docs + scripts) from the `./skills` directory based on the user's query (e.g., loading `react-query` patterns for a frontend task).

### B. The Orchestrator (`core/orchestrator.py`)
The central brain managing agent pipelines.
*   **Updated Logic**:
    *   **Agent 02 (Builder)**: Now uses the `ReasoningEngine` to "invent" solutions rather than calling `UniversalGenerator`.
*   **Pipelines**:
    *   **New Build**: `Agent 01 (Plan)` -> `ReasoningEngine (Dynamic Build)` -> `Agent 09 (Verify)`
    *   **Self-Healing**: `Agent 05` monitors runtime -> `Diagnostician` analyzes error -> `ReasoningEngine` applies fix.

### C. Skill Synapse (`core/skill_loader.py`)
A plugin system that injects "Expert Knowledge" at runtime.
*   **Integration**: The `ReasoningEngine` is fed the "Skill Context" (e.g., documentation for `better-auth`) so it knows *how* to use the libraries it decides to install.

### D. Universal Generator (`core/universal_generator.py`) [DEPRECATED]
*   Legacy template engine.
*   Now only used for "Basic" complexity tasks or as a fallback. "Advanced" tasks use the Reasoning Engine.

## 3. Key Workflows & Commands

### Interactive Autonomous Mode
`python vibecode_studio.py`

**New Feature: Option 4 (Scaffold New Fullstack App)**
*   **Full Autonomy**: The agent has permission to run shell commands (`npm install`, `git init`).
*   **Workflow**:
    1.  User enters project name/description.
    2.  System loads **Agent 02** persona.
    3.  System scans for relevant **Skills** and injects them.
    4.  Agent autonomously builds the folder structure, installs dependencies, and writes code.

**Examples:**

1.  **Antigravity Build (Reasoning Mode)**:
    ```bash
    python vibecode_studio.py --prompt "create a file called demo.txt with hello world" --auto
    ```
    *   **Thought**: "I need to file `demo.txt`."
    *   **Action**: `write_file('demo.txt', 'hello world')`
    *   **Observation**: "Success."
    *   **Result**: File created dynamically.

2.  **Full Project Construction**:
    ```bash
    python vibecode_studio.py --prompt "build a simple express server" --auto
    ```
    *   The agent will:
        1.  Initialize `package.json`.
        2.  Run `npm install express`.
        3.  Create `server.js`.
        4.  Verify it runs.

## 4. Modified Files Manifest
*   **`core/reasoning_engine.py`**: [NEW] The ReAct loop implementation.
*   **`core/orchestrator.py`**: Updated Agent 02 to use `ReasoningEngine` with Context Injection.
*   **`vibecode_studio.py`**: Entry point for the new autonomous mode (Option 4).
*   **`core/universal_generator.py`**: Retained for backward compatibility.

## 5. Known Capabilities & Limits
*   **True Autonomy**: Can navigate the filesystem and make decisions based on what it finds.
*   **Tool Use**: Can run any shell command (safeguarded) and read/write any file.
*   **Self-Correction**: If a command fails (e.g., "npm not found"), the agent "observes" the error and can try to fix it (e.g., "download node") in future iterations.
*   **Expert Context**: Uses your paid `agents` and `skills` to guide generation.

**To resume work**: Provide this document to the AI assistant to instantly restore deep context of the system's new reasoning capabilities.
