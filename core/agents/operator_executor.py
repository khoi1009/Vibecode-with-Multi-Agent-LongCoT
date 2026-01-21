"""
Operator Executor
Agent 06: Local Runtime Management and Environment Setup
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from core.agent_executor import AgentExecutor, AgentResult, Artifact
import subprocess
import json
import os
import platform


class OperatorExecutor(AgentExecutor):
    """Agent 06: Operator - Local runtime management"""

    def __init__(self, workspace: Path, ai_provider=None, skill_loader=None):
        super().__init__(workspace, ai_provider, skill_loader)
        self.system = platform.system()  # Windows, Linux, Darwin
        
        # Runtime detection patterns
        self.node_indicators = ['package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml']
        self.python_indicators = ['requirements.txt', 'pyproject.toml', 'Pipfile', 'setup.py']
        self.docker_indicators = ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml']

    def execute(self, query: str, context: Dict, **kwargs) -> AgentResult:
        """Execute runtime setup and management"""
        # Detect project type
        project_info = self._detect_project_type()
        
        # Check toolchain
        toolchain_status = self._verify_toolchain(project_info)
        
        # Check environment
        env_status = self._check_environment(project_info)
        
        # Attempt to run if everything is ready
        if toolchain_status['ready'] and env_status['ready']:
            return self._setup_and_run(project_info, context)
        else:
            return self._report_requirements(project_info, toolchain_status, env_status)

    def _detect_project_type(self) -> Dict:
        """Detect project type from workspace files"""
        info = {
            'type': 'unknown',
            'framework': None,
            'package_manager': None,
            'entry_point': None,
            'start_command': None,
            'port': 3000
        }
        
        # Check for Node.js project
        package_json = self.workspace / 'package.json'
        if package_json.exists():
            info['type'] = 'node'
            try:
                pkg = json.loads(package_json.read_text(encoding='utf-8'))
                
                # Detect framework
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                if 'next' in deps:
                    info['framework'] = 'nextjs'
                    info['start_command'] = 'npm run dev'
                elif 'vite' in deps:
                    info['framework'] = 'vite'
                    info['start_command'] = 'npm run dev'
                elif 'express' in deps:
                    info['framework'] = 'express'
                    info['start_command'] = pkg.get('scripts', {}).get('start', 'node server.js')
                elif 'react' in deps:
                    info['framework'] = 'react'
                    info['start_command'] = 'npm start'
                else:
                    info['start_command'] = pkg.get('scripts', {}).get('start', 'npm start')
                
                # Detect package manager from lockfile
                if (self.workspace / 'pnpm-lock.yaml').exists():
                    info['package_manager'] = 'pnpm'
                elif (self.workspace / 'yarn.lock').exists():
                    info['package_manager'] = 'yarn'
                elif (self.workspace / 'bun.lockb').exists():
                    info['package_manager'] = 'bun'
                else:
                    info['package_manager'] = 'npm'
                    
            except Exception:
                info['package_manager'] = 'npm'
                info['start_command'] = 'npm start'
        
        # Check for Python project
        elif (self.workspace / 'requirements.txt').exists() or (self.workspace / 'pyproject.toml').exists():
            info['type'] = 'python'
            info['package_manager'] = 'pip'
            
            # Detect framework
            req_file = self.workspace / 'requirements.txt'
            if req_file.exists():
                reqs = req_file.read_text(encoding='utf-8', errors='ignore').lower()
                if 'fastapi' in reqs or 'uvicorn' in reqs:
                    info['framework'] = 'fastapi'
                    info['start_command'] = 'uvicorn main:app --reload'
                    info['port'] = 8000
                elif 'flask' in reqs:
                    info['framework'] = 'flask'
                    info['start_command'] = 'flask run'
                    info['port'] = 5000
                elif 'django' in reqs:
                    info['framework'] = 'django'
                    info['start_command'] = 'python manage.py runserver'
                    info['port'] = 8000
                else:
                    info['start_command'] = 'python main.py'
        
        # Check for Docker
        elif (self.workspace / 'docker-compose.yml').exists():
            info['type'] = 'docker'
            info['start_command'] = 'docker-compose up'
        
        return info

    def _verify_toolchain(self, project_info: Dict) -> Dict:
        """Verify required tools are installed"""
        status = {'ready': True, 'missing': [], 'versions': {}}
        
        if project_info['type'] == 'node':
            # Check Node.js
            node_version = self._run_command('node --version')
            if node_version:
                status['versions']['node'] = node_version.strip()
            else:
                status['ready'] = False
                status['missing'].append('node')
            
            # Check package manager
            pm = project_info['package_manager']
            pm_version = self._run_command(f'{pm} --version')
            if pm_version:
                status['versions'][pm] = pm_version.strip()
            else:
                status['ready'] = False
                status['missing'].append(pm)
        
        elif project_info['type'] == 'python':
            # Check Python
            python_cmd = 'python' if self.system == 'Windows' else 'python3'
            python_version = self._run_command(f'{python_cmd} --version')
            if python_version:
                status['versions']['python'] = python_version.strip()
            else:
                status['ready'] = False
                status['missing'].append('python')
            
            # Check pip
            pip_version = self._run_command(f'{python_cmd} -m pip --version')
            if pip_version:
                status['versions']['pip'] = pip_version.split()[1] if pip_version else 'unknown'
            else:
                status['missing'].append('pip')
        
        elif project_info['type'] == 'docker':
            # Check Docker
            docker_version = self._run_command('docker --version')
            if docker_version:
                status['versions']['docker'] = docker_version.strip()
            else:
                status['ready'] = False
                status['missing'].append('docker')
        
        return status

    def _check_environment(self, project_info: Dict) -> Dict:
        """Check environment configuration"""
        status = {'ready': True, 'missing': [], 'warnings': []}
        
        # Check for .env files
        env_file = self.workspace / '.env'
        env_example = self.workspace / '.env.example'
        env_local = self.workspace / '.env.local'
        
        if env_example.exists() and not env_file.exists() and not env_local.exists():
            status['ready'] = False
            status['missing'].append('.env file (copy from .env.example)')
        
        # Check for node_modules (Node.js)
        if project_info['type'] == 'node':
            node_modules = self.workspace / 'node_modules'
            if not node_modules.exists():
                status['ready'] = False
                status['missing'].append('node_modules (run npm install)')
        
        # Check for venv (Python)
        elif project_info['type'] == 'python':
            venv = self.workspace / 'venv'
            if not venv.exists() and not os.environ.get('VIRTUAL_ENV'):
                status['warnings'].append('No virtual environment detected')
        
        return status

    def _setup_and_run(self, project_info: Dict, context: Dict) -> AgentResult:
        """Set up and run the application"""
        insights = []
        artifacts = []
        
        # Install dependencies if needed
        if project_info['type'] == 'node':
            node_modules = self.workspace / 'node_modules'
            if not node_modules.exists():
                pm = project_info['package_manager']
                install_result = self._run_command(f'{pm} install', cwd=str(self.workspace))
                if install_result:
                    insights.append(f"Dependencies installed with {pm}")
                else:
                    return AgentResult(
                        agent_id="06",
                        status="failed",
                        artifacts=[],
                        insights=["Failed to install dependencies"],
                        next_recommended_agent="07",
                        confidence=0.0
                    )
        
        elif project_info['type'] == 'python':
            # Install requirements
            req_file = self.workspace / 'requirements.txt'
            if req_file.exists():
                python_cmd = 'python' if self.system == 'Windows' else 'python3'
                install_result = self._run_command(
                    f'{python_cmd} -m pip install -r requirements.txt',
                    cwd=str(self.workspace)
                )
                if install_result:
                    insights.append("Python dependencies installed")

        # Generate run instructions
        run_instructions = self._generate_run_instructions(project_info)
        artifacts.append(Artifact(
            type="report",
            path="runtime_setup.md",
            content=run_instructions
        ))
        
        insights.append(f"Project type: {project_info['type']}")
        if project_info['framework']:
            insights.append(f"Framework: {project_info['framework']}")
        insights.append(f"Start command: {project_info['start_command']}")
        insights.append(f"Expected port: {project_info['port']}")
        
        return AgentResult(
            agent_id="06",
            status="success",
            artifacts=artifacts,
            insights=insights,
            next_recommended_agent="09",
            confidence=0.85
        )

    def _report_requirements(self, project_info: Dict, toolchain: Dict, env: Dict) -> AgentResult:
        """Report what's needed to run the project"""
        insights = []
        
        if toolchain['missing']:
            insights.append(f"Missing tools: {', '.join(toolchain['missing'])}")
        
        if env['missing']:
            insights.append(f"Missing environment: {', '.join(env['missing'])}")
        
        if env.get('warnings'):
            for warning in env['warnings']:
                insights.append(f"Warning: {warning}")
        
        # Generate setup instructions
        setup_guide = self._generate_setup_guide(project_info, toolchain, env)
        
        return AgentResult(
            agent_id="06",
            status="partial",
            artifacts=[Artifact(
                type="report",
                path="setup_requirements.md",
                content=setup_guide
            )],
            insights=insights,
            next_recommended_agent="06",  # Re-run after setup
            confidence=0.5
        )

    def _run_command(self, command: str, cwd: str = None, timeout: int = 60) -> Optional[str]:
        """Run a shell command and return output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or str(self.workspace),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout if result.returncode == 0 else None
        except Exception:
            return None

    def _generate_run_instructions(self, project_info: Dict) -> str:
        """Generate runtime instructions"""
        lines = [
            "# Runtime Setup Complete",
            "",
            "## Project Information",
            f"- **Type:** {project_info['type']}",
            f"- **Framework:** {project_info['framework'] or 'N/A'}",
            f"- **Package Manager:** {project_info['package_manager'] or 'N/A'}",
            "",
            "## Start the Application",
            "",
            "```bash",
            f"cd {self.workspace}",
            f"{project_info['start_command']}",
            "```",
            "",
            f"The application should be available at: **http://localhost:{project_info['port']}**",
            "",
            "## Next Steps",
            "- Run the application with the command above",
            "- Verify the application loads correctly",
            "- Proceed to Agent 09 (Testing) for automated tests"
        ]
        
        return "\n".join(lines)

    def _generate_setup_guide(self, project_info: Dict, toolchain: Dict, env: Dict) -> str:
        """Generate setup guide for missing requirements"""
        lines = [
            "# Setup Requirements",
            "",
            "The following items need to be set up before running the application:",
            ""
        ]
        
        if toolchain['missing']:
            lines.extend([
                "## Missing Tools",
                ""
            ])
            for tool in toolchain['missing']:
                if tool == 'node':
                    lines.append(f"- **Node.js**: Download from https://nodejs.org/")
                elif tool == 'npm':
                    lines.append(f"- **npm**: Comes with Node.js")
                elif tool == 'python':
                    lines.append(f"- **Python**: Download from https://python.org/")
                elif tool == 'docker':
                    lines.append(f"- **Docker**: Download from https://docker.com/")
                else:
                    lines.append(f"- **{tool}**: Please install")
            lines.append("")
        
        if env['missing']:
            lines.extend([
                "## Missing Environment",
                ""
            ])
            for item in env['missing']:
                lines.append(f"- {item}")
            lines.append("")
        
        if toolchain.get('versions'):
            lines.extend([
                "## Detected Versions",
                ""
            ])
            for tool, version in toolchain['versions'].items():
                lines.append(f"- **{tool}**: {version}")
            lines.append("")
        
        lines.extend([
            "## After Setup",
            "",
            "Run Agent 06 again to verify setup and start the application."
        ])
        
        return "\n".join(lines)
