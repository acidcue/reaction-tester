import pygame
import sys
import traceback
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.game_manager import GameManager
from src.config import Config

def main():
    """Main entry point for the game."""
    try:
        pygame.init()
        pygame.mixer.init()
        print("Pygame initialized successfully")
        
        # Create game manager and run
        print("Creating game manager...")
        game = GameManager()
        print("Starting game loop...")
        game.run()
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        print("Full traceback:")
        traceback.print_exc()
        input("Press Enter to exit...")  # Keep console open to see error
        
    except KeyboardInterrupt:
        print("Game interrupted by user")
        
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()