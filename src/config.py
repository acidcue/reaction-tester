"""Game configuration and constants."""
from pathlib import Path

class Config:
    """Central configuration for the game."""
    
    # Display settings
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    FPS = 60
    TITLE = "Twitch~y"
    
    # Cartoony Color Palette (SpongeBob + Minions inspired)
    # Primary Colors
    BRIGHT_YELLOW = (255, 235, 59)      # Main yellow (like SpongeBob)
    SUNNY_YELLOW = (255, 193, 7)       # Darker yellow for contrast
    BANANA_YELLOW = (255, 241, 118)    # Light yellow (like Minions)
    
    # Accent Colors
    AQUA_BLUE = (0, 188, 212)          # Aqua blue
    OCEAN_BLUE = (3, 169, 244)         # Slightly darker blue
    PLAYFUL_PURPLE = (156, 39, 176)    # Purple accent
    BUBBLEGUM_PURPLE = (233, 30, 99)   # Bright purple
    ENERGETIC_ORANGE = (255, 152, 0)   # Orange accent
    SUNSET_ORANGE = (255, 87, 34)      # Red-orange
    
    # Supporting Colors
    WHITE = (255, 255, 255)
    BLACK = (33, 33, 33)               # Softer black
    CARTOON_RED = (244, 67, 54)        # Bright red for errors
    CARTOON_GREEN = (76, 175, 80)      # Bright green for success
    LIGHT_GRAY = (240, 240, 240)       # Very light gray
    
    # Shadow/Outline colors for cartoon effect
    SHADOW_GRAY = (100, 100, 100)
    OUTLINE_DARK = (50, 50, 50)
    
    # Legacy color aliases (for compatibility)
    BLUE = AQUA_BLUE
    DARK_BLUE = OCEAN_BLUE
    RED = CARTOON_RED
    GREEN = CARTOON_GREEN
    PURPLE = PLAYFUL_PURPLE
    GOLD = SUNNY_YELLOW
    ORANGE = ENERGETIC_ORANGE
    GRAY = (128, 128, 128)
    
    # Difficulty colors (cartoony versions)
    DIFFICULTY_COLORS = {
        "easy": CARTOON_GREEN,
        "normal": AQUA_BLUE,
        "hard": ENERGETIC_ORANGE,
        "beast": PLAYFUL_PURPLE,
        "twitchy-god": SUNNY_YELLOW
    }
    
    # Background colors for different game states
    BACKGROUND_COLORS = {
        "menu": BRIGHT_YELLOW,
        "ready": CARTOON_RED,
        "go": CARTOON_GREEN,
        "result": WHITE
    }
    
    # Difficulty settings - Progressive challenge system
    DIFFICULTY_SETTINGS = {
        "easy": {
            "min_wait": 4.0,              # Longer, more predictable wait
            "max_wait": 5.0,              # Very narrow range (predictable)
            "countdown_enabled": True,     # Show countdown timer
            "warning_time": 1.0,          # 1 second warning before green
            "practice_mode": True,        # Show helpful hints
            "excellent_threshold": 400,
            "good_threshold": 600,
            "average_threshold": 800,
            "poor_threshold": 1000,
            "merh_threshold": 1500
        },
        "normal": {
            "min_wait": 2.5,
            "max_wait": 4.5,              # Medium range
            "countdown_enabled": False,
            "warning_time": 0.5,          # Brief warning
            "practice_mode": False,
            "excellent_threshold": 250,
            "good_threshold": 400,
            "average_threshold": 600,
            "poor_threshold": 800,
            "merh_threshold": 1200
        },
        "hard": {
            "min_wait": 1.5,
            "max_wait": 4.0,              # Wider range
            "countdown_enabled": False,
            "warning_time": 0.2,          # Very brief warning
            "practice_mode": False,
            "excellent_threshold": 180,
            "good_threshold": 300,
            "average_threshold": 450,
            "poor_threshold": 600,
            "merh_threshold": 900
        },
        "beast": {
            "min_wait": 0.8,
            "max_wait": 3.5,              # Very unpredictable
            "countdown_enabled": False,
            "warning_time": 0.0,          # No warning
            "practice_mode": False,
            "excellent_threshold": 120,
            "good_threshold": 200,
            "average_threshold": 300,
            "poor_threshold": 450,
            "merh_threshold": 600
        },
        "twitchy-god": {
            "min_wait": 0.3,              # Extremely short
            "max_wait": 2.0,              # Insanely unpredictable
            "countdown_enabled": False,
            "warning_time": 0.0,
            "practice_mode": False,
            "fake_signals": True,         # Sometimes show false greens!
            "excellent_threshold": 80,
            "good_threshold": 120,
            "average_threshold": 180,
            "poor_threshold": 250,
            "merh_threshold": 350
        }
    }
    
    # File paths
    BASE_DIR = Path(__file__).parent.parent
    ASSETS_DIR = BASE_DIR / "assets"
    SOUNDS_DIR = ASSETS_DIR / "sounds"
    IMAGES_DIR = ASSETS_DIR / "images"
    DATA_DIR = BASE_DIR / "data"
    
    # Sound files with cartoony descriptions
    SOUNDS = {
        'start': SOUNDS_DIR / "chime.mp3",        # Should be: Cartoon "BOING!" or bouncy spring sound
        'too_soon': SOUNDS_DIR / "oops.mp3",     # Should be: Silly "BONK!" or deflating balloon sound
        'success': SOUNDS_DIR / "ding.mp3",      # Should be: Happy "DING!" with sparkles or magic chime
        'menu_select': SOUNDS_DIR / "select.mp3", # Should be: Playful "POP!" or bubble burst
        'new_record': SOUNDS_DIR / "fanfare.mp3"  # Should be: Celebration fanfare with cartoon trumpets
    }
    
    # Font sizes (better scaling and readability)
    FONT_TINY = 16
    FONT_SMALL = 22
    FONT_MEDIUM = 32
    FONT_LARGE = 48
    FONT_HUGE = 64
    FONT_TITLE = 84
    FONT_MEGA = 96                    # For reaction times and main displays
    
    # Animation settings
    BOUNCE_AMPLITUDE = 12             # More dramatic bouncing
    WIGGLE_SPEED = 2.5               # Slightly slower for readability
    
    # Particle system
    PARTICLE_COUNT = 60              # Optimized count
    PARTICLE_MIN_SIZE = 4
    PARTICLE_MAX_SIZE = 12
    PARTICLE_SPEED_RANGE = (-3.0, 3.0)
    
    # UI Element sizes (responsive and well-proportioned)
    BUTTON_HEIGHT = 70
    BUTTON_WIDTH = 250
    BUTTON_SPACING = 85              # Space between buttons
    CORNER_RADIUS = 20               # More rounded for cartoon look
    BORDER_WIDTH = 5                 # Thicker borders
    
    # Responsive margins and padding
    MARGIN_SMALL = 15
    MARGIN_MEDIUM = 30
    MARGIN_LARGE = 50
    PADDING_SMALL = 10
    PADDING_MEDIUM = 20
    PADDING_LARGE = 35
    
    # Performance emojis/icons (placeholders)
    PERFORMANCE_ICONS = {
        "excellent": "🔥",             # Replace with: Cartoon lightning bolt with sparkles
        "good": "⚡",                  # Replace with: Happy star with googly eyes  
        "average": "👍",               # Replace with: Thumbs up with cartoon glove
        "poor": "😅",                  # Replace with: Wobbly clock with sweat drops
        "meh": "🐌",                   # Replace with: Sleepy snail with Z's
        "terrible": "💥"               # Replace with: Cartoon explosion cloud
    }
    
    # UI Icons (all need cartoon replacements)
    UI_ICONS = {
        "timer": "⏱️",                 # Replace with: Goofy stopwatch with bouncing numbers
        "trophy": "🏆",               # Replace with: Golden banana trophy
        "settings": "⚙️",             # Replace with: Colorful gear with happy face
        "back": "⬅️",                 # Replace with: Bouncy arrow button
        "pause": "⏸️",                # Replace with: Squishy pause symbol
        "play": "▶️",                 # Replace with: Bouncy play triangle
        "volume": "🔊",               # Replace with: Speaker with sound waves and musical notes
        "medal": "🥇"                 # Replace with: Shiny star medal with ribbon
    }