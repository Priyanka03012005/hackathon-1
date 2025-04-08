#!/usr/bin/env python3
import os
import tempfile
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from code_security_analyzer import SecurityAnalyzer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(tempfile.gettempdir(), 'security_analysis')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['SNIPPETS_FILE'] = 'snippets.json'

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Check if a file was submitted
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # If user doesn't select a file, browser submits empty file
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save the uploaded file to a temporary location
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Run the security analysis
    try:
        analyzer = SecurityAnalyzer(app.config['SNIPPETS_FILE'])
        findings = analyzer.analyze_file(file_path)
        
        # Convert findings to a more UI-friendly format
        formatted_findings = []
        for finding in findings:
            formatted_findings.append({
                'file': os.path.basename(finding['file']),
                'line': finding['line'],
                'code': finding['code'],
                'vulnerability': finding['vulnerability'],
                'explanation': finding['explanation']
            })
        
        return jsonify({
            'success': True,
            'findings': formatted_findings,
            'count': len(formatted_findings)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route('/analyze-code', methods=['POST'])
def analyze_code():
    # Get code from the request
    data = request.json
    if not data or 'code' not in data or 'language' not in data:
        return jsonify({'error': 'No code or language provided'}), 400
    
    code = data['code']
    language = data['language']
    
    # Save the code to a temporary file with the appropriate extension
    ext_map = {
        'python': '.py',
        'javascript': '.js',
        'java': '.java',
        'csharp': '.cs',
        'cpp': '.cpp',
        'php': '.php',
        'ruby': '.rb',
        'go': '.go',
        'rust': '.rs',
        'swift': '.swift',
        'kotlin': '.kt'
    }
    
    ext = ext_map.get(language.lower(), '.txt')
    fd, temp_path = tempfile.mkstemp(suffix=ext)
    
    try:
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(code)
        
        # Run the security analysis
        analyzer = SecurityAnalyzer(app.config['SNIPPETS_FILE'])
        findings = analyzer.analyze_file(temp_path)
        
        # Convert findings to a more UI-friendly format
        formatted_findings = []
        for finding in findings:
            formatted_findings.append({
                'line': finding['line'],
                'code': finding['code'],
                'vulnerability': finding['vulnerability'],
                'explanation': finding['explanation']
            })
        
        return jsonify({
            'success': True,
            'findings': formatted_findings,
            'count': len(formatted_findings)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/languages')
def supported_languages():
    """Return a list of supported programming languages."""
    languages = [
        {"name": "Python", "value": "python", "extension": ".py"},
        {"name": "JavaScript", "value": "javascript", "extension": ".js"},
        {"name": "Java", "value": "java", "extension": ".java"},
        {"name": "C#", "value": "csharp", "extension": ".cs"},
        {"name": "C++", "value": "cpp", "extension": ".cpp"},
        {"name": "PHP", "value": "php", "extension": ".php"},
        {"name": "Ruby", "value": "ruby", "extension": ".rb"},
        {"name": "Go", "value": "go", "extension": ".go"},
        {"name": "Rust", "value": "rust", "extension": ".rs"},
        {"name": "Swift", "value": "swift", "extension": ".swift"},
        {"name": "Kotlin", "value": "kotlin", "extension": ".kt"}
    ]
    return jsonify(languages)

if __name__ == '__main__':
    app.run(debug=True) 