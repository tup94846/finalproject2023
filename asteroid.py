import pygame
import sys
import random
import math
import time
from pygame import mixer

# Initialize Pygame
pygame.init()

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
BACKGROUND_COLOR = (0, 0, 0)
SHIP_COLOR = (255, 255, 255)
BULLET_COLOR = (255, 192, 203)
ASTEROID_COLOR = (127, 255, 0)
SHIP_SIZE = 20
SHIP_SPEED = 0.2
BULLET_SIZE = 3
ASTEROID_SIZE = 40
BULLET_SPEED = 1
ASTEROID_SPEED = 0.1
MAX_ASTEROIDS = 5
SPAWN_RATE = 0.4
MAX_LIVES = 3

# Create Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroids Game")

#Sound
mixer.music.load("background.wav.mp3")
mixer.music.play(-1)

# Ship variables
ship_x = SCREEN_WIDTH // 2
ship_y = SCREEN_HEIGHT // 2
ship_angle = 0
ship_exploded = False
lives = MAX_LIVES

# Bullet List
bullets = []

# Asteroid List
asteroids = []

# Explosion variables
explosions_radius = 0
explosions_max_radius = 40
explosions_duration = 500
explosions_start_time = 0
explosions_sound = pygame.mixer.Sound("explosion_sound.wav")

# Game Over variables
game_over = False
game_over_font = pygame.font.Font(None, 36)
game_over_text = game_over_font.render(
    "Game Over - Press R to Restart", True, (255, 255, 255))

# Bullet firing Control variables
last_bullet_fired_time = 0
bullet_fire_delay = 300

# Points variables
points = 0

# Create font for display points
points_font = pygame.font.Font(None, 36)


# Function to check collision between asteroid and ship
def check_ship_asteroid_collision(ship_x, ship_y, asteroids):
    asteroids_to_remove = []

    for asteroid in asteroids:
        asteroid_x, asteroid_y, _ = asteroid
        distance = math.sqrt(
            (ship_x - asteroid_x) ** 2 +
            (ship_y - asteroid_y) ** 2)
        if distance < ASTEROID_SIZE:
            asteroids_to_remove.append(asteroid)

    for asteroid in asteroids_to_remove:
        asteroids.remove(asteroid)

    return len(asteroids_to_remove) > 0


def spawn_asteroid():
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2

    edge = random.choice(["top", "bottom", "left", "right"])

    if edge == "top":
        x = random.randint(0, SCREEN_WIDTH)
        y = 0
        offset = random.randint(-x * 2, x * 2)
        angle = math.atan2(-center_y, center_x + offset)
    elif edge == "bottom":
        x = random.randint(0, SCREEN_WIDTH)
        y = SCREEN_HEIGHT
        offset = random.randint(-x * 2, x * 2)
        angle = math.atan2(-center_y, center_x + offset)
    elif edge == "left":
        x = 0
        y = random.randint(0, SCREEN_HEIGHT)
        offset = random.randint(-y * 2, y)
        angle = math.atan2(-center_y, center_x + offset)
    elif edge == "right":
        x = SCREEN_WIDTH
        y = random.randint(0, SCREEN_HEIGHT)
        offset = random.randint(-y, y * 2)
        angle = math.atan2(-center_y, center_x + offset)

    asteroids.append((x, y, angle))


# Functions checking collisions between asteroids and bullets
def check_bullet_asteroids_collisions(bullets, asteroids):
    global points
    bullets_to_remove = []

    for bullet in bullets:
        bullet_x, bullet_y, _ = bullet

        asteroids_to_remove = [asteroid for asteroid in asteroids if
                               math.sqrt(
                                   (bullet_x - asteroid[0])
                                   ** 2 +
                                   (bullet_y - asteroid[1])
                                   ** 2) < (BULLET_SIZE +
                                            ASTEROID_SIZE)]
        for asteroid in asteroids_to_remove:
            asteroids.remove(asteroid)
            points += 10

    for bullet in bullets_to_remove:
        bullets.remove(bullet)


# Function to draw explosion animation
def draw_explosion(ship_x, ship_y, explosion_radius):
    pygame.draw.circle(
        screen, (255, 0, 0),
        (int(ship_x), int(ship_y)),
        int(explosion_radius))


# Function for the explosion animation
def explosion_animation():
    current_time = pygame.time.get_ticks()
    if (current_time - explosions_start_time
            <= explosions_duration):
        explosion_radius = ((
            current_time - explosions_start_time)
            * explosions_max_radius / explosions_duration)
        draw_explosion(ship_x, ship_y, explosion_radius)
    else:
        explosions_sound.play()
        return True
    return False


