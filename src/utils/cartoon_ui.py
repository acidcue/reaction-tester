"""Cartoony UI utilities for Twitch~y game."""
import pygame
import math
import time
from config import Config

class CartoonUI:
    """Helper class for drawing cartoony UI elements with animations."""
    
    @staticmethod
    def draw_bouncy_button(screen, text, rect, bg_color, text_color, is_hovered=False, bounce_time=0):
        """Draw a bouncy cartoon button with outline and shadow."""
        # Calculate bounce offset
        bounce_offset = 0
        if is_hovered:
            bounce_offset = int(Config.BOUNCE_AMPLITUDE * math.sin(bounce_time * 8))
        
        # Adjust rect for bounce
        bouncy_rect = pygame.Rect(rect.x, rect.y + bounce_offset, rect.width, rect.height)
        
        # Draw shadow (offset down and right)
        shadow_rect = pygame.Rect(bouncy_rect.x + 4, bouncy_rect.y + 4, bouncy_rect.width, bouncy_rect.height)
        pygame.draw.rect(screen, Config.SHADOW_GRAY, shadow_rect, border_radius=Config.CORNER_RADIUS)
        
        # Draw main button
        pygame.draw.rect(screen, bg_color, bouncy_rect, border_radius=Config.CORNER_RADIUS)
        
        # Draw thick cartoon outline
        pygame.draw.rect(screen, Config.OUTLINE_DARK, bouncy_rect, Config.BORDER_WIDTH, border_radius=Config.CORNER_RADIUS)
        
        # Add shine/highlight on top
        shine_rect = pygame.Rect(bouncy_rect.x + 5, bouncy_rect.y + 5, bouncy_rect.width - 10, bouncy_rect.height // 3)
        shine_color = tuple(min(255, c + 40) for c in bg_color)
        pygame.draw.rect(screen, shine_color, shine_rect, border_radius=Config.CORNER_RADIUS // 2)
        
        # Draw text with shadow
        try:
            font = pygame.font.Font(None, Config.FONT_MEDIUM)
        except:
            font = pygame.font.Font(None, Config.FONT_MEDIUM)
        
        # Text shadow
        text_surface_shadow = font.render(text, True, Config.SHADOW_GRAY)
        text_rect_shadow = text_surface_shadow.get_rect(center=(bouncy_rect.centerx + 2, bouncy_rect.centery + 2))
        screen.blit(text_surface_shadow, text_rect_shadow)
        
        # Main text
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=bouncy_rect.center)
        screen.blit(text_surface, text_rect)
        
        return bouncy_rect
    
    @staticmethod
    def draw_cartoon_title(screen, text, x, y, wobble_time=0):
        """Draw a wobbly cartoon title like SpongeBob style."""
        try:
            font = pygame.font.Font(None, Config.FONT_TITLE)
        except:
            font = pygame.font.Font(None, Config.FONT_TITLE)
        
        # Each letter wobbles slightly different
        letter_spacing = Config.FONT_TITLE // 2
        start_x = x - (len(text) * letter_spacing) // 2
        
        for i, letter in enumerate(text):
            # Calculate wobble for this letter
            wobble_x = int(6 * math.sin(wobble_time * 2 + i * 0.5))
            wobble_y = int(8 * math.sin(wobble_time * 1.5 + i * 0.8))
            
            letter_x = start_x + (i * letter_spacing) + wobble_x
            letter_y = y + wobble_y
            
            # Letter shadow
            shadow_surface = font.render(letter, True, Config.OUTLINE_DARK)
            screen.blit(shadow_surface, (letter_x + 3, letter_y + 3))
            
            # Main letter with rainbow colors for "Twitch~y"
            colors = [Config.BRIGHT_YELLOW, Config.AQUA_BLUE, Config.PLAYFUL_PURPLE, 
                     Config.ENERGETIC_ORANGE, Config.SUNNY_YELLOW, Config.BUBBLEGUM_PURPLE,
                     Config.CARTOON_GREEN, Config.OCEAN_BLUE]
            letter_color = colors[i % len(colors)]
            
            letter_surface = font.render(letter, True, letter_color)
            screen.blit(letter_surface, (letter_x, letter_y))
    
    @staticmethod
    def draw_speech_bubble(screen, text, x, y, width=300):
        """Draw a cartoon speech bubble."""
        height = 60
        bubble_rect = pygame.Rect(x - width//2, y - height//2, width, height)
        
        # Draw bubble shadow
        shadow_rect = pygame.Rect(bubble_rect.x + 3, bubble_rect.y + 3, bubble_rect.width, bubble_rect.height)
        pygame.draw.ellipse(screen, Config.SHADOW_GRAY, shadow_rect)
        
        # Draw main bubble
        pygame.draw.ellipse(screen, Config.WHITE, bubble_rect)
        pygame.draw.ellipse(screen, Config.OUTLINE_DARK, bubble_rect, 3)
        
        # Draw speech bubble tail (pointing down)
        tail_points = [
            (x - 10, y + height//2),
            (x + 10, y + height//2),
            (x, y + height//2 + 15)
        ]
        pygame.draw.polygon(screen, Config.WHITE, tail_points)
        pygame.draw.polygon(screen, Config.OUTLINE_DARK, tail_points, 3)
        
        # Draw text
        try:
            font = pygame.font.Font(None, Config.FONT_MEDIUM)
        except:
            font = pygame.font.Font(None, Config.FONT_MEDIUM)
        
        text_surface = font.render(text, True, Config.BLACK)
        text_rect = text_surface.get_rect(center=bubble_rect.center)
        screen.blit(text_surface, text_rect)
    
    @staticmethod
    def draw_cartoon_panel(screen, rect, color=None):
        """Draw a cartoon panel with rounded corners and thick outline."""
        if color is None:
            color = Config.WHITE
            
        # Panel shadow
        shadow_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.width, rect.height)
        pygame.draw.rect(screen, Config.SHADOW_GRAY, shadow_rect, border_radius=Config.CORNER_RADIUS)
        
        # Main panel
        pygame.draw.rect(screen, color, rect, border_radius=Config.CORNER_RADIUS)
        pygame.draw.rect(screen, Config.OUTLINE_DARK, rect, Config.BORDER_WIDTH, border_radius=Config.CORNER_RADIUS)
        
        # Inner highlight
        inner_rect = pygame.Rect(rect.x + 8, rect.y + 8, rect.width - 16, rect.height - 16)
        highlight_color = tuple(min(255, c + 20) for c in color)
        pygame.draw.rect(screen, highlight_color, inner_rect, 2, border_radius=Config.CORNER_RADIUS)
    
    @staticmethod
    def draw_performance_burst(screen, x, y, performance_level, burst_time=0):
        """Draw animated performance feedback burst."""
        # Get performance info
        performance_data = {
            "excellent": {"color": Config.BRIGHT_YELLOW, "icon": "🔥", "particles": 12},
            "good": {"color": Config.AQUA_BLUE, "icon": "⚡", "particles": 8},
            "average": {"color": Config.CARTOON_GREEN, "icon": "👍", "particles": 5},
            "poor": {"color": Config.ENERGETIC_ORANGE, "icon": "😅", "particles": 3},
            "meh": {"color": Config.PLAYFUL_PURPLE, "icon": "🐌", "particles": 2},
            "terrible": {"color": Config.CARTOON_RED, "icon": "💥", "particles": 1}
        }
        
        data = performance_data.get(performance_level, performance_data["average"])
        
        # Animate burst scale
        scale = 1.0 + 0.3 * math.sin(burst_time * 10)
        
        # Draw radiating particles
        for i in range(data["particles"]):
            angle = (i / data["particles"]) * 2 * math.pi
            distance = 30 + 20 * math.sin(burst_time * 5 + i)
            
            particle_x = x + int(distance * math.cos(angle))
            particle_y = y + int(distance * math.sin(angle))
            
            pygame.draw.circle(screen, data["color"], (particle_x, particle_y), 
                             int(5 * scale))
        
        # Draw center icon placeholder (would be replaced with actual cartoon graphic)
        try:
            font = pygame.font.Font(None, int(Config.FONT_LARGE * scale))
        except:
            font = pygame.font.Font(None, int(Config.FONT_LARGE * scale))
        
        icon_surface = font.render(data["icon"], True, data["color"])
        icon_rect = icon_surface.get_rect(center=(x, y))
        screen.blit(icon_surface, icon_rect)
    
    @staticmethod
    def draw_wiggling_text(screen, text, x, y, wiggle_time=0, color=None, font_size=None):
        """Draw text that wiggles like jelly."""
        if color is None:
            color = Config.BLACK
        if font_size is None:
            font_size = Config.FONT_MEDIUM
            
        try:
            font = pygame.font.Font(None, font_size)
        except:
            font = pygame.font.Font(None, font_size)
        
        # Calculate wiggle
        wiggle_x = int(3 * math.sin(wiggle_time * Config.WIGGLE_SPEED))
        wiggle_y = int(2 * math.cos(wiggle_time * Config.WIGGLE_SPEED * 1.3))
        
        # Text shadow
        shadow_surface = font.render(text, True, Config.SHADOW_GRAY)
        screen.blit(shadow_surface, (x + wiggle_x + 2, y + wiggle_y + 2))
        
        # Main text
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x + wiggle_x, y + wiggle_y))
    
    @staticmethod
    def draw_countdown_circle(screen, x, y, progress, color=None):
        """Draw an animated countdown circle like a cartoon timer."""
        if color is None:
            color = Config.BRIGHT_YELLOW
            
        radius = 40
        
        # Draw shadow circle
        pygame.draw.circle(screen, Config.SHADOW_GRAY, (x + 3, y + 3), radius + 5)
        
        # Draw background circle
        pygame.draw.circle(screen, Config.WHITE, (x, y), radius + 3)
        pygame.draw.circle(screen, Config.OUTLINE_DARK, (x, y), radius + 3, 4)
        
        # Draw progress arc (like a pie slice)
        if progress > 0:
            # Calculate arc angle
            angle = int(360 * progress)
            
            # Create a surface for the arc
            arc_surface = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
            arc_rect = pygame.Rect(5, 5, radius * 2, radius * 2)
            
            # Draw the progress pie slice
            pygame.draw.circle(arc_surface, color, (radius + 5, radius + 5), radius)
            
            # This is a simplified version - in a real implementation you'd want
            # a proper arc drawing function or use pygame_gfx
            screen.blit(arc_surface, (x - radius - 5, y - radius - 5))
        
        # Draw center dot
        pygame.draw.circle(screen, Config.OUTLINE_DARK, (x, y), 8)
        pygame.draw.circle(screen, color, (x, y), 6)
    
    @staticmethod
    def get_cartoon_font_path():
        """Return path to cartoon font if available, otherwise None."""
        # In a real implementation, you'd have cartoon fonts like:
        # - "Fredoka-One.ttf"
        # - "BalooBhaina2-Bold.ttf" 
        # - "ComicNeue-Bold.ttf"
        # For now, return None to use system default
        return None