from flask import Blueprint, request, jsonify
from app.repo_manager import repo_manager
from app.context_analyzer import analyze_code_with_context
from app.suggestion_history import suggestion_history
import os

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/analyze', methods=['POST'])
def analyze_code():
    """API endpoint for code analysis from IDEs."""
    data = request.get_json()
    
    if not data or 'code' not in data:
        return jsonify({'error': 'No code provided'}), 400
    
    code_content = data['code']
    filename = data.get('filename', 'untitled.py')
    repo_name = data.get('repository')
    file_path = data.get('file_path')
    user_id = data.get('user_id')  # Optional: for tracking suggestion history
    
    try:
        # If repository is specified, use its context
        if repo_name:
            repo = repo_manager.get_repository(repo_name)
            if not repo:
                return jsonify({'error': f'Repository {repo_name} not found'}), 404
            project_root = repo.local_path or os.path.dirname(os.path.abspath(__file__))
        else:
            project_root = os.path.dirname(os.path.abspath(__file__))
        
        # Perform context-aware analysis
        analysis = analyze_code_with_context(code_content, filename, project_root)
        
        # If user_id is provided, handle suggestion history
        if user_id:
            all_suggestions = []
            
            # Combine all types of suggestions
            for category in ['bugs', 'security', 'optimizations', 'suggestions']:
                for item in analysis.get(category, []):
                    suggestion = {
                        'type': category[:-1],  # Remove 's' from plural
                        'message': item.get('message'),
                        'line': item.get('line'),
                        'severity': item.get('severity')
                    }
                    all_suggestions.append(suggestion)
            
            # Filter redundant suggestions
            filtered_suggestions = suggestion_history.filter_redundant_suggestions(
                user_id, all_suggestions
            )
            
            # Add new suggestions to history
            suggestion_history.add_suggestions(user_id, filtered_suggestions)
            
            # Update analysis with filtered suggestions
            analysis['filtered_suggestions'] = filtered_suggestions
        
        return jsonify({
            'status': 'success',
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/repositories', methods=['GET'])
def list_repositories():
    """List all managed repositories."""
    try:
        repos = repo_manager.list_repositories()
        return jsonify({
            'status': 'success',
            'repositories': [
                {
                    'name': repo.name,
                    'url': repo.url,
                    'last_synced': repo.last_synced.isoformat(),
                    'is_active': repo.is_active
                }
                for repo in repos
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/repositories', methods=['POST'])
def add_repository():
    """Add a new repository."""
    data = request.get_json()
    
    if not data or 'name' not in data or 'url' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        repo = repo_manager.add_repository(
            name=data['name'],
            url=data['url'],
            github_token=data.get('github_token')
        )
        return jsonify({
            'status': 'success',
            'repository': {
                'name': repo.name,
                'url': repo.url,
                'last_synced': repo.last_synced.isoformat(),
                'is_active': repo.is_active
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/repositories/<name>', methods=['DELETE'])
def remove_repository(name):
    """Remove a repository."""
    try:
        repo_manager.remove_repository(name)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/repositories/<name>/sync', methods=['POST'])
def sync_repository(name):
    """Sync a repository with GitHub."""
    try:
        result = repo_manager.sync_with_github(name)
        return jsonify({
            'status': 'success',
            'github_data': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 