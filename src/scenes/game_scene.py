"""Main game scene with enhanced cartoony SpongeBob + Minions style gameplay."""
import pygame
import time
import random
import math
from enum import Enum
from .base_scene import BaseScene
from config import Config
from game_states import GameState
from utils.particles import ParticleSystem
from utils.cartoon_ui import CartoonUI

class GamePhase(Enum):
    """Game phases during a reaction test."""
    WAITING = "waiting"
    READY = "ready"
    GREEN = "green"
    RESULT = "result"
    PAUSED = "paused"

class GameScene(BaseScene):
    """The main gameplay scene with enhanced cartoony reaction time testing."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        
        # Game state
        self.phase = GamePhase.WAITING
        self.start_time = 0
        self.wait_duration = 0
        self.reaction_time = None
        self.result_message = ""
        self.performance_rating = ""
        self.performance_level = "average"
        
        # Difficulty helpers
        self.countdown_time = 0          # For easy mode countdown
        self.warning_shown = False       # For warning before green
        self.fake_signal_active = False  # For twitchy-god mode tricks
        
        # Session tracking
        self.attempts = 0
        self.best_time = None
        self.session_times = []
        
        # Visual effects
        self.particles = ParticleSystem(Config.PARTICLE_COUNT)
        self.background_color = Config.BRIGHT_YELLOW
        self.target_color = Config.BRIGHT_YELLOW
        self.color_transition_speed = 8.0
        self.animation_time = 0
        self.result_burst_time = 0
        self.screen_shake = 0
        self.ui_bounce = 0  # For UI element bouncing
        
        # Enhanced UI elements
        self.setup_enhanced_ui_elements()
        
        # Load custom graphics if available
        self.load_custom_graphics()
    
    def load_custom_graphics(self):
        """Load custom graphics for enhanced UI."""
        try:
            # Try to load custom graphics, fall back to drawing if not available
            self.custom_background = None
            self.bubble_texture = None
            # Add your custom graphics loading code here
        except:
            print("Custom graphics not available, using drawn elements")
    
    def setup_enhanced_ui_elements(self):
        """Initialize enhanced UI elements with better visual design."""
        # Define missing color constants
        self.ENERGETIC_ORANGE_HOVER = (255, 180, 50)
        self.PLAYFUL_PURPLE_HOVER = (200, 100, 255)
        self.BANANA_YELLOW = (255, 240, 120)
        self.OUTLINE_DARK = (60, 60, 100)
        self.SHADOW_GRAY = (100, 100, 100, 150)  # Added alpha for transparency
        
        # Define font names
        self.FONT_CARTOON = "Arial"  # Fallback font
        
        # Font sizes (scaled down for better fit)
        self.FONT_TINY = 12
        self.FONT_SMALL = 16
        self.FONT_MEDIUM = 20
        self.FONT_LARGE = 28
        self.FONT_HUGE = 36
        self.FONT_TITLE = 42
        
        # Animated back button with icon (smaller size)
        self.back_button = {
            "rect": pygame.Rect(15, 15, 100, 40),
            "color": Config.ENERGETIC_ORANGE,
            "hover_color": self.ENERGETIC_ORANGE_HOVER,
            "icon": "🏠",
            "text": "MENU",
            "bounce": 0
        }
        
        # Animated pause button with icon (smaller size)
        self.pause_button = {
            "rect": pygame.Rect(Config.WINDOW_WIDTH - 115, 15, 100, 40),
            "color": Config.PLAYFUL_PURPLE,
            "hover_color": self.PLAYFUL_PURPLE_HOVER,
            "icon": "⏸️",
            "text": "PAUSE",
            "bounce": 0
        }
        
        # Central reaction area with enhanced design (smaller size)
        self.reaction_area = {
            "rect": pygame.Rect(
                Config.WINDOW_WIDTH // 2 - 100,
                Config.WINDOW_HEIGHT // 2 - 100,
                200, 200
            ),
            "outer_glow": 0,
            "pulse": 0
        }
        
        # Statistics panel with enhanced design (smaller size)
        self.stats_panel = {
            "rect": pygame.Rect(15, Config.WINDOW_HEIGHT - 130, 200, 115),
            "visible": True,
            "slide_offset": 0
        }
        
        # Performance indicators
        self.performance_indicators = {
            "excellent": "🔥",
            "good": "⚡",
            "average": "👍",
            "poor": "😅",
            "meh": "🐌",
            "terrible": "💀"
        }
    
    def enter(self):
        """Called when entering the game scene."""
        self.reset_game()
        self.particles.clear()
        self.animation_time = 0
        self.ui_bounce = 0
    
    def reset_game(self):
        """Reset game state for a new attempt."""
        self.phase = GamePhase.WAITING
        self.start_time = 0
        self.reaction_time = None
        self.wait_duration = 0
        self.result_message = ""
        self.performance_rating = ""
        self.performance_level = "average"
        self.result_burst_time = 0
        self.screen_shake = 0
        self.reaction_area["outer_glow"] = 0
        self.reaction_area["pulse"] = 0
    
    # ================================
    # EVENT HANDLING
    # ================================
    
    def handle_event(self, event):
        """Handle game input events."""
        if event.type == pygame.KEYDOWN:
            self.handle_keyboard_input(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_input(event)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event)
    
    def handle_mouse_motion(self, event):
        """Handle mouse motion for hover effects."""
        mouse_pos = pygame.mouse.get_pos()
        
        # Back button hover
        if self.back_button["rect"].collidepoint(mouse_pos):
            self.back_button["bounce"] = min(5, self.back_button["bounce"] + 0.5)
        else:
            self.back_button["bounce"] = max(0, self.back_button["bounce"] - 0.2)
        
        # Pause button hover
        if self.pause_button["rect"].collidepoint(mouse_pos):
            self.pause_button["bounce"] = min(5, self.pause_button["bounce"] + 0.5)
        else:
            self.pause_button["bounce"] = max(0, self.pause_button["bounce"] - 0.2)
    
    def handle_keyboard_input(self, event):
        """Process keyboard input."""
        if event.key == pygame.K_ESCAPE:
            self.game_manager.request_state_change(GameState.MAIN_MENU)
        elif event.key == pygame.K_p:
            self.toggle_pause()
        elif event.key == pygame.K_SPACE:
            self.handle_reaction_input()
        elif event.key == pygame.K_s:
            # Toggle statistics panel
            self.stats_panel["visible"] = not self.stats_panel["visible"]
    
    def handle_mouse_input(self, event):
        """Process mouse input."""
        if event.button == 1:  # Left click
            mouse_pos = pygame.mouse.get_pos()
            
            if self.back_button["rect"].collidepoint(mouse_pos):
                self.back_button["bounce"] = 8  # Big bounce on click
                self.game_manager.request_state_change(GameState.MAIN_MENU)
            elif self.pause_button["rect"].collidepoint(mouse_pos):
                self.pause_button["bounce"] = 8  # Big bounce on click
                self.toggle_pause()
            else:
                # Treat clicks like spacebar in game area
                self.handle_reaction_input()
    
    def handle_reaction_input(self):
        """Handle spacebar or click input based on current game phase."""
        if self.phase == GamePhase.PAUSED:
            return
        elif self.phase == GamePhase.WAITING:
            self.start_reaction_test()
        elif self.phase == GamePhase.READY:
            self.handle_early_press()
        elif self.phase == GamePhase.GREEN:
            self.handle_successful_reaction()
        elif self.phase == GamePhase.RESULT:
            self.reset_for_next_attempt()
    
    # ================================
    # GAME LOGIC
    # ================================
    
    def start_reaction_test(self):
        """Begin a new reaction time test with difficulty-specific features."""
        try:
            difficulty_config = self.get_difficulty_config()
            
            # Basic timing setup
            self.wait_duration = random.uniform(
                difficulty_config["min_wait"], 
                difficulty_config["max_wait"]
            )
            self.start_time = time.time()
            self.phase = GamePhase.READY
            self.target_color = Config.CARTOON_RED
            self.screen_shake = 5
            
            # Reset difficulty helpers
            self.countdown_time = self.wait_duration
            self.warning_shown = False
            self.fake_signal_active = False
            
            # Twitchy-god mode: Sometimes add fake signals
            if difficulty_config.get("fake_signals", False) and random.random() < 0.3:
                self.fake_signal_active = True
                self.wait_duration *= 1.5  # Make them wait longer after fake
            
            # Visual feedback
            self.reaction_area["outer_glow"] = 15
            self.play_sound('start')
        except Exception as e:
            print(f"Error starting reaction test: {e}")
            self.fallback_start_test()
    
    def fallback_start_test(self):
        """Fallback test start with basic settings."""
        self.wait_duration = random.uniform(2.0, 5.0)
        self.start_time = time.time()
        self.phase = GamePhase.READY
        self.target_color = Config.CARTOON_RED
        self.reaction_area["outer_glow"] = 15
    
    def handle_early_press(self):
        """Handle when player presses too early."""
        self.reaction_time = "Too soon!"
        self.result_message = "Wait for GREEN!"
        self.performance_rating = "💥 OOPS!"
        self.performance_level = "terrible"
        self.phase = GamePhase.RESULT
        self.target_color = Config.BRIGHT_YELLOW
        self.result_burst_time = time.time()
        self.screen_shake = 15
        
        self.play_sound('too_soon')
        self.add_error_particles()
    
    def handle_successful_reaction(self):
        """Handle successful reaction time measurement."""
        reaction_ms = round((time.time() - self.start_time) * 1000)
        self.reaction_time = f"{reaction_ms}ms"
        self.attempts += 1
        self.session_times.append(reaction_ms)
        
        # Check for session best
        if self.is_session_best(reaction_ms):
            self.handle_new_session_best(reaction_ms)
        else:
            self.handle_good_reaction(reaction_ms)
        
        # Rate performance
        self.rate_performance(reaction_ms)
        
        # Set result state
        self.phase = GamePhase.RESULT
        self.target_color = Config.BRIGHT_YELLOW
        self.result_burst_time = time.time()
        
        self.play_sound('success')
        self.add_celebration_particles()
        self.save_result(reaction_ms)
    
    def is_session_best(self, reaction_ms):
        """Check if this is a new session best time."""
        return self.best_time is None or reaction_ms < self.best_time
    
    def handle_new_session_best(self, reaction_ms):
        """Handle new session best time."""
        self.best_time = reaction_ms
        self.result_message = "NEW SESSION BEST!"
        self.screen_shake = 20
        self.play_sound('new_record')
    
    def handle_good_reaction(self, reaction_ms):
        """Handle good but not best reaction."""
        self.result_message = "AWESOME REFLEXES!"
        self.screen_shake = 8
    
    def rate_performance(self, time_ms):
        """Rate performance and get level for animations."""
        try:
            rating_info = self.get_performance_rating_with_level(time_ms)
            self.performance_rating = rating_info["rating"]
            self.performance_level = rating_info["level"]
        except Exception as e:
            print(f"Error rating performance: {e}")
            self.performance_rating = "Good job!"
            self.performance_level = "average"
    
    def get_performance_rating_with_level(self, time_ms):
        """Get performance rating with level for animations."""
        difficulty_config = self.get_difficulty_config()
        
        if time_ms <= difficulty_config["excellent_threshold"]:
            return {"rating": "🔥 LIGHTNING FAST!", "level": "excellent"}
        elif time_ms <= difficulty_config["good_threshold"]:
            return {"rating": "⚡ SUPER QUICK!", "level": "good"}
        elif time_ms <= difficulty_config["average_threshold"]:
            return {"rating": "👍 NICE JOB!", "level": "average"}
        elif time_ms <= difficulty_config["poor_threshold"]:
            return {"rating": "😅 NOT BAD!", "level": "poor"}
        elif time_ms <= difficulty_config["merh_threshold"]:
            return {"rating": "🐌 SLEEPY!", "level": "meh"}
        else:
            return {"rating": "💀 WAKE UP!", "level": "terrible"}
    
    def get_difficulty_config(self):
        """Get current difficulty configuration."""
        save_manager = self.game_manager.get_save_manager()
        difficulty = save_manager.get_setting("difficulty", "normal")
        return Config.DIFFICULTY_SETTINGS.get(difficulty, Config.DIFFICULTY_SETTINGS["normal"])
    
    def save_result(self, time_ms):
        """Save the result to persistent storage."""
        try:
            save_manager = self.game_manager.get_save_manager()
            difficulty = save_manager.get_setting("difficulty", "normal")
            save_manager.add_score(time_ms, difficulty)
        except Exception as e:
            print(f"Error saving result: {e}")
    
    def reset_for_next_attempt(self):
        """Reset for the next attempt."""
        self.reset_game()
    
    def toggle_pause(self):
        """Toggle pause state."""
        if self.phase == GamePhase.PAUSED:
            self.phase = GamePhase.WAITING
        else:
            self.phase = GamePhase.PAUSED
    
    # ================================
    # VISUAL EFFECTS
    # ================================
    
    def add_error_particles(self):
        """Add error particle burst."""
        try:
            center_x = Config.WINDOW_WIDTH // 2
            center_y = Config.WINDOW_HEIGHT // 2
            self.particles.add_burst(center_x, center_y, 20, color=Config.CARTOON_RED)
        except:
            pass
    
    def add_celebration_particles(self):
        """Add celebration particle burst."""
        try:
            center_x = Config.WINDOW_WIDTH // 2
            center_y = Config.WINDOW_HEIGHT // 2
            self.particles.add_burst(center_x, center_y, 30, color=Config.CARTOON_GREEN)
        except:
            pass
    
    def play_sound(self, sound_name):
        """Play a sound effect safely."""
        try:
            self.game_manager.get_sound_manager().play_sound(sound_name)
        except:
            pass
    
    # ================================
    # UPDATE LOGIC
    # ================================
    
    def update(self, dt):
        """Update game logic and animations."""
        if self.phase == GamePhase.PAUSED:
            return
        
        self.animation_time += dt
        self.ui_bounce += dt
        self.particles.update(dt)
        self.update_background_transition(dt)
        self.update_screen_shake(dt)
        self.update_ui_elements(dt)
        self.check_green_transition()
    
    def update_ui_elements(self, dt):
        """Update UI element animations."""
        # Update reaction area pulse
        if self.phase == GamePhase.READY:
            self.reaction_area["pulse"] = 0.5 + 0.3 * math.sin(self.animation_time * 8)
        
        # Update outer glow
        if self.reaction_area["outer_glow"] > 0:
            self.reaction_area["outer_glow"] = max(0, self.reaction_area["outer_glow"] - dt * 10)
        
        # Update button bounces
        self.back_button["bounce"] = max(0, self.back_button["bounce"] - dt * 5)
        self.pause_button["bounce"] = max(0, self.pause_button["bounce"] - dt * 5)
        
        # Update stats panel slide
        target_offset = 0 if self.stats_panel["visible"] else -300
        self.stats_panel["slide_offset"] += (target_offset - self.stats_panel["slide_offset"]) * dt * 5
    
    def update_background_transition(self, dt):
        """Smoothly transition background color."""
        current = list(self.background_color)
        target = list(self.target_color)
        
        for i in range(3):  # RGB channels
            diff = target[i] - current[i]
            if abs(diff) > 1:
                current[i] += diff * self.color_transition_speed * dt
            else:
                current[i] = target[i]
        
        self.background_color = tuple(int(c) for c in current)
    
    def update_screen_shake(self, dt):
        """Reduce screen shake over time."""
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - dt * 30)
    
    def check_green_transition(self):
        """Check if it's time to turn green with difficulty-specific features."""
        if self.phase == GamePhase.READY:
            current_time = time.time()
            elapsed = current_time - self.start_time
            difficulty_config = self.get_difficulty_config()
            
            # Update countdown for easy mode
            if difficulty_config.get("countdown_enabled", False):
                self.countdown_time = max(0, self.wait_duration - elapsed)
            
            # Show warning before green (if enabled)
            warning_time = difficulty_config.get("warning_time", 0)
            if warning_time > 0 and not self.warning_shown:
                if elapsed >= (self.wait_duration - warning_time):
                    self.warning_shown = True
                    self.screen_shake = 3  # Small shake for warning
                    self.reaction_area["outer_glow"] = 25  # Strong glow for warning
            
            # Fake signal for twitchy-god mode
            if self.fake_signal_active and elapsed >= (self.wait_duration * 0.6):
                # Show fake green briefly
                self.target_color = Config.CARTOON_GREEN
                self.screen_shake = 8
                if elapsed >= (self.wait_duration * 0.7):
                    self.target_color = Config.CARTOON_RED  # Back to red
                    self.fake_signal_active = False
            
            # Real green signal
            if elapsed >= self.wait_duration:
                self.phase = GamePhase.GREEN
                self.start_time = time.time()  # Reset for reaction timing
                self.target_color = Config.CARTOON_GREEN
                self.screen_shake = 12
                self.reaction_area["outer_glow"] = 30
    
    # ================================
    # ENHANCED RENDERING
    # ================================
    
    def render(self, screen):
        """Render the enhanced cartoony game scene."""
        # Calculate screen shake offset
        shake_offset = self.get_shake_offset()
        
        # Fill background with gradient
        self.render_gradient_background(screen)
        
        # Draw visual elements
        self.particles.render(screen)
        self.render_enhanced_game_content(screen, shake_offset)
        self.render_enhanced_ui_buttons(screen, shake_offset)
        self.render_enhanced_statistics(screen, shake_offset)
    
    def render_gradient_background(self, screen):
        """Render a gradient background instead of solid color."""
        try:
            # Create a gradient from bright yellow to a slightly darker yellow
            for y in range(Config.WINDOW_HEIGHT):
                # Calculate gradient factor (0 at top, 1 at bottom)
                factor = y / Config.WINDOW_HEIGHT
                
                # Interpolate between background color and a slightly darker version
                darker = tuple(max(0, int(c * (1 - 0.1 * factor))) for c in self.background_color)
                
                # Draw horizontal line with gradient color
                pygame.draw.line(screen, darker, (0, y), (Config.WINDOW_WIDTH, y))
        except:
            # Fallback to solid color if gradient fails
            screen.fill(self.background_color)
    
    def get_shake_offset(self):
        """Calculate screen shake offset."""
        if self.screen_shake > 0:
            shake_x = int(random.uniform(-self.screen_shake, self.screen_shake))
            shake_y = int(random.uniform(-self.screen_shake, self.screen_shake))
            return (shake_x, shake_y)
        return (0, 0)
    
    def render_enhanced_ui_buttons(self, screen, shake_offset):
        """Draw enhanced UI buttons with animations and effects."""
        shake_x, shake_y = shake_offset
        
        # Back button with enhanced design
        back_rect = pygame.Rect(
            self.back_button["rect"].x + shake_x, 
            self.back_button["rect"].y + shake_y - self.back_button["bounce"], 
            self.back_button["rect"].width, 
            self.back_button["rect"].height
        )
        self.render_enhanced_button(
            screen, back_rect, 
            self.back_button["icon"], self.back_button["text"],
            self.back_button["color"], self.back_button["hover_color"]
        )
        
        # Pause button with enhanced design
        pause_rect = pygame.Rect(
            self.pause_button["rect"].x + shake_x,
            self.pause_button["rect"].y + shake_y - self.pause_button["bounce"],
            self.pause_button["rect"].width,
            self.pause_button["rect"].height
        )
        self.render_enhanced_button(
            screen, pause_rect, 
            self.pause_button["icon"], self.pause_button["text"],
            self.pause_button["color"], self.pause_button["hover_color"]
        )
    
    def render_enhanced_button(self, screen, rect, icon, text, color, hover_color):
        """Render an enhanced cartoon button with icon and effects."""
        # Determine button color based on bounce (hover state)
        button_color = hover_color if rect.y < self.back_button["rect"].y else color
        
        # Draw button with rounded corners (draw shadow first)
        shadow_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.width, rect.height)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, self.SHADOW_GRAY, (0, 0, shadow_rect.width, shadow_rect.height), border_radius=10)
        screen.blit(shadow_surface, shadow_rect)
        
        # Draw main button
        self.draw_rounded_rect(screen, rect, button_color, 10)
        
        # Draw button outline
        outline_rect = pygame.Rect(rect.x - 1, rect.y - 1, rect.width + 2, rect.height + 2)
        self.draw_rounded_rect(screen, outline_rect, self.OUTLINE_DARK, 11, 2)
        
        # Draw icon and text
        icon_font = pygame.font.SysFont(self.FONT_CARTOON, 20)
        text_font = pygame.font.SysFont(self.FONT_CARTOON, 16)
        
        icon_surface = icon_font.render(icon, True, Config.WHITE)
        text_surface = text_font.render(text, True, Config.WHITE)
        
        # Center icon and text
        icon_x = rect.x + 15
        icon_y = rect.y + (rect.height - icon_surface.get_height()) // 2
        
        text_x = rect.x + 45
        text_y = rect.y + (rect.height - text_surface.get_height()) // 2
        
        screen.blit(icon_surface, (icon_x, icon_y))
        screen.blit(text_surface, (text_x, text_y))
    
    def draw_rounded_rect(self, screen, rect, color, radius, width=0):
        """Draw a rounded rectangle."""
        if width == 0:
            pygame.draw.rect(screen, color, rect, border_radius=radius)
        else:
            pygame.draw.rect(screen, color, rect, width, border_radius=radius)
    
    def render_enhanced_game_content(self, screen, shake_offset):
        """Render enhanced main game content based on current phase."""
        shake_x, shake_y = shake_offset
        
        if self.phase == GamePhase.WAITING:
            self.render_enhanced_waiting_phase(screen, shake_x, shake_y)
        elif self.phase == GamePhase.READY:
            self.render_enhanced_ready_phase(screen, shake_x, shake_y)
        elif self.phase == GamePhase.GREEN:
            self.render_enhanced_green_phase(screen, shake_x, shake_y)
        elif self.phase == GamePhase.RESULT:
            self.render_enhanced_result_phase(screen, shake_x, shake_y)
        elif self.phase == GamePhase.PAUSED:
            self.render_enhanced_paused_phase(screen)
    
    def render_enhanced_waiting_phase(self, screen, x_offset, y_offset):
        """Render the enhanced waiting phase with cartoon instructions."""
        difficulty_config = self.get_difficulty_config()
        save_manager = self.game_manager.get_save_manager()
        difficulty = save_manager.get_setting("difficulty", "normal")
        
        # Enhanced central reaction area with glow
        reaction_rect = pygame.Rect(
            self.reaction_area["rect"].x + x_offset,
            self.reaction_area["rect"].y + y_offset,
            self.reaction_area["rect"].width,
            self.reaction_area["rect"].height
        )
        
        # Draw outer glow if active
        if self.reaction_area["outer_glow"] > 0:
            glow_radius = self.reaction_area["outer_glow"]
            glow_surface = pygame.Surface((reaction_rect.width + 20, reaction_rect.height + 20), pygame.SRCALPHA)
            for r in range(int(glow_radius), 0, -2):
                alpha = 150 - (r * 10)
                if alpha > 0:
                    pygame.draw.ellipse(glow_surface, (255, 255, 100, alpha), 
                                      (glow_radius - r, glow_radius - r, 
                                       glow_surface.get_width() - 2*(glow_radius - r), 
                                       glow_surface.get_height() - 2*(glow_radius - r)))
            screen.blit(glow_surface, (reaction_rect.x - 10, reaction_rect.y - 10))
        
        # Draw main reaction circle with enhanced style
        pygame.draw.ellipse(screen, Config.WHITE, reaction_rect)
        pygame.draw.ellipse(screen, self.OUTLINE_DARK, reaction_rect, 4)
        
        # Pulsing "READY?" text with enhanced effect
        pulse_scale = 1.0 + 0.2 * math.sin(self.animation_time * 4)
        font_size = int(self.FONT_HUGE * pulse_scale)
        
        font = pygame.font.SysFont(self.FONT_CARTOON, font_size)
        text_surface = font.render("READY?", True, Config.AQUA_BLUE)
        text_rect = text_surface.get_rect(center=(Config.WINDOW_WIDTH // 2 + x_offset, 
                                                Config.WINDOW_HEIGHT // 2 - 15 + y_offset))
        screen.blit(text_surface, text_rect)
        
        # Enhanced instructions with speech bubbles
        self.render_enhanced_waiting_instructions(screen, x_offset, y_offset, difficulty, difficulty_config)
    
    def render_enhanced_waiting_instructions(self, screen, x_offset, y_offset, difficulty, difficulty_config):
        """Render enhanced waiting phase instructions."""
        instructions = [
            "Click anywhere or press SPACE when ready!",
            "Wait for GREEN, then react FAST!"
        ]
        
        # Add difficulty-specific tips
        if difficulty == "easy":
            instructions.append("💡 TIP: You'll see a countdown timer!")
        elif difficulty == "twitchy-god":
            instructions.append("⚠️ WARNING: Watch out for fake signals!")
        
        instruction_y = Config.WINDOW_HEIGHT // 2 + 100  # Moved up for better visibility
        for i, instruction in enumerate(instructions):
            if i < 2:  # Main instructions
                self.draw_speech_bubble(
                    screen, instruction,
                    Config.WINDOW_WIDTH // 2 + x_offset,
                    instruction_y + (i * 35) + y_offset,
                    380,  # Narrower bubbles
                    bubble_color=self.BANANA_YELLOW,
                    text_color=Config.BLACK
                )
            else:  # Tips
                font = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_SMALL)
                text_surface = font.render(instruction, True, Config.PLAYFUL_PURPLE)
                text_rect = text_surface.get_rect(center=(Config.WINDOW_WIDTH // 2 + x_offset,
                                                        instruction_y + 70 + ((i-2) * 20) + y_offset))
                screen.blit(text_surface, text_rect)
        
        # Enhanced difficulty info panel
        difficulty_info = [
            f"Mode: {difficulty.upper()}",
            f"Excellent: Under {difficulty_config['excellent_threshold']}ms",
            f"Wait: {difficulty_config['min_wait']:.1f}s-{difficulty_config['max_wait']:.1f}s"
        ]
        
        info_panel = pygame.Rect(
            Config.WINDOW_WIDTH // 2 - 120 + x_offset,
            instruction_y + 100 + y_offset,
            240, 70
        )
        self.draw_rounded_rect(screen, info_panel, self.BANANA_YELLOW, 10)
        self.draw_rounded_rect(screen, info_panel, self.OUTLINE_DARK, 10, 2)
        
        font = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_SMALL)
        for i, info in enumerate(difficulty_info):
            color = Config.DIFFICULTY_COLORS.get(difficulty, Config.BLACK) if i == 0 else Config.SHADOW_GRAY
            text_surface = font.render(info, True, color)
            screen.blit(text_surface, (info_panel.x + 10, info_panel.y + 10 + (i * 20)))
    
    def draw_speech_bubble(self, screen, text, x, y, width, bubble_color=Config.WHITE, text_color=Config.BLACK):
        """Draw a speech bubble with text."""
        font = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_SMALL)
        
        # Wrap text to fit width
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width < width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate bubble height
        line_height = font.get_linesize()
        bubble_height = len(lines) * line_height + 15
        
        # Draw bubble
        bubble_rect = pygame.Rect(x - width//2, y - bubble_height//2, width, bubble_height)
        self.draw_rounded_rect(screen, bubble_rect, bubble_color, 10)
        self.draw_rounded_rect(screen, bubble_rect, self.OUTLINE_DARK, 10, 2)
        
        # Draw text
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, text_color)
            text_rect = text_surface.get_rect(center=(x, y - bubble_height//2 + 8 + (i * line_height)))
            screen.blit(text_surface, text_rect)
    
    def render_enhanced_ready_phase(self, screen, x_offset, y_offset):
        """Render the enhanced ready phase with difficulty-specific features."""
        center_x = Config.WINDOW_WIDTH // 2 + x_offset
        center_y = Config.WINDOW_HEIGHT // 2 + y_offset
        difficulty_config = self.get_difficulty_config()
        
        # Show countdown timer for easy mode with enhanced design
        if difficulty_config.get("countdown_enabled", False):
            self.render_enhanced_countdown_timer(screen, center_x, center_y - 80)
        
        # Show warning indicator if enabled and active
        if self.warning_shown:
            self.render_enhanced_warning_indicator(screen, center_x, center_y - 100)
        
        # Main red circle with enhanced pulsing effect
        pulse_speed = 12 if self.warning_shown else 8
        pulse = 1.0 + 0.3 * math.sin(self.animation_time * pulse_speed) + self.reaction_area["pulse"]
        radius = int(80 * pulse)
        
        # Draw enhanced circle with glow
        if self.reaction_area["outer_glow"] > 0:
            glow_radius = self.reaction_area["outer_glow"]
            glow_surface = pygame.Surface((radius * 2 + 20, radius * 2 + 20), pygame.SRCALPHA)
            for r in range(int(glow_radius), 0, -2):
                alpha = 150 - (r * 10)
                if alpha > 0:
                    pygame.draw.circle(glow_surface, (255, 50, 50, alpha), 
                                     (glow_surface.get_width() // 2, glow_surface.get_height() // 2), 
                                     radius + r)
            screen.blit(glow_surface, (center_x - radius - 10, center_y - radius - 10))
        
        # Draw shadow and main circle
        pygame.draw.circle(screen, self.SHADOW_GRAY, (center_x + 3, center_y + 3), radius + 8)
        pygame.draw.circle(screen, Config.CARTOON_RED, (center_x, center_y), radius)
        
        # Enhanced outline with varying thickness
        outline_thickness = 4 + int(2 * math.sin(self.animation_time * 6))
        pygame.draw.circle(screen, self.OUTLINE_DARK, (center_x, center_y), radius, outline_thickness)
        
        # Warning text with enhanced style
        warning_text = "GET READY!" if self.warning_shown else "WAIT FOR"
        second_text = "ALMOST TIME!" if self.warning_shown else "GREEN!"
        
        font_large = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_LARGE)
        font_huge = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_HUGE)
        
        text1 = font_large.render(warning_text, True, Config.WHITE)
        text2 = font_huge.render(second_text, True, Config.BRIGHT_YELLOW)
        
        screen.blit(text1, (center_x - text1.get_width()//2, center_y - 25))
        screen.blit(text2, (center_x - text2.get_width()//2, center_y + 5))
    
    def render_enhanced_countdown_timer(self, screen, x, y):
        """Render enhanced countdown timer for easy mode."""
        if self.countdown_time > 0:
            countdown_text = f"{self.countdown_time:.1f}"
            seconds_text = "SECONDS"
            
            # Draw timer background
            timer_bg = pygame.Rect(x - 40, y - 25, 80, 60)
            self.draw_rounded_rect(screen, timer_bg, Config.ENERGETIC_ORANGE, 8)
            self.draw_rounded_rect(screen, timer_bg, self.OUTLINE_DARK, 8, 2)
            
            # Draw countdown numbers
            font = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_LARGE)
            text = font.render(countdown_text, True, Config.WHITE)
            screen.blit(text, (x - text.get_width()//2, y - 12))
            
            # Draw "seconds" text
            font_small = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_SMALL)
            text = font_small.render(seconds_text, True, Config.WHITE)
            screen.blit(text, (x - text.get_width()//2, y + 10))
    
    def render_enhanced_warning_indicator(self, screen, x, y):
        """Render enhanced warning indicator before green signal."""
        # Flashing warning with animation
        flash_factor = math.sin(self.animation_time * 8) * 0.5 + 0.5
        warning_color = (
            int(255 * flash_factor),
            int(200 * flash_factor),
            int(50 * flash_factor)
        )
        
        # Draw warning triangle
        points = [
            (x, y - 20),
            (x - 15, y + 15),
            (x + 15, y + 15)
        ]
        pygame.draw.polygon(screen, warning_color, points)
        pygame.draw.polygon(screen, self.OUTLINE_DARK, points, 2)
        
        # Draw exclamation mark
        pygame.draw.rect(screen, self.OUTLINE_DARK, (x - 3, y - 7, 6, 10))
        pygame.draw.circle(screen, self.OUTLINE_DARK, (x, y + 18), 3)
    
    def render_enhanced_green_phase(self, screen, x_offset, y_offset):
        """Render the enhanced green phase with exciting GO signal."""
        center_x = Config.WINDOW_WIDTH // 2 + x_offset
        center_y = Config.WINDOW_HEIGHT // 2 + y_offset
        
        # Growing green circle with enhanced effect
        growth = 1.0 + 0.5 * math.sin(self.animation_time * 12)
        radius = int(90 * growth)
        
        # Draw enhanced glow
        if self.reaction_area["outer_glow"] > 0:
            glow_radius = self.reaction_area["outer_glow"]
            glow_surface = pygame.Surface((radius * 2 + 30, radius * 2 + 30), pygame.SRCALPHA)
            for r in range(int(glow_radius), 0, -2):
                alpha = 200 - (r * 10)
                if alpha > 0:
                    pygame.draw.circle(glow_surface, (50, 255, 50, alpha), 
                                     (glow_surface.get_width() // 2, glow_surface.get_height() // 2), 
                                     radius + r)
            screen.blit(glow_surface, (center_x - radius - 15, center_y - radius - 15))
        
        # Draw shadow and main circle
        pygame.draw.circle(screen, self.SHADOW_GRAY, (center_x + 5, center_y + 5), radius + 10)
        pygame.draw.circle(screen, Config.CARTOON_GREEN, (center_x, center_y), radius)
        
        # Enhanced outline with sparkle effect
        outline_thickness = 6 + int(3 * math.sin(self.animation_time * 10))
        pygame.draw.circle(screen, self.OUTLINE_DARK, (center_x, center_y), radius, outline_thickness)
        
        # Sparkle effects with enhanced animation
        self.render_enhanced_sparkles(screen, center_x, center_y, radius)
        
        # "CLICK NOW!" text with enhanced style
        font = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_HUGE)
        
        text1 = font.render("CLICK", True, Config.WHITE)
        text2 = font.render("NOW!", True, Config.BRIGHT_YELLOW)
        
        screen.blit(text1, (center_x - text1.get_width()//2, center_y - 25))
        screen.blit(text2, (center_x - text2.get_width()//2, center_y + 10))
    
    def render_enhanced_sparkles(self, screen, center_x, center_y, radius):
        """Render enhanced sparkle effects around green circle."""
        for i in range(8):  # Fewer sparkles
            angle = (i / 8) * 2 * math.pi + self.animation_time * 5
            distance = radius + 20 + 8 * math.sin(self.animation_time * 3 + i)
            sparkle_x = center_x + int(distance * math.cos(angle))
            sparkle_y = center_y + int(distance * math.sin(angle))
            
            # Varying sparkle sizes and shapes
            sparkle_size = 3 + 3 * math.sin(self.animation_time * 6 + i)
            
            # Draw different sparkle shapes
            if i % 3 == 0:
                # Star shape
                points = []
                for j in range(5):
                    star_angle = j * 2 * math.pi / 5 + self.animation_time * 2
                    points.append((
                        sparkle_x + sparkle_size * math.cos(star_angle),
                        sparkle_y + sparkle_size * math.sin(star_angle)
                    ))
                    points.append((
                        sparkle_x + sparkle_size * 0.5 * math.cos(star_angle + math.pi/5),
                        sparkle_y + sparkle_size * 0.5 * math.sin(star_angle + math.pi/5)
                    ))
                pygame.draw.polygon(screen, Config.BRIGHT_YELLOW, points)
            else:
                # Circle sparkle
                pygame.draw.circle(screen, Config.BRIGHT_YELLOW, 
                                 (sparkle_x, sparkle_y), int(sparkle_size))
    
    def render_enhanced_result_phase(self, screen, x_offset, y_offset):
        """Render the enhanced result phase with celebration or failure animation."""
        center_x = Config.WINDOW_WIDTH // 2 + x_offset
        center_y = Config.WINDOW_HEIGHT // 2 + y_offset
        
        # Enhanced performance burst animation
        burst_age = time.time() - self.result_burst_time
        if burst_age < 2.0:
            self.draw_performance_burst(screen, center_x, center_y - 60, self.performance_level, burst_age)
        
        # Enhanced result panel - draw shadow first
        result_panel = pygame.Rect(center_x - 150, center_y - 50, 300, 150)
        shadow_panel = pygame.Rect(result_panel.x + 5, result_panel.y + 5, result_panel.width, result_panel.height)
        shadow_surface = pygame.Surface((shadow_panel.width, shadow_panel.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, self.SHADOW_GRAY, (0, 0, shadow_panel.width, shadow_panel.height), border_radius=15)
        screen.blit(shadow_surface, shadow_panel)
        
        # Draw main panel
        self.draw_rounded_rect(screen, result_panel, Config.WHITE, 15)
        self.draw_rounded_rect(screen, result_panel, self.OUTLINE_DARK, 15, 4)
        
        # Results content with enhanced design
        self.render_enhanced_result_content(screen, center_x, center_y)
    
    def draw_performance_burst(self, screen, x, y, level, age):
        """Draw a performance burst effect."""
        max_size = 70
        size = min(max_size, age * 35)
        alpha = max(0, 255 - (age * 127))
        
        if size > 0:
            # Create burst surface
            burst_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            
            # Draw burst based on performance level
            if level == "excellent":
                color = (255, 215, 0, alpha)  # Gold
            elif level == "good":
                color = (0, 255, 255, alpha)  # Cyan
            elif level == "average":
                color = (50, 205, 50, alpha)  # Green
            elif level == "poor":
                color = (255, 165, 0, alpha)  # Orange
            elif level == "meh":
                color = (128, 128, 128, alpha)  # Gray
            else:  # terrible
                color = (255, 0, 0, alpha)  # Red
            
            # Draw burst shape
            for i in range(8):
                angle = i * math.pi / 4
                end_x = size + size * math.cos(angle)
                end_y = size + size * math.sin(angle)
                pygame.draw.line(burst_surface, color, (size, size), (end_x, end_y), 3)
            
            # Draw central circle
            pygame.draw.circle(burst_surface, color, (size, size), size // 5)
            
            # Draw to screen
            screen.blit(burst_surface, (x - size, y - size))
    
    def render_enhanced_result_content(self, screen, center_x, center_y):
        """Render enhanced result phase content."""
        # Bouncy reaction time with enhanced animation
        time_bounce = 1.0 + 0.15 * math.sin(self.animation_time * 8)
        time_font_size = int(self.FONT_TITLE * time_bounce)
        
        font = pygame.font.SysFont(self.FONT_CARTOON, time_font_size)
        text = font.render(str(self.reaction_time), True, Config.AQUA_BLUE)
        screen.blit(text, (center_x - text.get_width()//2, center_y - 25))
        
        # Performance rating with icon
        performance_icon = self.performance_indicators.get(self.performance_level, "⭐")
        rating_text = f"{performance_icon} {self.performance_rating}"
        
        font_large = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_LARGE)
        text = font_large.render(rating_text, True, Config.PLAYFUL_PURPLE)
        screen.blit(text, (center_x - text.get_width()//2, center_y + 10))
        
        # Result message with enhanced style
        font_medium = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_MEDIUM)
        text = font_medium.render(self.result_message, True, Config.ENERGETIC_ORANGE)
        screen.blit(text, (center_x - text.get_width()//2, center_y + 40))
        
        # Continue instruction with animated arrow
        instruction = "Click or press SPACE to try again!"
        arrow = "➡️" if int(self.animation_time * 2) % 2 else "⬅️"
        
        self.draw_speech_bubble(
            screen, f"{instruction} {arrow}",
            center_x, center_y + 80, 350,
            bubble_color=self.BANANA_YELLOW,
            text_color=Config.BLACK
        )
    
    def render_enhanced_paused_phase(self, screen):
        """Render the enhanced paused state with cartoon overlay."""
        # Semi-transparent overlay with pattern
        overlay = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        
        # Add pattern to overlay
        for y in range(0, Config.WINDOW_HEIGHT, 20):
            for x in range(0, Config.WINDOW_WIDTH, 20):
                if (x + y) % 40 == 0:
                    pygame.draw.rect(overlay, (255, 255, 255, 30), (x, y, 10, 10))
        
        screen.blit(overlay, (0, 0))
        
        center_x = Config.WINDOW_WIDTH // 2
        center_y = Config.WINDOW_HEIGHT // 2
        
        # Enhanced pause panel - draw shadow first
        pause_panel = pygame.Rect(center_x - 140, center_y - 70, 280, 140)
        shadow_panel = pygame.Rect(pause_panel.x + 8, pause_panel.y + 8, pause_panel.width, pause_panel.height)
        shadow_surface = pygame.Surface((shadow_panel.width, shadow_panel.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, self.SHADOW_GRAY, (0, 0, shadow_panel.width, shadow_panel.height), border_radius=15)
        screen.blit(shadow_surface, shadow_panel)
        
        # Draw main panel
        self.draw_rounded_rect(screen, pause_panel, Config.BRIGHT_YELLOW, 15)
        self.draw_rounded_rect(screen, pause_panel, self.OUTLINE_DARK, 15, 5)
        
        # Pause text with enhanced style
        font_title = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_TITLE)
        text = font_title.render("GAME PAUSED", True, Config.AQUA_BLUE)
        screen.blit(text, (center_x - text.get_width()//2, center_y - 35))
        
        # Animated pause icon
        pause_icon = "⏸️" if int(self.animation_time * 2) % 2 else "▶️"
        font_icon = pygame.font.SysFont(self.FONT_CARTOON, 35)
        text = font_icon.render(pause_icon, True, Config.PLAYFUL_PURPLE)
        screen.blit(text, (center_x - text.get_width()//2, center_y))
        
        # Continue instruction
        font_medium = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_MEDIUM)
        text = font_medium.render("Press P to resume", True, Config.BLACK)
        screen.blit(text, (center_x - text.get_width()//2, center_y + 35))
    
    def render_enhanced_statistics(self, screen, shake_offset):
        """Render enhanced session statistics in cartoon style."""
        shake_x, shake_y = shake_offset
        
        # Apply slide offset for hiding/showing
        slide_offset = self.stats_panel["slide_offset"]
        
        stats_panel = pygame.Rect(
            self.stats_panel["rect"].x + shake_x + slide_offset,
            self.stats_panel["rect"].y + shake_y,
            self.stats_panel["rect"].width,
            self.stats_panel["rect"].height
        )
        
        # Only render if visible or sliding
        if self.stats_panel["visible"] or slide_offset > -280:
            # Draw panel shadow first
            shadow_panel = pygame.Rect(stats_panel.x + 5, stats_panel.y + 5, stats_panel.width, stats_panel.height)
            shadow_surface = pygame.Surface((shadow_panel.width, shadow_panel.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, self.SHADOW_GRAY, (0, 0, shadow_panel.width, shadow_panel.height), border_radius=10)
            screen.blit(shadow_surface, shadow_panel)
            
            # Draw panel
            self.draw_rounded_rect(screen, stats_panel, self.BANANA_YELLOW, 10)
            self.draw_rounded_rect(screen, stats_panel, self.OUTLINE_DARK, 10, 3)
            
            # Statistics content
            self.render_enhanced_statistics_content(screen, stats_panel)
    
    def render_enhanced_statistics_content(self, screen, stats_panel):
        """Render the enhanced content of the statistics panel."""
        save_manager = self.game_manager.get_save_manager()
        difficulty = save_manager.get_setting("difficulty", "normal")
        difficulty_color = Config.DIFFICULTY_COLORS.get(difficulty, Config.GRAY)
        
        stats_x = stats_panel.x + 10
        stats_y = stats_panel.y + 10
        
        # Panel title
        font_small = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_SMALL)
        text = font_small.render("SESSION STATS", True, Config.PLAYFUL_PURPLE)
        screen.blit(text, (stats_x + 50, stats_y - 5))
        
        # Render each stat line with icons
        stats_data = [
            (f"🎯 {difficulty.upper()}", difficulty_color, 20),
            (f"📊 Attempts: {self.attempts}", Config.BLACK, 40),
            (f"🏆 Best: {self.best_time}ms" if self.best_time else "🏆 Best: --", 
             Config.CARTOON_GREEN, 60),
            (f"📈 Avg: {sum(self.session_times) / len(self.session_times):.0f}ms" if self.session_times else "📈 Average: --", 
             Config.AQUA_BLUE, 80)
        ]
        
        font_small = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_SMALL)
        for text, color, y_offset in stats_data:
            text_surface = font_small.render(text, True, color)
            screen.blit(text_surface, (stats_x, stats_y + y_offset))
        
        # Draw toggle hint
        if not self.stats_panel["visible"] or self.stats_panel["slide_offset"] < 0:
            font_tiny = pygame.font.SysFont(self.FONT_CARTOON, self.FONT_TINY)
            hint_text = "Press S to show stats"
            text = font_tiny.render(hint_text, True, Config.SHADOW_GRAY)
            screen.blit(text, (stats_x + 30, stats_y + 100))