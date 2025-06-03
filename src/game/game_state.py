from enum import Enum
from typing import Optional

class GameState(Enum):
    PLAYING = "playing"
    GAME_OVER = "game_over"
    NAME_ENTRY = "name_entry"
    HIGH_SCORES = "high_scores"
    PAUSED = "paused"

class GameStateManager:
    def __init__(self):
        self.current_state = GameState.PLAYING
        self.previous_state = GameState.PLAYING
        
        # Game progress tracking
        self.score = 0
        self.game_time = 0.0
        self.target_score = 100
        
        # Name entry state
        self.entered_name = ""
        self.name_entry_complete = False
        
        # High score data
        self.final_score = 0
        self.final_time = 0.0
        self.score_position = 0  # Position in high score list (0 if not in top 10)
        
    def set_state(self, new_state: GameState):
        """Change to a new game state"""
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # Handle state-specific initialization
        if new_state == GameState.NAME_ENTRY:
            self.entered_name = ""
            self.name_entry_complete = False
        elif new_state == GameState.PLAYING:
            self.reset_game()
    
    def reset_game(self):
        """Reset game progress for a new game"""
        self.score = 0
        self.game_time = 0.0
        self.entered_name = ""
        self.name_entry_complete = False
        self.final_score = 0
        self.final_time = 0.0
        self.score_position = 0
    
    def update_game_time(self, delta_time: float):
        """Update the game timer (only during PLAYING state)"""
        if self.current_state == GameState.PLAYING:
            self.game_time += delta_time
    
    def add_score(self, points: int):
        """Add points to the current score"""
        self.score += points
        
        # Check if target score reached
        if self.score >= self.target_score:
            self.complete_game()
    
    def reset_score(self):
        """Reset score to zero (when hitting wrong color)"""
        self.score = 0
    
    def complete_game(self):
        """Called when player reaches target score"""
        self.final_score = self.score
        self.final_time = self.game_time
        self.set_state(GameState.GAME_OVER)
    
    def add_name_character(self, char: str):
        """Add a character to the entered name"""
        if len(self.entered_name) < 20:  # Limit name length
            self.entered_name += char
    
    def remove_name_character(self):
        """Remove the last character from the entered name"""
        if self.entered_name:
            self.entered_name = self.entered_name[:-1]
    
    def confirm_name(self):
        """Confirm the entered name and move to high scores"""
        if not self.entered_name.strip():
            self.entered_name = "Anonymous"
        self.name_entry_complete = True
        self.set_state(GameState.HIGH_SCORES)
    
    def is_playing(self) -> bool:
        return self.current_state == GameState.PLAYING
    
    def is_game_over(self) -> bool:
        return self.current_state == GameState.GAME_OVER
    
    def is_name_entry(self) -> bool:
        return self.current_state == GameState.NAME_ENTRY
    
    def is_high_scores(self) -> bool:
        return self.current_state == GameState.HIGH_SCORES
    
    def is_paused(self) -> bool:
        return self.current_state == GameState.PAUSED
    
    def start_playing(self):
        """Start or resume playing state"""
        self.set_state(GameState.PLAYING)
    
    def show_high_scores(self):
        """Show the high scores screen"""
        self.set_state(GameState.HIGH_SCORES)
    
    def start_name_entry(self):
        """Start name entry for high score"""
        self.set_state(GameState.NAME_ENTRY) 