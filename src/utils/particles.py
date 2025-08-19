"""Particle system for visual effects."""
import pygame
import random
import math
from config import Config

class Particle:
    """Individual particle with position, velocity, and visual properties."""
    
    def __init__(self, x=None, y=None):
        self.x = x if x is not None else random.randint(0, Config.WINDOW_WIDTH)
        self.y = y if y is not None else random.randint(0, Config.WINDOW_HEIGHT)
        self.size = random.randint(Config.PARTICLE_MIN_SIZE, Config.PARTICLE_MAX_SIZE)
        self.speed_x = random.uniform(*Config.PARTICLE_SPEED_RANGE)
        self.speed_y = random.uniform(*Config.PARTICLE_SPEED_RANGE)
        self.color = self.generate_color()
        self.alpha = random.randint(100, 255)
        self.life = 1.0
        self.decay_rate = random.uniform(0.1, 0.3)
    
    def generate_color(self):
        """Generate a random particle color."""
        return (
            random.randint(100, 255),
            random.randint(150, 255),
            random.randint(200, 255)
        )
    
    def update(self, dt):
        """Update particle position and properties."""
        self.x += self.speed_x * dt * 60  # Scale by 60 for frame-rate independence
        self.y += self.speed_y * dt * 60
        
        # Bounce off edges
        if self.x <= 0 or self.x >= Config.WINDOW_WIDTH:
            self.speed_x *= -0.8  # Slight damping
        if self.y <= 0 or self.y >= Config.WINDOW_HEIGHT:
            self.speed_y *= -0.8
        
        # Keep within bounds
        self.x = max(0, min(Config.WINDOW_WIDTH, self.x))
        self.y = max(0, min(Config.WINDOW_HEIGHT, self.y))
        
        # Fade out over time
        self.life -= self.decay_rate * dt
        self.alpha = int(255 * max(0, self.life))
    
    def render(self, screen):
        """Draw the particle."""
        if self.life <= 0:
            return
        
        # Create a surface with per-pixel alpha
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color, self.alpha)
        pygame.draw.circle(particle_surface, color_with_alpha, (self.size, self.size), self.size)
        
        screen.blit(particle_surface, (self.x - self.size, self.y - self.size))
    
    def is_alive(self):
        """Check if particle should continue existing."""
        return self.life > 0

class ParticleSystem:
    """Manages a collection of particles."""
    
    def __init__(self, max_particles=50):
        self.max_particles = max_particles
        self.particles = []
        self.spawn_timer = 0.0
        self.spawn_rate = 0.1  # seconds between spawns
        
        # Create initial particles
        for _ in range(max_particles // 2):
            self.particles.append(Particle())
    
    def update(self, dt):
        """Update all particles."""
        # Update existing particles
        for particle in self.particles[:]:  # Use slice to avoid issues with removal
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)
        
        # Spawn new particles
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_rate and len(self.particles) < self.max_particles:
            self.particles.append(Particle())
            self.spawn_timer = 0.0
    
    def render(self, screen):
        """Render all particles."""
        for particle in self.particles:
            particle.render(screen)
    
    def add_burst(self, x, y, count=10):
        """Add a burst of particles at a specific location."""
        for _ in range(count):
            if len(self.particles) < self.max_particles:
                particle = Particle(x, y)
                # Give burst particles more initial velocity
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 5)
                particle.speed_x = math.cos(angle) * speed
                particle.speed_y = math.sin(angle) * speed
                self.particles.append(particle)
    
    def clear(self):
        """Remove all particles."""
        self.particles.clear()