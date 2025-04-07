import re
from typing import Dict, List, Any

class CodeAnalyzer:
    def __init__(self):
        # Define bug patterns
        self.bug_patterns = [
            r'except\s*:',  # Bare except clause
            r'global\s+\w+',  # Global variable usage
            r'assert\s+',  # Assert statements
            r'print\s*\(',  # Print statements in production code
            r'pass\s*$',  # Empty pass statements
            r'while\s+True:',  # Infinite loops
            r'break\s*$',  # Break statements
            r'continue\s*$',  # Continue statements
            r'return\s+None',  # Explicit None returns
            r'except\s+Exception\s+as\s+\w+:',  # Generic exception handling
            r'if\s+True:',  # Unnecessary if True
            r'if\s+False:',  # Unnecessary if False
            r'while\s+False:',  # Unnecessary while False
            r'for\s+\w+\s+in\s+range\s*\(0\):',  # Empty range loop
            r'def\s+\w+\s*\([^)]*\)\s*:\s*pass',  # Empty function
            r'class\s+\w+\s*\([^)]*\)\s*:\s*pass',  # Empty class
            r'lambda\s+[^:]+:\s*None',  # Empty lambda
            r'raise\s+Exception\s*\(',  # Generic exception raising
            r'except\s+Exception\s+as\s+\w+:\s*pass',  # Silent exception handling
            r'finally:\s*pass',  # Empty finally block
        ]
        
        # Define security patterns
        self.security_patterns = [
            r'eval\s*\(',  # eval() usage
            r'exec\s*\(',  # exec() usage
            r'os\.system\s*\(',  # os.system() usage
            r'subprocess\.call\s*\(',  # subprocess.call() usage
            r'input\s*\(',  # input() usage
            r'pickle\.loads\s*\(',  # pickle.loads() usage
            r'json\.loads\s*\(',  # json.loads() usage
            r'open\s*\([^)]*\)',  # File operations
            r'sqlite3\.connect\s*\(',  # Database connections
            r'requests\.get\s*\(',  # HTTP requests
            r'password\s*=\s*["\'].*["\']',  # Hardcoded passwords
            r'secret\s*=\s*["\'].*["\']',  # Hardcoded secrets
            r'key\s*=\s*["\'].*["\']',  # Hardcoded keys
            r'\.decode\s*\(["\']utf-8["\']\)',  # Unsafe decode
            r'\.encode\s*\(["\']utf-8["\']\)',  # Unsafe encode
            r'random\.random\s*\(',  # Weak random
            r'random\.randint\s*\(',  # Weak random
            r'random\.choice\s*\(',  # Weak random
            r'random\.randrange\s*\(',  # Weak random
            r'random\.uniform\s*\(',  # Weak random
        ]
        
        # Define optimization patterns
        self.optimization_patterns = [
            r'for\s+\w+\s+in\s+range\s*\(len\s*\(',  # Range-based for loops
            r'list\.append\s*\(',  # List append in loops
            r'\+=\s*\[',  # List concatenation
            r'\.join\s*\(',  # String join
            r'sorted\s*\(',  # Sorting operations
            r'\.sort\s*\(',  # In-place sorting
            r'\.index\s*\(',  # List index operations
            r'\.count\s*\(',  # List count operations
            r'\.remove\s*\(',  # List remove operations
            r'\.pop\s*\(',  # List pop operations
            r'\+=\s*["\']',  # String concatenation
            r'\.format\s*\(',  # Old-style string formatting
            r'%[sdf]',  # Old-style string formatting
            r'\.strip\s*\(\)',  # Multiple strip calls
            r'\.lower\s*\(\)',  # Multiple lower calls
            r'\.upper\s*\(\)',  # Multiple upper calls
            r'\.split\s*\(\)',  # Multiple split calls
            r'\.replace\s*\(',  # Multiple replace calls
            r'\.startswith\s*\(',  # Multiple startswith calls
            r'\.endswith\s*\(',  # Multiple endswith calls
            r'\.isdigit\s*\(\)',  # Multiple isdigit calls
            r'\.isalpha\s*\(\)',  # Multiple isalpha calls
        ]

    def analyze_code(self, code_content: str, filename: str) -> Dict[str, Any]:
        """Analyze code using pattern matching and static analysis."""
        results = {
            'bugs': [],
            'security': [],
            'optimizations': [],
            'suggestions': [],
            'complexity_score': 0,
            'maintainability_score': 0,
            'security_score': 0,
            'performance_score': 0,
            'reliability_score': 0
        }
        
        # Split code into lines for analysis
        lines = code_content.split('\n')
        
        # Analyze each line for bugs
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Check for bug patterns
            for pattern in self.bug_patterns:
                if re.search(pattern, line):
                    results['bugs'].append({
                        'message': f'Potential bug found: {pattern}',
                        'line': i,
                        'severity': 'medium'
                    })
            
            # Check for security patterns
            for pattern in self.security_patterns:
                if re.search(pattern, line):
                    results['security'].append({
                        'message': f'Potential security issue: {pattern}',
                        'line': i,
                        'severity': 'high'
                    })
            
            # Check for optimization patterns
            for pattern in self.optimization_patterns:
                if re.search(pattern, line):
                    results['optimizations'].append({
                        'message': f'Potential optimization: {pattern}',
                        'line': i,
                        'severity': 'low'
                    })
        
        # Calculate code quality metrics
        results['complexity_score'] = self._calculate_complexity(code_content)
        results['maintainability_score'] = self._calculate_maintainability(code_content)
        results['security_score'] = self._calculate_security_score(results['security'])
        results['performance_score'] = self._calculate_performance_score(results['optimizations'])
        results['reliability_score'] = self._calculate_reliability_score(results['bugs'])
        
        # Add context-aware suggestions
        results['suggestions'].extend(self._generate_suggestions(results))
        
        return results
    
    def _calculate_complexity(self, code: str) -> float:
        """Calculate code complexity score."""
        # Count control structures
        control_structures = len(re.findall(r'\b(if|for|while|except|finally|with)\b', code))
        # Count function definitions
        functions = len(re.findall(r'\bdef\s+\w+\s*\(', code))
        # Count class definitions
        classes = len(re.findall(r'\bclass\s+\w+\s*\(', code))
        
        # Calculate complexity score (0-100)
        complexity = min(100, (control_structures * 10 + functions * 15 + classes * 20))
        return max(0, 100 - complexity)  # Invert so higher is better
    
    def _calculate_maintainability(self, code: str) -> float:
        """Calculate code maintainability score."""
        # Count lines of code
        loc = len(code.split('\n'))
        # Count comments
        comments = len(re.findall(r'#.*$', code, re.MULTILINE))
        # Count docstrings
        docstrings = len(re.findall(r'""".*?"""', code, re.DOTALL))
        
        # Calculate maintainability score (0-100)
        maintainability = min(100, (comments + docstrings * 2) / max(1, loc) * 100)
        return maintainability
    
    def _calculate_security_score(self, security_issues: List[Dict]) -> float:
        """Calculate security score based on security issues."""
        if not security_issues:
            return 100
        
        # Weight issues by severity
        weights = {'high': 3, 'medium': 2, 'low': 1}
        total_weight = sum(weights[issue['severity']] for issue in security_issues)
        
        # Calculate security score (0-100)
        security_score = max(0, 100 - (total_weight * 10))
        return security_score
    
    def _calculate_performance_score(self, optimizations: List[Dict]) -> float:
        """Calculate performance score based on optimization opportunities."""
        if not optimizations:
            return 100
        
        # Weight issues by severity
        weights = {'high': 3, 'medium': 2, 'low': 1}
        total_weight = sum(weights[issue['severity']] for issue in optimizations)
        
        # Calculate performance score (0-100)
        performance_score = max(0, 100 - (total_weight * 5))
        return performance_score
    
    def _calculate_reliability_score(self, bugs: List[Dict]) -> float:
        """Calculate reliability score based on bugs."""
        if not bugs:
            return 100
        
        # Weight issues by severity
        weights = {'high': 3, 'medium': 2, 'low': 1}
        total_weight = sum(weights[bug['severity']] for bug in bugs)
        
        # Calculate reliability score (0-100)
        reliability_score = max(0, 100 - (total_weight * 8))
        return reliability_score
    
    def _generate_suggestions(self, results: Dict) -> List[Dict]:
        """Generate context-aware suggestions based on analysis results."""
        suggestions = []
        
        # Generate suggestions based on bugs
        if results['bugs']:
            suggestions.append({
                'message': 'Consider adding more error handling and input validation',
                'severity': 'medium'
            })
        
        # Generate suggestions based on security issues
        if results['security']:
            suggestions.append({
                'message': 'Review security best practices and consider using safer alternatives',
                'severity': 'high'
            })
        
        # Generate suggestions based on optimizations
        if results['optimizations']:
            suggestions.append({
                'message': 'Consider using more efficient data structures and algorithms',
                'severity': 'low'
            })
        
        # Generate suggestions based on complexity
        if results['complexity_score'] < 50:
            suggestions.append({
                'message': 'Consider breaking down complex functions into smaller, more manageable pieces',
                'severity': 'medium'
            })
        
        # Generate suggestions based on maintainability
        if results['maintainability_score'] < 50:
            suggestions.append({
                'message': 'Add more documentation and comments to improve code maintainability',
                'severity': 'low'
            })
        
        return suggestions

# Create a global instance of the analyzer
code_analyzer = CodeAnalyzer() 