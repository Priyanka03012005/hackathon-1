class CodeAnalyzer:
    def __init__(self):
        self.bug_patterns = {
            r'print\\s*\\(.*?\\)': {
                'message': 'Potential bug found: print\\s*\\(',
                'severity': 'medium',
                'suggestion': 'Use f-strings or string formatting instead of concatenation',
                'fix': {
                    'before': 'print("Value is " + str(value))',
                    'after': 'print(f"Value is {value}")',
                    'explanation': 'Use f-strings for better readability and performance'
                }
            },
            r'print\\s*\\(.*?\\+.*?\\)': {
                'message': 'Potential bug found: string concatenation in print',
                'severity': 'medium',
                'suggestion': 'Use f-strings instead of string concatenation',
                'fix': {
                    'before': 'print("Hello " + name + "!")',
                    'after': 'print(f"Hello {name}!")',
                    'explanation': 'F-strings are more readable and efficient'
                }
            }
        }
        
        self.security_patterns = {
            r'eval\\s*\\(': {
                'message': 'Security risk: eval() function usage',
                'severity': 'high',
                'suggestion': 'Avoid using eval() as it can execute arbitrary code',
                'fix': {
                    'before': 'result = eval(expression)',
                    'after': 'result = safe_evaluate(expression)',
                    'explanation': 'Use a safe evaluation method instead of eval()'
                }
            },
            r'exec\\s*\\(': {
                'message': 'Security risk: exec() function usage',
                'severity': 'high',
                'suggestion': 'Avoid using exec() as it can execute arbitrary code',
                'fix': {
                    'before': 'exec(code_string)',
                    'after': '# Use a safer alternative or implement proper validation',
                    'explanation': 'exec() can execute arbitrary code and should be avoided'
                }
            },
            r'input\\s*\\(': {
                'message': 'Security risk: unvalidated input',
                'severity': 'medium',
                'suggestion': 'Always validate and sanitize user input',
                'fix': {
                    'before': 'user_input = input("Enter value: ")',
                    'after': 'user_input = validate_input(input("Enter value: "))',
                    'explanation': 'Validate and sanitize all user input to prevent security issues'
                }
            }
        }

    def analyze_code(self, code_content: str) -> dict:
        """Analyze code for bugs and security issues."""
        results = {
            'bugs': [],
            'security_issues': [],
            'optimizations': []
        }
        
        # Split code into lines for analysis
        lines = code_content.split('\n')
        
        # Analyze each line
        for line_num, line in enumerate(lines, 1):
            # Check for bugs
            for pattern, bug_info in self.bug_patterns.items():
                if re.search(pattern, line):
                    results['bugs'].append({
                        'line': line_num,
                        'message': bug_info['message'],
                        'severity': bug_info['severity'],
                        'code_snippet': line.strip(),
                        'suggestion': bug_info['suggestion'],
                        'fix': bug_info['fix']
                    })
            
            # Check for security issues
            for pattern, security_info in self.security_patterns.items():
                if re.search(pattern, line):
                    results['security_issues'].append({
                        'line': line_num,
                        'message': security_info['message'],
                        'severity': security_info['severity'],
                        'code_snippet': line.strip(),
                        'suggestion': security_info['suggestion'],
                        'fix': security_info['fix']
                    })
        
        return results

    def _get_context(self, lines: List[str], line_num: int, context_lines: int = 2) -> str:
        """Get context around a specific line."""
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        return '\n'.join(lines[start:end]) 