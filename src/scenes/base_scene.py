"""Base scene class that all game scenes inherit from."""
import pygame
from abc import ABC, abstractmethod
from config import Config

class BaseScene(ABC):
    """Abstract base class for all game scenes."""
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.font_small = pygame.font.Font(None, Config.FONT_SMALL)
        self.font_medium = pygame.font.Font(None, Config.FONT_MEDIUM)
        self.font_large = pygame.font.Font(None, Config.FONT_LARGE)
        self.font_title = pygame.font.Font(None, Config.FONT_TITLE)
    
    def enter(self):
        """Called when entering this scene."""
        pass
    
    def exit(self):
        """Called when leaving this scene."""
        pass
    
    @abstractmethod
    def handle_event(self, event):
        """Handle pygame events."""
        pass
    
    @abstractmethod
    def update(self, dt):
        """Update scene logic."""
        pass
    
    @abstractmethod
    def render(self, screen):
        """Render the scene."""
        pass
    
    def draw_text(self, screen, text, font, color, x, y, center=False):
        """Helper method to draw text."""
        text_surface = font.render(text, True, color)
        if center:
            x -= text_surface.get_width() // 2
            y -= text_surface.get_height() // 2
        screen.blit(text_surface, (x, y))
        return text_surface
    
    def draw_button(self, screen, text, rect, color, text_color, hover=False):
        """Helper method to draw a button."""
        button_color = color if not hover else tuple(min(255, c + 30) for c in color)
        pygame.draw.rect(screen, button_color, rect)
        pygame.draw.rect(screen, Config.BLACK, rect, 2)
        
        text_surface = self.font_medium.render(text, True, text_color)
        text_x = rect.centerx - text_surface.get_width() // 2
        text_y = rect.centery - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))
        
        return rect