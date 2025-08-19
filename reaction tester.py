import pygame  # type: ignore
import random
import time
import math

# Initialize
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Twitch-y")

font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 64)

# Colors
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)

# Load sounds (replace with your actual mp3 files)
start_sound = pygame.mixer.Sound("assets/chime.mp3")
too_soon_sound = pygame.mixer.Sound("assets/oops.mp3")
success_sound = pygame.mixer.Sound("assets/ding.mp3")

# Game states
WAITING = "waiting"
READY = "ready"
RESULT = "result"
GREEN_STATE = "green"
state = WAITING

start_time = 0
reaction_time = None
wait_duration = 0

running = True
clock = pygame.time.Clock()

# -----------------------------
# Particle system for animation
# -----------------------------
class Particle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-0.5, 0.5)
        self.color = (random.randint(150, 255), random.randint(150, 255), 255)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x < 0 or self.x > WIDTH:
            self.speed_x *= -1
        if self.y < 0 or self.y > HEIGHT:
            self.speed_y *= -1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

# Create particles
particles = [Particle() for _ in range(30)]

# -----------------------------
# Main Loop
# -----------------------------
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if state == WAITING:
                    # Start waiting phase
                    wait_duration = random.uniform(2, 5)  # 2–5 seconds
                    start_time = time.time()
                    state = READY
                    start_sound.play()
                elif state == READY:
                    # Pressed too early
                    reaction_time = "Too soon! Wait for green."
                    state = RESULT
                    too_soon_sound.play()
                elif state == RESULT:
                    # Restart
                    reaction_time = None
                    state = WAITING
    
    # Game logic
    if state == READY:
        if time.time() - start_time >= wait_duration:
            # Change to green, record time
            screen.fill(GREEN)
            if reaction_time is None:  # only once
                start_time = time.time()
                state = GREEN_STATE
        else:
            screen.fill(RED)
    
    elif state == GREEN_STATE:
        screen.fill(GREEN)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            reaction_time = round((time.time() - start_time) * 1000)  # in ms
            state = RESULT
            success_sound.play()
    
    # Draw text and animations
    if state == WAITING:
        # Draw animated particles
        for p in particles:
            p.move()
            p.draw(screen)

        # Title with pulsing effect
        pulse = int(20 * math.sin(time.time() * 2))  # oscillates between -20 and +20
        title_text = title_font.render("Twitch-y", True, BLUE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 80 + pulse//4))

        # Instructions
        text = font.render("Press SPACE to start", True, BLACK)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 50))

    elif state == RESULT:
        result_text = font.render(f"Result: {reaction_time}", True, BLACK)
        restart_text = font.render("Press SPACE to try again", True, BLACK)
        screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2 - 20))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
