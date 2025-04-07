import os
import ast
import re
from typing import Dict, List, Set, Tuple
import importlib.util
import sys

class ProjectContextAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.file_dependencies = {}
        self.import_patterns = {
            'python': r'^import\s+(\w+)|^from\s+(\w+)\s+import',
            'javascript': r'^import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',
            'typescript': r'^import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
        }
    
    def analyze_project_structure(self) -> Dict:
        """Analyze the project structure and dependencies."""
        structure = {
            'files': [],
            'dependencies': {},
            'entry_points': []
        }
        
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.project_root)
                    structure['files'].append(rel_path)
                    
                    # Analyze file dependencies
                    deps = self._analyze_file_dependencies(file_path)
                    structure['dependencies'][rel_path] = deps
                    
                    # Identify entry points
                    if self._is_entry_point(file_path):
                        structure['entry_points'].append(rel_path)
        
        return structure
    
    def _analyze_file_dependencies(self, file_path: str) -> List[str]:
        """Analyze dependencies for a single file."""
        deps = []
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if ext == '.py':
                    # Parse Python imports
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.Import, ast.ImportFrom)):
                            if isinstance(node, ast.Import):
                                deps.extend(n.name for n in node.names)
                            else:
                                deps.append(node.module)
                
                elif ext in ('.js', '.ts', '.jsx', '.tsx'):
                    # Parse JavaScript/TypeScript imports
                    pattern = self.import_patterns.get(ext[1:], self.import_patterns['javascript'])
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    deps.extend(match.group(1) for match in matches)
        
        except Exception as e:
            print(f"Error analyzing dependencies for {file_path}: {str(e)}")
        
        return deps
    
    def _is_entry_point(self, file_path: str) -> bool:
        """Check if a file is likely an entry point."""
        filename = os.path.basename(file_path)
        return (
            filename in ('main.py', 'index.js', 'app.py', 'server.py') or
            filename.startswith('run') or
            filename.endswith('_main.py')
        )
    
    def get_file_context(self, file_path: str) -> Dict:
        """Get context information for a specific file."""
        rel_path = os.path.relpath(file_path, self.project_root)
        structure = self.analyze_project_structure()
        
        return {
            'file_path': rel_path,
            'dependencies': structure['dependencies'].get(rel_path, []),
            'dependent_files': self._get_dependent_files(rel_path, structure['dependencies']),
            'is_entry_point': rel_path in structure['entry_points'],
            'file_type': os.path.splitext(file_path)[1].lower(),
            'project_structure': structure
        }
    
    def _get_dependent_files(self, file_path: str, dependencies: Dict) -> List[str]:
        """Find files that depend on the given file."""
        deps = []
        for other_file, other_deps in dependencies.items():
            if file_path in other_deps:
                deps.append(other_file)
        return deps

def analyze_code_with_context(code_content: str, file_path: str, project_root: str) -> Dict:
    """Analyze code with project context awareness."""
    analyzer = ProjectContextAnalyzer(project_root)
    context = analyzer.get_file_context(file_path)
    
    # Enhanced analysis based on context
    analysis = {
        'context': context,
        'suggestions': [],
        'warnings': [],
        'improvements': []
    }
    
    # Add context-aware suggestions
    if context['is_entry_point']:
        analysis['suggestions'].append({
            'type': 'entry_point',
            'message': 'This is an entry point file. Consider adding proper error handling and logging.',
            'severity': 'info'
        })
    
    # Analyze dependencies
    if len(context['dependencies']) > 10:
        analysis['warnings'].append({
            'type': 'dependencies',
            'message': 'High number of dependencies. Consider modularizing the code.',
            'severity': 'warning'
        })
    
    # Check for circular dependencies
    if any(file_path in analyzer._get_dependent_files(dep, context['project_structure']['dependencies'])
           for dep in context['dependencies']):
        analysis['warnings'].append({
            'type': 'circular_dependency',
            'message': 'Potential circular dependency detected.',
            'severity': 'warning'
        })
    
    return analysis 