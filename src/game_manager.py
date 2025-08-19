"""Main game manager that handles game states and coordination."""
import pygame
from config import Config
from game_states import GameState
from scenes.main_menu import MainMenuScene
from scenes.game_scene import GameScene
from scenes.settings_scene import SettingsScene
from scenes.leaderboard_scene import LeaderboardScene
from utils.sound_manager import SoundManager
from utils.save_manager import SaveManager

class GameManager:
    """Manages the overall game flow and state transitions."""
    
    def __init__(self):
        # Initialize pygame components
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        pygame.display.set_caption(Config.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize managers
        self.sound_manager = SoundManager()
        self.save_manager = SaveManager()
        
        # Game state
        self.current_state = GameState.MAIN_MENU
        self.next_state = None
        
        # Initialize scenes
        self.scenes = {
            GameState.MAIN_MENU: MainMenuScene(self),
            GameState.PLAYING: GameScene(self),
            GameState.SETTINGS: SettingsScene(self),
            GameState.LEADERBOARD: LeaderboardScene(self)
        }
        
        # Current scene
        self.current_scene = self.scenes[self.current_state]
    
    def run(self):
        """Main game loop."""
        while self.running:
            try:
                dt = self.clock.tick(Config.FPS) / 1000.0  # Delta time in seconds
                
                # Handle events
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        self.running = False
                    else:
                        try:
                            self.current_scene.handle_event(event)
                        except Exception as e:
                            print(f"Error handling event in {self.current_scene.__class__.__name__}: {e}")
                            import traceback
                            traceback.print_exc()
                
                # Update current scene
                try:
                    self.current_scene.update(dt)
                except Exception as e:
                    print(f"Error updating {self.current_scene.__class__.__name__}: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Handle state changes
                if self.next_state:
                    try:
                        self.change_state(self.next_state)
                        self.next_state = None
                    except Exception as e:
                        print(f"Error changing state to {self.next_state}: {e}")
                        import traceback
                        traceback.print_exc()
                        self.next_state = None
                
                # Render
                try:
                    self.screen.fill(Config.WHITE)
                    self.current_scene.render(self.screen)
                    pygame.display.flip()
                except Exception as e:
                    print(f"Error rendering {self.current_scene.__class__.__name__}: {e}")
                    import traceback
                    traceback.print_exc()
                    
            except Exception as e:
                print(f"Critical error in main game loop: {e}")
                import traceback
                traceback.print_exc()
                self.running = False
    
    def change_state(self, new_state):
        """Change to a new game state."""
        if new_state == GameState.QUIT:
            self.running = False
            return
            
        self.current_state = new_state
        self.current_scene = self.scenes[new_state]
        self.current_scene.enter()
    
    def request_state_change(self, new_state):
        """Request a state change (will happen next frame)."""
        self.next_state = new_state
    
    def get_sound_manager(self):
        """Get the sound manager."""
        return self.sound_manager
    
    def get_save_manager(self):
        """Get the save manager."""
        return self.save_manager