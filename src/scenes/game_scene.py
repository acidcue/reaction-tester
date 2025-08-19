"""Main game scene with cartoony SpongeBob + Minions style gameplay."""
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
    """The main gameplay scene with cartoony reaction time testing."""
    
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
        
        # UI elements
        self.setup_ui_elements()
    
    def setup_ui_elements(self):
        """Initialize UI button positions and reaction area."""
        self.back_button = pygame.Rect(20, 20, 120, 50)
        self.pause_button = pygame.Rect(Config.WINDOW_WIDTH - 140, 20, 120, 50)
        
        # Central reaction area (big cartoon circle)
        self.reaction_area = pygame.Rect(
            Config.WINDOW_WIDTH // 2 - 150,
            Config.WINDOW_HEIGHT // 2 - 150,
            300, 300
        )
    
    def enter(self):
        """Called when entering the game scene."""
        self.reset_game()
        self.particles.clear()
        self.animation_time = 0
    
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
    
    # ================================
    # EVENT HANDLING
    # ================================
    
    def handle_event(self, event):
        """Handle game input events."""
        if event.type == pygame.KEYDOWN:
            self.handle_keyboard_input(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_input(event)
    
    def handle_keyboard_input(self, event):
        """Process keyboard input."""
        if event.key == pygame.K_ESCAPE:
            self.game_manager.request_state_change(GameState.MAIN_MENU)
        elif event.key == pygame.K_p:
            self.toggle_pause()
        elif event.key == pygame.K_SPACE:
            self.handle_reaction_input()
    
    def handle_mouse_input(self, event):
        """Process mouse input."""
        if event.button == 1:  # Left click
            mouse_pos = pygame.mouse.get_pos()
            
            if self.back_button.collidepoint(mouse_pos):
                self.game_manager.request_state_change(GameState.MAIN_MENU)
            elif self.pause_button.collidepoint(mouse_pos):
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
            self.particles.add_burst(center_x, center_y, 20)
        except:
            pass
    
    def add_celebration_particles(self):
        """Add celebration particle burst."""
        try:
            center_x = Config.WINDOW_WIDTH // 2
            center_y = Config.WINDOW_HEIGHT // 2
            self.particles.add_burst(center_x, center_y, 30)
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
        self.particles.update(dt)
        self.update_background_transition(dt)
        self.update_screen_shake(dt)
        self.check_green_transition()
    
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
    
    # ================================
    # RENDERING
    # ================================
    
    def render(self, screen):
        """Render the cartoony game scene."""
        # Calculate screen shake offset
        shake_offset = self.get_shake_offset()
        
        # Fill background
        screen.fill(self.background_color)
        
        # Draw visual elements
        self.particles.render(screen)
        self.render_ui_buttons(screen, shake_offset)
        self.render_game_content(screen, shake_offset)
        self.render_statistics_if_enabled(screen, shake_offset)
    
    def get_shake_offset(self):
        """Calculate screen shake offset."""
        if self.screen_shake > 0:
            shake_x = int(random.uniform(-self.screen_shake, self.screen_shake))
            shake_y = int(random.uniform(-self.screen_shake, self.screen_shake))
            return (shake_x, shake_y)
        return (0, 0)
    
    def render_ui_buttons(self, screen, shake_offset):
        """Draw UI buttons with shake effect."""
        shake_x, shake_y = shake_offset
        
        # Back button
        back_rect = pygame.Rect(
            self.back_button.x + shake_x, 
            self.back_button.y + shake_y, 
            self.back_button.width, 
            self.back_button.height
        )
        CartoonUI.draw_bouncy_button(
            screen, "🏠 BACK", back_rect, 
            Config.ENERGETIC_ORANGE, Config.WHITE, 
            bounce_time=self.animation_time
        )
        
        # Pause button
        pause_rect = pygame.Rect(
            self.pause_button.x + shake_x,
            self.pause_button.y + shake_y,
            self.pause_button.width,
            self.pause_button.height
        )
        CartoonUI.draw_bouncy_button(
            screen, "⏸️ PAUSE", pause_rect, 
            Config.PLAYFUL_PURPLE, Config.WHITE,
            bounce_time=self.animation_time
        )
    
    def render_game_content(self, screen, shake_offset):
        """Render main game content based on current phase."""
        shake_x, shake_y = shake_offset
        
        if self.phase == GamePhase.WAITING:
            self.render_waiting_phase(screen, shake_x, shake_y)
        elif self.phase == GamePhase.READY:
            self.render_ready_phase(screen, shake_x, shake_y)
        elif self.phase == GamePhase.GREEN:
            self.render_green_phase(screen, shake_x, shake_y)
        elif self.phase == GamePhase.RESULT:
            self.render_result_phase(screen, shake_x, shake_y)
        elif self.phase == GamePhase.PAUSED:
            self.render_paused_phase(screen)
    
    def render_waiting_phase(self, screen, x_offset, y_offset):
        """Render the waiting phase with cartoon instructions."""
        difficulty_config = self.get_difficulty_config()
        save_manager = self.game_manager.get_save_manager()
        difficulty = save_manager.get_setting("difficulty", "normal")
        
        # Central reaction area
        reaction_rect = pygame.Rect(
            self.reaction_area.x + x_offset,
            self.reaction_area.y + y_offset,
            self.reaction_area.width,
            self.reaction_area.height
        )
        CartoonUI.draw_cartoon_panel(screen, reaction_rect, Config.WHITE)
        
        # Pulsing "READY?" text
        pulse_scale = 1.0 + 0.2 * math.sin(self.animation_time * 4)
        font_size = int(Config.FONT_HUGE * pulse_scale)
        
        CartoonUI.draw_wiggling_text(
            screen, "READY?", 
            Config.WINDOW_WIDTH // 2 - 80 + x_offset, 
            Config.WINDOW_HEIGHT // 2 - 20 + y_offset,
            self.animation_time, Config.AQUA_BLUE, font_size
        )
        
        # Instructions
        self.render_waiting_instructions(screen, x_offset, y_offset, difficulty, difficulty_config)
    
    def render_waiting_instructions(self, screen, x_offset, y_offset, difficulty, difficulty_config):
        """Render waiting phase instructions with difficulty-specific tips."""
        instructions = [
            "Click anywhere or press SPACE when ready!",
            "Wait for GREEN, then react FAST!"
        ]
        
        # Add difficulty-specific tips
        if difficulty == "easy":
            instructions.append("💡 TIP: You'll see a countdown timer!")
        elif difficulty == "twitchy-god":
            instructions.append("⚠️ WARNING: Watch out for fake signals!")
        
        instruction_y = Config.WINDOW_HEIGHT // 2 + 180
        for i, instruction in enumerate(instructions):
            if i < 2:  # Main instructions
                CartoonUI.draw_speech_bubble(
                    screen, instruction,
                    Config.WINDOW_WIDTH // 2 + x_offset,
                    instruction_y + (i * 60) + y_offset,
                    500  # Wider bubbles
                )
            else:  # Tips
                CartoonUI.draw_wiggling_text(
                    screen, instruction,
                    Config.WINDOW_WIDTH // 2 - 120 + x_offset,
                    instruction_y + 120 + ((i-2) * 30) + y_offset,
                    self.animation_time * 0.8, Config.PLAYFUL_PURPLE, Config.FONT_SMALL
                )
        
        # Difficulty info
        difficulty_info = [
            f"Mode: {difficulty.upper()}",
            f"Excellent: Under {difficulty_config['excellent_threshold']}ms",
            f"Wait Range: {difficulty_config['min_wait']:.1f}s - {difficulty_config['max_wait']:.1f}s"
        ]
        
        for i, info in enumerate(difficulty_info):
            color = Config.DIFFICULTY_COLORS.get(difficulty, Config.BLACK)
            if i == 0:
                color = Config.DIFFICULTY_COLORS.get(difficulty, Config.BLACK)
            else:
                color = Config.SHADOW_GRAY
                
            CartoonUI.draw_wiggling_text(
                screen, info,
                Config.WINDOW_WIDTH // 2 - 100 + x_offset,
                instruction_y + 200 + (i * 25) + y_offset,
                self.animation_time * (0.8 - i * 0.1), color, Config.FONT_SMALL
            )
    
    def render_ready_phase(self, screen, x_offset, y_offset):
        """Render the ready phase with difficulty-specific features."""
        center_x = Config.WINDOW_WIDTH // 2 + x_offset
        center_y = Config.WINDOW_HEIGHT // 2 + y_offset
        difficulty_config = self.get_difficulty_config()
        
        # Show countdown timer for easy mode
        if difficulty_config.get("countdown_enabled", False):
            self.render_countdown_timer(screen, center_x, center_y - 100)
        
        # Show warning indicator if enabled and active
        if self.warning_shown:
            self.render_warning_indicator(screen, center_x, center_y - 150)
        
        # Main red circle (pulsing faster if warning is shown)
        pulse_speed = 12 if self.warning_shown else 8
        pulse = 1.0 + 0.3 * math.sin(self.animation_time * pulse_speed)
        radius = int(120 * pulse)
        
        # Draw shadow and main circle
        pygame.draw.circle(screen, Config.SHADOW_GRAY, (center_x + 5, center_y + 5), radius + 10)
        pygame.draw.circle(screen, Config.CARTOON_RED, (center_x, center_y), radius)
        pygame.draw.circle(screen, Config.OUTLINE_DARK, (center_x, center_y), radius, 6)
        
        # Warning text
        warning_text = "GET READY!" if self.warning_shown else "WAIT FOR"
        second_text = "ALMOST TIME!" if self.warning_shown else "GREEN!"
        
        CartoonUI.draw_wiggling_text(
            screen, warning_text, center_x - 80, center_y - 30,
            self.animation_time, Config.WHITE, Config.FONT_LARGE
        )
        CartoonUI.draw_wiggling_text(
            screen, second_text, center_x - 60, center_y + 10,
            self.animation_time, Config.BRIGHT_YELLOW, Config.FONT_HUGE
        )
    
    def render_countdown_timer(self, screen, x, y):
        """Render countdown timer for easy mode."""
        if self.countdown_time > 0:
            countdown_text = f"{self.countdown_time:.1f}s"
            CartoonUI.draw_wiggling_text(
                screen, countdown_text, x - 30, y,
                self.animation_time, Config.ENERGETIC_ORANGE, Config.FONT_LARGE
            )
    
    def render_warning_indicator(self, screen, x, y):
        """Render warning indicator before green signal."""
        # Flashing warning
        if int(self.animation_time * 8) % 2:
            CartoonUI.draw_wiggling_text(
                screen, "⚠️ READY ⚠️", x - 60, y,
                self.animation_time, Config.BRIGHT_YELLOW, Config.FONT_MEDIUM
            )
    
    def render_green_phase(self, screen, x_offset, y_offset):
        """Render the green phase with exciting GO signal."""
        center_x = Config.WINDOW_WIDTH // 2 + x_offset
        center_y = Config.WINDOW_HEIGHT // 2 + y_offset
        
        # Growing green circle
        growth = 1.0 + 0.5 * math.sin(self.animation_time * 12)
        radius = int(140 * growth)
        
        # Draw shadow and main circle
        pygame.draw.circle(screen, Config.SHADOW_GRAY, (center_x + 8, center_y + 8), radius + 15)
        pygame.draw.circle(screen, Config.CARTOON_GREEN, (center_x, center_y), radius)
        pygame.draw.circle(screen, Config.OUTLINE_DARK, (center_x, center_y), radius, 8)
        
        # Sparkle effects
        self.render_sparkles(screen, center_x, center_y, radius)
        
        # "CLICK NOW!" text
        CartoonUI.draw_wiggling_text(
            screen, "CLICK", center_x - 60, center_y - 30,
            self.animation_time, Config.WHITE, Config.FONT_HUGE
        )
        CartoonUI.draw_wiggling_text(
            screen, "NOW!", center_x - 50, center_y + 20,
            self.animation_time, Config.BRIGHT_YELLOW, Config.FONT_HUGE
        )
    
    def render_sparkles(self, screen, center_x, center_y, radius):
        """Render sparkle effects around green circle."""
        for i in range(8):
            angle = (i / 8) * 2 * math.pi + self.animation_time * 3
            sparkle_x = center_x + int((radius + 30) * math.cos(angle))
            sparkle_y = center_y + int((radius + 30) * math.sin(angle))
            sparkle_size = 5 + 3 * math.sin(self.animation_time * 6 + i)
            pygame.draw.circle(screen, Config.BRIGHT_YELLOW, 
                             (sparkle_x, sparkle_y), int(sparkle_size))
    
    def render_result_phase(self, screen, x_offset, y_offset):
        """Render the result phase with celebration or failure animation."""
        center_x = Config.WINDOW_WIDTH // 2 + x_offset
        center_y = Config.WINDOW_HEIGHT // 2 + y_offset
        
        # Performance burst animation
        burst_age = time.time() - self.result_burst_time
        if burst_age < 2.0:
            CartoonUI.draw_performance_burst(
                screen, center_x, center_y - 80, 
                self.performance_level, burst_age
            )
        
        # Result panel
        result_panel = pygame.Rect(center_x - 200, center_y - 50, 400, 200)
        CartoonUI.draw_cartoon_panel(screen, result_panel, Config.WHITE)
        
        # Results content
        self.render_result_content(screen, center_x, center_y)
    
    def render_result_content(self, screen, center_x, center_y):
        """Render result phase content."""
        # Bouncy reaction time
        time_bounce = 1.0 + 0.1 * math.sin(self.animation_time * 6)
        time_font_size = int(Config.FONT_TITLE * time_bounce)
        
        CartoonUI.draw_wiggling_text(
            screen, str(self.reaction_time),
            center_x - 80, center_y - 30,
            self.animation_time, Config.AQUA_BLUE, time_font_size
        )
        
        # Performance rating
        CartoonUI.draw_wiggling_text(
            screen, self.performance_rating,
            center_x - 120, center_y + 20,
            self.animation_time, Config.PLAYFUL_PURPLE, Config.FONT_LARGE
        )
        
        # Result message
        CartoonUI.draw_wiggling_text(
            screen, self.result_message,
            center_x - 100, center_y + 60,
            self.animation_time * 0.7, Config.ENERGETIC_ORANGE, Config.FONT_MEDIUM
        )
        
        # Continue instruction
        CartoonUI.draw_speech_bubble(
            screen, "Click or press SPACE to try again!",
            center_x, center_y + 140, 350
        )
    
    def render_paused_phase(self, screen):
        """Render the paused state with cartoon overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(Config.SHADOW_GRAY)
        screen.blit(overlay, (0, 0))
        
        center_x = Config.WINDOW_WIDTH // 2
        center_y = Config.WINDOW_HEIGHT // 2
        
        # Pause panel
        pause_panel = pygame.Rect(center_x - 150, center_y - 80, 300, 160)
        CartoonUI.draw_cartoon_panel(screen, pause_panel, Config.BRIGHT_YELLOW)
        
        # Pause text
        CartoonUI.draw_wiggling_text(
            screen, "PAUSED", center_x - 80, center_y - 40,
            self.animation_time, Config.AQUA_BLUE, Config.FONT_TITLE
        )
        CartoonUI.draw_wiggling_text(
            screen, "Press P to resume", center_x - 90, center_y + 20,
            self.animation_time * 0.8, Config.PLAYFUL_PURPLE, Config.FONT_MEDIUM
        )
    
    def render_statistics_if_enabled(self, screen, shake_offset):
        """Render statistics if enabled in settings."""
        save_manager = self.game_manager.get_save_manager()
        show_stats = save_manager.get_setting("show_statistics", True)
        if show_stats:
            self.render_statistics(screen, shake_offset)
    
    def render_statistics(self, screen, shake_offset):
        """Render session statistics in cartoon style."""
        shake_x, shake_y = shake_offset
        stats_panel = pygame.Rect(
            20 + shake_x, 
            Config.WINDOW_HEIGHT - 140 + shake_y, 
            250, 120
        )
        CartoonUI.draw_cartoon_panel(screen, stats_panel, Config.BANANA_YELLOW)
        
        # Statistics content
        self.render_statistics_content(screen, stats_panel)
    
    def render_statistics_content(self, screen, stats_panel):
        """Render the content of the statistics panel."""
        save_manager = self.game_manager.get_save_manager()
        difficulty = save_manager.get_setting("difficulty", "normal")
        difficulty_color = Config.DIFFICULTY_COLORS.get(difficulty, Config.GRAY)
        
        stats_x = stats_panel.x + 15
        stats_y = stats_panel.y + 15
        
        # Render each stat line
        stats_data = [
            (f"Mode: {difficulty.upper()}", difficulty_color, 0),
            (f"Attempts: {self.attempts}", Config.BLACK, 25),
            (f"Session Best: {self.best_time}ms" if self.best_time else "Session Best: --", 
             Config.CARTOON_GREEN, 50),
            (f"Average: {sum(self.session_times) / len(self.session_times):.0f}ms" if self.session_times else "Average: --", 
             Config.AQUA_BLUE, 75)
        ]
        
        for i, (text, color, y_offset) in enumerate(stats_data):
            CartoonUI.draw_wiggling_text(
                screen, text, stats_x, stats_y + y_offset,
                self.animation_time * (0.9 - i * 0.1), color, Config.FONT_SMALL
            )