import re
from typing import Dict, List, Any

class CodeAnalyzer:
    def __init__(self):
        # Define bug patterns with fixes
        self.bug_patterns = {
            r'except\s*:': {
                'message': 'Bare except clause detected. This can mask errors and make debugging difficult.',
                'severity': 'high',
                'fix': {
                    'before': 'except:',
                    'after': 'except Exception as e:',
                    'explanation': 'Use specific exception handling to catch only expected exceptions.'
                }
            },
            r'if\s+[^=]+==\s*None': {
                'message': 'Using == for None comparison. Use is None instead.',
                'severity': 'medium',
                'fix': {
                    'before': 'if x == None:',
                    'after': 'if x is None:',
                    'explanation': 'Use is None for None comparison as it is more explicit and efficient.'
                }
            },
            r'while\s+True:': {
                'message': 'Infinite loop detected. Add a break condition.',
                'severity': 'high',
                'fix': {
                    'before': 'while True:',
                    'after': 'while True:\n    # Add a break condition\n    if condition:\n        break',
                    'explanation': 'Add a break condition to prevent infinite loops.'
                }
            },
            r'print\s*\([^)]*\)': {
                'message': 'Using print statement in production code. Use logging instead.',
                'severity': 'medium',
                'fix': {
                    'before': 'print("message")',
                    'after': 'import logging\nlogging.info("message")',
                    'explanation': 'Use logging for better debugging and production code.'
                }
            }
        }
        
        # Define security patterns with fixes
        self.security_patterns = {
            r'eval\s*\([^)]*\)': {
                'message': 'Using eval() is dangerous as it can execute arbitrary code.',
                'severity': 'critical',
                'fix': {
                    'before': 'eval(user_input)',
                    'after': '# Use safer alternatives like ast.literal_eval()\nimport ast\nast.literal_eval(user_input)',
                    'explanation': 'Use ast.literal_eval() for safely evaluating string literals.'
                }
            },
            r'exec\s*\([^)]*\)': {
                'message': 'Using exec() is dangerous as it can execute arbitrary code.',
                'severity': 'critical',
                'fix': {
                    'before': 'exec(user_input)',
                    'after': '# Avoid using exec()\n# Use safer alternatives based on your needs',
                    'explanation': 'Avoid using exec() as it can execute arbitrary code.'
                }
            },
            r'os\.system\s*\([^)]*\)': {
                'message': 'Using os.system() is dangerous as it can execute shell commands.',
                'severity': 'critical',
                'fix': {
                    'before': 'os.system(command)',
                    'after': 'import subprocess\nsubprocess.run(command, shell=False)',
                    'explanation': 'Use subprocess.run() with shell=False for safer command execution.'
                }
            }
        }
        
        # Define optimization patterns with fixes
        self.optimization_patterns = {
            r'for\s+(\w+)\s+in\s+range\(len\([^)]+\)\)': {
                'message': 'Using range(len()) for iteration. Use enumerate() instead.',
                'severity': 'low',
                'fix': {
                    'before': 'for i in range(len(items)):',
                    'after': 'for i, item in enumerate(items):',
                    'explanation': 'Use enumerate() for cleaner and more Pythonic iteration.'
                }
            },
            r'if\s+(\w+)\s+in\s+\[[^\]]+\]': {
                'message': 'Using list for membership testing. Use set for better performance.',
                'severity': 'low',
                'fix': {
                    'before': 'if x in [1, 2, 3]:',
                    'after': 'if x in {1, 2, 3}:',
                    'explanation': 'Use set for O(1) membership testing.'
                }
            },
            r'\.append\([^)]*\)\s*in\s+loop': {
                'message': 'Using append() in a loop. Consider list comprehension.',
                'severity': 'low',
                'fix': {
                    'before': 'result = []\nfor x in items:\n    result.append(x)',
                    'after': 'result = [x for x in items]',
                    'explanation': 'Use list comprehension for cleaner and more efficient list creation.'
                }
            }
        }

    def analyze_code(self, code_content: str, filename: str) -> Dict[str, Any]:
        """Analyze code for bugs, security issues, and optimization opportunities."""
        results = {
            'bugs': [],
            'security': [],
            'optimizations': [],
            'metrics': {
                'complexity': 0,
                'maintainability': 0,
                'performance': 0
            }
        }
        
        # Split code into lines for line-by-line analysis
        lines = code_content.split('\n')
        
        # Analyze each line
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Check for bugs
            for pattern, info in self.bug_patterns.items():
                if re.search(pattern, line):
                    # Get context (3 lines before and after)
                    start = max(0, i - 4)
                    end = min(len(lines), i + 3)
                    context = '\n'.join(lines[start:end])
                    
                    results['bugs'].append({
                        'line': i,
                        'message': info['message'],
                        'severity': info['severity'],
                        'code_snippet': context,
                        'fix': info['fix']
                    })
            
            # Check for security issues
            for pattern, info in self.security_patterns.items():
                if re.search(pattern, line):
                    # Get context (3 lines before and after)
                    start = max(0, i - 4)
                    end = min(len(lines), i + 3)
                    context = '\n'.join(lines[start:end])
                    
                    results['security'].append({
                        'line': i,
                        'message': info['message'],
                        'severity': info['severity'],
                        'code_snippet': context,
                        'fix': info['fix']
                    })
            
            # Check for optimization opportunities
            for pattern, info in self.optimization_patterns.items():
                if re.search(pattern, line):
                    # Get context (3 lines before and after)
                    start = max(0, i - 4)
                    end = min(len(lines), i + 3)
                    context = '\n'.join(lines[start:end])
                    
                    results['optimizations'].append({
                        'line': i,
                        'message': info['message'],
                        'severity': info['severity'],
                        'code_snippet': context,
                        'fix': info['fix']
                    })
        
        # Calculate metrics
        results['metrics'] = self.calculate_metrics(code_content)
        
        return results

    def calculate_metrics(self, code_content: str) -> Dict[str, float]:
        """Calculate code quality metrics."""
        lines = code_content.split('\n')
        total_lines = len(lines)
        code_lines = len([l for l in lines if l.strip() and not l.startswith('#')])
        
        # Calculate complexity based on control structures
        complexity = len(re.findall(r'\b(if|for|while|except)\b', code_content))
        
        # Calculate maintainability based on function length and nesting
        maintainability = 100 - (complexity * 10) - (code_lines / 10)
        maintainability = max(0, min(100, maintainability))
        
        # Calculate performance score based on optimization patterns
        performance = 100 - (len(re.findall(r'\.append\([^)]*\)\s*in\s+loop', code_content)) * 10)
        performance = max(0, min(100, performance))
        
        return {
            'complexity': complexity,
            'maintainability': round(maintainability, 2),
            'performance': round(performance, 2)
        }

# Create a global instance of the analyzer
code_analyzer = CodeAnalyzer() 