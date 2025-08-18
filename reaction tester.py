import pygame
import random
import time

# Initialize
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reaction Time Tester")

font = pygame.font.Font(None, 36)

# Colors
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLACK = (0, 0, 0)

# Load sounds (replace with your actual mp3 files)
start_sound = pygame.mixer.Sound("chime.mp3")
too_soon_sound = pygame.mixer.Sound("oops.mp3")
success_sound = pygame.mixer.Sound("ding.mp3")

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
    
    # Draw text
    if state == WAITING:
        text = font.render("Press SPACE to start", True, BLACK)
        screen.blit(text, (150, 180))
    elif state == RESULT:
        result_text = font.render(f"Result: {reaction_time}", True, BLACK)
        restart_text = font.render("Press SPACE to try again", True, BLACK)
        screen.blit(result_text, (180, 150))
        screen.blit(restart_text, (150, 200))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