# Function to reset game
def reset_game():
    global ship_x, ship_y, ship_angle, ship_exploded
    global lives, game_over, bullets, asteroids, points
    ship_x = SCREEN_WIDTH // 2
    ship_y = SCREEN_HEIGHT // 2
    ship_angle = 0
    ship_exploded = False
    lives = MAX_LIVES
    game_over = False
    bullets = []
    asteroids = []
    points = 0


# Game Loop
running = True
last_spawn_time = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    current_time = pygame.time.get_ticks()

    if not ship_exploded and not game_over:
        if keys[pygame.K_LEFT]:
            ship_angle += 0.004
        if keys[pygame.K_RIGHT]:
            ship_angle -= 0.004

        if keys[pygame.K_UP]:
            ship_x += SHIP_SPEED * math.cos(ship_angle)
            ship_y -= SHIP_SPEED * math.sin(ship_angle)

            if ship_x < 0:
                ship_x = SCREEN_WIDTH
            elif ship_x > SCREEN_WIDTH:
                ship_x = 0
            if ship_y < 0:
                ship_y = SCREEN_HEIGHT
            elif ship_y > SCREEN_HEIGHT:
                ship_y = 0

        if check_ship_asteroid_collision(
                ship_x, ship_y, asteroids):
            ship_exploded = True
            explosions_start_time = current_time
            lives -= 1
            if lives <= 0:
                game_over = True

        check_bullet_asteroids_collisions(
            bullets, asteroids)

        if (keys[pygame.K_SPACE] and
                current_time - last_bullet_fired_time >=
                bullet_fire_delay):
            bullet_x = ship_x + SHIP_SIZE * math.cos(
                ship_angle)
            bullet_y = ship_y - SHIP_SIZE * math.sin(
                ship_angle)
            bullets.append(
                (bullet_x, bullet_y, ship_angle))
            last_bullet_fired_time = current_time

    screen.fill(BACKGROUND_COLOR)

    new_bullets = []
    for bullet in bullets:
        bullet_x, bullet_y, bullet_angle = bullet
        bullet_x += BULLET_SPEED * math.cos(bullet_angle)
        bullet_y -= BULLET_SPEED * math.sin(bullet_angle)
        if (0 <= bullet_x < SCREEN_WIDTH and
                0 <= bullet_y < SCREEN_HEIGHT):
            new_bullets.append(
                (bullet_x, bullet_y, bullet_angle))
            pygame.draw.circle(
                screen, BULLET_COLOR,
                (int(bullet_x), int(bullet_y)),
                int(BULLET_SIZE))
    bullets = new_bullets

    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time > SPAWN_RATE:
        if len(asteroids) < MAX_ASTEROIDS:
            spawn_asteroid()
        last_spawn_time = current_time

    new_asteroids = []
    for asteroid in asteroids:
        asteroid_x, asteroid_y, asteroid_angle = asteroid
        asteroid_x += ASTEROID_SPEED * math.cos(
            asteroid_angle)
        asteroid_y -= ASTEROID_SPEED * math.sin(
            asteroid_angle)
        if (-ASTEROID_SIZE <= asteroid_x
                <= SCREEN_WIDTH + ASTEROID_SIZE and
                -ASTEROID_SIZE <= asteroid_y <=
                SCREEN_HEIGHT + ASTEROID_SIZE):
            new_asteroids.append(
                (asteroid_x, asteroid_y, asteroid_angle))
            pygame.draw.circle(
                screen, ASTEROID_COLOR,
                (int(asteroid_x), int(asteroid_y)),
                ASTEROID_SIZE)

    asteroids = new_asteroids
    # Draw Ship
    if not ship_exploded:
        ship_vertices = [
            (ship_x + SHIP_SIZE * math.cos(
                ship_angle),
             ship_y - SHIP_SIZE * math.sin(
                 ship_angle)),
            (ship_x + SHIP_SIZE * math.cos(
                ship_angle + 2.5),
             ship_y - SHIP_SIZE * math.sin(
                 ship_angle + 2.5)),
            (ship_x, ship_y),
            (ship_x + SHIP_SIZE * math.cos(
                ship_angle - 2.5),
             ship_y - SHIP_SIZE * math.sin(
                 ship_angle - 2.5)),
        ]

        pygame.draw.polygon(
            screen, SHIP_COLOR, ship_vertices)

    if ship_exploded:
        if explosion_animation():
            ship_exploded = False

    lives_font = pygame.font.Font(None, 36)
    lives_text = lives_font.render(
        f"Points: {points}", True, (255, 255, 255))
    screen.blit(lives_text, (10, 10))

    if game_over:
        screen.blit(
            game_over_text,
            (SCREEN_WIDTH // 2 - 200,
             SCREEN_HEIGHT // 2))

    pygame.display.update()

    if game_over and keys[pygame.K_r]:
        reset_game()

pygame.quit()
sys.exit()

            
            

 
        
    
