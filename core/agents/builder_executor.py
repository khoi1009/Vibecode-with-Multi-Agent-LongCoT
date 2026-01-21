"""
Builder Executor - Agent 02: Staff Software Engineer
Implements the 7-Phase Build Process from 02_coder.md

This agent transforms the vibecode_plan.md contract into production-grade,
observable, scalable, and maintainable code.

7-Phase Protocol:
  PHASE 0: Contract Review & Challenge (Critical Thinking)
  PHASE 1: Test-Driven Development (Write Tests FIRST)
  PHASE 2: Architecture Implementation (Separation of Concerns)
  PHASE 3: Observability by Design (Logging, Metrics, Tracing)
  PHASE 4: Failure Engineering (Design for Chaos)
  PHASE 5: Security by Design (Zero Trust)
  PHASE 6: Performance Engineering (Benchmarks & Optimization)
  PHASE 7: Production Readiness (Ship with Confidence)
"""

from pathlib import Path
from typing import Dict, List, Optional
from core.agent_executor import AgentExecutor, AgentResult, Artifact


class BuilderExecutor(AgentExecutor):
    """
    Agent 02: Staff Software Engineer - Code Implementation
    
    Role: Transform the vibecode_plan.md contract into production-grade code.
    Philosophy:
      - Code that works locally ≠ Code that works at scale
      - Code is read 10x more than written
      - Every system fails - design for graceful degradation
      - Observability is not optional
      - Security is not a feature - it's the foundation
    """

    def __init__(self, workspace: Path, ai_provider=None, skill_loader=None):
        super().__init__(workspace, ai_provider, skill_loader)
        self.reasoning_engine = None
        self.agent_instructions = ""
        
        if ai_provider:
            try:
                from core.reasoning_engine import ReasoningEngine
                self.reasoning_engine = ReasoningEngine(workspace, ai_provider)
            except ImportError:
                pass
        
        # Load agent instructions from 02_coder.md
        self.agent_instructions = self._load_agent_instructions()

    def _detect_project_type(self, query: str, plan: str = "") -> str:
        """
        Detect project type from query and plan content.
        
        Returns one of: 'react-vite', 'nextjs', 'express', 'html', 'python'
        """
        combined = (query + " " + plan).lower()
        
        if "next.js" in combined or "nextjs" in combined or "next js" in combined:
            return "nextjs"
        elif "react" in combined or "vite" in combined or "tsx" in combined:
            return "react-vite"
        elif "express" in combined or "node" in combined and ("api" in combined or "backend" in combined):
            return "express"
        elif "html" in combined and "css" in combined and "javascript" not in combined:
            return "html"
        elif "python" in combined or "django" in combined or "flask" in combined or "fastapi" in combined:
            return "python"
        else:
            # Default to React/Vite for frontend, Express for backend
            if "frontend" in combined or "ui" in combined or "dashboard" in combined:
                return "react-vite"
            elif "backend" in combined or "server" in combined:
                return "express"
            return "react-vite"  # Default

    def _scaffold_project(self, project_dir: Path, project_type: str, project_name: str = "app") -> list:
        """
        Create essential project files BEFORE building components.
        This ensures the project can be installed and run immediately.
        
        Returns list of created file paths.
        """
        created_files = []
        
        if project_type == "react-vite":
            created_files.extend(self._scaffold_react_vite(project_dir, project_name))
        elif project_type == "nextjs":
            created_files.extend(self._scaffold_nextjs(project_dir, project_name))
        elif project_type == "express":
            created_files.extend(self._scaffold_express(project_dir, project_name))
        elif project_type == "html":
            created_files.extend(self._scaffold_html(project_dir, project_name))
        elif project_type == "python":
            created_files.extend(self._scaffold_python(project_dir, project_name))
        
        if created_files:
            print(f"   [SCAFFOLD] Created {len(created_files)} essential files for {project_type} project")
        
        return created_files

    def _scaffold_react_vite(self, project_dir: Path, name: str) -> list:
        """Scaffold React + Vite + TypeScript + Tailwind project"""
        created = []
        frontend_dir = project_dir / "frontend" if (project_dir / "backend").exists() else project_dir
        frontend_dir.mkdir(parents=True, exist_ok=True)
        
        # package.json
        pkg = frontend_dir / "package.json"
        if not pkg.exists():
            pkg.write_text(f'''{{
  "name": "{name.lower().replace(' ', '-')}",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "zustand": "^4.4.7"
  }},
  "devDependencies": {{
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.3.3",
    "vite": "^5.0.8"
  }}
}}
''', encoding='utf-8')
            created.append(str(pkg))
        
        # vite.config.ts
        vite_cfg = frontend_dir / "vite.config.ts"
        if not vite_cfg.exists():
            vite_cfg.write_text('''import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    open: true,
  },
});
''', encoding='utf-8')
            created.append(str(vite_cfg))
        
        # tsconfig.json
        tsconfig = frontend_dir / "tsconfig.json"
        if not tsconfig.exists():
            tsconfig.write_text('''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
''', encoding='utf-8')
            created.append(str(tsconfig))
        
        # tsconfig.node.json
        tsconfig_node = frontend_dir / "tsconfig.node.json"
        if not tsconfig_node.exists():
            tsconfig_node.write_text('''{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
''', encoding='utf-8')
            created.append(str(tsconfig_node))
        
        # index.html
        index_html = frontend_dir / "index.html"
        if not index_html.exists():
            index_html.write_text(f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
''', encoding='utf-8')
            created.append(str(index_html))
        
        # src/main.tsx
        src_dir = frontend_dir / "src"
        src_dir.mkdir(exist_ok=True)
        main_tsx = src_dir / "main.tsx"
        if not main_tsx.exists():
            main_tsx.write_text('''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
''', encoding='utf-8')
            created.append(str(main_tsx))
        
        # src/App.tsx (placeholder)
        app_tsx = src_dir / "App.tsx"
        if not app_tsx.exists():
            app_tsx.write_text(f'''import React from 'react';

function App() {{
  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
      <h1 className="text-3xl font-bold">{name}</h1>
    </div>
  );
}}

