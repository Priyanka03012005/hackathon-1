#!/usr/bin/env python3
import json
import re
import sys
import os
from pathlib import Path

class SecurityAnalyzer:
    def __init__(self, snippets_file):
        self.vulnerabilities = {}
        self.load_snippets(snippets_file)
        self.add_additional_patterns()
        
    def load_snippets(self, snippets_file):
        """Load vulnerability patterns from the JSON file."""
        try:
            with open(snippets_file, 'r') as f:
                self.snippets = json.load(f)
        except Exception as e:
            print(f"Error loading snippets file: {e}")
            sys.exit(1)
            
        # Create a lookup of patterns for each language
        for lang, data in self.snippets.items():
            # Extract the key parts from the vulnerable code that might indicate a vulnerability
            vulnerable_code = data['code']['vulnerable']
            
            # Create simplified pattern based on the vulnerability type
            if data['vulnerability'] == "Remote Code Execution (RCE)":
                if lang == "Python":
                    self.vulnerabilities.setdefault(lang, []).append(
                        {"pattern": r"eval\s*\(.*\)", "vulnerability": data['vulnerability'], "explanation": data['explanation']}
                    )
                elif lang == "PHP":
                    self.vulnerabilities.setdefault(lang, []).append(
                        {"pattern": r"eval\s*\(\s*\$.*\)", "vulnerability": data['vulnerability'], "explanation": data['explanation']}
                    )
            
            elif data['vulnerability'] == "SQL Injection (SQLi)" or data['vulnerability'] == "SQL Injection":
                if lang == "Java":
                    self.vulnerabilities.setdefault(lang, []).append(
                        {"pattern": r"executeQuery\s*\([\"'].*\+", "vulnerability": data['vulnerability'], "explanation": data['explanation']}
                    )
                elif lang == "C#":
                    self.vulnerabilities.setdefault(lang, []).append(
                        {"pattern": r"SELECT.*FROM.*WHERE.*=\s*['\"]\s*\+", "vulnerability": data['vulnerability'], "explanation": data['explanation']}
                    )
                elif lang == "Python":
                    self.vulnerabilities.setdefault(lang, []).append(
                        {"pattern": r"SELECT.*FROM.*WHERE.*=\s*[\'\"]?\{.*\}|f[\"']SELECT", "vulnerability": "SQL Injection (SQLi)", 
                         "explanation": "Use parameterized queries with placeholders instead of string formatting in SQL queries."}
                    )
            
            elif data['vulnerability'] == "Cross-site Scripting (XSS)":
                if lang == "JavaScript":
                    self.vulnerabilities.setdefault(lang, []).append(
                        {"pattern": r"(innerHTML|outerHTML)\s*=", "vulnerability": data['vulnerability'], "explanation": data['explanation']}
                    )
            
            elif data['vulnerability'] == "Buffer Overflow":
                if lang == "C++":
                    self.vulnerabilities.setdefault(lang, []).append(
                        {"pattern": r"strcpy\s*\(", "vulnerability": data['vulnerability'], "explanation": data['explanation']}
                    )
            
            elif data['vulnerability'] == "Command Injection":
                if lang == "Go":
                    self.vulnerabilities.setdefault(lang, []).append(
                        {"pattern": r"exec\.Command\s*\(\s*[\"']bash[\"']\s*,\s*[\"']-c[\"']\s*,", "vulnerability": data['vulnerability'], "explanation": data['explanation']}
                    )
                elif lang == "Ruby":
                    self.vulnerabilities.setdefault(lang, []).append(
                        {"pattern": r"system\s*\([\"'].*#\{", "vulnerability": data['vulnerability'], "explanation": data['explanation']}
                    )
            
            elif data['vulnerability'] == "Hardcoded Secrets":
                if lang == "Kotlin":
                    self.vulnerabilities.setdefault(lang, []).append(
                        {"pattern": r"val\s+\w+\s*=\s*[\"'][\w\-]+[\"']", "vulnerability": data['vulnerability'], "explanation": data['explanation']}
                    )
            
            elif data['vulnerability'] == "Panic from unwrap":
                if lang == "Rust":
                    self.vulnerabilities.setdefault(lang, []).append(
                        {"pattern": r"\.unwrap\(\)", "vulnerability": data['vulnerability'], "explanation": data['explanation']}
                    )
            
            elif data['vulnerability'] == "Force Unwrapping":
                if lang == "Swift":
                    self.vulnerabilities.setdefault(lang, []).append(
                        {"pattern": r"try!", "vulnerability": data['vulnerability'], "explanation": data['explanation']}
                    )
    
    def add_additional_patterns(self):
        """Add additional vulnerability patterns not found in the snippets file."""
        # JavaScript additional vulnerabilities
        js_vulnerabilities = [
            {
                "pattern": r"eval\s*\(.+\)", 
                "vulnerability": "Remote Code Execution (RCE)", 
                "explanation": "Avoid using eval() with user input in JavaScript as it can lead to code execution vulnerabilities."
            },
            {
                "pattern": r"document\.write\s*\(", 
                "vulnerability": "Cross-site Scripting (XSS)", 
                "explanation": "Avoid using document.write() with untrusted data as it can lead to XSS vulnerabilities."
            },
            {
                "pattern": r"setTimeout\s*\(\s*['\"]", 
                "vulnerability": "Code Injection", 
                "explanation": "Avoid passing strings to setTimeout() or setInterval() as they use eval() internally."
            },
            {
                "pattern": r"new\s+Function\s*\(", 
                "vulnerability": "Code Injection", 
                "explanation": "Avoid using the Function constructor with user input as it creates functions from strings, similar to eval()."
            },
            {
                "pattern": r"localStorage\.(get|set)Item\s*\(\s*['\"]password['\"]", 
                "vulnerability": "Insecure Storage", 
                "explanation": "Don't store sensitive data like passwords in localStorage as it's accessible to any script from the same origin."
            }
        ]
        
        for vuln in js_vulnerabilities:
            self.vulnerabilities.setdefault("JavaScript", []).append(vuln)
        
        # Python additional vulnerabilities
        py_vulnerabilities = [
            {
                "pattern": r"subprocess\.(call|Popen|run)\s*\(\s*.*shell\s*=\s*True", 
                "vulnerability": "Command Injection", 
                "explanation": "Avoid using shell=True with subprocess as it can lead to command injection vulnerabilities."
            },
            {
                "pattern": r"pickle\.(loads|load)", 
                "vulnerability": "Insecure Deserialization", 
                "explanation": "Avoid using pickle with untrusted data as it can lead to remote code execution."
            },
            {
                "pattern": r"yaml\.load\s*\(.*Loader\s*=\s*None\)|yaml\.load\s*\([^,)]+\)", 
                "vulnerability": "YAML Deserialization", 
                "explanation": "Use yaml.safe_load() instead of yaml.load() to prevent code execution from YAML."
            },
            {
                "pattern": r"hashlib\.md5\s*\(", 
                "vulnerability": "Weak Cryptography", 
                "explanation": "MD5 is cryptographically broken. Use a stronger hash algorithm like SHA-256."
            }
        ]
        
        for vuln in py_vulnerabilities:
            self.vulnerabilities.setdefault("Python", []).append(vuln)
    
    def get_supported_extensions(self):
        """Return a list of supported file extensions."""
        return [
            '.py', '.php', '.java', '.js', '.jsx', '.ts', '.tsx',
            '.cpp', '.cc', '.c', '.h', '.hpp', '.cs', '.go', 
            '.kt', '.rb', '.rs', '.swift'
        ]
    
    def detect_language(self, file_path):
        """Detect programming language based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        
        lang_map = {
            '.py': 'Python',
            '.php': 'PHP',
            '.java': 'Java',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript',
            '.ts': 'JavaScript',
            '.tsx': 'JavaScript',
            '.cpp': 'C++',
            '.cc': 'C++',
            '.c': 'C++',
            '.h': 'C++',
            '.hpp': 'C++',
            '.cs': 'C#',
            '.go': 'Go',
            '.kt': 'Kotlin',
            '.rb': 'Ruby',
            '.rs': 'Rust',
            '.swift': 'Swift'
        }
        
        return lang_map.get(ext)
    
    def analyze_file(self, file_path):
        """Analyze a file for security vulnerabilities."""
        language = self.detect_language(file_path)
        
        if not language or language not in self.vulnerabilities:
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []
        
        findings = []
        
        for vuln_data in self.vulnerabilities[language]:
            pattern = vuln_data['pattern']
            for line_no, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    findings.append({
                        'file': file_path,
                        'line': line_no,
                        'code': line.strip(),
                        'vulnerability': vuln_data['vulnerability'],
                        'explanation': vuln_data['explanation']
                    })
        
        return findings
    
    def analyze_directory(self, directory, extensions=None):
        """Recursively analyze all files in a directory."""
        findings = []
        
        if extensions is None:
            extensions = self.get_supported_extensions()
            
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                # Skip files that don't match our extensions
                if file_ext not in extensions:
                    continue
                
                # Skip files in certain directories
                if '.git' in root.split(os.sep) or 'node_modules' in root.split(os.sep):
                    continue
                    
                # Skip any binary or packaged files
                if os.path.getsize(file_path) > 1024 * 1024:  # Skip files larger than 1MB
                    continue
                
                file_findings = self.analyze_file(file_path)
                findings.extend(file_findings)
        
        return findings

def format_output(findings, output_json=False):
    """Format the findings into a readable output."""
    if output_json:
        return json.dumps(findings, indent=2)
    
    if not findings:
        return "No security vulnerabilities found."
    
    # Group findings by file
    findings_by_file = {}
    for finding in findings:
        if finding['file'] not in findings_by_file:
            findings_by_file[finding['file']] = []
        findings_by_file[finding['file']].append(finding)
    
    output = []
    total_vulnerabilities = len(findings)
    output.append(f"Found {total_vulnerabilities} potential security issue{'' if total_vulnerabilities == 1 else 's'}:")
    
    for file_path, file_findings in findings_by_file.items():
        output.append(f"\n{file_path}:")
        
        # Sort findings by line number
        file_findings.sort(key=lambda x: x['line'])
        
        for i, finding in enumerate(file_findings, 1):
            output.append(f"  {i}. {finding['vulnerability']} at line {finding['line']}")
            output.append(f"     Code: {finding['code']}")
            output.append(f"     Fix: {finding['explanation']}")
    
    return "\n".join(output)

def main():
    if len(sys.argv) < 3:
        print("Usage: python code_security_analyzer.py snippets.json path1 [path2 ...] [--json] [--all-files]")
        sys.exit(1)
    
    snippets_file = sys.argv[1]
    paths = []
    
    # Parse arguments
    output_json = False
    scan_all_files = False
    
    for arg in sys.argv[2:]:
        if arg == "--json":
            output_json = True
        elif arg == "--all-files":
            scan_all_files = True
        else:
            paths.append(arg)
    
    if not paths:
        print("Error: No paths specified for analysis.")
        sys.exit(1)
    
    analyzer = SecurityAnalyzer(snippets_file)
    all_findings = []
    
    print(f"Analyzing {len(paths)} path(s)...")
    
    for path in paths:
        print(f"Scanning: {path}")
        if os.path.isfile(path):
            findings = analyzer.analyze_file(path)
            print(f"  Found {len(findings)} issues in file.")
            all_findings.extend(findings)
        else:
            if scan_all_files:
                findings = analyzer.analyze_directory(path, extensions=None)
            else:
                findings = analyzer.analyze_directory(path)
            print(f"  Found {len(findings)} issues in directory.")
            all_findings.extend(findings)
    
    # Sort findings by file path and line number
    all_findings.sort(key=lambda x: (x['file'], x['line']))
    
    print(f"Total findings: {len(all_findings)}")
    
    try:
        output = format_output(all_findings, output_json)
        print(output)
    except BrokenPipeError:
        # If output is being piped and the pipe is broken, exit gracefully
        sys.stderr.close()
        sys.exit(0)

if __name__ == "__main__":
    main() 