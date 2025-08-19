"""Main menu scene with cartoony SpongeBob + Minions style."""
import pygame
import math
import time
import random
from .base_scene import BaseScene
from config import Config
from game_states import GameState
from utils.particles import ParticleSystem
from utils.cartoon_ui import CartoonUI

class MainMenuScene(BaseScene):
    """Main menu with cartoony animated background and bouncy menu options."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        
        # Animation and timing
        self.animation_time = 0
        
        # Particle system for background effects
        self.particles = ParticleSystem(Config.PARTICLE_COUNT)
        
        # Menu navigation
        self.selected_option = 0
        self.menu_options = [
            ("🎮 PLAY", GameState.PLAYING),
            ("🏆 SCORES", GameState.LEADERBOARD), 
            ("⚙️ SETTINGS", GameState.SETTINGS),
            ("👋 QUIT", GameState.QUIT)
        ]
        
        # UI elements
        self.button_rects = []
        self.background_bubbles = []
        
        # Setup UI
        self.setup_buttons()
        self.setup_background_elements()
    
    def setup_buttons(self):
        """Create bouncy button rectangles with proper spacing."""
        button_width = Config.BUTTON_WIDTH
        button_height = Config.BUTTON_HEIGHT
        
        # Center the buttons vertically with better spacing
        total_height = len(self.menu_options) * button_height + (len(self.menu_options) - 1) * Config.BUTTON_SPACING
        start_y = (Config.WINDOW_HEIGHT - total_height) // 2 + 50  # Offset down a bit
        
        self.button_rects = []
        for i, (text, _) in enumerate(self.menu_options):
            x = (Config.WINDOW_WIDTH - button_width) // 2  # Perfect center
            y = start_y + (i * (button_height + Config.BUTTON_SPACING))
            self.button_rects.append(pygame.Rect(x, y, button_width, button_height))
    
    def setup_background_elements(self):
        """Create floating background bubbles for cartoon atmosphere."""
        self.background_bubbles = []
        
        # Create floating bubbles/elements
        for _ in range(15):
            bubble = {
                'x': random.randint(0, Config.WINDOW_WIDTH),
                'y': random.randint(0, Config.WINDOW_HEIGHT),
                'size': random.randint(20, 60),
                'speed': random.uniform(0.5, 2.0),
                'wobble_offset': random.uniform(0, 2 * math.pi),
                'color': random.choice([
                    Config.BANANA_YELLOW,
                    Config.AQUA_BLUE,
                    Config.PLAYFUL_PURPLE,
                    Config.ENERGETIC_ORANGE
                ])
            }
            self.background_bubbles.append(bubble)
    
    def handle_event(self, event):
        """Handle menu events with bouncy feedback."""
        if event.type == pygame.KEYDOWN:
            self.handle_keyboard_input(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_click(event)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_hover(event)
    
    def handle_keyboard_input(self, event):
        """Process keyboard navigation."""
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            self.play_menu_sound()
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            self.play_menu_sound()
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self.select_current_option()
    
    def handle_mouse_click(self, event):
        """Process mouse clicks on buttons."""
        if event.button == 1:  # Left click
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_option = i
                    self.select_current_option()
    
    def handle_mouse_hover(self, event):
        """Process mouse hover for button highlighting."""
        mouse_pos = pygame.mouse.get_pos()
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(mouse_pos):
                if self.selected_option != i:
                    self.selected_option = i
                    self.play_menu_sound()
    
    def select_current_option(self):
        """Execute the currently selected menu option."""
        _, target_state = self.menu_options[self.selected_option]
        self.game_manager.request_state_change(target_state)
    
    def play_menu_sound(self):
        """Play menu navigation sound effect."""
        try:
            self.game_manager.get_sound_manager().play_sound('menu_select')
        except:
            pass  # Ignore sound errors
    
    def update(self, dt):
        """Update animations and particles."""
        self.animation_time += dt
        
        # Update particle system
        self.particles.update(dt)
        
        # Update floating bubbles
        self.update_background_bubbles(dt)
    
    def update_background_bubbles(self, dt):
        """Update floating bubble animations."""
        for bubble in self.background_bubbles:
            # Move bubbles upward with wobble
            bubble['y'] -= bubble['speed']
            bubble['x'] += math.sin(self.animation_time + bubble['wobble_offset']) * 0.5
            
            # Reset bubble when it goes off screen
            if bubble['y'] < -bubble['size']:
                bubble['y'] = Config.WINDOW_HEIGHT + bubble['size']
                bubble['x'] = random.randint(0, Config.WINDOW_WIDTH)
    
    def render(self, screen):
        """Render the cartoony main menu."""
        # Draw gradient background
        self.render_background(screen)
        
        # Draw floating background bubbles
        self.render_background_bubbles(screen)
        
        # Draw animated particles
        self.particles.render(screen)
        
        # Draw game title
        self.render_title(screen)
        
        # Draw subtitle
        self.render_subtitle(screen)
        
        # Draw menu buttons
        self.render_menu_buttons(screen)
        
        # Draw instructions
        self.render_instructions(screen)
        
        # Draw credits
        self.render_credits(screen)
    
    def render_background(self, screen):
        """Draw bright yellow gradient background."""
        for y in range(Config.WINDOW_HEIGHT):
            ratio = y / Config.WINDOW_HEIGHT
            color = [
                int(Config.BRIGHT_YELLOW[i] * (1 - ratio * 0.3) + Config.BANANA_YELLOW[i] * ratio * 0.3)
                for i in range(3)
            ]
            pygame.draw.line(screen, color, (0, y), (Config.WINDOW_WIDTH, y))
    
    def render_background_bubbles(self, screen):
        """Draw floating cartoon bubbles in the background."""
        for bubble in self.background_bubbles:
            # Calculate wobble animation
            wobble_x = bubble['x'] + math.sin(self.animation_time + bubble['wobble_offset']) * 10
            wobble_y = bubble['y'] + math.cos(self.animation_time * 0.8 + bubble['wobble_offset']) * 5
            
            # Draw bubble shadow
            shadow_x = int(wobble_x + 3)
            shadow_y = int(wobble_y + 3)
            pygame.draw.circle(screen, Config.SHADOW_GRAY, (shadow_x, shadow_y), bubble['size'] // 2)
            
            # Draw main bubble with transparency
            bubble_surface = pygame.Surface((bubble['size'], bubble['size']), pygame.SRCALPHA)
            bubble_color = (*bubble['color'], 100)  # Semi-transparent
            pygame.draw.circle(bubble_surface, bubble_color, 
                             (bubble['size'] // 2, bubble['size'] // 2), 
                             bubble['size'] // 2)
            
            # Add highlight
            highlight_color = tuple(min(255, c + 50) for c in bubble['color'][:3]) + (150,)
            pygame.draw.circle(bubble_surface, highlight_color,
                             (bubble['size'] // 3, bubble['size'] // 3),
                             bubble['size'] // 6)
            
            # Draw outline
            pygame.draw.circle(bubble_surface, Config.OUTLINE_DARK + (100,),
                             (bubble['size'] // 2, bubble['size'] // 2),
                             bubble['size'] // 2, 2)
            
            screen.blit(bubble_surface, (int(wobble_x - bubble['size'] // 2), 
                                       int(wobble_y - bubble['size'] // 2)))
    
    def render_title(self, screen):
        """Draw bouncing cartoon title."""
        CartoonUI.draw_cartoon_title(
            screen, 
            "Twitch~y", 
            Config.WINDOW_WIDTH // 2, 
            150, 
            self.animation_time
        )
    
    def render_subtitle(self, screen):
        """Draw subtitle in speech bubble."""
        CartoonUI.draw_speech_bubble(
            screen,
            "Test your lightning-fast reflexes!",
            Config.WINDOW_WIDTH // 2,
            220,
            400
        )
    
    def render_menu_buttons(self, screen):
        """Draw bouncy menu buttons."""
        for i, (text, _) in enumerate(self.menu_options):
            is_selected = (i == self.selected_option)
            
            # Button colors based on selection
            if is_selected:
                bg_color = Config.DIFFICULTY_COLORS.get(
                    ["easy", "normal", "hard", "beast"][i % 4], 
                    Config.AQUA_BLUE
                )
                text_color = Config.WHITE
            else:
                bg_color = Config.WHITE
                text_color = Config.BLACK
            
            # Draw bouncy button
            CartoonUI.draw_bouncy_button(
                screen,
                text,
                self.button_rects[i],
                bg_color,
                text_color,
                is_hovered=is_selected,
                bounce_time=self.animation_time
            )
    
    def render_instructions(self, screen):
        """Draw navigation instructions."""
        instruction_y = Config.WINDOW_HEIGHT - 80
        CartoonUI.draw_wiggling_text(
            screen,
            "Use arrow keys or mouse to navigate • ENTER or SPACE to select",
            Config.WINDOW_WIDTH // 2 - 280,
            instruction_y,
            self.animation_time,
            Config.SHADOW_GRAY,
            Config.FONT_SMALL
        )
    
    def render_credits(self, screen):
        """Draw version/credits information."""
        CartoonUI.draw_wiggling_text(
            screen,
            "Made with 💛 for lightning-fast reflexes!",
            Config.WINDOW_WIDTH // 2 - 150,
            Config.WINDOW_HEIGHT - 40,
            self.animation_time * 0.7,
            Config.PLAYFUL_PURPLE,
            Config.FONT_TINY
        )