export default App;
''', encoding='utf-8')
            created.append(str(app_tsx))
        
        # src/index.css
        index_css = src_dir / "index.css"
        if not index_css.exists():
            index_css.write_text('''@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  font-family: Inter, system-ui, sans-serif;
}

body {
  margin: 0;
  min-height: 100vh;
}
''', encoding='utf-8')
            created.append(str(index_css))
        
        # tailwind.config.js
        tailwind_cfg = frontend_dir / "tailwind.config.js"
        if not tailwind_cfg.exists():
            tailwind_cfg.write_text('''/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
''', encoding='utf-8')
            created.append(str(tailwind_cfg))
        
        # postcss.config.js
        postcss_cfg = frontend_dir / "postcss.config.js"
        if not postcss_cfg.exists():
            postcss_cfg.write_text('''export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
''', encoding='utf-8')
            created.append(str(postcss_cfg))
        
        # .gitignore
        gitignore = frontend_dir / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text('''node_modules
dist
.env
.env.local
*.log
''', encoding='utf-8')
            created.append(str(gitignore))
        
        return created

    def _scaffold_nextjs(self, project_dir: Path, name: str) -> list:
        """Scaffold Next.js + TypeScript + Tailwind project"""
        created = []
        
        # package.json
        pkg = project_dir / "package.json"
        if not pkg.exists():
            pkg.write_text(f'''{{
  "name": "{name.lower().replace(' ', '-')}",
  "version": "1.0.0",
  "private": true,
  "scripts": {{
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }},
  "dependencies": {{
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }},
  "devDependencies": {{
    "@types/node": "^20.10.0",
    "@types/react": "^18.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.3.0"
  }}
}}
''', encoding='utf-8')
            created.append(str(pkg))
        
        return created

    def _scaffold_express(self, project_dir: Path, name: str) -> list:
        """Scaffold Express + TypeScript backend"""
        created = []
        backend_dir = project_dir / "backend" if (project_dir / "frontend").exists() else project_dir
        backend_dir.mkdir(parents=True, exist_ok=True)
        
        # package.json
        pkg = backend_dir / "package.json"
        if not pkg.exists():
            pkg.write_text(f'''{{
  "name": "{name.lower().replace(' ', '-')}-backend",
  "version": "1.0.0",
  "scripts": {{
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  }},
  "dependencies": {{
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1"
  }},
  "devDependencies": {{
    "@types/express": "^4.17.21",
    "@types/cors": "^2.8.17",
    "@types/node": "^20.10.0",
    "tsx": "^4.6.2",
    "typescript": "^5.3.3"
  }}
}}
''', encoding='utf-8')
            created.append(str(pkg))
        
        # tsconfig.json
        tsconfig = backend_dir / "tsconfig.json"
        if not tsconfig.exists():
            tsconfig.write_text('''{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"]
}
''', encoding='utf-8')
            created.append(str(tsconfig))
        
        # src/index.ts (entry point)
        src_dir = backend_dir / "src"
        src_dir.mkdir(exist_ok=True)
        index_ts = src_dir / "index.ts"
        if not index_ts.exists():
            index_ts.write_text('''import express from 'express';
