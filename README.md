# Code Security Analyzer

A web-based tool for detecting security vulnerabilities in code across multiple programming languages.

## Features

- Analyze code snippets directly in the browser
- Upload files for security analysis
- Support for multiple programming languages:
  - Python
  - JavaScript
  - Java
  - C#
  - C++
  - PHP
  - Ruby
  - Go
  - Rust
  - Swift
  - Kotlin
- Detection of common security vulnerabilities:
  - Remote Code Execution (RCE)
  - SQL Injection
  - Cross-site Scripting (XSS)
  - Buffer Overflow
  - Command Injection
  - Hardcoded Secrets
  - And more...

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python security_analyzer_ui.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Command-Line Usage

You can also use the security analyzer from the command line:

```bash
# Analyze a single file
python code_security_analyzer.py snippets.json path/to/file.py

# Analyze multiple files
python code_security_analyzer.py snippets.json file1.py file2.js

# Analyze a directory
python code_security_analyzer.py snippets.json path/to/directory

# Output results in JSON format
python code_security_analyzer.py snippets.json path/to/file.py --json
```

## How It Works

The security analyzer uses pattern matching to detect potentially vulnerable code patterns based on a database of known security vulnerabilities. It compares your code against these patterns and identifies matches that could indicate security risks.

## Security Database

The security vulnerability patterns are stored in `snippets.json`, which includes:
- Vulnerability type
- Vulnerable code patterns
- Secure alternatives
- Explanations of the vulnerabilities

## Contributing

Feel free to contribute by adding new vulnerability patterns to `snippets.json` or improving the detection algorithms.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 