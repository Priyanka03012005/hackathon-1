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
            'typescript': r'^import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',
            'java': r'^import\s+([\w.]+);',
            'cpp': r'#include\s+[<"]([^>"]+)[>"]',
            'c': r'#include\s+[<"]([^>"]+)[>"]',
            'csharp': r'using\s+([\w.]+);',
            'go': r'^import\s+[\("]([\w./]+)["\)]',
            'ruby': r'^require\s+[\'"]([^\'"]+)[\'"]',
            'rust': r'^use\s+([\w:]+)',
            'php': r'^use\s+([\w\\]+)|^require(_once)?\s+[\'"]([^\'"]+)[\'"]|^include(_once)?\s+[\'"]([^\'"]+)[\'"]',
            'swift': r'^import\s+(\w+)',
            'kotlin': r'^import\s+([\w.]+)'
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
        """
        Analyze dependencies for a single file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            List[str]: List of dependencies found in the file
        """
        deps = []
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Map file extension to language
                language_map = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.ts': 'typescript',
                    '.jsx': 'javascript',
                    '.tsx': 'typescript',
                    '.java': 'java',
                    '.c': 'c',
                    '.cpp': 'cpp',
                    '.cs': 'csharp',
                    '.go': 'go',
                    '.rb': 'ruby',
                    '.rs': 'rust',
                    '.php': 'php',
                    '.swift': 'swift',
                    '.kt': 'kotlin'
                }
                
                language = language_map.get(ext, 'unknown')
                
                if language == 'python':
                    # Parse Python imports using AST
                    try:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.Import, ast.ImportFrom)):
                                if isinstance(node, ast.Import):
                                    deps.extend(n.name for n in node.names)
                                else:
                                    if node.module:  # module might be None for relative imports
                                        deps.append(node.module)
                    except SyntaxError:
                        # Fall back to regex if AST parsing fails
                        print(f"[WARNING] AST parsing failed for {file_path}, using regex fallback")
                        pattern = self.import_patterns.get('python')
                        for line in content.split('\n'):
                            match = re.search(pattern, line)
                            if match:
                                module = match.group(1) or match.group(2)
                                if module:
                                    deps.append(module)
                
                elif language in self.import_patterns:
                    # Use the appropriate import pattern for the language
                    pattern = self.import_patterns.get(language)
                    for match in re.finditer(pattern, content, re.MULTILINE):
                        for group in match.groups():
                            if group:
                                deps.append(group)
                
                # Log the dependencies found
                print(f"[DEBUG] Found {len(deps)} dependencies in {file_path}")
        
        except Exception as e:
            print(f"[ERROR] Error analyzing dependencies for {file_path}: {str(e)}")
        
        return deps
    
    def _is_entry_point(self, file_path: str) -> bool:
        """
        Check if a file is likely an entry point.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if the file is likely an entry point
        """
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        # Common entry point filenames by language
        entry_points = {
            '.py': {'main.py', 'app.py', 'server.py', 'run.py', 'wsgi.py', 'asgi.py', 'manage.py'},
            '.js': {'index.js', 'main.js', 'app.js', 'server.js', 'start.js'},
            '.ts': {'index.ts', 'main.ts', 'app.ts', 'server.ts', 'start.ts'},
            '.java': {'Main.java', 'Application.java', 'App.java'},
            '.c': {'main.c', 'program.c'},
            '.cpp': {'main.cpp', 'program.cpp'},
            '.cs': {'Program.cs', 'Main.cs'},
            '.go': {'main.go'},
            '.rb': {'main.rb', 'app.rb', 'server.rb'},
            '.rs': {'main.rs'},
            '.php': {'index.php', 'app.php'},
            '.swift': {'main.swift', 'app.swift'},
            '.kt': {'Main.kt', 'App.kt'}
        }
        
        # Check filename against known entry points
        if ext in entry_points and filename in entry_points[ext]:
            return True
            
        # Check content for entry point patterns
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for language-specific entry point patterns
                if ext == '.py' and '__name__ == "__main__"' in content:
                    return True
                elif ext in ('.js', '.ts') and 'module.exports' in content:
                    return True
                elif ext == '.java' and 'public static void main(' in content:
                    return True
                elif ext in ('.c', '.cpp') and 'int main(' in content:
                    return True
                elif ext == '.go' and 'func main()' in content:
                    return True
                elif ext == '.rb' and 'if __FILE__ == $0' in content:
                    return True
                elif ext == '.php' and '<?php' in content and not re.search(r'^\s*class\s+', content, re.MULTILINE):
                    return True
        except Exception as e:
            print(f"[WARNING] Error checking if {file_path} is an entry point: {str(e)}")
        
        return False
    
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

def analyze_code_with_context(code_content: str, file_path: str, project_root: str) -> List:
    """
    Analyze code with project context awareness.
    
    Args:
        code_content (str): Content of the code to analyze
        file_path (str): Path to the file
        project_root (str): Root directory of the project
        
    Returns:
        List: List of suggestions based on context analysis
    """
    analyzer = ProjectContextAnalyzer(project_root)
    context = analyzer.get_file_context(file_path)
    
    # Get file extension and language
    file_ext = os.path.splitext(file_path)[1].lower()
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.cs': 'csharp',
        '.go': 'go',
        '.rb': 'ruby',
        '.rs': 'rust',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin'
    }
    language = language_map.get(file_ext, 'unknown')
    
    # Enhanced analysis based on context and language
    suggestions = []
    
    # Add context-aware suggestions
    if context['is_entry_point']:
        suggestions.append({
            'type': 'context',
            'message': 'This is an entry point file. Consider adding proper error handling and logging.',
            'severity': 'medium'
        })
    
    # Analyze dependencies
    if len(context['dependencies']) > 10:
        suggestions.append({
            'type': 'context',
            'message': 'High number of dependencies. Consider modularizing the code.',
            'severity': 'low'
        })
    
    # Check for circular dependencies
    if any(file_path in analyzer._get_dependent_files(dep, context['project_structure']['dependencies'])
           for dep in context['dependencies']):
        suggestions.append({
            'type': 'context',
            'message': 'Potential circular dependency detected.',
            'severity': 'high'
        })
    
    # Language-specific suggestions
    if language == 'python':
        if '__main__' in code_content and not '__name__ == "__main__"' in code_content:
            suggestions.append({
                'type': 'context',
                'message': 'Code may execute when imported. Consider using if __name__ == "__main__" guard.',
                'severity': 'medium'
            })
    elif language == 'javascript' or language == 'typescript':
        if 'document.write(' in code_content:
            suggestions.append({
                'type': 'context',
                'message': 'document.write() is not recommended as it can overwrite the entire document.',
                'severity': 'high'
            })
    elif language == 'java':
        if 'public static void main' in code_content and 'System.exit' not in code_content:
            suggestions.append({
                'type': 'context',
                'message': 'Entry point missing proper exit handling. Consider adding System.exit().',
                'severity': 'low'
            })
    
    return suggestions 