from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime, timedelta
from app.context_analyzer import analyze_code_with_context
from app.suggestion_history import suggestion_history
from app.repo_manager import repo_manager
from app.ai_model import code_analyzer, detect_language, generate_test_code
from app.ai_optimizer import ai_optimizer
from app.ollama_integration import ollama_code_llama

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
    
    # Basic stats
    stats = {
        'total_scans': len(user_history),
        'bugs_found': sum(scan.get('bugs_count', 0) for scan in user_history),
        'security_issues': sum(scan.get('security_count', 0) for scan in user_history),
        'optimizations': sum(scan.get('optimization_count', 0) for scan in user_history)
    }
    
    # Prepare data for trend chart (last 7 days)
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    trend_data = {
        'dates': dates,
        'scans': [0] * 7,
        'bugs': [0] * 7,
        'security': [0] * 7,
        'optimizations': [0] * 7
    }
    
    for scan in user_history:
        scan_date = scan['timestamp'].strftime('%Y-%m-%d')
        if scan_date in dates:
            idx = dates.index(scan_date)
            trend_data['scans'][idx] += 1
            trend_data['bugs'][idx] += scan.get('bugs_count', 0)
            trend_data['security'][idx] += scan.get('security_count', 0)
            trend_data['optimizations'][idx] += scan.get('optimization_count', 0)
    
    # Prepare data for language distribution
    language_stats = {}
    for scan in user_history:
        lang = scan.get('language', 'Unknown')
        language_stats[lang] = language_stats.get(lang, 0) + 1
    
    # Prepare data for code quality metrics
    quality_metrics = {
        'complexity': sum(scan.get('complexity_score', 0) for scan in user_history) / max(len(user_history), 1),
        'maintainability': sum(scan.get('maintainability_score', 0) for scan in user_history) / max(len(user_history), 1),
        'security': sum(scan.get('security_score', 0) for scan in user_history) / max(len(user_history), 1),
        'performance': sum(scan.get('performance_score', 0) for scan in user_history) / max(len(user_history), 1),
        'reliability': sum(scan.get('reliability_score', 0) for scan in user_history) / max(len(user_history), 1)
    }
    
    # Prepare data for activity heatmap
    activity_data = {
        'hours': list(range(24)),
        'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'data': [[0] * 24 for _ in range(7)]  # 7 days x 24 hours
    }
    
    for scan in user_history:
        day = scan['timestamp'].weekday()
        hour = scan['timestamp'].hour
        activity_data['data'][day][hour] += 1
    
    return render_template('dashboard.html', 
                         user=user, 
                         stats=stats, 
                         recent_scans=user_history[:5],
                         trend_data=trend_data,
                         language_stats=language_stats,
                         quality_metrics=quality_metrics,
                         activity_data=activity_data)

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        code_content = request.form.get('code_content')
        filename = request.form.get('filename', 'untitled.py')
        
        # Process uploaded file if any
        if 'code_file' in request.files:
            file = request.files['code_file']
            if file.filename:
                filename = file.filename
                code_content = file.read().decode('utf-8')
        
        if not code_content:
            flash('No code provided')
            return redirect(url_for('main.upload'))
        
        # Auto-detect language based on file extension and code content
        language = detect_language(filename, code_content)
        
        # Process the code with AI and context awareness
        global current_id
        scan_id = current_id
        current_id += 1
        
        try:
            # Use the system's temp directory instead of app directory
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_file_path = os.path.join(temp_dir, f'ai_code_reviewer_{scan_id}_{filename}')
            
            # Write the code to the temporary file
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write(code_content)
            
            # Get project root (using the temp directory as project root)
            project_root = temp_dir
            
            # Get Ollama setting from session
            use_ollama = session.get('use_ollama', True)
            print(f"[DEBUG] Upload: use_ollama setting = {use_ollama}")
            
            try:
                if use_ollama:
                    # Update Ollama URL if set in session
                    ollama_url = session.get('ollama_url', 'http://localhost:11434')
                    print(f"[DEBUG] Upload: Ollama URL = {ollama_url}")
                    
                    # Update the Ollama URL
                    ollama_code_llama.base_url = ollama_url
                    ollama_code_llama.api_url = f"{ollama_url}/api/generate"
                    print(f"[DEBUG] Upload: Set API URL to {ollama_code_llama.api_url}")
                    
                    # Check if Ollama is available
                    ollama_available = ollama_code_llama.check_availability()
                    print(f"[DEBUG] Upload: Ollama availability check result = {ollama_available}")
                    
                    if ollama_available:
                        print(f"[INFO] Using Ollama Code Llama model at {ollama_url} for analysis")
                        try:
                            print(f"[DEBUG] Upload: Starting Ollama code analysis for {language}")
                            ai_analysis = ollama_code_llama.analyze_code(code_content, language)
                            print(f"[SUCCESS] Ollama analysis completed with {len(ai_analysis.get('bugs', []))} bugs, " +
                                  f"{len(ai_analysis.get('security', []))} security issues, and " +
                                  f"{len(ai_analysis.get('optimizations', []))} optimization suggestions")
                            
                            # Add model info
                            model_info = {
                                'name': f"Ollama {ollama_code_llama.model_name}",
                                'is_ollama': True,
                                'url': ollama_url
                            }
                        except Exception as ollama_error:
                            print(f"[ERROR] Ollama analysis failed: {str(ollama_error)}")
                            print(f"[INFO] Falling back to rule-based analyzer")
                            flash(f"Ollama analysis failed: {str(ollama_error)}. Using rule-based analyzer instead.", "warning")
                            ai_analysis = code_analyzer.analyze_code(code_content, filename)
                            
                            # Add model info
                            model_info = {
                                'name': "Pattern Matcher (Fallback)",
                                'is_ollama': False,
                                'reason': str(ollama_error)
                            }
                    else:
                        print(f"[ERROR] Ollama not available at {ollama_url}")
                        print(f"[INFO] Falling back to rule-based analyzer")
                        flash("Ollama server not available. Using rule-based analyzer instead.", "warning")
                        ai_analysis = code_analyzer.analyze_code(code_content, filename)
                        
                        # Add model info
                        model_info = {
                            'name': "Pattern Matcher (Fallback)",
                            'is_ollama': False,
                            'reason': "Ollama server not available"
                        }
                else:
                    print("[INFO] Rule-based analyzer selected per user settings")
                    ai_analysis = code_analyzer.analyze_code(code_content, filename)
                    
                    # Add model info
                    model_info = {
                        'name': "Pattern Matcher",
                        'is_ollama': False
                    }
            except Exception as e:
                print(f"[ERROR] Critical error during analysis setup: {str(e)}")
                flash(f"Analysis setup error: {str(e)}. Using rule-based analyzer.", "danger")
                # Fall back to built-in analyzer if any error occurs
                ai_analysis = code_analyzer.analyze_code(code_content, filename)
                
                # Add model info
                model_info = {
                    'name': "Pattern Matcher (Error Recovery)",
                    'is_ollama': False,
                    'reason': str(e)
                }

            # Add debug prints
            print(f"Detected language: {language}")
            print(f"Number of bugs found: {len(ai_analysis.get('bugs', []))}")
            print(f"Number of security issues found: {len(ai_analysis.get('security', []))}")
            print(f"Number of optimization issues found: {len(ai_analysis.get('optimizations', []))}")
            
            # Perform context-aware analysis
            context_analysis = analyze_code_with_context(code_content, temp_file_path, project_root)
            
            # Combine all suggestions
            all_suggestions = []
            
            # Add bugs from AI analysis
            for bug in ai_analysis.get('bugs', []):
                all_suggestions.append({
                    'type': 'bug',
                    'message': bug['message'],
                    'line': bug['line'],
                    'severity': bug['severity']
                })
            
            # Add security issues from AI analysis
            for security in ai_analysis.get('security', []):
                all_suggestions.append({
                    'type': 'security',
                    'message': security['message'],
                    'line': security['line'],
                    'severity': security['severity']
                })
            
            # Add optimizations from AI analysis
            for optimization in ai_analysis.get('optimizations', []):
                all_suggestions.append({
                    'type': 'optimization',
                    'message': optimization['message'],
                    'line': optimization['line'],
                    'severity': optimization['severity']
                })
            
            # Add context-aware suggestions
            for suggestion in context_analysis.get('suggestions', []):
                all_suggestions.append({
                    'type': 'context',
                    'message': suggestion['message'],
                    'severity': suggestion['severity']
                })
            
            # Filter out redundant suggestions
            filtered_suggestions = suggestion_history.filter_redundant_suggestions(
                session['user_id'], 
                all_suggestions
            )
            
            # Add new suggestions to history
            suggestion_history.add_suggestions(session['user_id'], filtered_suggestions)
            
            # Organize filtered suggestions back into categories
            bugs = [s for s in filtered_suggestions if s['type'] == 'bug']
            security = [s for s in filtered_suggestions if s['type'] == 'security']
            optimizations = [s for s in filtered_suggestions if s['type'] == 'optimization']
            context_suggestions = [s for s in filtered_suggestions if s['type'] == 'context']
            
            # Combine with existing analysis
            analysis = {
                'id': scan_id,
                'filename': filename,
                'language': language,
                'timestamp': datetime.now(),
                'code_content': code_content,  # Save the original code content
                'bugs': ai_analysis.get('bugs', []),
                'security': ai_analysis.get('security', []),
                'optimizations': ai_analysis.get('optimizations', []),
                'bugs_count': len(bugs),
                'security_count': len(security),
                'optimization_count': len(optimizations),
                'complexity_score': ai_analysis.get('metrics', {}).get('complexity', 0),
                'maintainability_score': ai_analysis.get('metrics', {}).get('maintainability', 0),
                'performance_score': ai_analysis.get('metrics', {}).get('performance', 0),
                'context_analysis': {
                    **context_analysis,
                    'suggestions': context_suggestions
                },
                # Include the metrics object to match the template
                'metrics': ai_analysis.get('metrics', {
                    'complexity': 0,
                    'maintainability': 0,
                    'performance': 0
                }),
                # Add model info
                'model_info': model_info
            }
            
            # Save to history
            if session['user_id'] not in code_history:
                code_history[session['user_id']] = []
            
            code_history[session['user_id']].append(analysis)
            
            return redirect(url_for('main.report', scan_id=scan_id))
            
        except Exception as e:
            flash(f'Error processing code: {str(e)}')
            return redirect(url_for('main.upload'))
            
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception as e:
                print(f'Error cleaning up temporary file: {str(e)}')
    
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
    
    # Find the scan in user's history
    scan = None
    for s in code_history.get(session['user_id'], []):
        if s['id'] == scan_id:
            scan = s
            break
    
    if not scan:
        flash('Scan not found')
        return redirect(url_for('main.dashboard'))
    
    # Get the code content from the scan
    code_content = scan.get('code_content', '')
    
    # Analyze code with AI optimizer
    optimization_results = ai_optimizer.analyze_code(code_content, scan['filename'])
    
    # Update scan with optimization results
    scan.update({
        'optimizations': [],  # Clear existing optimizations
        'performance_score': optimization_results['performance_score'],
        'complexity_metrics': optimization_results['complexity_metrics']
    })
    
    # Process each optimization result
    for opt in optimization_results['optimizations']:
        # Get the actual code snippet from the file
        lines = code_content.split('\n')
        line_number = opt['line']
        if 1 <= line_number <= len(lines):
            code_snippet = lines[line_number - 1].strip()
            
            # Create optimization entry with code snippet
            optimization_entry = {
                'message': opt['message'],
                'line': line_number,
                'severity': opt['severity'],
                'code_snippet': code_snippet,
                'suggestions': opt['suggestions'],
                'fix': None
            }
            
            # Add fix if available
            if opt.get('fix'):
                optimization_entry['fix'] = {
                    'before': code_snippet,
                    'after': opt['fix'].get('after', ''),
                    'explanation': opt['fix'].get('explanation', '')
                }
            
            scan['optimizations'].append(optimization_entry)
    
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
    
    if request.method == 'POST':
        # Update settings in session
        ai_model = request.form.get('ai_model', 'default')
        print(f"[DEBUG] Settings: ai_model form value = '{ai_model}'")
        
        # Explicitly set use_ollama to True or False based on the selection
        if ai_model == 'ollama':
            session['use_ollama'] = True
            print("[DEBUG] Settings: Enabling Ollama integration")
        else:
            session['use_ollama'] = False
            print("[DEBUG] Settings: Disabling Ollama integration")
        
        # Store the Ollama URL
        ollama_url = request.form.get('ollama_url', 'http://localhost:11434')
        session['ollama_url'] = ollama_url
        print(f"[DEBUG] Settings: Setting Ollama URL to {ollama_url}")
        
        # Update context setting
        session['use_context'] = 'use_context' in request.form
        
        # Update Ollama URL if it changed and Ollama is enabled
        if session['use_ollama'] and session['ollama_url']:
            ollama_code_llama.base_url = session['ollama_url']
            ollama_code_llama.api_url = f"{session['ollama_url']}/api/generate"
            print(f"[DEBUG] Settings: Updated Ollama API URL to {ollama_code_llama.api_url}")
        
        flash('Settings updated successfully', 'success')
        return redirect(url_for('main.settings'))
    
    # Debug current session settings
    print(f"[DEBUG] Current session settings: use_ollama = {session.get('use_ollama', 'Not set')}")
    print(f"[DEBUG] Current session settings: ollama_url = {session.get('ollama_url', 'Not set')}")
    
    return render_template('settings.html')

