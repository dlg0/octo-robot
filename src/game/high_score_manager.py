import json
import os
from typing import List, Dict, Optional
from datetime import datetime

class HighScoreManager:
    def __init__(self, score_file: str = "high_scores.json"):
        self.score_file = score_file
        self.high_scores: List[Dict] = []
        self.load_scores()
    
    def load_scores(self):
        """Load high scores from JSON file"""
        try:
            if os.path.exists(self.score_file):
                with open(self.score_file, 'r') as f:
                    self.high_scores = json.load(f)
                # Ensure we have the expected structure
                for score in self.high_scores:
                    if 'name' not in score:
                        score['name'] = 'Unknown'
                    if 'score' not in score:
                        score['score'] = 0
                    if 'time' not in score:
                        score['time'] = 999.99
                    if 'date' not in score:
                        score['date'] = datetime.now().isoformat()
            else:
                self.high_scores = []
        except Exception as e:
            print(f"Error loading high scores: {e}")
            self.high_scores = []
    
    def save_scores(self):
        """Save high scores to JSON file"""
        try:
            # Sort by score descending, then by time ascending (faster time is better)
            self.high_scores.sort(key=lambda x: (-x['score'], x['time']))
            # Keep only top 10
            self.high_scores = self.high_scores[:10]
            
            with open(self.score_file, 'w') as f:
                json.dump(self.high_scores, f, indent=2)
        except Exception as e:
            print(f"Error saving high scores: {e}")
    
    def is_high_score(self, score: int, time: float) -> bool:
        """Check if the given score qualifies for the top 10"""
        if len(self.high_scores) < 10:
            return True
        
        # If we have 10 scores, check if this one is better
        # Sort temporarily to check position
        temp_scores = self.high_scores.copy()
        temp_scores.append({"score": score, "time": time, "name": "", "date": ""})
        temp_scores.sort(key=lambda x: (-x['score'], x['time']))
        
        # Find position of our score
        for i, entry in enumerate(temp_scores[:10]):
            if entry['score'] == score and entry['time'] == time and entry['name'] == "":
                return True
        
        return False
    
    def add_score(self, name: str, score: int, time: float) -> int:
        """Add a new high score and return its position (1-based), or 0 if not in top 10"""
        if not self.is_high_score(score, time):
            return 0
        
        new_entry = {
            "name": name,
            "score": score,
            "time": time,
            "date": datetime.now().isoformat()
        }
        
        self.high_scores.append(new_entry)
        self.save_scores()
        
        # Find the position of the new score
        for i, entry in enumerate(self.high_scores):
            if (entry['name'] == name and 
                entry['score'] == score and 
                entry['time'] == time):
                return i + 1
        
        return 0
    
    def get_top_scores(self, limit: int = 10) -> List[Dict]:
        """Get the top scores up to the specified limit"""
        return self.high_scores[:min(limit, len(self.high_scores))]
    
    def clear_scores(self):
        """Clear all high scores (for testing/reset purposes)"""
        self.high_scores = []
        self.save_scores() 