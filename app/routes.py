from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime

main_bp = Blueprint('main', __name__)

# Mock database (will be replaced with a real database)
users = {}
code_history = {}
current_id = 0

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users and check_password_hash(users[email]['password'], password):
            session['user_id'] = email
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@main_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if email in users:
            flash('Email already exists')
        else:
            users[email] = {
                'name': name,
                'password': generate_password_hash(password),
                'created_at': datetime.now()
            }
            session['user_id'] = email
            return redirect(url_for('main.dashboard'))
    
    return render_template('signup.html')

@main_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user = users.get(session['user_id'])
    user_history = code_history.get(session['user_id'], [])
    
    stats = {
        'total_scans': len(user_history),
        'bugs_found': sum(scan.get('bugs_count', 0) for scan in user_history),
        'security_issues': sum(scan.get('security_count', 0) for scan in user_history),
        'optimizations': sum(scan.get('optimization_count', 0) for scan in user_history)
    }
    
    return render_template('dashboard.html', user=user, stats=stats, recent_scans=user_history[:5])

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        code_content = request.form.get('code_content')
        filename = request.form.get('filename', 'untitled.py')
        language = request.form.get('language', 'python')
        
        # Process uploaded file if any
        if 'code_file' in request.files:
            file = request.files['code_file']
            if file.filename:
                filename = file.filename
                code_content = file.read().decode('utf-8')
        
        if not code_content:
            flash('No code provided')
            return redirect(url_for('main.upload'))
        
        # Process the code with AI (mock for now)
        global current_id
        scan_id = current_id
        current_id += 1
        
        # Mock analysis results
        analysis = {
            'id': scan_id,
            'filename': filename,
            'language': language,
            'timestamp': datetime.now(),
            'bugs': [
                {'line': 10, 'severity': 'high', 'message': 'Potential null reference', 'suggestion': 'Add null check'},
                {'line': 25, 'severity': 'medium', 'message': 'Unused variable', 'suggestion': 'Remove or use the variable'}
            ],
            'security': [
                {'line': 15, 'severity': 'critical', 'message': 'SQL Injection vulnerability', 'suggestion': 'Use parameterized queries'}
            ],
            'optimizations': [
                {'line': 30, 'severity': 'info', 'message': 'Inefficient loop', 'suggestion': 'Use list comprehension'}
            ],
            'bugs_count': 2,
            'security_count': 1,
            'optimization_count': 1
        }
        
        # Save to history
        if session['user_id'] not in code_history:
            code_history[session['user_id']] = []
        
        code_history[session['user_id']].append(analysis)
        
        return redirect(url_for('main.report', scan_id=scan_id))
    
    return render_template('upload.html')

@main_bp.route('/report/<int:scan_id>')
def report(scan_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_scans = code_history.get(session['user_id'], [])
    scan = next((s for s in user_scans if s['id'] == scan_id), None)
    
    if not scan:
        flash('Scan not found')
        return redirect(url_for('main.dashboard'))
    
    return render_template('report.html', scan=scan)

@main_bp.route('/optimization/<int:scan_id>')
def optimization(scan_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_scans = code_history.get(session['user_id'], [])
    scan = next((s for s in user_scans if s['id'] == scan_id), None)
    
    if not scan:
        flash('Scan not found')
        return redirect(url_for('main.dashboard'))
    
    return render_template('optimization.html', scan=scan)

@main_bp.route('/code-completion', methods=['GET', 'POST'])
def code_completion():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    completed_code = None
    
    if request.method == 'POST':
        code_content = request.form.get('code_content')
        language = request.form.get('language', 'python')
        
        if not code_content:
            flash('No code provided')
        else:
            # Mock AI completion (in real app, this would call an AI service)
            completed_code = code_content + "\n\n# AI-completed code\ndef optimize_algorithm():\n    print('Optimized!')\n    return True\n"
    
    return render_template('code_completion.html', completed_code=completed_code)

@main_bp.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_history = code_history.get(session['user_id'], [])
    return render_template('history.html', scans=user_history)

@main_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user = users.get(session['user_id'])
    
    if request.method == 'POST':
        name = request.form.get('name')
        github_link = request.form.get('github_link')
        theme = request.form.get('theme')
        
        # Update user settings
        user['name'] = name
        user['github_link'] = github_link
        user['theme'] = theme
        
        flash('Settings updated successfully')
    
    return render_template('settings.html', user=user) 