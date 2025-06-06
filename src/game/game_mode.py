from enum import Enum

class GameMode(Enum):
    FLETCHY = "fletchy"  # Easy mode - half the margin
    SPENCY = "spency"    # Normal mode - default margin
    CHARLIE = "charlie"  # Hard mode - double the margin

    @classmethod
    def get_margin_multiplier(cls, mode: 'GameMode') -> float:
        """Get the margin multiplier for a given mode"""
        if mode == cls.FLETCHY:
            return 3.5  # Half the margin - easier gameplay
        elif mode == cls.SPENCY:
            return 1.0  # Default margin - balanced gameplay
        elif mode == cls.CHARLIE:
            return 0.7  # Double the margin - harder gameplay
        return 1.0  # Default to normal mode if invalid 