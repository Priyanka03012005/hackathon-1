from typing import Dict, List, Set
from datetime import datetime, timedelta
import hashlib

class SuggestionHistory:
    def __init__(self):
        self.history: Dict[str, List[Dict]] = {}  # user_id -> list of suggestions
        self.suggestion_hashes: Dict[str, Set[str]] = {}  # user_id -> set of suggestion hashes
        self.history_retention_days = 30  # Keep history for 30 days
    
    def _generate_suggestion_hash(self, suggestion: Dict) -> str:
        """Generate a unique hash for a suggestion based on its content."""
        # Create a string representation of the suggestion
        suggestion_str = f"{suggestion.get('type', '')}:{suggestion.get('message', '')}:{suggestion.get('line', '')}"
        return hashlib.md5(suggestion_str.encode()).hexdigest()
    
    def _cleanup_old_history(self, user_id: str):
        """Remove suggestions older than retention period."""
        if user_id not in self.history:
            return
        
        cutoff_date = datetime.now() - timedelta(days=self.history_retention_days)
        self.history[user_id] = [
            suggestion for suggestion in self.history[user_id]
            if suggestion['timestamp'] > cutoff_date
        ]
    
    def add_suggestions(self, user_id: str, suggestions: List[Dict]):
        """Add new suggestions to the history."""
        if user_id not in self.history:
            self.history[user_id] = []
            self.suggestion_hashes[user_id] = set()
        
        # Clean up old history
        self._cleanup_old_history(user_id)
        
        # Add new suggestions with timestamp
        for suggestion in suggestions:
            suggestion['timestamp'] = datetime.now()
            self.history[user_id].append(suggestion)
            self.suggestion_hashes[user_id].add(self._generate_suggestion_hash(suggestion))
    
    def filter_redundant_suggestions(self, user_id: str, new_suggestions: List[Dict]) -> List[Dict]:
        """Filter out suggestions that were already given in recent history."""
        if user_id not in self.suggestion_hashes:
            return new_suggestions
        
        filtered_suggestions = []
        for suggestion in new_suggestions:
            suggestion_hash = self._generate_suggestion_hash(suggestion)
            if suggestion_hash not in self.suggestion_hashes[user_id]:
                filtered_suggestions.append(suggestion)
        
        return filtered_suggestions
    
    def get_suggestion_history(self, user_id: str) -> List[Dict]:
        """Get the suggestion history for a user."""
        if user_id not in self.history:
            return []
        
        self._cleanup_old_history(user_id)
        return self.history[user_id]
    
    def clear_history(self, user_id: str):
        """Clear the suggestion history for a user."""
        if user_id in self.history:
            del self.history[user_id]
        if user_id in self.suggestion_hashes:
            del self.suggestion_hashes[user_id]

# Create a global instance
suggestion_history = SuggestionHistory() 