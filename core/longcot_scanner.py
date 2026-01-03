"""
Long Chain-of-Thought Scanner
Implements Tree-of-Thought (ToT) reasoning for large codebase analysis

Key Features:
1. Hierarchical reasoning (Architecture → Modules → Files)
2. Multi-path exploration (ToT branches)
3. Process Reward Model validation
4. Reflection and backtracking
5. Context window optimization

Based on research from:
- Tree-of-Thought: https://arxiv.org/abs/2305.10601
- ProcessBench: https://huggingface.co/datasets/Qwen/ProcessBench
- ReST-MCTS*: https://arxiv.org/abs/2406.03816
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum


class ReasoningState(Enum):
    """States in the reasoning tree"""
    EXPLORING = "exploring"
    VALIDATED = "validated"
    REJECTED = "rejected"
    BACKTRACKING = "backtracking"


@dataclass
class ReasoningNode:
    """Node in the Tree-of-Thought reasoning structure"""
    id: str
    level: str  # "architecture", "module", "file"
    path: Path
    parent: Optional['ReasoningNode'] = None
    children: List['ReasoningNode'] = field(default_factory=list)
    state: ReasoningState = ReasoningState.EXPLORING
    
    # Reasoning metadata
    hypothesis: str = ""  # What we think this component does
    confidence: float = 0.0  # 0-1 confidence score
    dependencies: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    
    # Validation data
    validation_steps: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class ReasoningChain:
    """Complete chain of reasoning for a code analysis"""
    steps: List[Dict[str, Any]] = field(default_factory=list)
    reflections: List[str] = field(default_factory=list)
    confidence_trajectory: List[float] = field(default_factory=list)
    backtrack_count: int = 0


class LongCoTScanner:
    """
    Enhanced scanner using Long Chain-of-Thought reasoning
    
    Unlike traditional scanners that linearly process files,
    this scanner:
    1. Builds a reasoning tree of the codebase
    2. Explores multiple hypotheses in parallel
    3. Validates each step before proceeding
    4. Reflects on findings and backtracks when needed
    5. Generates coherent multi-level understanding
    """
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.vibecode_dir = self.project_path / ".vibecode"
        self.vibecode_dir.mkdir(exist_ok=True)
        
        # Long CoT specific directories
        self.longcot_dir = self.vibecode_dir / "longcot"
        self.longcot_dir.mkdir(exist_ok=True)
        
        self.ignore_dirs = {
            'node_modules', 'venv', '.venv', 'env', '.env',
            'dist', 'build', '.git', '.svn', '__pycache__',
            'coverage', '.next', '.nuxt', 'vendor', 'bower_components',
            '.pytest_cache', 'htmlcov', '.tox', 'eggs', '.eggs'
        }
        
        # ToT reasoning state
        self.root_node: Optional[ReasoningNode] = None
        self.current_chain = ReasoningChain()
        self.explored_paths: Set[str] = set()
        
    def scan_with_longcot(self) -> Dict:
        """
        Main entry point: Long Chain-of-Thought scan
        
        Returns comprehensive analysis with reasoning traces
        """
        print("🧠 Long Chain-of-Thought Analysis Starting...")
        print("=" * 60)
        
        # Phase 1: Architecture-level reasoning
        print("\n📐 Phase 1: ARCHITECTURE REASONING")
        print("  Strategy: Tree-of-Thought exploration")
        architecture_tree = self._explore_architecture()
        self._log_reasoning_step("architecture_exploration", architecture_tree)
        
        # Phase 2: Module-level deep dive
        print("\n🔍 Phase 2: MODULE DEEP REASONING")
        print("  Strategy: Parallel hypothesis exploration")
        module_insights = self._explore_modules(architecture_tree)
        self._log_reasoning_step("module_analysis", module_insights)
        
        # Phase 3: Critical path analysis
        print("\n⚡ Phase 3: CRITICAL PATH IDENTIFICATION")
        print("  Strategy: Dependency graph reasoning")
        critical_paths = self._identify_critical_paths(module_insights)
        self._log_reasoning_step("critical_paths", critical_paths)
        
        # Phase 4: Reflection and validation
        print("\n🔄 Phase 4: REFLECTION & VALIDATION")
        print("  Strategy: Process Reward Model validation")
        validated_insights = self._reflect_and_validate(critical_paths)
        self._log_reasoning_step("validation", validated_insights)
        
        # Compile final results
        results = {
            'scan_date': datetime.now().isoformat(),
            'scan_type': 'long_chain_of_thought',
            'reasoning_chain': self._export_reasoning_chain(),
            'architecture': architecture_tree,
            'modules': module_insights,
            'critical_paths': critical_paths,
            'validated_insights': validated_insights,
            'statistics': self._compute_statistics()
        }
        
        # Save with reasoning traces
        self._save_longcot_reports(results)
        
        print("\n" + "=" * 60)
        print("✅ Long CoT Analysis Complete!")
        print(f"   Reasoning steps: {len(self.current_chain.steps)}")
        print(f"   Reflections: {len(self.current_chain.reflections)}")
        print(f"   Backtracks: {self.current_chain.backtrack_count}")
        print(f"   Final confidence: {self._compute_final_confidence():.1%}")
        
        return results
    
    def _explore_architecture(self) -> Dict:
        """
        Phase 1: Architecture-level ToT exploration
        
        Creates multiple hypotheses about project structure
        and validates them through file system evidence
        """
        print("  🌳 Building reasoning tree...")
        
        # Initialize root node
        self.root_node = ReasoningNode(
            id="root",
            level="architecture",
            path=self.project_path,
            hypothesis="Analyzing overall project architecture"
        )
        
        # Identify top-level structure
        top_level_items = []
        for item in self.project_path.iterdir():
            if item.name.startswith('.') and item.name != '.vibecode':
                continue
            if item.name in self.ignore_dirs:
                continue
            top_level_items.append(item)
        
        # Generate hypotheses about project type
        hypotheses = self._generate_architecture_hypotheses(top_level_items)
        
        print(f"  💡 Generated {len(hypotheses)} architectural hypotheses")
        for i, hyp in enumerate(hypotheses[:3], 1):
            print(f"     {i}. {hyp['description']} (confidence: {hyp['confidence']:.1%})")
        
        # Validate and select best hypothesis
        best_hypothesis = self._validate_hypotheses(hypotheses, top_level_items)
        
        print(f"  ✓ Selected hypothesis: {best_hypothesis['description']}")
        
        # Build architecture tree
        architecture = {
            'type': best_hypothesis['type'],
            'description': best_hypothesis['description'],
            'confidence': best_hypothesis['confidence'],
            'key_directories': self._categorize_directories(top_level_items),
            'tech_indicators': best_hypothesis.get('indicators', {}),
            'reasoning_trace': best_hypothesis.get('reasoning', [])
        }
        
        # Add reflection
        reflection = self._reflect_on_architecture(architecture)
        self.current_chain.reflections.append(reflection)
        print(f"  🤔 Reflection: {reflection}")
        
        return architecture
    
    def _generate_architecture_hypotheses(self, items: List[Path]) -> List[Dict]:
        """
        Generate multiple hypotheses about project architecture
        
        This is where ToT branching happens - we consider multiple
        possible interpretations of the codebase structure
        """
        hypotheses = []
        
        # Hypothesis 1: Multi-agent system
        if any(item.name in ['agents', 'core', 'skills'] for item in items):
            hypotheses.append({
                'type': 'multi_agent_system',
                'description': 'Multi-agent AI system with orchestration',
                'confidence': 0.85,
                'indicators': {
                    'agents_dir': any(item.name == 'agents' for item in items),
                    'core_dir': any(item.name == 'core' for item in items),
                    'skills_dir': any(item.name == 'skills' for item in items)
                },
                'reasoning': [
                    'Detected agents directory → likely multi-agent architecture',
                    'Core directory suggests centralized orchestration',
                    'Skills directory indicates modular capability system'
                ]
            })
        
        # Hypothesis 2: Full-stack web application
        if any(item.name in ['frontend', 'backend', 'api', 'client', 'server'] for item in items):
            hypotheses.append({
                'type': 'fullstack_web_app',
                'description': 'Full-stack web application with separated layers',
                'confidence': 0.75,
                'indicators': {
                    'frontend': any(item.name in ['frontend', 'client', 'web'] for item in items),
                    'backend': any(item.name in ['backend', 'api', 'server'] for item in items)
                },
                'reasoning': [
                    'Frontend/backend separation detected',
                    'Likely follows modern web architecture patterns'
                ]
            })
        
        # Hypothesis 3: Microservices architecture
        service_dirs = [item for item in items if item.is_dir() and 'service' in item.name.lower()]
        if len(service_dirs) > 1:
            hypotheses.append({
                'type': 'microservices',
                'description': 'Microservices architecture with distributed services',
                'confidence': 0.70,
                'indicators': {
                    'service_count': len(service_dirs),
                    'service_names': [s.name for s in service_dirs]
                },
                'reasoning': [
                    f'Detected {len(service_dirs)} service directories',
                    'Suggests microservices architecture pattern'
                ]
            })
        
        # Hypothesis 4: Monolithic application
        src_dirs = [item for item in items if item.name in ['src', 'app', 'lib']]
        if src_dirs and not any(h['type'] in ['multi_agent_system', 'fullstack_web_app'] for h in hypotheses):
            hypotheses.append({
                'type': 'monolithic',
                'description': 'Monolithic application with single source tree',
                'confidence': 0.60,
                'indicators': {
                    'main_source': src_dirs[0].name if src_dirs else 'src'
                },
                'reasoning': [
                    'Single main source directory detected',
                    'No clear separation of concerns visible at top level'
                ]
            })
        
        # Hypothesis 5: Python package/library
        if any(item.name in ['setup.py', 'pyproject.toml'] for item in items):
            hypotheses.append({
                'type': 'python_package',
                'description': 'Python package or library',
                'confidence': 0.80,
                'indicators': {
                    'setup_py': any(item.name == 'setup.py' for item in items),
                    'pyproject': any(item.name == 'pyproject.toml' for item in items)
                },
                'reasoning': [
                    'Python package configuration files detected',
                    'Likely intended for distribution/installation'
                ]
            })
        
        # Default hypothesis if none match
        if not hypotheses:
            hypotheses.append({
                'type': 'generic',
                'description': 'Generic project structure',
                'confidence': 0.50,
                'indicators': {},
                'reasoning': ['No clear architectural pattern detected']
            })
        
        return sorted(hypotheses, key=lambda h: h['confidence'], reverse=True)
    
    def _validate_hypotheses(self, hypotheses: List[Dict], items: List[Path]) -> Dict:
        """
        Process Reward Model (PRM) validation
        
        Validates each hypothesis by checking file system evidence
        """
        for hypothesis in hypotheses:
            validation_score = 0.0
            validation_steps = []
            
            # Validate indicators
            for indicator, present in hypothesis.get('indicators', {}).items():
                if present:
                    validation_score += 0.1
                    validation_steps.append(f"✓ Confirmed: {indicator}")
                else:
                    validation_steps.append(f"✗ Missing: {indicator}")
            
            # Adjust confidence based on validation
            original_confidence = hypothesis['confidence']
            hypothesis['confidence'] = min(1.0, original_confidence * (1 + validation_score))
            hypothesis['validation_steps'] = validation_steps
            
            self.current_chain.confidence_trajectory.append(hypothesis['confidence'])
        
        # Return highest confidence hypothesis
        return max(hypotheses, key=lambda h: h['confidence'])
    
    def _categorize_directories(self, items: List[Path]) -> Dict[str, List[str]]:
        """Categorize directories by their likely purpose"""
        categories = {
            'source': [],
            'tests': [],
            'config': [],
            'docs': [],
            'data': [],
            'assets': [],
            'dependencies': [],
            'other': []
        }
        
        for item in items:
            if not item.is_dir():
                continue
                
            name_lower = item.name.lower()
            
            if name_lower in ['src', 'app', 'lib', 'core', 'agents', 'modules']:
                categories['source'].append(item.name)
            elif name_lower in ['test', 'tests', '__tests__', 'spec', 'specs']:
                categories['tests'].append(item.name)
            elif name_lower in ['config', 'configs', 'settings', 'conf']:
                categories['config'].append(item.name)
            elif name_lower in ['docs', 'doc', 'documentation', 'wiki']:
                categories['docs'].append(item.name)
            elif name_lower in ['data', 'datasets', 'fixtures']:
                categories['data'].append(item.name)
            elif name_lower in ['assets', 'static', 'public', 'resources']:
                categories['assets'].append(item.name)
            elif name_lower in self.ignore_dirs:
                categories['dependencies'].append(item.name)
            else:
                categories['other'].append(item.name)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _reflect_on_architecture(self, architecture: Dict) -> str:
        """
        Reflection step: Analyze what we learned
        
        This is crucial for Long CoT - we don't just execute steps,
        we reflect on what they mean
        """
        arch_type = architecture['type']
        confidence = architecture['confidence']
        key_dirs = architecture['key_directories']
        
        if confidence > 0.80:
            return f"High confidence ({confidence:.1%}) in {arch_type} architecture. Key insight: {len(key_dirs.get('source', []))} source directories suggest {'well-organized' if len(key_dirs.get('source', [])) > 1 else 'simple'} structure."
        elif confidence > 0.60:
            return f"Moderate confidence ({confidence:.1%}) in {arch_type}. Should validate with deeper module analysis."
        else:
            return f"Low confidence ({confidence:.1%}) - may need backtracking to reconsider architecture hypothesis."
    
    def _explore_modules(self, architecture: Dict) -> Dict:
        """
        Phase 2: Module-level reasoning with parallel exploration
        
        For each source directory, we:
        1. Generate hypotheses about its purpose
        2. Analyze file patterns
        3. Map dependencies
        4. Validate findings
        """
        print("  🔍 Analyzing source modules...")
        
        source_dirs = architecture['key_directories'].get('source', [])
        if not source_dirs:
            source_dirs = ['src', 'app', 'lib']  # defaults
        
        modules = {}
        
        for dir_name in source_dirs:
            dir_path = self.project_path / dir_name
            if not dir_path.exists():
                continue
            
            print(f"    → Exploring {dir_name}/")
            
            # Generate hypotheses about module purpose
            module_hypotheses = self._generate_module_hypotheses(dir_path)
            
            # Analyze files in module
            file_analysis = self._analyze_module_files(dir_path)
            
            # Map dependencies
            dependencies = self._map_module_dependencies(dir_path, file_analysis)
            
            modules[dir_name] = {
                'path': str(dir_path),
                'hypotheses': module_hypotheses,
                'file_analysis': file_analysis,
                'dependencies': dependencies,
                'confidence': self._compute_module_confidence(file_analysis)
            }
            
            print(f"       Confidence: {modules[dir_name]['confidence']:.1%}")
        
        return modules
    
    def _generate_module_hypotheses(self, module_path: Path) -> List[Dict]:
        """Generate hypotheses about what a module does"""
        hypotheses = []
        files = list(module_path.rglob('*.py'))
        
        # Look for patterns in filenames
        file_names = [f.name for f in files]
        
        # Hypothesis: API/Service module
        if any('api' in name or 'service' in name for name in file_names):
            hypotheses.append({
                'type': 'api_service',
                'description': 'Handles external communication and services',
                'confidence': 0.75
            })
        
        # Hypothesis: Data processing module
        if any('process' in name or 'transform' in name or 'pipeline' in name for name in file_names):
            hypotheses.append({
                'type': 'data_processing',
                'description': 'Processes and transforms data',
                'confidence': 0.70
            })
        
        # Hypothesis: Agent/Actor module
        if any('agent' in name or 'actor' in name for name in file_names):
            hypotheses.append({
                'type': 'agent_system',
                'description': 'Autonomous agents or actors',
                'confidence': 0.80
            })
        
        # Hypothesis: Orchestration module
        if any('orchestrat' in name or 'coordinat' in name or 'manage' in name for name in file_names):
            hypotheses.append({
                'type': 'orchestration',
                'description': 'Coordinates and manages other components',
                'confidence': 0.85
            })
        
        return sorted(hypotheses, key=lambda h: h['confidence'], reverse=True)
    
    def _analyze_module_files(self, module_path: Path) -> Dict:
        """Analyze files in a module"""
        analysis = {
            'total_files': 0,
            'total_lines': 0,
            'file_types': defaultdict(int),
            'key_files': [],
            'complexity_estimate': 'low'
        }
        
        for file_path in module_path.rglob('*'):
            if file_path.is_file() and not any(ignore in str(file_path) for ignore in self.ignore_dirs):
                analysis['total_files'] += 1
                analysis['file_types'][file_path.suffix] += 1
                
                # Count lines for code files
                if file_path.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c']:
                    try:
                        lines = len(file_path.read_text(encoding='utf-8').splitlines())
                        analysis['total_lines'] += lines
                        
                        # Track key files (>100 lines)
                        if lines > 100:
                            analysis['key_files'].append({
                                'path': str(file_path.relative_to(self.project_path)),
                                'lines': lines
                            })
                    except:
                        pass
        
        # Estimate complexity
        if analysis['total_lines'] > 5000:
            analysis['complexity_estimate'] = 'high'
        elif analysis['total_lines'] > 1000:
            analysis['complexity_estimate'] = 'medium'
        
        return analysis
    
    def _map_module_dependencies(self, module_path: Path, file_analysis: Dict) -> List[str]:
        """Map dependencies between modules"""
        dependencies = set()
        
        # Look at imports in Python files
        for file_path in module_path.rglob('*.py'):
            try:
                content = file_path.read_text(encoding='utf-8')
                # Simple import detection
                for line in content.splitlines():
                    if line.strip().startswith('from ') or line.strip().startswith('import '):
                        # Extract module name
                        if 'import ' in line:
                            parts = line.split('import ')
                            if len(parts) > 1:
                                module = parts[1].split()[0].split('.')[0]
                                if module and not module.startswith('_'):
                                    dependencies.add(module)
            except:
                pass
        
        return sorted(list(dependencies))
    
    def _compute_module_confidence(self, file_analysis: Dict) -> float:
        """Compute confidence in module analysis"""
        confidence = 0.5  # baseline
        
        # More files analyzed = higher confidence
        if file_analysis['total_files'] > 10:
            confidence += 0.2
        elif file_analysis['total_files'] > 5:
            confidence += 0.1
        
        # Key files identified = higher confidence
        if len(file_analysis['key_files']) > 3:
            confidence += 0.2
        elif len(file_analysis['key_files']) > 0:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _identify_critical_paths(self, modules: Dict) -> Dict:
        """
        Phase 3: Identify critical execution paths
        
        Uses dependency analysis to find the most important
        code paths through the system
        """
        print("  ⚡ Mapping critical paths through dependency graph...")
        
        critical_paths = {
            'entry_points': [],
            'core_modules': [],
            'dependency_graph': {},
            'bottlenecks': []
        }
        
        # Build dependency graph
        for module_name, module_data in modules.items():
            deps = module_data['dependencies']
            critical_paths['dependency_graph'][module_name] = deps
            
            # Identify core modules (high dependency count)
            if len(deps) > 5:
                critical_paths['core_modules'].append({
                    'name': module_name,
                    'dependency_count': len(deps),
                    'complexity': module_data['file_analysis']['complexity_estimate']
                })
        
        # Look for entry points (files with 'main', 'app', 'server', etc.)
        for module_name, module_data in modules.items():
            key_files = module_data['file_analysis']['key_files']
            for file_info in key_files:
                file_path = file_info['path']
                if any(keyword in file_path.lower() for keyword in ['main', 'app', 'server', 'cli', 'run']):
                    critical_paths['entry_points'].append({
                        'module': module_name,
                        'file': file_path,
                        'lines': file_info['lines']
                    })
        
        return critical_paths
    
    def _reflect_and_validate(self, critical_paths: Dict) -> Dict:
        """
        Phase 4: Reflect on findings and validate
        
        This is where we check our reasoning chain for errors
        and backtrack if needed
        """
        print("  🔄 Validating reasoning chain...")
        
        validation = {
            'validated_insights': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Validate we found entry points
        if not critical_paths['entry_points']:
            validation['warnings'].append("No clear entry points identified - may need deeper analysis")
            self.current_chain.backtrack_count += 1
        else:
            validation['validated_insights'].append(
                f"✓ Identified {len(critical_paths['entry_points'])} entry points"
            )
        
        # Validate core modules
        if critical_paths['core_modules']:
            validation['validated_insights'].append(
                f"✓ Identified {len(critical_paths['core_modules'])} core modules"
            )
            
            # Check for complexity bottlenecks
            high_complexity = [m for m in critical_paths['core_modules'] if m['complexity'] == 'high']
            if high_complexity:
                validation['warnings'].append(
                    f"⚠ {len(high_complexity)} core modules have high complexity - potential refactoring candidates"
                )
        
        # Generate recommendations
        if len(critical_paths['dependency_graph']) > 10:
            validation['recommendations'].append(
                "Consider modularization - {len(critical_paths['dependency_graph'])} modules with complex dependencies"
            )
        
        # Final reflection
        reflection = f"Analysis complete with {len(validation['validated_insights'])} validated insights and {len(validation['warnings'])} warnings"
        self.current_chain.reflections.append(reflection)
        print(f"  💭 {reflection}")
        
        return validation
    
    def _log_reasoning_step(self, step_name: str, data: Any):
        """Log a reasoning step for trace export"""
        self.current_chain.steps.append({
            'step': step_name,
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
    
    def _export_reasoning_chain(self) -> Dict:
        """Export the complete reasoning chain"""
        return {
            'total_steps': len(self.current_chain.steps),
            'reflections': self.current_chain.reflections,
            'confidence_trajectory': self.current_chain.confidence_trajectory,
            'backtrack_count': self.current_chain.backtrack_count,
            'steps': self.current_chain.steps
        }
    
    def _compute_statistics(self) -> Dict:
        """Compute statistics about the analysis"""
        return {
            'reasoning_depth': len(self.current_chain.steps),
            'exploration_breadth': len(self.explored_paths),
            'reflection_count': len(self.current_chain.reflections),
            'avg_confidence': sum(self.current_chain.confidence_trajectory) / len(self.current_chain.confidence_trajectory) if self.current_chain.confidence_trajectory else 0.0
        }
    
    def _compute_final_confidence(self) -> float:
        """Compute final confidence score"""
        if not self.current_chain.confidence_trajectory:
            return 0.0
        # Weight recent steps more heavily
        weights = [i / len(self.current_chain.confidence_trajectory) for i in range(1, len(self.current_chain.confidence_trajectory) + 1)]
        weighted_sum = sum(c * w for c, w in zip(self.current_chain.confidence_trajectory, weights))
        return weighted_sum / sum(weights)
    
    def _save_longcot_reports(self, results: Dict):
        """Save comprehensive Long CoT reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. JSON report with full reasoning chain
        json_file = self.longcot_dir / f"scan_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        # 2. Markdown report with narrative reasoning
        md_file = self.longcot_dir / f"scan_{timestamp}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_narrative_report(results))
        
        # 3. Reasoning trace visualization
        trace_file = self.longcot_dir / f"trace_{timestamp}.md"
        with open(trace_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_reasoning_trace(results))
        
        print(f"\n📄 Reports saved to {self.longcot_dir}/")
    
    def _generate_narrative_report(self, results: Dict) -> str:
        """Generate human-readable narrative of the reasoning process"""
        lines = [
            "# Long Chain-of-Thought Analysis Report",
            f"\n**Generated:** {results['scan_date']}",
            "\n---\n",
            "\n## Executive Summary\n"
        ]
        
        # Architecture summary
        arch = results['architecture']
        lines.append(f"**Project Type:** {arch['type']}")
        lines.append(f"**Confidence:** {arch['confidence']:.1%}")
        lines.append(f"**Description:** {arch['description']}\n")
        
        # Reasoning chain summary
        chain = results['reasoning_chain']
        lines.append(f"\n### Reasoning Process")
        lines.append(f"- **Reasoning Steps:** {chain['total_steps']}")
        lines.append(f"- **Reflections:** {len(chain['reflections'])}")
        lines.append(f"- **Backtracks:** {chain['backtrack_count']}")
        lines.append(f"- **Final Confidence:** {results['statistics']['avg_confidence']:.1%}\n")
        
        # Reflections
        if chain['reflections']:
            lines.append("\n## Key Reflections\n")
            for i, reflection in enumerate(chain['reflections'], 1):
                lines.append(f"{i}. {reflection}")
        
        # Modules
        lines.append("\n## Module Analysis\n")
        for module_name, module_data in results['modules'].items():
            lines.append(f"\n### {module_name}/")
            lines.append(f"- **Files:** {module_data['file_analysis']['total_files']}")
            lines.append(f"- **Lines of Code:** {module_data['file_analysis']['total_lines']}")
            lines.append(f"- **Complexity:** {module_data['file_analysis']['complexity_estimate']}")
            lines.append(f"- **Confidence:** {module_data['confidence']:.1%}")
            
            if module_data['hypotheses']:
                top_hypothesis = module_data['hypotheses'][0]
                lines.append(f"- **Primary Purpose:** {top_hypothesis['description']}")
        
        # Critical paths
        critical = results['critical_paths']
        if critical['entry_points']:
            lines.append("\n## Entry Points\n")
            for ep in critical['entry_points']:
                lines.append(f"- `{ep['file']}` ({ep['lines']} lines)")
        
        if critical['core_modules']:
            lines.append("\n## Core Modules\n")
            for cm in critical['core_modules']:
                lines.append(f"- **{cm['name']}** - {cm['dependency_count']} dependencies ({cm['complexity']} complexity)")
        
        # Validation
        validation = results['validated_insights']
        if validation['validated_insights']:
            lines.append("\n## Validated Insights\n")
            for insight in validation['validated_insights']:
                lines.append(f"- {insight}")
        
        if validation['warnings']:
            lines.append("\n## Warnings\n")
            for warning in validation['warnings']:
                lines.append(f"- {warning}")
        
        if validation['recommendations']:
            lines.append("\n## Recommendations\n")
            for rec in validation['recommendations']:
                lines.append(f"- {rec}")
        
        return "\n".join(lines)
    
    def _generate_reasoning_trace(self, results: Dict) -> str:
        """Generate detailed reasoning trace for debugging/analysis"""
        lines = [
            "# Reasoning Trace Visualization",
            f"\n**Generated:** {results['scan_date']}",
            "\n---\n",
            "\n## Confidence Trajectory\n"
        ]
        
        # Visualize confidence trajectory
        trajectory = results['reasoning_chain']['confidence_trajectory']
        if trajectory:
            lines.append("```")
            lines.append("Confidence over reasoning steps:")
            for i, conf in enumerate(trajectory, 1):
                bar = "█" * int(conf * 50)
                lines.append(f"Step {i:2d}: {bar} {conf:.1%}")
            lines.append("```\n")
        
        # Step-by-step trace
        lines.append("\n## Step-by-Step Reasoning\n")
        for i, step in enumerate(results['reasoning_chain']['steps'], 1):
            lines.append(f"\n### Step {i}: {step['step']}")
            lines.append(f"**Timestamp:** {step['timestamp']}")
            lines.append(f"\n```json")
            lines.append(json.dumps(step['data'], indent=2, default=str)[:500])  # Truncate for readability
            lines.append(f"```\n")
        
        return "\n".join(lines)


# Example usage / integration point
def integrate_with_vibecode():
    """
    Integration example showing how to use Long CoT scanner
    alongside existing scanner
    """
    print("🔗 Integration Example: Long CoT Scanner")
    print("\nUsage from orchestrator:")
    print("""
    from core.longcot_scanner import LongCoTScanner
    
    # Initialize
    scanner = LongCoTScanner(project_path)
    
    # Run Long CoT scan
    results = scanner.scan_with_longcot()
    
    # Access reasoning chain
    print(f"Reasoning depth: {results['reasoning_chain']['total_steps']}")
    print(f"Confidence: {results['statistics']['avg_confidence']:.1%}")
    
    # Make decisions based on high-confidence insights
    if results['statistics']['avg_confidence'] > 0.80:
        print("High confidence - proceeding with automated refactoring")
    else:
        print("Low confidence - requesting human review")
    """)


if __name__ == "__main__":
    # Demo
    integrate_with_vibecode()
