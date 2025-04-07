import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import requests
from pathlib import Path

@dataclass
class Repository:
    name: str
    url: str
    local_path: Optional[str]
    github_token: Optional[str]
    last_synced: datetime
    is_active: bool

class RepoManager:
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.repos: Dict[str, Repository] = {}
        self.config_file = os.path.join(workspace_dir, 'repo_config.json')
        self._load_config()

    def _load_config(self):
        """Load repository configuration from file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                for repo_data in config.get('repositories', []):
                    self.repos[repo_data['name']] = Repository(
                        name=repo_data['name'],
                        url=repo_data['url'],
                        local_path=repo_data.get('local_path'),
                        github_token=repo_data.get('github_token'),
                        last_synced=datetime.fromisoformat(repo_data['last_synced']),
                        is_active=repo_data.get('is_active', True)
                    )

    def _save_config(self):
        """Save repository configuration to file."""
        config = {
            'repositories': [
                {
                    'name': repo.name,
                    'url': repo.url,
                    'local_path': repo.local_path,
                    'github_token': repo.github_token,
                    'last_synced': repo.last_synced.isoformat(),
                    'is_active': repo.is_active
                }
                for repo in self.repos.values()
            ]
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def add_repository(self, name: str, url: str, github_token: Optional[str] = None) -> Repository:
        """Add a new repository to manage."""
        if name in self.repos:
            raise ValueError(f"Repository {name} already exists")

        local_path = os.path.join(self.workspace_dir, 'repos', name)
        repo = Repository(
            name=name,
            url=url,
            local_path=local_path,
            github_token=github_token,
            last_synced=datetime.now(),
            is_active=True
        )
        self.repos[name] = repo
        self._save_config()
        return repo

    def remove_repository(self, name: str):
        """Remove a repository from management."""
        if name not in self.repos:
            raise ValueError(f"Repository {name} not found")
        
        del self.repos[name]
        self._save_config()

    def get_repository(self, name: str) -> Optional[Repository]:
        """Get repository by name."""
        return self.repos.get(name)

    def list_repositories(self) -> List[Repository]:
        """List all managed repositories."""
        return list(self.repos.values())

    def sync_with_github(self, repo_name: str):
        """Sync repository with GitHub."""
        repo = self.get_repository(repo_name)
        if not repo or not repo.github_token:
            raise ValueError("Repository not found or GitHub token not configured")

        headers = {
            'Authorization': f'token {repo.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        # Get repository information from GitHub
        response = requests.get(f'https://api.github.com/repos/{repo_name}', headers=headers)
        if response.status_code == 200:
            repo.last_synced = datetime.now()
            self._save_config()
            return response.json()
        else:
            raise Exception(f"Failed to sync with GitHub: {response.status_code}")

    def get_file_content(self, repo_name: str, file_path: str) -> Optional[str]:
        """Get file content from a repository."""
        repo = self.get_repository(repo_name)
        if not repo:
            raise ValueError(f"Repository {repo_name} not found")

        if repo.local_path:
            # Read from local path
            full_path = os.path.join(repo.local_path, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()
        elif repo.github_token:
            # Get from GitHub API
            headers = {
                'Authorization': f'token {repo.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            response = requests.get(
                f'https://api.github.com/repos/{repo_name}/contents/{file_path}',
                headers=headers
            )
            if response.status_code == 200:
                import base64
                content = response.json()['content']
                return base64.b64decode(content).decode('utf-8')

        return None

# Create a global instance
repo_manager = RepoManager(os.path.dirname(os.path.abspath(__file__))) 