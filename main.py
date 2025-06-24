import pygame
from sys import exit
import random

# Initialize Pygame and clock
pygame.init()
clock = pygame.time.Clock()

# Window settings
win_height = 720
win_width = 551
window = pygame.display.set_mode((win_width, win_height))

# Load assets
bird_images = [pygame.image.load("assets/bird_down.png"),
               pygame.image.load("assets/bird_mid.png"),
               pygame.image.load("assets/bird_up.png")]
skyline_image = pygame.image.load("assets/background.png")
night_background_image = pygame.image.load("assets/background_night.png")
ground_image = pygame.image.load("assets/ground.png")
top_pipe_image = pygame.image.load("assets/pipe_top.png")
bottom_pipe_image = pygame.image.load("assets/pipe_bottom.png")
red_pipe_top_image = pygame.image.load("assets/pipe-red_top.png")
red_pipe_bottom_image = pygame.image.load("assets/pipe-red_bottom.png")
coin_image = pygame.image.load("assets/coin.png")
portal_image = pygame.image.load("assets/portal.png")
game_over_image = pygame.image.load("assets/game_over.png")
start_image = pygame.image.load("assets/start.png")
start_btn_image = pygame.image.load("assets/start_btn.png")
how_to_play_image = pygame.image.load("assets/how_to_play.png")
exit_image = pygame.image.load("assets/exit.png")
title_image = pygame.image.load("assets/flapetite.png")

# Game variables
scroll_speed = 1
bird_start_position = (100, 250)
score = 0
best_score = 0
font = pygame.font.SysFont('Segoe', 26)
game_stopped = True

# Bird class - player-controlled character
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bird_images[0]
        self.rect = self.image.get_rect(center=bird_start_position)
        self.image_index = 0
        self.vel = 0
        self.flap = False
        self.alive = True

    def update(self, user_input):
        # Animate bird
        if self.alive:
            self.image_index += 1
        if self.image_index >= 30:
            self.image_index = 0
        self.image = bird_images[self.image_index // 10]

        # Apply gravity
        self.vel += 0.5
        if self.vel > 7:
            self.vel = 7
        if self.rect.y < 500:
            self.rect.y += int(self.vel)
        if self.vel == 0:
            self.flap = False

        # Rotate bird depending on speed
        self.image = pygame.transform.rotate(self.image, self.vel * -7)

        # Flap if SPACE is pressed
        if user_input[pygame.K_SPACE] and not self.flap and self.rect.y > 0 and self.alive:
            self.flap = True
            self.vel = -7

# Pipe class - obstacles for the player
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, image, pipe_type):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.enter, self.exit, self.passed = False, False, False
        self.pipe_type = pipe_type

    def update(self):
        # Move pipe to the left
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

        # Update score if bird passes pipe
        global score
        if self.pipe_type == 'bottom':
            if bird_start_position[0] > self.rect.topleft[0] and not self.passed:
                self.enter = True
            if bird_start_position[0] > self.rect.topright[0] and not self.passed:
                self.exit = True
            if self.enter and self.exit and not self.passed:
                self.passed = True
                score += 1

# Coin class - collectable for extra points
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = coin_image
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# Portal class - toggles between day and night
class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = portal_image
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# Ground class - scrollable floor
class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ground_image
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# Quit game handler
def quit_game():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

# How to Play instructions screen
def how_to_play_screen():
    viewing = True
    while viewing:
        quit_game()
        window.fill((0, 191, 255))

        lines = [
            "HOW TO PLAY:",
            "Press SPACE to flap",
            "Avoid the pipes",
            "Collect coins (+2 points)",
            "Every 2 points: a portal appears",
            "Enter the portal to change theme",
            "Press ESC to return"
        ]

        for idx, line in enumerate(lines):
            text_surf = font.render(line, True, (255, 255, 255))
            window.blit(text_surf, (50, 100 + idx * 40))

        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            viewing = False

        pygame.display.update()
        clock.tick(60)