@main_bp.route('/check_ollama', methods=['GET'])
def check_ollama():
    print("[DEBUG] check_ollama route called")
    url = request.args.get('url', 'http://localhost:11434')
    print(f"[DEBUG] check_ollama: Checking URL {url}")
    
    # Temporarily update the Ollama URL
    from app.ollama_integration import OllamaCodeLlama
    temp_ollama = OllamaCodeLlama(base_url=url)
    
    try:
        is_available = temp_ollama.check_availability()
        print(f"[DEBUG] check_ollama: Availability result = {is_available}")
        
        if is_available:
            return jsonify({
                'available': True,
                'model': temp_ollama.model_name
            })
        else:
            return jsonify({
                'available': False,
                'message': 'Ollama is not available or the model could not be loaded. Make sure Ollama is running and the URL is correct.'
            })
    except Exception as e:
        print(f"[ERROR] check_ollama: Error checking availability: {str(e)}")
        return jsonify({
            'available': False,
            'error': str(e),
            'message': 'An error occurred while checking Ollama availability.'
        })

@main_bp.route('/suggestion-history')
def suggestion_history_view():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    history = suggestion_history.get_suggestion_history(session['user_id'])
    return render_template('suggestion_history.html', history=history)

@main_bp.route('/clear-history', methods=['POST'])
def clear_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    suggestion_history.clear_history(session['user_id'])
    flash('Suggestion history cleared successfully')
    return redirect(url_for('main.suggestion_history_view'))

@main_bp.route('/repositories')
def repositories():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    repositories = repo_manager.list_repositories()
    return render_template('repositories.html', repositories=repositories)

@main_bp.route('/test_bug_detection/<language>')
def test_bug_detection(language):
    """Test route to verify bug detection is working."""
    if language not in ['python', 'javascript', 'java']:
        language = 'python'
    
    # Generate test code with known bugs
    test_code = generate_test_code(language)
    filename = f"test.{language}"
    
    # Use the code analyzer to detect bugs
    analysis = code_analyzer.analyze_code(test_code, filename)
    
    # Return the results as JSON
    return jsonify({
        'language': language,
        'code': test_code,
        'bugs': analysis.get('bugs', []),
        'security': analysis.get('security', []),
        'optimizations': analysis.get('optimizations', []),
        'metrics': analysis.get('metrics', {})
    }) 