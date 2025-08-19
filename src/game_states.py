"""Game state definitions."""
from enum import Enum

class GameState(Enum):
    """Possible game states."""
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    SETTINGS = "settings"
    LEADERBOARD = "leaderboard"
    QUIT = "quit"