# AI Code Reviewer

A web application that leverages AI to review and improve code quality.

## Features

- Automated code reviews
- Code optimization suggestions
- Security vulnerability detection
- Best practices recommendations

## Tech Stack

- Python / Flask
- HTML / CSS / JavaScript
- Machine Learning for code analysis

## Setup

1. Clone the repository:
```
git clone https://github.com/yourusername/ai-code-reviewer.git
cd ai-code-reviewer
```

2. Create a virtual environment and activate it:
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run the application:
```
python run.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
ai-code-reviewer/
├── app/
│   ├── __init__.py      # Flask application factory
│   └── routes.py        # Route definitions
├── static/
│   ├── css/
│   │   └── style.css    # Main stylesheet
│   ├── js/
│   │   └── main.js      # JavaScript functionality
│   └── img/             # Images directory
├── templates/
│   ├── base.html        # Base template with layout
│   ├── index.html       # Home page
│   └── about.html       # About page
├── run.py               # Application entry point
└── requirements.txt     # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 