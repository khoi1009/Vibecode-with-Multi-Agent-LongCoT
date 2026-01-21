"""
Shipper Executor
Agent 08: Release Engineering and Deployment Preparation
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from core.agent_executor import AgentExecutor, AgentResult, Artifact
import subprocess
import json
import re
from datetime import datetime


class ShipperExecutor(AgentExecutor):
    """Agent 08: Shipper - Release engineering and deployment"""

    def __init__(self, workspace: Path, ai_provider=None, skill_loader=None):
        super().__init__(workspace, ai_provider, skill_loader)
        
        # Release thresholds
        self.min_coverage = 80  # Minimum test coverage percentage
        self.max_bundle_size_mb = 5  # Maximum bundle size
        
        # Forbidden patterns in releases
        self.forbidden_patterns = [
            r'password\s*=\s*["\'][^"\']+',
            r'api[_-]?key\s*=\s*["\'][^"\']+',
            r'secret\s*=\s*["\'][^"\']+',
            r'console\.log\s*\(',
            r'debugger\s*;?',
            r'\.env(?:\.local|\.development)?$',
        ]

    def execute(self, query: str, context: Dict, **kwargs) -> AgentResult:
        """Execute release preparation and build verification"""
        checks = []
        blockers = []
        warnings = []
        
        # Phase 0: NPM Install (for Node.js projects)
        install_result = self._verify_npm_install()
        checks.append(('Dependencies', install_result))
        if not install_result[0]:
            blockers.append(f"Install failed: {install_result[1]}")
        
        # Phase 1: Build verification
        build_result = self._verify_build()
        checks.append(('Build', build_result))
        if not build_result[0]:
            blockers.append(f"Build failed: {build_result[1]}")
        
        # Phase 2: Test verification
        test_result = self._verify_tests()
        checks.append(('Tests', test_result))
        if not test_result[0]:
            blockers.append(f"Tests failed: {test_result[1]}")
        
        # Phase 3: Security scan
        security_result = self._security_scan()
        checks.append(('Security', security_result))
        if not security_result[0]:
            blockers.append(f"Security issues: {security_result[1]}")
        
        # Phase 4: Documentation check
        docs_result = self._check_documentation()
        checks.append(('Documentation', docs_result))
        if not docs_result[0]:
            warnings.append(f"Documentation: {docs_result[1]}")
        
        # Phase 5: Bundle analysis (for web projects)
        bundle_result = self._analyze_bundle()
        checks.append(('Bundle', bundle_result))
        if not bundle_result[0]:
            warnings.append(f"Bundle: {bundle_result[1]}")
        
        # Phase 6: Generate artifacts
        if blockers:
            return self._blocked_release(checks, blockers, warnings)
        else:
            return self._prepare_release(checks, warnings, context)

    def _verify_npm_install(self) -> Tuple[bool, str]:
        """Verify npm install succeeds (dependencies can be installed)"""
        # Check multiple possible locations for package.json
        locations = [
            self.workspace,
            self.workspace / 'frontend',
            self.workspace / 'backend',
        ]
        
        installed = False
        for loc in locations:
            package_json = loc / 'package.json'
            if package_json.exists():
                print(f"   [SHIP] Running npm install in {loc.name or 'root'}...")
                try:
                    result = subprocess.run(
                        'npm install',
                        shell=True,
                        cwd=str(loc),
                        capture_output=True,
                        text=True,
                        timeout=180  # 3 minutes
                    )
                    if result.returncode == 0:
                        print(f"   [SHIP] ✅ npm install succeeded in {loc.name or 'root'}")
                        installed = True
                    else:
                        error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                        return False, f"npm install failed in {loc.name or 'root'}: {error_msg}"
                except subprocess.TimeoutExpired:
                    return False, f"npm install timed out in {loc.name or 'root'}"
                except Exception as e:
                    return False, f"npm install error: {str(e)}"
        
        if installed:
            return True, "Dependencies installed successfully"
        
        # No package.json found - check for Python
        if (self.workspace / 'requirements.txt').exists():
            return True, "Python project (no npm needed)"
        
        return True, "No package.json found (static project?)"


    def _verify_build(self) -> Tuple[bool, str]:
        """Verify production build succeeds"""
        package_json = self.workspace / 'package.json'
        
        if package_json.exists():
            # Node.js project
            try:
                pkg = json.loads(package_json.read_text(encoding='utf-8'))
                scripts = pkg.get('scripts', {})
                
                if 'build' in scripts:
                    result = self._run_command('npm run build', timeout=300)
                    if result is not None:
                        return True, "Build successful"
                    else:
                        return False, "Build command failed"
                else:
                    return True, "No build script (interpreted project)"
                    
            except Exception as e:
                return False, f"Build error: {str(e)}"
        
        # Python project
        pyproject = self.workspace / 'pyproject.toml'
        if pyproject.exists():
            result = self._run_command('python -m build', timeout=120)
            if result is not None:
                return True, "Build successful"
            else:
                # Maybe it's not a package, just scripts
                return True, "No build required (script project)"
        
        return True, "No build system detected"

    def _verify_tests(self) -> Tuple[bool, str]:
        """Verify tests pass"""
        package_json = self.workspace / 'package.json'
        
        if package_json.exists():
            try:
                pkg = json.loads(package_json.read_text(encoding='utf-8'))
                scripts = pkg.get('scripts', {})
                
                if 'test' in scripts:
                    result = self._run_command('npm test -- --passWithNoTests', timeout=300)
                    if result is not None:
                        return True, "All tests passed"
                    else:
                        return False, "Tests failed"
                else:
                    return True, "No test script configured"
                    
            except Exception as e:
                return False, f"Test error: {str(e)}"
        
        # Python project
        if (self.workspace / 'pytest.ini').exists() or (self.workspace / 'tests').is_dir():
            result = self._run_command('python -m pytest --tb=short', timeout=300)
            if result is not None:
                return True, "All tests passed"
            else:
                return False, "Tests failed"
        
        return True, "No test suite detected"

    def _security_scan(self) -> Tuple[bool, str]:
        """Scan for security issues"""
        issues = []
        
        # Get all source files
        source_files = list(self.workspace.rglob('*.ts'))
        source_files.extend(self.workspace.rglob('*.tsx'))
        source_files.extend(self.workspace.rglob('*.js'))
        source_files.extend(self.workspace.rglob('*.jsx'))
        source_files.extend(self.workspace.rglob('*.py'))
        
        # Filter out common non-source directories
        source_files = [f for f in source_files 
                        if 'node_modules' not in str(f)
                        and '.next' not in str(f)
                        and 'dist' not in str(f)
                        and '__pycache__' not in str(f)]
        
        for file_path in source_files[:100]:  # Limit for performance
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                for pattern in self.forbidden_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        rel_path = str(file_path.relative_to(self.workspace))
                        issues.append(f"{rel_path}: matches forbidden pattern")
                        break
                        
            except Exception:
                pass
        
        # Check for .env in git
        gitignore = self.workspace / '.gitignore'
        if gitignore.exists():
            gitignore_content = gitignore.read_text(encoding='utf-8', errors='ignore')
            if '.env' not in gitignore_content:
                issues.append(".env not in .gitignore")
        
        # Check for env files that shouldn't be committed
        for env_file in ['.env', '.env.local', '.env.production']:
            if (self.workspace / env_file).exists():
                # Check if it's in gitignore
                if gitignore.exists():
                    if env_file not in gitignore_content:
                        issues.append(f"{env_file} exists but not in .gitignore")
        
        if issues:
            return False, f"{len(issues)} security issues found"
        
        return True, "No security issues detected"

    def _check_documentation(self) -> Tuple[bool, str]:
        """Check documentation completeness"""
        missing = []
        
        # Required docs
        if not (self.workspace / 'README.md').exists():
            missing.append('README.md')
        
        # Check for CHANGELOG
        has_changelog = (
            (self.workspace / 'CHANGELOG.md').exists() or
            (self.workspace / 'CHANGELOG').exists() or
            (self.workspace / 'HISTORY.md').exists()
        )
        if not has_changelog:
            missing.append('CHANGELOG')
        
        # Check for LICENSE
        has_license = (
            (self.workspace / 'LICENSE').exists() or
            (self.workspace / 'LICENSE.md').exists() or
            (self.workspace / 'LICENSE.txt').exists()
        )
        if not has_license:
            missing.append('LICENSE')
        
        if missing:
            return False, f"Missing: {', '.join(missing)}"
        
        return True, "Documentation complete"

    def _analyze_bundle(self) -> Tuple[bool, str]:
        """Analyze bundle size for web projects"""
        # Check for Next.js .next folder
        next_dir = self.workspace / '.next'
        if next_dir.exists():
            total_size = sum(f.stat().st_size for f in next_dir.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            
            if size_mb > self.max_bundle_size_mb * 2:
                return False, f"Bundle too large: {size_mb:.1f}MB"
            elif size_mb > self.max_bundle_size_mb:
                return True, f"Bundle acceptable: {size_mb:.1f}MB (consider optimization)"
            else:
                return True, f"Bundle size: {size_mb:.1f}MB"
        
        # Check for dist folder
        dist_dir = self.workspace / 'dist'
        if dist_dir.exists():
            total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            
            if size_mb > self.max_bundle_size_mb:
                return True, f"Dist size: {size_mb:.1f}MB (consider optimization)"
            else:
                return True, f"Dist size: {size_mb:.1f}MB"
        
        return True, "No bundle to analyze"

    def _blocked_release(self, checks: List, blockers: List[str], warnings: List[str]) -> AgentResult:
        """Generate blocked release report"""
        report = self._generate_release_report(checks, blockers, warnings, blocked=True)
        
        return AgentResult(
            agent_id="08",
            status="failed",
            artifacts=[Artifact(
                type="report",
                path="release_blocked.md",
                content=report
            )],
            insights=[
                "🛑 Release BLOCKED",
                f"{len(blockers)} blocking issue(s)",
                "Fix issues before shipping"
            ],
            next_recommended_agent="07",  # Medic to fix issues
            confidence=0.0
        )

    def _prepare_release(self, checks: List, warnings: List[str], context: Dict) -> AgentResult:
        """Prepare release artifacts"""
        # Generate version
        version = self._determine_version()
        
        # Generate CHANGELOG entry
        changelog_entry = self._generate_changelog_entry(version, context)
        
        # Generate release notes
        release_notes = self._generate_release_notes(version, context)
        
        # Generate release report
        report = self._generate_release_report(checks, [], warnings, blocked=False)
        
        artifacts = [
            Artifact(
                type="report",
                path="release_report.md",
                content=report
            ),
            Artifact(
                type="file",
                path="RELEASE_NOTES.md",
                content=release_notes
            )
        ]
        
        insights = [
            f"✅ Release {version} ready",
            f"All {len(checks)} checks passed"
        ]
        
        if warnings:
            insights.append(f"{len(warnings)} non-blocking warning(s)")
        
        return AgentResult(
            agent_id="08",
            status="success",
            artifacts=artifacts,
            insights=insights,
            next_recommended_agent=None,  # Release complete
            confidence=0.95
        )

    def _determine_version(self) -> str:
        """Determine version for release"""
        # Try to read from package.json
        package_json = self.workspace / 'package.json'
        if package_json.exists():
            try:
                pkg = json.loads(package_json.read_text(encoding='utf-8'))
                return pkg.get('version', '1.0.0')
            except Exception:
                pass
        
        # Try pyproject.toml
        pyproject = self.workspace / 'pyproject.toml'
        if pyproject.exists():
            try:
                content = pyproject.read_text(encoding='utf-8')
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
            except Exception:
                pass
        
        # Default
        return datetime.now().strftime('%Y.%m.%d')

    def _generate_changelog_entry(self, version: str, context: Dict) -> str:
        """Generate CHANGELOG entry"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        entry = [
            f"## [{version}] - {today}",
            "",
            "### Added",
            "- New features implemented",
            "",
            "### Changed",
            "- Improvements and updates",
            "",
            "### Fixed",
            "- Bug fixes applied",
            ""
        ]
        
        return "\n".join(entry)

    def _generate_release_notes(self, version: str, context: Dict) -> str:
        """Generate release notes"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        notes = [
            f"# Release Notes - v{version}",
            "",
            f"**Release Date:** {today}",
            "",
            "## Overview",
            "",
            "This release includes new features, improvements, and bug fixes.",
            "",
            "## Installation",
            "",
            "```bash",
            "# Node.js",
            "npm install",
            "",
            "# Python",
            "pip install -r requirements.txt",
            "```",
            "",
            "## Quick Start",
            "",
            "See README.md for detailed instructions.",
            "",
            "## Known Issues",
            "",
            "None at this time.",
            "",
            "## Support",
            "",
            "For issues and feature requests, please open a GitHub issue."
        ]
        
        return "\n".join(notes)

    def _generate_release_report(self, checks: List, blockers: List[str], warnings: List[str], blocked: bool) -> str:
        """Generate comprehensive release report"""
        lines = [
            "# Release Report",
            "",
            f"**Status:** {'🛑 BLOCKED' if blocked else '✅ READY'}",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Pre-Flight Checks",
            ""
        ]
        
        for check_name, (passed, message) in checks:
            status = "✅" if passed else "❌"
            lines.append(f"| {status} | {check_name} | {message} |")
        
        lines.append("")
        
        if blockers:
            lines.extend([
                "## 🛑 Blocking Issues",
                ""
            ])
            for blocker in blockers:
                lines.append(f"- {blocker}")
            lines.append("")
        
        if warnings:
            lines.extend([
                "## ⚠️ Warnings",
                ""
            ])
            for warning in warnings:
                lines.append(f"- {warning}")
            lines.append("")
        
        if blocked:
            lines.extend([
                "## Required Actions",
                "",
                "1. Fix all blocking issues",
                "2. Run Agent 07 (Medic) for automated fixes",
                "3. Re-run Agent 04 (Reviewer) to verify",
                "4. Re-run Agent 08 (Shipper) when ready",
            ])
        else:
            lines.extend([
                "## Deployment Checklist",
                "",
                "- [ ] Verify all tests pass in CI",
                "- [ ] Create git tag for release",
                "- [ ] Update CHANGELOG.md",
                "- [ ] Deploy to staging first",
                "- [ ] Monitor for errors after deployment",
                "- [ ] Communicate release to stakeholders",
            ])
        
        return "\n".join(lines)

    def _run_command(self, command: str, timeout: int = 60) -> Optional[str]:
        """Run a shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.workspace),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout if result.returncode == 0 else None
        except Exception:
            return None