# Main game loop
def main():
    global score, best_score

    # Sprite groups
    bird = pygame.sprite.GroupSingle()
    bird.add(Bird())
    pipes = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    portal = pygame.sprite.Group()
    ground = pygame.sprite.Group()
    ground.add(Ground(0, 520))

    # Game logic variables
    pipe_timer = 0
    is_night = False
    current_background = skyline_image
    portal_active = False
    portal_spawn_score = None
    run = True

    while run:
        quit_game()
        user_input = pygame.key.get_pressed()
        window.blit(current_background, (0, 0))

        # Draw sprites
        pipes.draw(window)
        coins.draw(window)
        portal.draw(window)
        ground.draw(window)
        bird.draw(window)

        # Show score
        score_text = font.render(f'Score: {score}', True, pygame.Color(255, 255, 255))
        window.blit(score_text, (20, 20))

        # Update sprites
        if bird.sprite.alive:
            pipes.update()
            coins.update()
            portal.update()
            ground.update()
        bird.update(user_input)

        # Collision detection
        if pygame.sprite.spritecollide(bird.sprite, pipes, False) or \
           pygame.sprite.spritecollide(bird.sprite, ground, False):
            bird.sprite.alive = False
            if score > best_score:
                best_score = score

            # Game Over screen
            while True:
                quit_game()
                window.blit(current_background, (0, 0))
                pipes.draw(window)
                coins.draw(window)
                portal.draw(window)
                ground.draw(window)
                bird.draw(window)
                window.blit(game_over_image, (win_width // 2 - game_over_image.get_width() // 2, win_height // 2 - 100))

                curr_text = font.render(f"Your Score: {score}", True, (255, 255, 255))
                best_text = font.render(f"Best Score: {best_score}", True, (255, 215, 0))
                info_text = font.render("Press R to Restart", True, (200, 200, 200))

                window.blit(curr_text, (win_width // 2 - curr_text.get_width() // 2, win_height // 2 + 10))
                window.blit(best_text, (win_width // 2 - best_text.get_width() // 2, win_height // 2 + 50))
                window.blit(info_text, (win_width // 2 - info_text.get_width() // 2, win_height // 2 + 90))

                pygame.display.update()
                if pygame.key.get_pressed()[pygame.K_r]:
                    score = 0
                    return

        # Collect coin
        if pygame.sprite.spritecollide(bird.sprite, coins, True):
            score += 2

        # Enter portal (toggle theme)
        if pygame.sprite.spritecollide(bird.sprite, portal, True):
            is_night = not is_night
            current_background = night_background_image if is_night else skyline_image
            portal_active = False
            portal_spawn_score = None

        # Spawn pipes, coins, portal
        if pipe_timer <= 0 and bird.sprite.alive:
            x_pipe = 550
            y_top = random.randint(-600, -480)
            gap = random.randint(90, 130)
            y_bottom = y_top + gap + bottom_pipe_image.get_height()

            top_img = red_pipe_top_image if is_night else top_pipe_image
            bot_img = red_pipe_bottom_image if is_night else bottom_pipe_image

            pipes.add(Pipe(x_pipe, y_top, top_img, 'top'))
            pipes.add(Pipe(x_pipe, y_bottom, bot_img, 'bottom'))

            if random.random() < 0.5:
                coin_x = x_pipe + top_img.get_width() // 2
                coin_y = y_top + top_img.get_height() + gap // 2
                coins.add(Coin(coin_x, coin_y))

            if score != 0 and score % 2 == 0 and not portal_active and portal_spawn_score != score:
                portal_x = x_pipe + 80
                portal_y = y_top + top_img.get_height() + gap // 2
                portal.add(Portal(portal_x, portal_y))
                portal_active = True
                portal_spawn_score = score

            pipe_timer = random.randint(180, 250)

        pipe_timer -= 1
        pygame.display.update()
        clock.tick(60)

# Main menu loop
def menu():
    global game_stopped

    # Button positions
    start_rect = start_btn_image.get_rect(center=(win_width // 2, 250))
    howto_rect = how_to_play_image.get_rect(center=(win_width // 2, 320))
    exit_rect = exit_image.get_rect(center=(win_width // 2, 390))
    title_rect = title_image.get_rect(center=(win_width // 2, 60))
    while game_stopped:
        quit_game()
        window.fill((0, 191, 255))

        # Title
        window.blit(title_image, title_rect.topleft)
        
        # Bird image (decoration)
        window.blit(bird_images[1], (win_width // 2 - 24, 130))

        # Draw button images
        window.blit(start_btn_image, start_rect.topleft)
        window.blit(how_to_play_image, howto_rect.topleft)
        window.blit(exit_image, exit_rect.topleft)

        # Mouse input handling
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if start_rect.collidepoint(mouse) and click[0]:
            pygame.time.delay(150)
            main()
        elif howto_rect.collidepoint(mouse) and click[0]:
            pygame.time.delay(150)
            how_to_play_screen()
        elif exit_rect.collidepoint(mouse) and click[0]:
            pygame.quit()
            exit()

        pygame.display.update()
        clock.tick(60)

# Start the game
menu()
