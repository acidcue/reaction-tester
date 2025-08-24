"""Cartoony Settings scene for configuring game options."""
import pygame
import math
import random
from .base_scene import BaseScene
from config import Config
from game_states import GameState

class SettingsScene(BaseScene):
    """Cartoony settings menu with fun visuals and organized layout."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.selected_option = 0
        self.back_button = pygame.Rect(20, 20, 140, 50)
        self.reset_button = pygame.Rect(Config.WINDOW_WIDTH - 170, 20, 150, 50)  # top right
        
        # Floating cartoon background bubbles
        self.bubbles = []
        for _ in range(20):
            self.bubbles.append({
                "x": random.randint(0, Config.WINDOW_WIDTH),
                "y": random.randint(0, Config.WINDOW_HEIGHT),
                "r": random.randint(10, 40),
                "speed": random.uniform(0.2, 1.0)
            })
        
        # Setting categories and options
        self.settings_options = [
            {"name": "Sound Volume", "type": "slider", "key": "sound_volume", "min": 0.0, "max": 1.0, "step": 0.1},
            {"name": "Sound Effects", "type": "toggle", "key": "sfx_enabled"},
            {"name": "Background Music", "type": "toggle", "key": "music_enabled"},
            {"name": "Difficulty", "type": "choice", "key": "difficulty", "choices": ["easy", "normal", "hard", "beast", "twitchy-god"]},
            {"name": "Show Game Statistics", "type": "toggle", "key": "show_statistics"},
            {"name": "Theme", "type": "choice", "key": "theme", "choices": ["default", "dark", "colorful"]},
            {"name": "Fullscreen", "type": "toggle", "key": "fullscreen"},
        ]
        
        # Calculate option positions
        self.option_rects = []
        self.setup_option_rects()
    
    def setup_option_rects(self):
        """Create rectangles for each setting option in a neat cartoony list."""
        start_y = 150
        spacing = 55  # reduced from 70
        self.option_rects = []
        for i, option in enumerate(self.settings_options):
            y = start_y + (i * spacing)
            rect = pygame.Rect(120, y, Config.WINDOW_WIDTH - 240, 45)  # reduced from 55
            self.option_rects.append(rect)
    
    def handle_event(self, event):
        """Handle settings interactions."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_manager.request_state_change(GameState.MAIN_MENU)
            elif event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.settings_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.settings_options)
            elif event.key == pygame.K_LEFT:
                self.adjust_setting(-1)
            elif event.key == pygame.K_RIGHT:
                self.adjust_setting(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.toggle_setting()
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.back_button.collidepoint(mouse_pos):
                self.game_manager.request_state_change(GameState.MAIN_MENU)
            elif self.reset_button.collidepoint(mouse_pos):
                self.reset_settings()
            else:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_option = i
                        option = self.settings_options[i]
                        if option["type"] == "toggle":
                            self.toggle_setting()
                        break
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_option = i
                    break
    
    def adjust_setting(self, direction):
        """Adjust slider/choice settings."""
        option = self.settings_options[self.selected_option]
        save_manager = self.game_manager.get_save_manager()
        current_value = save_manager.get_setting(option["key"])
        
        if option["type"] == "slider":
            step = option["step"] * direction
            new_value = max(option["min"], min(option["max"], current_value + step))
            save_manager.update_setting(option["key"], new_value)
            if option["key"] == "sound_volume":
                self.game_manager.get_sound_manager().set_volume(new_value)
        
        elif option["type"] == "choice":
            choices = option["choices"]
            current_index = choices.index(current_value) if current_value in choices else 0
            new_index = (current_index + direction) % len(choices)
            save_manager.update_setting(option["key"], choices[new_index])
        
        elif option["type"] == "toggle" and direction != 0:
            self.toggle_setting()
    
    def toggle_setting(self):
        """Toggle booleans like fullscreen/music/sfx."""
        option = self.settings_options[self.selected_option]
        if option["type"] == "toggle":
            save_manager = self.game_manager.get_save_manager()
            current_value = save_manager.get_setting(option["key"])
            new_value = not current_value
            save_manager.update_setting(option["key"], new_value)
            
            if option["key"] == "sfx_enabled":
                self.game_manager.get_sound_manager().sfx_enabled = new_value
            elif option["key"] == "music_enabled":
                self.game_manager.get_sound_manager().toggle_music()
            elif option["key"] == "fullscreen":
                self.toggle_fullscreen()
    
    def toggle_fullscreen(self):
        """Fullscreen toggle with bounce effect."""
        if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
            pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        else:
            pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.FULLSCREEN)
    
    def reset_settings(self):
        """Restore defaults."""
        save_manager = self.game_manager.get_save_manager()
        defaults = {
            "sound_volume": 0.7,
            "sfx_enabled": True,
            "music_enabled": True,
            "difficulty": "normal",
            "show_statistics": True,
            "theme": "default",
            "fullscreen": False,
        }
        for k, v in defaults.items():
            save_manager.update_setting(k, v)
        
        sm = self.game_manager.get_sound_manager()
        sm.set_volume(defaults["sound_volume"])
        sm.sfx_enabled = defaults["sfx_enabled"]
        sm.play_sound("menu_select")
    
    def update(self, dt):
        """Update floating bubbles."""
        for bubble in self.bubbles:
            bubble["y"] -= bubble["speed"]
            if bubble["y"] + bubble["r"] < 0:
                bubble["y"] = Config.WINDOW_HEIGHT + bubble["r"]
                bubble["x"] = random.randint(0, Config.WINDOW_WIDTH)
    
    def render(self, screen):
        """Render cartoony settings scene."""
        screen.fill(Config.WHITE)
        
        # Floating cartoon bubbles
        for bubble in self.bubbles:
            pygame.draw.circle(screen, Config.LIGHT_GRAY, (int(bubble["x"]), int(bubble["y"])), bubble["r"])
            pygame.draw.circle(screen, Config.GRAY, (int(bubble["x"]), int(bubble["y"])), bubble["r"], 2)
        
        # Title with bounce effect
        title_y = 50 + int(math.sin(pygame.time.get_ticks() * 0.003) * 10)
        self.draw_text(screen, "⚙ Settings ⚙", self.font_title, Config.DARK_BLUE, Config.WINDOW_WIDTH // 2, title_y, center=True)
        
        # Buttons
        self.draw_button(screen, "← Back", self.back_button, Config.LIGHT_GRAY, Config.BLACK)
        self.draw_button(screen, "Reset All", self.reset_button, Config.RED, Config.WHITE)
        
        # Instructions
        self.draw_text(screen, "Use ↑↓ to move • ←→ to adjust • Enter to toggle", self.font_small, Config.GRAY,
                       Config.WINDOW_WIDTH // 2, 110, center=True)
        
        save_manager = self.game_manager.get_save_manager()
        for i, (option, rect) in enumerate(zip(self.settings_options, self.option_rects)):
            is_selected = (i == self.selected_option)
            
            # Option background
            pygame.draw.rect(screen, Config.LIGHT_GRAY if is_selected else Config.WHITE, rect, border_radius=12)
            pygame.draw.rect(screen, Config.BLUE if is_selected else Config.GRAY, rect, 2, border_radius=12)
            
            # Setting label
            self.draw_text(screen, option["name"], self.font_medium, Config.DARK_BLUE if is_selected else Config.BLACK,
                           rect.x + 20, rect.y + 10)
            
            # Render control
            value = save_manager.get_setting(option["key"])
            if option["type"] == "toggle":
                self.render_toggle(screen, rect, value, is_selected)
            elif option["type"] == "slider":
                self.render_slider(screen, rect, option, value, is_selected)
            elif option["type"] == "choice":
                self.render_choice(screen, rect, option, value, is_selected)
            
            # Mini preview for stats
            # if option["key"] == "show_statistics" and is_selected:
                # self.render_statistics_preview(screen, rect, value)
    
    def render_toggle(self, screen, rect, value, is_selected):
        toggle_rect = pygame.Rect(rect.right - 100, rect.y + 10, 60, 25)
        pygame.draw.rect(screen, Config.GREEN if value else Config.GRAY, toggle_rect, border_radius=12)
        pygame.draw.rect(screen, Config.BLACK, toggle_rect, 2, border_radius=12)
        knob_x = toggle_rect.x + (35 if value else 5)
        pygame.draw.circle(screen, Config.WHITE, (knob_x, toggle_rect.centery), 10)
        label = "ON" if value else "OFF"
        self.draw_text(screen, label, self.font_small, Config.BLACK if is_selected else Config.GRAY,
                       toggle_rect.right + 10, toggle_rect.y + 3)
    
    def render_slider(self, screen, rect, option, value, is_selected):
        slider_x = rect.right - 200
        slider_y = rect.y + 22
        track = pygame.Rect(slider_x, slider_y, 140, 6)
        pygame.draw.rect(screen, Config.LIGHT_GRAY, track, border_radius=4)
        handle_ratio = (value - option["min"]) / (option["max"] - option["min"])
        handle_x = slider_x + int(handle_ratio * track.width)
        pygame.draw.circle(screen, Config.BLUE if is_selected else Config.DARK_BLUE, (handle_x, slider_y + 3), 8)
        val_text = f"{int(value * 100)}%" if option["key"] == "sound_volume" else f"{value:.1f}"
        self.draw_text(screen, val_text, self.font_small, Config.BLACK if is_selected else Config.GRAY,
                       slider_x + track.width + 15, slider_y - 10)
    
    def render_choice(self, screen, rect, option, value, is_selected):
        box = pygame.Rect(rect.right - 160, rect.y + 5, 120, 30)
        pygame.draw.rect(screen, Config.WHITE if not is_selected else Config.LIGHT_GRAY, box, border_radius=8)
        pygame.draw.rect(screen, Config.BLACK, box, 2, border_radius=8)
        self.draw_text(screen, value.title(), self.font_small, Config.BLACK if is_selected else Config.GRAY,
                       box.x + 10, box.y + 5)
        if is_selected:
            self.draw_text(screen, "◀", self.font_small, Config.BLUE, box.x - 20, box.y + 5)
            self.draw_text(screen, "▶", self.font_small, Config.BLUE, box.right + 5, box.y + 5)
    
    def render_statistics_preview(self, screen, rect, show_stats):
        preview_y = rect.y + 40
        if not show_stats:
            self.draw_text(screen, "(Statistics hidden)", self.font_small, Config.GRAY, rect.x + 20, preview_y)
        else:
            save_manager = self.game_manager.get_save_manager()
            difficulty = save_manager.get_setting("difficulty", "normal")
            preview = [
                f"Difficulty: {difficulty.upper()}",
                "Attempts: 5",
                "Best: 234ms",
                "Average: 287ms"
            ]
            color = Config.DIFFICULTY_COLORS.get(difficulty, Config.DARK_BLUE)
            for i, txt in enumerate(preview):
                self.draw_text(screen, txt, self.font_small, color if i == 0 else Config.GRAY,
                               rect.x + 20 + (i * 110), preview_y)
