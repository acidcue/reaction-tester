"""Settings scene for configuring game options."""
import pygame
from .base_scene import BaseScene
from config import Config
from game_states import GameState

class SettingsScene(BaseScene):
    """Settings menu for game configuration."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.selected_option = 0
        self.back_button = pygame.Rect(20, 20, 100, 40)
        self.reset_button = pygame.Rect(Config.WINDOW_WIDTH - 150, Config.WINDOW_HEIGHT - 60, 130, 40)
        
        # Setting categories and options
        self.settings_options = [
            {
                "name": "Sound Volume",
                "type": "slider",
                "key": "sound_volume",
                "min": 0.0,
                "max": 1.0,
                "step": 0.1
            },
            {
                "name": "Sound Effects",
                "type": "toggle",
                "key": "sfx_enabled"
            },
            {
                "name": "Background Music",
                "type": "toggle",
                "key": "music_enabled"
            },
            {
                "name": "Difficulty",
                "type": "choice",
                "key": "difficulty",
                "choices": ["easy", "normal", "hard", "beast", "twitchy-god"]
            },
            {
                "name": "Show Game Statistics",
                "type": "toggle",
                "key": "show_statistics",
                "description": "Display difficulty, attempts, and best time during gameplay"
            },
            {
                "name": "Theme",
                "type": "choice",
                "key": "theme",
                "choices": ["default", "dark", "colorful"]
            },
            {
                "name": "Fullscreen",
                "type": "toggle",
                "key": "fullscreen"
            }
        ]
        
        # Calculate option positions
        self.option_rects = []
        self.setup_option_rects()
    
    def setup_option_rects(self):
        """Create rectangles for each setting option."""
        start_y = 150
        spacing = 60
        
        self.option_rects = []
        for i, option in enumerate(self.settings_options):
            y = start_y + (i * spacing)
            rect = pygame.Rect(100, y, Config.WINDOW_WIDTH - 200, 50)
            self.option_rects.append(rect)
    
    def handle_event(self, event):
        """Handle settings events."""
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
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.toggle_setting()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                if self.back_button.collidepoint(mouse_pos):
                    self.game_manager.request_state_change(GameState.MAIN_MENU)
                elif self.reset_button.collidepoint(mouse_pos):
                    self.reset_settings()
                else:
                    # Check if clicked on a setting
                    for i, rect in enumerate(self.option_rects):
                        if rect.collidepoint(mouse_pos):
                            self.selected_option = i
                            # Handle different click behaviors based on setting type
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
        """Adjust the currently selected setting."""
        option = self.settings_options[self.selected_option]
        save_manager = self.game_manager.get_save_manager()
        current_value = save_manager.get_setting(option["key"])
        
        if option["type"] == "slider":
            step = option["step"] * direction
            new_value = max(option["min"], min(option["max"], current_value + step))
            save_manager.update_setting(option["key"], new_value)
            
            # Apply sound volume change immediately
            if option["key"] == "sound_volume":
                self.game_manager.get_sound_manager().set_volume(new_value)
        
        elif option["type"] == "choice":
            choices = option["choices"]
            current_index = choices.index(current_value) if current_value in choices else 0
            new_index = (current_index + direction) % len(choices)
            save_manager.update_setting(option["key"], choices[new_index])
        
        elif option["type"] == "toggle":
            if direction != 0:  # Any direction toggles
                self.toggle_setting()
    
    def toggle_setting(self):
        """Toggle the currently selected boolean setting."""
        option = self.settings_options[self.selected_option]
        
        if option["type"] == "toggle":
            save_manager = self.game_manager.get_save_manager()
            current_value = save_manager.get_setting(option["key"])
            new_value = not current_value
            save_manager.update_setting(option["key"], new_value)
            
            # Apply changes immediately where applicable
            if option["key"] == "sfx_enabled":
                self.game_manager.get_sound_manager().sfx_enabled = new_value
            elif option["key"] == "music_enabled":
                self.game_manager.get_sound_manager().toggle_music()
            elif option["key"] == "fullscreen":
                self.toggle_fullscreen()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
            pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        else:
            pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.FULLSCREEN)
    
    def reset_settings(self):
        """Reset all settings to defaults."""
        save_manager = self.game_manager.get_save_manager()
        
        # Reset to default values
        defaults = {
            "sound_volume": 0.7,
            "sfx_enabled": True,
            "music_enabled": True,
            "difficulty": "normal",
            "show_statistics": True,
            "theme": "default",
            "fullscreen": False
        }
        
        for key, value in defaults.items():
            save_manager.update_setting(key, value)
        
        # Apply changes
        self.game_manager.get_sound_manager().set_volume(defaults["sound_volume"])
        self.game_manager.get_sound_manager().sfx_enabled = defaults["sfx_enabled"]
        
        # Play confirmation sound
        self.game_manager.get_sound_manager().play_sound('menu_select')
    
    def update(self, dt):
        """Update settings display."""
        pass  # Static display
    
    def render(self, screen):
        """Render the settings scene."""
        screen.fill(Config.WHITE)
        
        # Draw back button
        self.draw_button(screen, "Back", self.back_button, Config.LIGHT_GRAY, Config.BLACK)
        
        # Draw reset button
        self.draw_button(screen, "Reset All", self.reset_button, Config.RED, Config.WHITE)
        
        # Draw title
        self.draw_text(
            screen, "Settings", self.font_title, Config.DARK_BLUE,
            Config.WINDOW_WIDTH // 2, 50, center=True
        )
        
        # Draw instructions
        instructions = "Use arrow keys to navigate • LEFT/RIGHT to adjust • ENTER to toggle"
        self.draw_text(
            screen, instructions, self.font_small, Config.GRAY,
            Config.WINDOW_WIDTH // 2, 100, center=True
        )
        
        # Draw settings options
        save_manager = self.game_manager.get_save_manager()
        
        for i, (option, rect) in enumerate(zip(self.settings_options, self.option_rects)):
            is_selected = (i == self.selected_option)
            
            # Background highlight for selected option
            if is_selected:
                highlight_rect = pygame.Rect(rect.x - 10, rect.y - 5, rect.width + 20, rect.height + 10)
                pygame.draw.rect(screen, Config.LIGHT_GRAY, highlight_rect)
                pygame.draw.rect(screen, Config.BLUE, highlight_rect, 2)
            
            # Setting name
            name_color = Config.BLACK if not is_selected else Config.DARK_BLUE
            self.draw_text(screen, option["name"], self.font_medium, name_color, rect.x + 20, rect.y + 10)
            
            # Setting value/control
            current_value = save_manager.get_setting(option["key"])
            
            if option["type"] == "toggle":
                self.render_toggle(screen, rect, current_value, is_selected)
            elif option["type"] == "slider":
                self.render_slider(screen, rect, option, current_value, is_selected)
            elif option["type"] == "choice":
                self.render_choice(screen, rect, option, current_value, is_selected)
            
            # Show preview for show_statistics setting
            if option["key"] == "show_statistics" and is_selected:
                self.render_statistics_preview(screen, rect, current_value)
        
        # Draw help text at bottom
        help_texts = [
            "Changes are saved automatically",
            "Show Game Statistics: Controls the stats display in the bottom-left during gameplay"
        ]
        
        for i, help_text in enumerate(help_texts):
            color = Config.GRAY if i == 0 else Config.DARK_BLUE
            self.draw_text(
                screen, help_text, self.font_small, color,
                Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT - 50 + (i * 20), center=True
            )
    
    def render_toggle(self, screen, rect, value, is_selected):
        """Render a toggle switch."""
        toggle_x = rect.right - 100
        toggle_y = rect.y + 15
        
        # Toggle background
        toggle_rect = pygame.Rect(toggle_x, toggle_y, 60, 20)
        bg_color = Config.GREEN if value else Config.GRAY
        pygame.draw.rect(screen, bg_color, toggle_rect)
        pygame.draw.rect(screen, Config.BLACK, toggle_rect, 2)
        
        # Toggle handle
        handle_x = toggle_x + 35 if value else toggle_x + 5
        handle_rect = pygame.Rect(handle_x, toggle_y + 2, 16, 16)
        pygame.draw.rect(screen, Config.WHITE, handle_rect)
        pygame.draw.rect(screen, Config.BLACK, handle_rect, 1)
        
        # Text
        text = "ON" if value else "OFF"
        text_color = Config.BLACK if is_selected else Config.GRAY
        self.draw_text(screen, text, self.font_small, text_color, toggle_x + 70, toggle_y)
    
    def render_slider(self, screen, rect, option, value, is_selected):
        """Render a slider control."""
        slider_x = rect.right - 200
        slider_y = rect.y + 20
        slider_width = 120
        
        # Slider track
        track_rect = pygame.Rect(slider_x, slider_y, slider_width, 10)
        pygame.draw.rect(screen, Config.LIGHT_GRAY, track_rect)
        pygame.draw.rect(screen, Config.BLACK, track_rect, 1)
        
        # Slider handle
        handle_ratio = (value - option["min"]) / (option["max"] - option["min"])
        handle_x = slider_x + (handle_ratio * slider_width) - 5
        handle_rect = pygame.Rect(handle_x, slider_y - 5, 10, 20)
        
        handle_color = Config.BLUE if is_selected else Config.DARK_BLUE
        pygame.draw.rect(screen, handle_color, handle_rect)
        
        # Value text
        if option["key"] == "sound_volume":
            value_text = f"{int(value * 100)}%"
        else:
            value_text = f"{value:.1f}"
        
        text_color = Config.BLACK if is_selected else Config.GRAY
        self.draw_text(screen, value_text, self.font_small, text_color, slider_x + slider_width + 10, slider_y - 5)
    
    def render_choice(self, screen, rect, option, value, is_selected):
        """Render a choice selector."""
        choice_x = rect.right - 200
        choice_y = rect.y + 10
        
        # Choice box
        choice_rect = pygame.Rect(choice_x, choice_y, 120, 30)
        bg_color = Config.WHITE if not is_selected else Config.LIGHT_GRAY
        pygame.draw.rect(screen, bg_color, choice_rect)
        pygame.draw.rect(screen, Config.BLACK, choice_rect, 2)
        
        # Current value
        text_color = Config.BLACK if is_selected else Config.GRAY
        self.draw_text(screen, value.title(), self.font_medium, text_color, 
                      choice_x + 10, choice_y + 5)
        
        # Arrows
        if is_selected:
            # Left arrow
            self.draw_text(screen, "◀", self.font_small, Config.BLUE, choice_x - 20, choice_y + 5)
            # Right arrow
            self.draw_text(screen, "▶", self.font_small, Config.BLUE, choice_x + 125, choice_y + 5)
    
    def render_statistics_preview(self, screen, rect, show_stats):
        """Show a preview of what the statistics display looks like."""
        if not show_stats:
            # Show what it looks like when disabled
            preview_text = "Statistics hidden during gameplay"
            self.draw_text(screen, preview_text, self.font_small, Config.GRAY, 
                          rect.x + 20, rect.y + 35)
        else:
            # Show a mini preview of the statistics
            preview_y = rect.y + 35
            save_manager = self.game_manager.get_save_manager()
            difficulty = save_manager.get_setting("difficulty", "normal")
            
            # Mini preview of stats
            preview_texts = [
                f"Difficulty: {difficulty.upper()}",
                "Attempts: 5",
                "Best: 234ms",
                "Average: 287ms"
            ]
            
            difficulty_color = Config.DIFFICULTY_COLORS.get(difficulty, Config.GRAY)
            
            for i, text in enumerate(preview_texts):
                color = difficulty_color if i == 0 else Config.GRAY
                self.draw_text(screen, text, self.font_small, color, 
                              rect.x + 20 + (i * 90), preview_y)