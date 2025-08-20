"""Main menu scene with cartoony SpongeBob + Minions style."""
import pygame
import math
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
        self.setup_background_elements()
        self.setup_buttons()

    def setup_buttons(self):
        """Create smaller bouncy button rectangles below subtitle."""
        button_width = int(Config.BUTTON_WIDTH * 0.6)
        button_height = int(Config.BUTTON_HEIGHT * 0.6)
        spacing = int(Config.BUTTON_SPACING * 0.6)

        total_height = len(self.menu_options) * button_height + (len(self.menu_options) - 1) * spacing
        start_y = 180  # just below subtitle

        self.button_rects = []
        for i, (text, _) in enumerate(self.menu_options):
            x = (Config.WINDOW_WIDTH - button_width) // 2
            y = start_y + (i * (button_height + spacing))
            self.button_rects.append(pygame.Rect(x, y, button_width, button_height))

    def setup_background_elements(self):
        """Create floating background bubbles for cartoon atmosphere."""
        self.background_bubbles = []
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

    # ---------------------------
    # Input handling
    # ---------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.handle_keyboard_input(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_click(event)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_hover(event)

    def handle_keyboard_input(self, event):
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            self.play_menu_sound()
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            self.play_menu_sound()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.select_current_option()

    def handle_mouse_click(self, event):
        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_option = i
                    self.select_current_option()

    def handle_mouse_hover(self, event):
        mouse_pos = pygame.mouse.get_pos()
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(mouse_pos):
                if self.selected_option != i:
                    self.selected_option = i
                    self.play_menu_sound()

    def select_current_option(self):
        _, target_state = self.menu_options[self.selected_option]
        self.game_manager.request_state_change(target_state)

    def play_menu_sound(self):
        try:
            self.game_manager.get_sound_manager().play_sound('menu_select')
        except:
            pass

    # ---------------------------
    # Update & animation
    # ---------------------------
    def update(self, dt):
        self.animation_time += dt
        self.particles.update(dt)
        self.update_background_bubbles(dt)

    def update_background_bubbles(self, dt):
        for bubble in self.background_bubbles:
            bubble['y'] -= bubble['speed']
            bubble['x'] += math.sin(self.animation_time + bubble['wobble_offset']) * 0.5
            if bubble['y'] < -bubble['size']:
                bubble['y'] = Config.WINDOW_HEIGHT + bubble['size']
                bubble['x'] = random.randint(0, Config.WINDOW_WIDTH)

    # ---------------------------
    # Render
    # ---------------------------
    def render(self, screen):
        self.render_background(screen)
        self.render_background_bubbles(screen)
        self.particles.render(screen)

        # Title and subtitle
        self.render_title(screen)
        self.render_subtitle(screen)

        # Menu buttons
        self.render_menu_buttons(screen)

        # Footer: instructions + credits
        self.render_instructions(screen)
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
        for bubble in self.background_bubbles:
            wobble_x = bubble['x'] + math.sin(self.animation_time + bubble['wobble_offset']) * 10
            wobble_y = bubble['y'] + math.cos(self.animation_time * 0.8 + bubble['wobble_offset']) * 5
            pygame.draw.circle(screen, Config.SHADOW_GRAY, (int(wobble_x + 3), int(wobble_y + 3)), bubble['size'] // 2)

            bubble_surface = pygame.Surface((bubble['size'], bubble['size']), pygame.SRCALPHA)
            bubble_color = (*bubble['color'], 100)
            pygame.draw.circle(bubble_surface, bubble_color, (bubble['size']//2, bubble['size']//2), bubble['size']//2)

            highlight_color = tuple(min(255, c + 50) for c in bubble['color'][:3]) + (150,)
            pygame.draw.circle(bubble_surface, highlight_color, (bubble['size']//3, bubble['size']//3), bubble['size']//6)

            pygame.draw.circle(bubble_surface, Config.OUTLINE_DARK + (100,), (bubble['size']//2, bubble['size']//2), bubble['size']//2, 2)
            screen.blit(bubble_surface, (int(wobble_x - bubble['size']//2), int(wobble_y - bubble['size']//2)))

    def render_title(self, screen):
        CartoonUI.draw_cartoon_title(
            screen,
            "Twitch~y",
            Config.WINDOW_WIDTH // 2,
            40,
            self.animation_time
        )

    def render_subtitle(self, screen):
        CartoonUI.draw_speech_bubble(
            screen,
            "Test your lightning-fast reflexes!",
            Config.WINDOW_WIDTH // 2,
            120,
            420
        )

    def render_menu_buttons(self, screen):
        for i, (text, _) in enumerate(self.menu_options):
            is_selected = (i == self.selected_option)
            if is_selected:
                bg_color = Config.DIFFICULTY_COLORS.get(["easy", "normal", "hard", "beast"][i % 4], Config.AQUA_BLUE)
                text_color = Config.WHITE
            else:
                bg_color = Config.WHITE
                text_color = Config.BLACK

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
        """Footer instructions aligned left with brighter colors."""
        lines = [
            "🎯 Controls:",
            "• Mouse: Hover & Click",
            "• Arrows: Navigate",
            "• ENTER / SPACE: Select",
        ]
        base_y = Config.WINDOW_HEIGHT - 120
        for i, line in enumerate(lines):
            CartoonUI.draw_wiggling_text(
                screen,
                line,
                40,  # aligned left
                base_y + i * 26,
                self.animation_time,
                Config.WHITE,  # brighter text color for readability
                Config.FONT_SMALL
            )

    def render_credits(self, screen):
        CartoonUI.draw_wiggling_text(
            screen,
            "Made with 💛 for lightning-fast reflexes!",
            Config.WINDOW_WIDTH // 2 - 150,
            Config.WINDOW_HEIGHT - 30,
            self.animation_time * 0.7,
            Config.PLAYFUL_PURPLE,
            Config.FONT_TINY
        )
