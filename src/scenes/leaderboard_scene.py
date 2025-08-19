"""Leaderboard scene showing best times and statistics."""
import pygame
from .base_scene import BaseScene
from config import Config
from game_states import GameState

class LeaderboardScene(BaseScene):
    """Display leaderboards, statistics, and achievements."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.selected_tab = 0
        self.selected_difficulty = "normal"  # Current difficulty filter
        self.tabs = ["Best Times", "Statistics", "Achievements"]
        self.difficulties = ["easy", "normal", "hard", "beast", "twitchy-god"]
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # UI elements
        self.back_button = pygame.Rect(20, 20, 100, 40)
        self.tab_buttons = []
        self.difficulty_buttons = []
        self.setup_buttons()
    
    def setup_buttons(self):
        """Create tab and difficulty button rectangles."""
        # Tab buttons
        tab_width = 150
        tab_height = 40
        start_x = (Config.WINDOW_WIDTH - (len(self.tabs) * tab_width)) // 2
        
        self.tab_buttons = []
        for i, tab in enumerate(self.tabs):
            x = start_x + (i * tab_width)
            y = 80
            self.tab_buttons.append(pygame.Rect(x, y, tab_width, tab_height))
        
        # Difficulty buttons (only for Best Times and Statistics tabs)
        diff_width = 80
        diff_height = 30
        diff_start_x = (Config.WINDOW_WIDTH - (len(self.difficulties) * diff_width)) // 2
        
        self.difficulty_buttons = []
        for i, difficulty in enumerate(self.difficulties):
            x = diff_start_x + (i * diff_width)
            y = 130
            self.difficulty_buttons.append(pygame.Rect(x, y, diff_width, diff_height))
    
    def handle_event(self, event):
        """Handle leaderboard events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_manager.request_state_change(GameState.MAIN_MENU)
            elif event.key == pygame.K_LEFT:
                if self.selected_tab in [0, 1]:  # Best Times or Statistics
                    current_idx = self.difficulties.index(self.selected_difficulty)
                    self.selected_difficulty = self.difficulties[(current_idx - 1) % len(self.difficulties)]
                    self.scroll_offset = 0
                else:
                    self.selected_tab = (self.selected_tab - 1) % len(self.tabs)
                    self.scroll_offset = 0
            elif event.key == pygame.K_RIGHT:
                if self.selected_tab in [0, 1]:  # Best Times or Statistics
                    current_idx = self.difficulties.index(self.selected_difficulty)
                    self.selected_difficulty = self.difficulties[(current_idx + 1) % len(self.difficulties)]
                    self.scroll_offset = 0
                else:
                    self.selected_tab = (self.selected_tab + 1) % len(self.tabs)
                    self.scroll_offset = 0
            elif event.key == pygame.K_UP:
                if self.selected_tab in [0, 1]:
                    self.selected_tab = (self.selected_tab - 1) % len(self.tabs)
                    self.scroll_offset = 0
                else:
                    self.scroll_offset = max(0, self.scroll_offset - 30)
            elif event.key == pygame.K_DOWN:
                if self.selected_tab in [0, 1]:
                    self.selected_tab = (self.selected_tab + 1) % len(self.tabs)
                    self.scroll_offset = 0
                else:
                    self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                if self.back_button.collidepoint(mouse_pos):
                    self.game_manager.request_state_change(GameState.MAIN_MENU)
                
                # Check tab buttons
                for i, rect in enumerate(self.tab_buttons):
                    if rect.collidepoint(mouse_pos):
                        self.selected_tab = i
                        self.scroll_offset = 0
                
                # Check difficulty buttons (only for relevant tabs)
                if self.selected_tab in [0, 1]:
                    for i, rect in enumerate(self.difficulty_buttons):
                        if rect.collidepoint(mouse_pos):
                            self.selected_difficulty = self.difficulties[i]
                            self.scroll_offset = 0
        
        elif event.type == pygame.MOUSEWHEEL:
            # Mouse wheel scrolling
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - event.y * 30))
    
    def update(self, dt):
        """Update leaderboard display."""
        pass  # Static display, no updates needed
    
    def render(self, screen):
        """Render the leaderboard scene."""
        screen.fill(Config.WHITE)
        
        # Draw back button
        self.draw_button(screen, "Back", self.back_button, Config.LIGHT_GRAY, Config.BLACK)
        
        # Draw title
        self.draw_text(
            screen, "Leaderboard", self.font_title, Config.DARK_BLUE,
            Config.WINDOW_WIDTH // 2, 40, center=True
        )
        
        # Draw tabs
        self.render_tabs(screen)
        
        # Draw difficulty selector for relevant tabs
        if self.selected_tab in [0, 1]:  # Best Times or Statistics
            self.render_difficulty_selector(screen)
        
        # Draw current tab content
        content_y = 180 if self.selected_tab in [0, 1] else 140
        if self.selected_tab == 0:
            self.render_best_times(screen, content_y)
        elif self.selected_tab == 1:
            self.render_statistics(screen, content_y)
        elif self.selected_tab == 2:
            self.render_achievements(screen, content_y)
        
        # Draw scroll indicator if needed
        if self.max_scroll > 0:
            self.render_scroll_indicator(screen)
    
    def render_tabs(self, screen):
        """Render tab buttons."""
        for i, (tab_name, rect) in enumerate(zip(self.tabs, self.tab_buttons)):
            is_selected = (i == self.selected_tab)
            button_color = Config.BLUE if is_selected else Config.LIGHT_GRAY
            text_color = Config.WHITE if is_selected else Config.BLACK
            
            self.draw_button(screen, tab_name, rect, button_color, text_color)
    
    def render_difficulty_selector(self, screen):
        """Render difficulty selector buttons."""
        for i, (difficulty, rect) in enumerate(zip(self.difficulties, self.difficulty_buttons)):
            is_selected = (difficulty == self.selected_difficulty)
            
            # Color coding for difficulties using the config
            button_color = Config.DIFFICULTY_COLORS.get(difficulty, Config.LIGHT_GRAY)
            if not is_selected:
                button_color = Config.LIGHT_GRAY
            
            text_color = Config.WHITE if is_selected else Config.BLACK
            
            # Shorten text for display
            display_text = difficulty.replace("twitchy-", "T-").title()
            self.draw_button(screen, display_text, rect, button_color, text_color)
    
    def render_best_times(self, screen, start_y):
        """Render the best times tab for selected difficulty."""
        save_manager = self.game_manager.get_save_manager()
        best_times = save_manager.get_best_times(self.selected_difficulty, 20)
        
        if not best_times:
            self.draw_text(
                screen, f"No times recorded for {self.selected_difficulty.upper()} difficulty yet!", 
                self.font_medium, Config.GRAY,
                Config.WINDOW_WIDTH // 2, start_y + 100, center=True
            )
            return
        
        # Header with difficulty
        title = f"Best Times - {self.selected_difficulty.upper().replace('TWITCHY-', 'T-')} Difficulty"
        title_color = Config.DIFFICULTY_COLORS.get(self.selected_difficulty, Config.BLACK)
        
        self.draw_text(
            screen, title, self.font_large, title_color,
            Config.WINDOW_WIDTH // 2, start_y, center=True
        )
        
        # Column headers
        header_y = start_y + 50
        self.draw_text(screen, "Rank", self.font_medium, Config.DARK_BLUE, 150, header_y)
        self.draw_text(screen, "Time", self.font_medium, Config.DARK_BLUE, 250, header_y)
        self.draw_text(screen, "Rating", self.font_medium, Config.DARK_BLUE, 400, header_y)
        
        # Draw line under headers
        pygame.draw.line(screen, Config.GRAY, (100, header_y + 30), (Config.WINDOW_WIDTH - 100, header_y + 30), 2)
        
        # List entries
        list_start_y = header_y + 50 - self.scroll_offset
        visible_entries = 0
        
        for i, time_ms in enumerate(best_times):
            y = list_start_y + (i * 40)
            
            # Only render visible entries
            if y < start_y - 40 or y > Config.WINDOW_HEIGHT:
                continue
            
            visible_entries += 1
            
            # Rank with medal icons for top 3
            rank_text = f"#{i + 1}"
            if i == 0:
                rank_text = "🥇 #1"
            elif i == 1:
                rank_text = "🥈 #2"
            elif i == 2:
                rank_text = "🥉 #3"
            
            self.draw_text(screen, rank_text, self.font_medium, Config.BLACK, 150, y)
            
            # Time with color coding based on difficulty thresholds
            time_text = f"{time_ms}ms"
            difficulty_config = Config.DIFFICULTY_SETTINGS.get(self.selected_difficulty, Config.DIFFICULTY_SETTINGS["normal"])
            if time_ms <= difficulty_config["excellent_threshold"]:
                time_color = Config.GREEN
            else:
                time_color = Config.BLACK
            self.draw_text(screen, time_text, self.font_medium, time_color, 250, y)
            
            # Rating based on difficulty
            difficulty_config = Config.DIFFICULTY_SETTINGS.get(self.selected_difficulty, Config.DIFFICULTY_SETTINGS["normal"])
            if time_ms <= difficulty_config["excellent_threshold"]:
                rating = "🔥 Excellent"
            elif time_ms <= difficulty_config["good_threshold"]:
                rating = "⚡ Good"
            elif time_ms <= difficulty_config["average_threshold"]:
                rating = "👍 Average"
            elif time_ms <= difficulty_config["poor_threshold"]:
                rating = "😐 Poor"
            elif time_ms <= difficulty_config["merh_threshold"]:
                rating = "🐌 Meh"
            else:
                rating = "💀 Terrible"
            
            self.draw_text(screen, rating, self.font_medium, Config.GRAY, 400, y)
        
        # Update max scroll
        total_height = len(best_times) * 40
        visible_height = Config.WINDOW_HEIGHT - start_y - 100
        self.max_scroll = max(0, total_height - visible_height)
    
    def render_statistics(self, screen, start_y):
        """Render the statistics tab for selected difficulty."""
        save_manager = self.game_manager.get_save_manager()
        stats = save_manager.get_statistics(self.selected_difficulty)
        daily_stats = save_manager.get_daily_stats(self.selected_difficulty)
        overall_stats = save_manager.get_overall_statistics()
        
        # Difficulty-specific Statistics
        title = f"Statistics - {self.selected_difficulty.upper().replace('TWITCHY-', 'T-')} Difficulty"
        title_color = Config.DIFFICULTY_COLORS.get(self.selected_difficulty, Config.BLACK)
        
        self.draw_text(
            screen, title, self.font_large, title_color,
            Config.WINDOW_WIDTH // 2, start_y, center=True
        )
        
        stats_y = start_y + 60
        
        # Total attempts
        self.draw_text(
            screen, f"Total Attempts: {stats['total_attempts']}", 
            self.font_medium, Config.BLACK, 100, stats_y
        )
        
        # Best time with color coding
        if stats['best_time']:
            difficulty_config = Config.DIFFICULTY_SETTINGS.get(self.selected_difficulty, Config.DIFFICULTY_SETTINGS["normal"])
            if stats['best_time'] <= difficulty_config["excellent_threshold"]:
                best_color = Config.GREEN
            else:
                best_color = Config.BLACK
            self.draw_text(
                screen, f"Best Time: {stats['best_time']}ms", 
                self.font_medium, best_color, 100, stats_y + 40
            )
        
        # Average time
        if stats['average_time']:
            avg_text = f"Average Time: {stats['average_time']:.1f}ms"
            self.draw_text(screen, avg_text, self.font_medium, Config.BLACK, 100, stats_y + 80)
        
        # Today's Statistics
        if daily_stats:
            self.draw_text(
                screen, "Today's Performance", self.font_large, Config.BLACK,
                Config.WINDOW_WIDTH // 2, stats_y + 150, center=True
            )
            
            today_y = stats_y + 210
            
            self.draw_text(
                screen, f"Attempts Today: {daily_stats['attempts']}", 
                self.font_medium, Config.BLACK, 100, today_y
            )
            
            self.draw_text(
                screen, f"Best Today: {daily_stats['best_time']}ms", 
                self.font_medium, Config.GREEN, 100, today_y + 40
            )
            
            self.draw_text(
                screen, f"Average Today: {daily_stats['average_time']:.1f}ms", 
                self.font_medium, Config.BLACK, 100, today_y + 80
            )
        
        # Performance distribution
        if stats['total_attempts'] > 0:
            recent_attempts = save_manager.get_recent_attempts(50)
            if recent_attempts:
                self.render_performance_chart(screen, recent_attempts, stats_y + 320)
    
    def render_performance_chart(self, screen, attempts, y):
        """Render a simple performance chart."""
        self.draw_text(
            screen, "Recent Performance (Last 50 attempts)", 
            self.font_medium, Config.BLACK, 100, y
        )
        
        if len(attempts) < 2:
            return
        
        chart_x = 100
        chart_y = y + 40
        chart_width = 400
        chart_height = 100
        
        # Draw chart background
        chart_rect = pygame.Rect(chart_x, chart_y, chart_width, chart_height)
        pygame.draw.rect(screen, Config.LIGHT_GRAY, chart_rect)
        pygame.draw.rect(screen, Config.BLACK, chart_rect, 2)
        
        # Get time values
        times = [attempt['time_ms'] for attempt in attempts]
        min_time = min(times)
        max_time = max(times)
        time_range = max_time - min_time
        
        if time_range == 0:
            time_range = 1  # Avoid division by zero
        
        # Draw data points
        difficulty_config = Config.DIFFICULTY_SETTINGS.get(self.selected_difficulty, Config.DIFFICULTY_SETTINGS["normal"])
        
        for i, time_ms in enumerate(times):
            x = chart_x + (i * chart_width / len(times))
            normalized_time = (time_ms - min_time) / time_range
            point_y = chart_y + chart_height - (normalized_time * chart_height)
            
            # Color based on performance using difficulty thresholds
            if time_ms <= difficulty_config["excellent_threshold"]:
                color = Config.GREEN
            elif time_ms <= difficulty_config["good_threshold"]:
                color = Config.BLUE
            else:
                color = Config.RED
            
            pygame.draw.circle(screen, color, (int(x), int(point_y)), 3)
        
        # Draw labels
        self.draw_text(screen, f"{min_time}ms", self.font_small, Config.BLACK, 
                      chart_x - 20, chart_y + chart_height)
        self.draw_text(screen, f"{max_time}ms", self.font_small, Config.BLACK, 
                      chart_x - 20, chart_y)
    
    def render_achievements(self, screen, start_y):
        """Render the achievements tab."""
        save_manager = self.game_manager.get_save_manager()
        achievements = save_manager.get_achievement_list()
        
        self.draw_text(
            screen, "Achievements", self.font_large, Config.BLACK,
            Config.WINDOW_WIDTH // 2, start_y, center=True
        )
        
        # Count unlocked achievements
        unlocked_count = sum(1 for ach in achievements.values() if ach['unlocked'])
        total_count = len(achievements)
        
        progress_text = f"Unlocked: {unlocked_count}/{total_count}"
        self.draw_text(
            screen, progress_text, self.font_medium, Config.DARK_BLUE,
            Config.WINDOW_WIDTH // 2, start_y + 40, center=True
        )
        
        # Draw achievements
        achievement_y = start_y + 100 - self.scroll_offset
        
        for achievement_id, data in achievements.items():
            if achievement_y < start_y - 60 or achievement_y > Config.WINDOW_HEIGHT:
                achievement_y += 80
                continue
            
            # Achievement box
            box_rect = pygame.Rect(100, achievement_y, Config.WINDOW_WIDTH - 200, 60)
            
            if data['unlocked']:
                pygame.draw.rect(screen, Config.LIGHT_GRAY, box_rect)
                pygame.draw.rect(screen, Config.GREEN, box_rect, 3)
                text_color = Config.BLACK
            else:
                pygame.draw.rect(screen, Config.WHITE, box_rect)
                pygame.draw.rect(screen, Config.GRAY, box_rect, 2)
                text_color = Config.GRAY
            
            # Icon
            icon_x = box_rect.x + 15
            icon_y = box_rect.y + 15
            if data['unlocked']:
                self.draw_text(screen, data['icon'], self.font_large, text_color, icon_x, icon_y)
            else:
                self.draw_text(screen, "🔒", self.font_large, text_color, icon_x, icon_y)
            
            # Name and description
            name_x = icon_x + 60
            self.draw_text(screen, data['name'], self.font_medium, text_color, name_x, icon_y)
            self.draw_text(screen, data['description'], self.font_small, text_color, name_x, icon_y + 25)
            
            achievement_y += 80
        
        # Update max scroll for achievements
        total_height = len(achievements) * 80
        visible_height = Config.WINDOW_HEIGHT - start_y - 100
        self.max_scroll = max(0, total_height - visible_height)
    
    def render_scroll_indicator(self, screen):
        """Render scroll indicator on the right side."""
        if self.max_scroll <= 0:
            return
        
        indicator_x = Config.WINDOW_WIDTH - 20
        indicator_y = 200
        indicator_height = 300
        
        # Background track
        pygame.draw.rect(screen, Config.LIGHT_GRAY, 
                        (indicator_x, indicator_y, 10, indicator_height))
        
        # Thumb
        thumb_ratio = min(1.0, indicator_height / (self.max_scroll + indicator_height))
        thumb_height = max(20, indicator_height * thumb_ratio)
        thumb_y = indicator_y + (self.scroll_offset / self.max_scroll) * (indicator_height - thumb_height)
        
        pygame.draw.rect(screen, Config.DARK_BLUE, 
                        (indicator_x, thumb_y, 10, thumb_height))