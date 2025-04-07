import re
from typing import Dict, List, Any

class CodeAnalyzer:
    def __init__(self):
        # Define language-specific patterns
        self.language_patterns = {
            'python': {
                'bugs': {
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
                    r'while\s+True\s*:': {
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
                },
                'security': {
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
                },
                'optimizations': {
                    r'for\s+(\w+)\s+in\s+range\s*\(\s*len\s*\([^)]+\)\s*\)': {
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
                    r'\.append\s*\([^)]*\)': {
                        'message': 'Using append() in a loop. Consider list comprehension.',
                        'severity': 'low',
                        'fix': {
                            'before': 'result = []\nfor x in items:\n    result.append(x)',
                            'after': 'result = [x for x in items]',
                            'explanation': 'Use list comprehension for cleaner and more efficient list creation.'
                        }
                    }
                }
            },
            'javascript': {
                'bugs': {
                    r'==\s*null': {
                        'message': 'Using == for null comparison. Use === null instead.',
                        'severity': 'medium',
                        'fix': {
                            'before': 'if (x == null)',
                            'after': 'if (x === null)',
                            'explanation': 'Use strict equality (===) for null comparison.'
                        }
                    },
                    r'var\s+\w+\s*=\s*undefined': {
                        'message': 'Using undefined as a value. Use null instead.',
                        'severity': 'medium',
                        'fix': {
                            'before': 'var x = undefined',
                            'after': 'var x = null',
                            'explanation': 'Use null for intentional absence of value.'
                        }
                    }
                },
                'security': {
                    r'eval\s*\([^)]*\)': {
                        'message': 'Using eval() is dangerous as it can execute arbitrary code.',
                        'severity': 'critical',
                        'fix': {
                            'before': 'eval(userInput)',
                            'after': '// Avoid using eval()\n// Use safer alternatives based on your needs',
                            'explanation': 'Avoid using eval() as it can execute arbitrary code.'
                        }
                    },
                    r'new\s+Function\s*\([^)]*\)': {
                        'message': 'Using Function constructor is dangerous as it can execute arbitrary code.',
                        'severity': 'critical',
                        'fix': {
                            'before': 'new Function(code)',
                            'after': '// Avoid using Function constructor\n// Use safer alternatives based on your needs',
                            'explanation': 'Avoid using Function constructor as it can execute arbitrary code.'
                        }
                    }
                },
                'optimizations': {
                    r'for\s*\(\s*var\s+\w+\s*=\s*0\s*;\s*\w+\s*<\s*array\.length\s*;\s*\w+\+\+\)': {
                        'message': 'Using traditional for loop. Consider using forEach or for...of.',
                        'severity': 'low',
                        'fix': {
                            'before': 'for (var i = 0; i < array.length; i++)',
                            'after': 'array.forEach((item, index) => {\n    // Your code here\n})',
                            'explanation': 'Use forEach or for...of for cleaner iteration.'
                        }
                    }
                }
            },
            'java': {
                'bugs': {
                    r'catch\s*\(Exception\s+e\)': {
                        'message': 'Catching generic Exception. Catch specific exceptions instead.',
                        'severity': 'high',
                        'fix': {
                            'before': 'catch (Exception e)',
                            'after': 'catch (SpecificException e)',
                            'explanation': 'Catch specific exceptions to handle errors appropriately.'
                        }
                    }
                },
                'security': {
                    r'Runtime\.exec\s*\([^)]*\)': {
                        'message': 'Using Runtime.exec() is dangerous as it can execute shell commands.',
                        'severity': 'critical',
                        'fix': {
                            'before': 'Runtime.exec(command)',
                            'after': '// Use ProcessBuilder instead\nProcessBuilder pb = new ProcessBuilder(command);\npb.start();',
                            'explanation': 'Use ProcessBuilder for safer command execution.'
                        }
                    }
                },
                'optimizations': {
                    r'for\s*\(\s*int\s+\w+\s*=\s*0\s*;\s*\w+\s*<\s*list\.size\(\)\s*;\s*\w+\+\+\)': {
                        'message': 'Using traditional for loop with list.size(). Use enhanced for loop instead.',
                        'severity': 'low',
                        'fix': {
                            'before': 'for (int i = 0; i < list.size(); i++)',
                            'after': 'for (Item item : list)',
                            'explanation': 'Use enhanced for loop for cleaner iteration.'
                        }
                    }
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
        
        # Detect language
        language = detect_language(filename, code_content)
        print(f"Analyzing code with language: {language}")
        
        # Get language-specific patterns
        patterns = self.language_patterns.get(language, self.language_patterns['python'])
        print(f"Number of bug patterns for {language}: {len(patterns['bugs'])}")
        print(f"Number of security patterns for {language}: {len(patterns['security'])}")
        print(f"Number of optimization patterns for {language}: {len(patterns['optimizations'])}")
        
        # Split code into lines for line-by-line analysis
        lines = code_content.split('\n')
        print(f"Total lines of code: {len(lines)}")
        
        # First, check for patterns in the entire code content
        # This captures patterns that might span multiple lines
        for pattern_type in ['bugs', 'security', 'optimizations']:
            for pattern, info in patterns[pattern_type].items():
                for match in re.finditer(pattern, code_content, re.MULTILINE):
                    # Find the line number of the match
                    line_number = code_content[:match.start()].count('\n') + 1
                    print(f"Found {pattern_type} issue at line {line_number}: {info['message']}")
                    
                    # Get context (3 lines before and after)
                    start_line = max(0, line_number - 4)
                    end_line = min(len(lines), line_number + 3)
                    context = '\n'.join(lines[start_line:end_line])
                    
                    results[pattern_type].append({
                        'line': line_number,
                        'message': info['message'],
                        'severity': info['severity'],
                        'code_snippet': context,
                        'fix': info['fix']
                    })
        
        # Check for line-specific patterns
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

        # Calculate metrics
        results['metrics'] = self.calculate_metrics(code_content, language)
        
        return results

    def calculate_metrics(self, code_content: str, language: str) -> Dict[str, float]:
        """Calculate code quality metrics."""
        lines = code_content.split('\n')
        total_lines = len(lines)
        code_lines = len([l for l in lines if l.strip() and not l.startswith('#')])
        
        # Calculate complexity based on control structures
        complexity_patterns = {
            'python': r'\b(if|for|while|except|elif|else)\b',
            'javascript': r'\b(if|for|while|catch|else)\b',
            'java': r'\b(if|for|while|catch|else)\b'
        }
        pattern = complexity_patterns.get(language, complexity_patterns['python'])
        complexity = len(re.findall(pattern, code_content))
        
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

def generate_test_code(language):
    """
    Generate test code with known bugs for testing purposes.
    
    Args:
        language (str): The programming language ('python', 'javascript', 'java')
        
    Returns:
        str: Code with deliberate bugs for testing
    """
    if language == 'python':
        return """
# Python code with deliberate bugs
def buggy_function():
    try:
        # Bare except
        x = 1 / 0
    except:
        print("Error occurred")
    
    # Wrong comparison with None
    if x == None:
        print("x is None")
    
    # Infinite loop
    while True:
        print("This will run forever")
    
    # Security issue
    user_input = "1 + 1"
    result = eval(user_input)
    
    # Performance issue
    items = [1, 2, 3, 4, 5]
    result = []
    for i in range(len(items)):
        result.append(items[i] * 2)
    
    # Membership test using list
    if 3 in [1, 2, 3, 4, 5]:
        print("Found it")
"""
    elif language == 'javascript':
        return """
// JavaScript code with deliberate bugs
function buggyFunction() {
    // Loose equality
    if (x == null) {
        console.log("x is null");
    }
    
    // Using undefined
    var y = undefined;
    
    // Security issue
    var userInput = "1 + 1";
    var result = eval(userInput);
    
    // Performance issue
    var array = [1, 2, 3, 4, 5];
    for (var i = 0; i < array.length; i++) {
        console.log(array[i]);
    }
}
"""
    elif language == 'java':
        return """
// Java code with deliberate bugs
public class BuggyClass {
    public void buggyMethod() {
        try {
            // Something that might throw an exception
            int x = 1 / 0;
        } catch (Exception e) {
            // Catching generic Exception
            System.out.println("Error occurred");
        }
        
        // Performance issue
        List<String> list = new ArrayList<>();
        for (int i = 0; i < list.size(); i++) {
            System.out.println(list.get(i));
        }
        
        // Security issue
        String command = "ls";
        Runtime.getRuntime().exec(command);
    }
}
"""
    else:
        return "// No test code available for this language"

def detect_language(filename=None, code_content=None):
    """
    Detect programming language from file extension or code content.
    
    Args:
        filename (str, optional): Name of the file with extension
        code_content (str, optional): Content of the code to analyze
        
    Returns:
        str: Detected language ('python', 'javascript', etc.)
    """
    # Extension to language mapping
    extension_map = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'html': 'html',
        'css': 'css',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'h': 'c',
        'hpp': 'cpp',
        'go': 'go',
        'php': 'php',
        'rb': 'ruby',
        'rs': 'rust',
        'swift': 'swift',
        'kt': 'kotlin',
        'cs': 'csharp',
        'sh': 'bash',
        'json': 'json',
        'xml': 'xml',
        'md': 'markdown',
        'yml': 'yaml',
        'yaml': 'yaml',
        'sql': 'sql'
    }
    
    # First try by file extension if filename is provided
    if filename:
        extension = filename.split('.')[-1].lower()
        if extension in extension_map:
            return extension_map[extension]
    
    # If can't detect by extension, try to detect by content patterns
    if code_content:
        # Check for Python
        if re.search(r'import\s+[a-zA-Z_]+|from\s+[a-zA-Z_]+\s+import|def\s+[a-zA-Z_]+\s*\(|class\s+[a-zA-Z_]+\s*\(?', code_content):
            return 'python'
        # Check for JavaScript/TypeScript
        elif re.search(r'const\s+[a-zA-Z_]+|let\s+[a-zA-Z_]+|var\s+[a-zA-Z_]+|function\s+[a-zA-Z_]+\s*\(|=>|async|await', code_content):
            if re.search(r'interface\s+|type\s+\w+\s*=|:\s*\w+Type', code_content):
                return 'typescript'
            return 'javascript'
        # Check for HTML
        elif re.search(r'<!DOCTYPE\s+html>|<html>|<head>|<body>|<div>|<span>|<p>', code_content, re.IGNORECASE):
            return 'html'
        # Check for CSS
        elif re.search(r'{\s*[\w-]+\s*:\s*[^;]+;\s*}', code_content) and not re.search(r'function|var|let|const', code_content):
            return 'css'
        # Check for Java
        elif re.search(r'public\s+class|private\s+class|protected\s+class|class\s+\w+\s+{|import\s+java\.', code_content):
            return 'java'
        # Check for C/C++
        elif re.search(r'#include\s+<\w+\.h>|#include\s+"[\w.]+"|void\s+\w+\s*\(|int\s+main\s*\(', code_content):
            if re.search(r'std::|namespace|template|class\s+\w+|public:|private:', code_content):
                return 'cpp'
            return 'c'
    
    # Default to Python if can't determine
    return 'python' 