import re
from typing import Dict, List, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os

class AIOptimizer:
    def __init__(self):
        # Initialize TF-IDF vectorizer for code analysis
        self.vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 4),
            max_features=1000
        )
        
        # Define optimization patterns with weights and fixes
        self.optimization_patterns = {
            'loop_optimization': {
                'patterns': [
                    r'for\s+\w+\s+in\s+range\s*\(len\s*\(',
                    r'while\s+True:',
                    r'for\s+\w+\s+in\s+range\s*\(0\):',
                ],
                'weight': 0.3,
                'suggestions': [
                    'Consider using list comprehension',
                    'Use generator expressions for large datasets',
                    'Implement early exit conditions'
                ],
                'fixes': {
                    r'for\s+\w+\s+in\s+range\s*\(len\s*\(': {
                        'before': 'for i in range(len(my_list)):\n    print(my_list[i])',
                        'after': 'for item in my_list:\n    print(item)',
                        'explanation': 'Using direct iteration is more Pythonic and efficient'
                    },
                    r'while\s+True:': {
                        'before': 'while True:\n    if condition:\n        break',
                        'after': 'while not condition:\n    # your code here',
                        'explanation': 'Using a proper condition in while loop is clearer and safer'
                    }
                }
            },
            'data_structure': {
                'patterns': [
                    r'list\.append\s*\(',
                    r'\+=\s*\[',
                    r'\.join\s*\(',
                ],
                'weight': 0.2,
                'suggestions': [
                    'Use set for unique elements',
                    'Consider using deque for queue operations',
                    'Use defaultdict for counting'
                ],
                'fixes': {
                    r'list\.append\s*\(': {
                        'before': 'my_list = []\nfor item in items:\n    my_list.append(item)',
                        'after': 'my_list = [item for item in items]',
                        'explanation': 'List comprehension is more concise and efficient'
                    }
                }
            },
            'algorithm': {
                'patterns': [
                    r'sorted\s*\(',
                    r'\.sort\s*\(',
                    r'\.index\s*\(',
                ],
                'weight': 0.25,
                'suggestions': [
                    'Use binary search for sorted data',
                    'Consider using hash tables',
                    'Implement memoization for recursive functions'
                ],
                'fixes': {
                    r'\.index\s*\(': {
                        'before': 'try:\n    index = my_list.index(value)\nexcept ValueError:\n    index = -1',
                        'after': 'index = my_list.index(value) if value in my_list else -1',
                        'explanation': 'Using conditional expression is more concise'
                    }
                }
            },
            'memory': {
                'patterns': [
                    r'\[x\s+for\s+x\s+in\s+',
                    r'\.copy\s*\(',
                    r'list\s*\(',
                ],
                'weight': 0.15,
                'suggestions': [
                    'Use generators instead of lists',
                    'Implement lazy loading',
                    'Use memory-efficient data structures'
                ],
                'fixes': {
                    r'\[x\s+for\s+x\s+in\s+': {
                        'before': 'squares = [x**2 for x in range(1000)]',
                        'after': 'squares = (x**2 for x in range(1000))',
                        'explanation': 'Using generator expression saves memory for large datasets'
                    }
                }
            },
            'io_operations': {
                'patterns': [
                    r'open\s*\([^)]*\)',
                    r'\.read\s*\(',
                    r'\.write\s*\(',
                ],
                'weight': 0.1,
                'suggestions': [
                    'Use context managers for file operations',
                    'Implement buffering for large files',
                    'Use async/await for I/O operations'
                ],
                'fixes': {
                    r'open\s*\([^)]*\)': {
                        'before': 'f = open("file.txt")\ntry:\n    data = f.read()\nfinally:\n    f.close()',
                        'after': 'with open("file.txt") as f:\n    data = f.read()',
                        'explanation': 'Using context manager ensures proper file handling'
                    }
                }
            }
        }
        
        # Load pre-trained model if available
        self.model_path = os.path.join(os.path.dirname(__file__), 'models', 'optimization_model.joblib')
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        else:
            self.model = None

    def analyze_code(self, code_content: str, filename: str) -> Dict[str, Any]:
        """Analyze code for optimization opportunities using AI and pattern matching."""
        results = {
            'optimizations': [],
            'performance_score': 100,
            'suggestions': [],
            'complexity_metrics': self._calculate_complexity_metrics(code_content),
            'ai_suggestions': []
        }
        
        # Split code into lines for analysis
        lines = code_content.split('\n')
        
        # Analyze each line for optimization patterns
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Check each optimization category
            for category, config in self.optimization_patterns.items():
                for pattern in config['patterns']:
                    if re.search(pattern, line):
                        # Calculate severity based on pattern match
                        severity = self._calculate_severity(line, pattern, config['weight'])
                        
                        # Get fix suggestion if available
                        fix = config.get('fixes', {}).get(pattern, {})
                        
                        # Add optimization suggestion with fix
                        results['optimizations'].append({
                            'message': f'Potential {category} optimization',
                            'line': i,
                            'severity': severity,
                            'category': category,
                            'suggestions': config['suggestions'],
                            'fix': fix,
                            'code_snippet': line
                        })
        
        # Calculate performance score
        results['performance_score'] = self._calculate_performance_score(results['optimizations'])
        
        # Generate AI-based suggestions if model is available
        if self.model:
            results['ai_suggestions'] = self._generate_ai_suggestions(code_content)
        
        # Add general suggestions based on analysis
        results['suggestions'].extend(self._generate_suggestions(results))
        
        return results
    
    def _calculate_complexity_metrics(self, code: str) -> Dict[str, float]:
        """Calculate code complexity metrics."""
        metrics = {
            'cyclomatic_complexity': 0,
            'cognitive_complexity': 0,
            'maintainability_index': 0,
            'duplication_percentage': 0
        }
        
        # Calculate cyclomatic complexity
        control_structures = len(re.findall(r'\b(if|for|while|except|finally|with)\b', code))
        functions = len(re.findall(r'\bdef\s+\w+\s*\(', code))
        classes = len(re.findall(r'\bclass\s+\w+\s*\(', code))
        
        metrics['cyclomatic_complexity'] = control_structures + functions + classes + 1
        
        # Calculate cognitive complexity
        nested_structures = len(re.findall(r'if\s+.*?if\s+', code))
        loops = len(re.findall(r'\b(for|while)\b', code))
        conditions = len(re.findall(r'\bif\b', code))
        
        metrics['cognitive_complexity'] = (nested_structures * 2) + loops + conditions
        
        # Calculate maintainability index
        loc = len(code.split('\n'))
        comments = len(re.findall(r'#.*$', code, re.MULTILINE))
        docstrings = len(re.findall(r'""".*?"""', code, re.DOTALL))
        
        metrics['maintainability_index'] = min(100, (comments + docstrings * 2) / max(1, loc) * 100)
        
        # Calculate code duplication percentage
        lines = code.split('\n')
        unique_lines = set(lines)
        metrics['duplication_percentage'] = ((len(lines) - len(unique_lines)) / max(1, len(lines))) * 100
        
        return metrics
    
    def _calculate_severity(self, line: str, pattern: str, weight: float) -> str:
        """Calculate severity of optimization issue."""
        # Count occurrences of pattern in line
        occurrences = len(re.findall(pattern, line))
        
        # Calculate base severity
        if occurrences > 2:
            return 'high'
        elif occurrences > 1:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_performance_score(self, optimizations: List[Dict]) -> float:
        """Calculate performance score based on optimization issues."""
        if not optimizations:
            return 100
        
        # Weight issues by severity and category
        weights = {'high': 3, 'medium': 2, 'low': 1}
        total_weight = sum(
            weights[opt['severity']] * self.optimization_patterns[opt['category']]['weight']
            for opt in optimizations
        )
        
        # Calculate performance score (0-100)
        performance_score = max(0, 100 - (total_weight * 10))
        return performance_score
    
    def _generate_ai_suggestions(self, code_content: str) -> List[Dict]:
        """Generate AI-based optimization suggestions."""
        if not self.model:
            return []
        
        # Vectorize code content
        code_vector = self.vectorizer.transform([code_content])
        
        # Get model predictions
        predictions = self.model.predict_proba(code_vector)[0]
        
        # Generate suggestions based on predictions
        suggestions = []
        for i, prob in enumerate(predictions):
            if prob > 0.5:  # Confidence threshold
                suggestions.append({
                    'message': f'AI-suggested optimization (confidence: {prob:.2f})',
                    'severity': 'medium',
                    'category': 'ai_suggestion'
                })
        
        return suggestions
    
    def _generate_suggestions(self, results: Dict) -> List[Dict]:
        """Generate context-aware suggestions based on analysis results."""
        suggestions = []
        
        # Generate suggestions based on complexity metrics
        if results['complexity_metrics']['cyclomatic_complexity'] > 10:
            suggestions.append({
                'message': 'Consider breaking down complex functions into smaller, more manageable pieces',
                'severity': 'medium'
            })
        
        if results['complexity_metrics']['cognitive_complexity'] > 15:
            suggestions.append({
                'message': 'Reduce nesting levels and simplify control flow',
                'severity': 'medium'
            })
        
        if results['complexity_metrics']['maintainability_index'] < 50:
            suggestions.append({
                'message': 'Add more documentation and comments to improve code maintainability',
                'severity': 'low'
            })
        
        # Generate suggestions based on optimization categories
        categories = set(opt['category'] for opt in results['optimizations'])
        for category in categories:
            if category in self.optimization_patterns:
                suggestions.append({
                    'message': f'Review {category} patterns and consider applying suggested optimizations',
                    'severity': 'medium'
                })
        
        return suggestions

# Create a global instance of the optimizer
ai_optimizer = AIOptimizer() 