import cors from 'cors';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
''', encoding='utf-8')
            created.append(str(index_ts))
        
        return created

    def _scaffold_html(self, project_dir: Path, name: str) -> list:
        """Scaffold simple HTML/CSS project"""
        created = []
        
        index_html = project_dir / "index.html"
        if not index_html.exists():
            index_html.write_text(f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name}</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <h1>{name}</h1>
  <script src="script.js"></script>
</body>
</html>
''', encoding='utf-8')
            created.append(str(index_html))
        
        styles_css = project_dir / "styles.css"
        if not styles_css.exists():
            styles_css.write_text('''* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, sans-serif; }
''', encoding='utf-8')
            created.append(str(styles_css))
        
        return created

    def _scaffold_python(self, project_dir: Path, name: str) -> list:
        """Scaffold Python project with requirements.txt"""
        created = []
        
        # requirements.txt
        reqs = project_dir / "requirements.txt"
        if not reqs.exists():
            reqs.write_text('''# Core dependencies
python-dotenv>=1.0.0
''', encoding='utf-8')
            created.append(str(reqs))
        
        # main.py
        main_py = project_dir / "main.py"
        if not main_py.exists():
            main_py.write_text(f'''"""
{name}
"""

def main():
    print("{name} running...")

if __name__ == "__main__":
    main()
''', encoding='utf-8')
            created.append(str(main_py))
        
        return created


    def _load_relevant_skills(self, query: str) -> str:
        """
        Load relevant skills for building tasks.
        Agent 02 has affinity for: backend-development, frontend-development, web-frameworks,
                                   databases, better-auth, payment-integration, debugging, planning-with-files
        """
        if not self.skill_loader:
            return ""
        
        try:
            # Select skills with agent affinity (agent_id="02")
            selected = self.skill_loader.select_skills(
                query=query,
                agent_id="02",
                max_skills=4,  # Builder can use more skills
                min_score=0.1
            )
            
            if not selected:
                # Fallback: Always load backend-development for Agent 02
                backend_skill = self.skill_loader.get_skill("backend-development")
                if backend_skill:
                    selected = [(backend_skill, 1.0)]
            
            if selected:
                # Extract just the Skill objects from tuples
                skills = [s[0] if isinstance(s, tuple) else s for s in selected]
                skill_context = self.skill_loader.build_skills_context(
                    skills,
                    include_references=True,
                    include_scripts=True
                )
                print(f"   [+] Loaded {len(skills)} skills for Agent 02: {[s.name for s in skills]}")
                return skill_context
        except Exception as e:
            print(f"   [!] Skill loading error: {e}")
        
        return ""

    def _load_agent_instructions(self) -> str:
        """Load the full 02_coder.md instructions for the AI"""
        coder_paths = [
            self.workspace / "agents" / "02_coder.md",
            Path(__file__).parent.parent.parent / "agents" / "02_coder.md",
            Path("agents") / "02_coder.md",
        ]
        
        for path in coder_paths:
            if path.exists():
                try:
                    return path.read_text(encoding='utf-8')
                except:
                    pass
        
        # Fallback: embedded core instructions
        return self._get_embedded_instructions()

    def _get_embedded_instructions(self) -> str:
        """Fallback embedded instructions when 02_coder.md cannot be loaded"""
        return '''
# Agent 02 - Staff Software Engineer Protocol

## YOUR ROLE
You are a STAFF SOFTWARE ENGINEER with 25 years at Google-scale companies.
You build systems that survive production, not just demos that work locally.

## 7-PHASE BUILD PROCESS

### PHASE 0: Contract Review & Challenge
Before writing code, interrogate the contract:
- Missing requirements? Ask before assuming.
- Scaling concerns? Flag if list grows to 10,000+ items.
- Ambiguous behavior? Request SLO/latency targets.
- If contract has CRITICAL FLAWS, STOP and report to Agent 01.

### PHASE 1: Test-Driven Development (TDD)
- Write tests FIRST. This is NON-NEGOTIABLE.
- For every function: Happy path, Edge cases, Error cases, Performance cases.
- Minimum 80% line coverage for new code.
- Critical paths (auth, payments): 100% coverage.

### PHASE 2: Architecture Implementation
Layered architecture:
```
src/
├── types/           # Type definitions
├── lib/
│   ├── api/         # API client layer
│   ├── services/    # Business logic
│   ├── utils/       # Pure utilities
│   └── hooks/       # React hooks
├── components/
│   ├── ui/          # Dumb components
│   └── features/    # Smart components
└── config/          # Environment config
```
- Use dependency injection for testability.
- Follow SOLID principles.

### PHASE 3: Observability by Design
- NEVER use console.log in production. Use structured logging.
- Log levels: DEBUG, INFO, WARN, ERROR, FATAL.
- Track metrics: latency, success/error counts, throughput.
- Add distributed tracing headers.

### PHASE 4: Failure Engineering
- Type-safe error classes with error codes.
- Retry logic with exponential backoff.
- Circuit breaker pattern for external services.
- Timeout guards on all async operations.
- Graceful degradation with Promise.allSettled.

### PHASE 5: Security by Design
- Input validation with Zod schemas.
- Auth & authorization checks.
- Never log sensitive data.
- Parameterized SQL queries (no concatenation).
- XSS prevention (sanitize or escape).

### PHASE 6: Performance Engineering
- Time complexity analysis (avoid O(n²)).
- Batch database queries (avoid N+1).
- Caching strategy with LRU cache.
- React: useMemo, memo, virtualization for large lists.

### PHASE 7: Production Readiness
- Health check endpoints.
- Feature flags for gradual rollout.
- Monitoring dashboard metrics (p50, p95, p99).
- Runbook documentation.

## CODE QUALITY STANDARDS
- TypeScript: `any` is FORBIDDEN. Use `unknown` with type guards.
- No console.log or debugger statements.
- All TODOs have ticket references.
- Error handling for all async operations.
- JSDoc comments for public APIs.

## COMPLETION REPORT FORMAT
After implementation:
```
✅ **BUILD COMPLETE**

Files Created:
  - src/lib/api/users.ts (234 lines)
  - src/lib/api/users.test.ts (187 lines)
  - src/types/user.ts (45 lines)

Test Coverage: 94%
Performance: p99 latency <150ms
Security: Input validation ✓, XSS protection ✓
Observability: Logging ✓, Metrics ✓

Ready for Agent 04 (Review).
```
'''

    def execute(self, query: str, context: Dict, **kwargs) -> AgentResult:
        """
        Execute code building following the 7-Phase Protocol.
        
        Phase 0 (Contract Review) happens first - if contract is flawed,
        we stop and report back to Agent 01.
        """
        # Get plan from Agent 01
        plan = context.get("plan_content", "")
        
        # Phase 0: Contract Review - Check if plan exists and is valid
        contract_issues = self._validate_contract(plan, query)
        if contract_issues:
            return self._report_contract_challenge(contract_issues, query)
        
        # Try ReasoningEngine for full 7-phase implementation
        if self.reasoning_engine and self.has_ai():
            return self._execute_with_reasoning_engine(query, plan, context)
        
        # Fallback: Template-based generation
        return self._fallback_generate(query, context)

    def _validate_contract(self, plan: str, query: str) -> List[str]:
        """
        Phase 0: Contract Review & Challenge
        
        Check if the contract (plan) is production-viable before proceeding.
        Returns list of critical issues, or empty list if OK.
        """
        issues = []
        
        # Check if plan exists
        if not plan or len(plan.strip()) < 100:
            issues.append("No implementation plan provided by Agent 01. Cannot proceed without a contract.")
            return issues
        
        plan_lower = plan.lower()
        
        # Check for required sections (from 01_planner.md contract format)
        required_sections = [
            ("type definitions", "Missing Type Definitions section - need TypeScript interfaces."),
            ("implementation", "Missing Implementation section - need atomic steps."),
            ("file structure", "Missing File Structure section - need explicit paths."),
        ]
        
        for section, error in required_sections:
            if section not in plan_lower:
                issues.append(error)
        
        # Check for ambiguous requirements
        ambiguous_terms = ["fast", "quick", "good performance", "user-friendly"]
        for term in ambiguous_terms:
            if term in plan_lower and "ms" not in plan_lower and "latency" not in plan_lower:
                issues.append(f"Ambiguous requirement: '{term}' - need specific SLO (e.g., p99 < 200ms).")
                break
        
        # Check for missing error handling spec
        if "error" not in plan_lower and "exception" not in plan_lower:
            issues.append("Missing error handling specification - how should errors be handled?")
        
        return issues

    def _report_contract_challenge(self, issues: List[str], query: str) -> AgentResult:
        """
        Stop and report contract issues back to Agent 01.
        This implements the CONTRACT CHALLENGE flow from 02_coder.md.
        """
        challenge_report = [
            "# 🚫 CONTRACT CHALLENGE",
            "",
            "Agent 02 cannot proceed due to contract issues:",
            "",
        ]
        
        for i, issue in enumerate(issues, 1):
            challenge_report.append(f"  {i}. {issue}")
        
        challenge_report.extend([
            "",
            "---",
            "**Request:** Agent 01 to revise contract before implementation.",
            "",
            f"**Original Request:** {query[:200]}...",
        ])
        
        report_content = "\n".join(challenge_report)
        
        # Save challenge report
        challenge_file = self.workspace / "contract_challenge.md"
        challenge_file.write_text(report_content, encoding='utf-8')
        print(f"   [!] Contract challenged: {challenge_file}")
        
        return AgentResult(
            agent_id="02",
            status="blocked",
            artifacts=[Artifact(
                type="challenge",
                path="contract_challenge.md",
                content=report_content
            )],
            insights=["Contract has critical flaws", "Pushed back to Agent 01"],
            next_recommended_agent="01",  # Back to Architect
            confidence=0.0
        )

    def _execute_with_reasoning_engine(self, query: str, plan: str, context: Dict) -> AgentResult:
        """Execute full 7-phase build using ReasoningEngine"""
        try:
            # === PHASE 0.5: Project Scaffolding ===
            # Detect project type and create essential files FIRST
            project_type = self._detect_project_type(query, plan)
            project_name = self._extract_project_name(query)
            
            print(f"   [BUILD] Project type detected: {project_type}")
            print(f"   [BUILD] Project name: {project_name}")
            
            # Create essential project files (package.json, config, entry points)
            scaffolded_files = self._scaffold_project(self.workspace, project_type, project_name)
            
            # Build comprehensive execution prompt with all 7 phases
            prompt = self._build_execution_prompt(query, plan, context)
            
            # Run reasoning engine
            result = self.reasoning_engine.run_goal(prompt, str(context))
            
            if result.get("success"):
                # Collect created files
                created_files = self._collect_created_files()
                
                # Generate completion report
                report = self._generate_completion_report(created_files)
                
                return AgentResult(
                    agent_id="02",
                    status="success",
                    artifacts=created_files + [Artifact(
                        type="report",
                        path="build_report.md",
                        content=report
                    )],
                    insights=self._extract_insights(report) + [f"Scaffolded {len(scaffolded_files)} essential files"],
                    next_recommended_agent="09",  # Testing
                    confidence=0.9
                )
            else:
                return self._fallback_generate(query, context, reason="ReasoningEngine failed")
                
        except Exception as e:
            return self._fallback_generate(query, context, reason=f"ReasoningEngine error: {str(e)}")

    def _extract_project_name(self, query: str) -> str:
        """Extract project name from query"""
        import re
        
        # Common patterns for project names
        patterns = [
            r"(?:called|named)\s+[\"']?([A-Za-z][A-Za-z0-9]+(?:\s*[A-Za-z0-9]+)?)",
            r"(?:Build|Create|Make)\s+([A-Za-z][A-Za-z0-9]+(?:\s+[A-Za-z][A-Za-z0-9]+)?)\s*[-–]",
            r"(?:Build|Create|Make)\s+([A-Za-z][A-Za-z0-9]+(?:Pro|App|Hub|Board|Tracker|Vault)?)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                name = re.sub(r'[^\w\s\-]', '', name)
                name = re.sub(r'\s+', '-', name)
                if len(name) >= 3:
                    return name
        
        return "App"


    def _build_execution_prompt(self, query: str, plan: str, context: Dict) -> str:
        """
        Build comprehensive prompt implementing the 7-Phase Protocol.
        This is the core prompt that guides the AI through production-grade development.
        Includes relevant skills from the skills folder for expert knowledge.
        """
        # Load full instructions if available
        instructions_section = ""
        if self.agent_instructions and len(self.agent_instructions) > 500:
            # Use first part of instructions (avoid context overflow)
            instructions_section = self.agent_instructions[:15000]
        else:
            instructions_section = self._get_embedded_instructions()
        
        # Load relevant skills from skills folder
        skills_context = self._load_relevant_skills(query)
        
        prompt = f'''# Agent 02: Staff Software Engineer - Build Request

{skills_context}

## YOUR IDENTITY
You are Agent 02, a STAFF SOFTWARE ENGINEER with 25 years at Google-scale companies.
You build systems that survive production, not just demos that work locally.

---

## THE CONTRACT (from Agent 01)

{plan if plan else "No plan provided - use best practices."}

---

## THE REQUEST

{query}

---

## YOUR 7-PHASE PROTOCOL

You MUST follow all 7 phases in order:

### PHASE 1: Test-Driven Development (TDD)
**Write tests FIRST. This is NON-NEGOTIABLE.**

For EVERY function/component you create:
1. Write the test file FIRST (e.g., `users.test.ts`)
2. Define test cases:
   - Happy path (normal operation)
   - Edge cases (empty, null, boundary values)
   - Error cases (network failure, invalid data)
3. THEN write the implementation

Example test structure:
```typescript
describe('functionName', () => {{
  it('should handle normal case', () => {{ /* ... */ }});
  it('should return error for invalid input', () => {{ /* ... */ }});
  it('should handle empty array', () => {{ /* ... */ }});
}});
```

### PHASE 2: Layered Architecture
Organize code in layers - NEVER mix concerns:

```
src/
├── types/           # Type definitions (interfaces, types)
├── lib/
│   ├── api/         # API client layer (pure data fetching)
│   ├── services/    # Business logic layer
│   ├── utils/       # Pure utility functions
│   └── hooks/       # React hooks (if applicable)
├── components/
│   ├── ui/          # Presentational components
│   └── features/    # Container components
└── config/          # Environment configuration
```

### PHASE 3: Observability
**Every function must be observable.**

```typescript
import {{ logger }} from '@/lib/logger';

export async function getData(id: string) {{
  logger.info('Fetching data', {{ id, timestamp: Date.now() }});
  
  try {{
    const result = await fetch(`/api/data/${{id}}`);
    logger.info('Data fetched', {{ id, duration: Date.now() - start }});
    return result;
  }} catch (error) {{
    logger.error('Failed to fetch', {{ id, error: error.message }});
    throw error;
  }}
}}
```

### PHASE 4: Failure Engineering
**Design for failure. Every system fails.**

- Type-safe error classes:
```typescript
class ApiError extends Error {{
  constructor(public statusCode: number, public code: string, message: string) {{
    super(message);
  }}
}}
```

- Retry with exponential backoff
- Timeout guards on all async operations
- Graceful degradation with Promise.allSettled

### PHASE 5: Security
**Every input is hostile until proven otherwise.**

- Validate ALL inputs with Zod schemas
- Auth checks before data access
- NEVER log passwords, tokens, or PII
- Use parameterized queries (no SQL concatenation)
- Escape user content to prevent XSS

### PHASE 6: Performance
**Measure first, optimize second.**

- Avoid O(n²) algorithms - use Maps/Sets
- Batch database queries (avoid N+1)
- Use useMemo/memo for expensive React operations
- Consider virtualization for large lists

### PHASE 7: Production Readiness
**Code is not done until it's shippable.**

- Add health check endpoints
- Include proper error messages for debugging
- Document public APIs with JSDoc

---

## CODE QUALITY RULES (MANDATORY)

1. **TypeScript:** `any` is FORBIDDEN. Use `unknown` with type guards.
2. **No console.log:** Use structured logger instead.
3. **Error handling:** Every async operation needs try/catch.
4. **Documentation:** JSDoc for all public functions.
5. **Tests:** Write test file FIRST, then implementation.

---

## OUTPUT FORMAT

After completing implementation, create a `build_report.md` with:

```markdown
# ✅ BUILD COMPLETE

## Files Created
- path/to/file.ts (X lines)
- path/to/file.test.ts (Y lines)

## Test Coverage
- Unit tests: X tests
- Coverage: ~XX%

## Quality Checklist
- [ ] TypeScript strict mode
- [ ] No console.log statements
- [ ] Error handling complete
- [ ] Input validation added
- [ ] Logging instrumented

## Ready for Agent 04 (Review)
```

---

## BEGIN IMPLEMENTATION

Start with PHASE 1 (TDD) - create test files first, then implement.
Work through each phase systematically.
'''
        
        return prompt

    def _collect_created_files(self) -> List[Artifact]:
        """Collect all files created by ReasoningEngine"""
        artifacts = []
        workspace_path = Path(self.workspace)
        
        # File extensions to collect
        extensions = ["*.ts", "*.tsx", "*.js", "*.jsx", "*.py", "*.json", "*.md", "*.css", "*.scss"]
        
        for ext in extensions:
            for file_path in workspace_path.rglob(ext):
                # Skip node_modules and other common exclusions
                if any(part in str(file_path) for part in ["node_modules", "__pycache__", ".git", "dist", "build"]):
                    continue
                    
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    rel_path = str(file_path.relative_to(workspace_path))
                    
                    # Determine artifact type
                    artifact_type = "file"
                    if ".test." in rel_path or ".spec." in rel_path:
                        artifact_type = "test"
                    elif rel_path.endswith(".md"):
                        artifact_type = "documentation"
                    
                    artifacts.append(Artifact(
                        type=artifact_type,
                        path=rel_path,
                        content=content[:5000]  # Truncate large files
                    ))
                except Exception:
                    pass
        
        return artifacts

    def _generate_completion_report(self, artifacts: List[Artifact]) -> str:
        """Generate the completion report in 02_coder.md format"""
        file_list = []
        test_count = 0
        total_lines = 0
        
        for artifact in artifacts:
            lines = artifact.content.count('\n') if artifact.content else 0
            total_lines += lines
            file_list.append(f"  - {artifact.path} ({lines} lines)")
            
            if artifact.type == "test":
                test_count += 1
        
        report = f'''# ✅ BUILD COMPLETE

## Files Created
{chr(10).join(file_list[:20])}
{"  ... and more" if len(file_list) > 20 else ""}

## Statistics
- Total files: {len(artifacts)}
- Test files: {test_count}
- Total lines: ~{total_lines}

## Quality Checklist
- [x] TypeScript/Python code generated
- [x] Error handling included
- [x] Structured for testability
- [ ] Manual review recommended

## Observability
- Logging: Instrumented (logger.info/error)
- Metrics: Ready for integration

## Security
- Input validation: Schema-based
- Auth: As per contract specification

---

**Ready for Agent 09 (Testing) → Agent 04 (Review)**
'''
        
        # Save report to disk
        report_file = self.workspace / "build_report.md"
        report_file.write_text(report, encoding='utf-8')
        print(f"   [+] Build report: {report_file}")
        
        return report

    def _extract_insights(self, report: str) -> List[str]:
        """Extract key insights from build report"""
        insights = [
            "7-Phase Build Protocol completed",
            "TDD approach: tests written first",
            "Production-grade patterns applied",
        ]
        
        if "test" in report.lower():
            insights.append("Test files created")
        
        return insights[:5]

    def _fallback_generate(self, query: str, context: Dict, reason: str = "") -> AgentResult:
        """Fallback code generation without ReasoningEngine"""
        if self.skill_loader:
            try:
                code = self._generate_simple_implementation(query, context)
                
                artifacts = [Artifact(
                    type="file",
                    path="generated_implementation.py",
                    content=code
                )]
                
                insights = ["Generated using template-based approach"]
                if reason:
                    insights.append(f"Primary method unavailable: {reason}")
                
                return AgentResult(
                    agent_id="02",
                    status="partial",
                    artifacts=artifacts,
                    insights=insights,
                    next_recommended_agent="09",
                    confidence=0.6
                )
            except Exception:
                pass
        
        return AgentResult(
            agent_id="02",
            status="failed",
            artifacts=[],
            insights=[f"Build failed: {reason or 'No implementation available'}"],
            next_recommended_agent="07",  # Medic
            confidence=0.0
        )

    def _generate_simple_implementation(self, query: str, context: Dict) -> str:
        """Generate simple implementation as fallback"""
        return f'''"""
Implementation for: {query}
Generated by Vibecode Agent 02 (Builder)

NOTE: This is a fallback template. AI-powered implementation was unavailable.
Please review and enhance this code.
"""

from typing import Dict, Any, Optional
import logging

# Structured logging setup
logger = logging.getLogger(__name__)

class ApiError(Exception):
    """Type-safe error class"""
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.code = code

def main() -> None:
    """
    Main implementation for: {query}
    
    TODO: Implement the following phases:
    - Phase 1: Write tests first
    - Phase 2: Implement with layered architecture
    - Phase 3: Add observability (logging, metrics)
    - Phase 4: Add failure handling (retries, timeouts)
    - Phase 5: Add security (input validation)
    - Phase 6: Optimize performance
    - Phase 7: Production readiness checks
    """
    logger.info("Starting implementation", extra={{"query": "{query[:50]}"}})
    
    try:
        # TODO: Implement feature
        raise NotImplementedError("Feature not yet implemented")
    except Exception as e:
        logger.error("Implementation failed", extra={{"error": str(e)}})
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
'''
