# --- Import Libraries ---
import pygame
from sys import exit
import random

# --- Initialize Pygame and Clock ---
pygame.init()
clock = pygame.time.Clock()

# --- Set Window Properties ---
win_width = 551
win_height = 720
window = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Flapetite")

# --- Load Bird Animation Frames ---
bird_images = [pygame.image.load("assets/bird_down.png"),
               pygame.image.load("assets/bird_mid.png"),
               pygame.image.load("assets/bird_up.png")]

# --- Load Backgrounds for Mood States ---
normal_background = pygame.image.load("assets/background_normal.png")
happy_background = pygame.image.load("assets/background_happy.png")
sad_background = pygame.image.load("assets/background_sad.png")
angy_background = pygame.image.load("assets/background_angry.png")

# --- Load Pipe Images for Each Mood ---
top_normal_pipe_image = pygame.image.load("assets/pipe_normal_top1.png")
bottom_normal_pipe_image = pygame.image.load("assets/pipe_normal_bottom1.png")
top_happy_pipe_image = pygame.image.load("assets/pipe_happy_top.png")
bottom_happy_pipe_image = pygame.image.load("assets/pipe_happy_bottom.png")
top_sad_pipe_image = pygame.image.load("assets/pipe_sad_top.png")
bottom_sad_pipe_image = pygame.image.load("assets/pipe_sad_bottom.png")
top_angry_pipe_image = pygame.image.load("assets/pipe_angry_top.png")
bottom_angry_pipe_image = pygame.image.load("assets/pipe_angry_bottom.png")

# --- Load UI Button and Panel Assets ---
start_btn_image = pygame.image.load("assets/start.png")
play_btn_image = pygame.image.load("assets/play.png")
how_to_play_btn_image1 = pygame.image.load("assets/how_to_play1.png")
how_to_play_btn_image2 = pygame.image.load("assets/how_to_play2.png")
exit_btn_image = pygame.image.load("assets/exit.png")
continue_btn_image = pygame.image.load("assets/continue.png")
title_image = pygame.image.load("assets/flapetite.png")
quickie_image = pygame.image.load("assets/quickie.png")
pause_btn_image = pygame.image.load("assets/pause.png")
how_to_play_image = pygame.image.load("assets/how_to_play_panel.png")
pause_image = pygame.image.load("assets/pause_panel.png")
game_over_image = pygame.image.load("assets/game_over_panel.png")

# --- Load Gameplay Sprites ---
portal_image = pygame.image.load("assets/portal.png")
food_images = [pygame.image.load(f"assets/food{i}.png") for i in range(1, 11)]  # 10 random food images

# --- Game Constants and Initial Values ---
scroll_speed = 2
bird_start_position = (100, 250)
score = 0
best_score = 0
font = pygame.font.Font("assets/more_sugar.ttf", 50)
big_font = pygame.font.Font("assets/more_sugar.ttf", 90)
game_stopped = True
pipe_gap = 200

# --- Pause Button Rect (for click detection) ---
pause_btn_rect = pause_btn_image.get_rect(topleft=(20, 20))

# --- Pause Game Menu ---
def pause_game():
    global score
    paused = True

    while paused:
        # Event handling inside pause screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and pause_btn_rect.collidepoint(pygame.mouse.get_pos()):
                    paused = False

        # Draw pause panel
        window.blit(pause_image, (win_width // 2 - pause_image.get_width() // 2, win_height // 2 - pause_image.get_height() // 2))

        # Draw resume and exit buttons
        continue_rect = continue_btn_image.get_rect(center=(win_width // 2 + 100, 510))
        exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 510))

        window.blit(continue_btn_image, continue_rect.topleft)
        window.blit(exit_btn_image, exit_rect.topleft)

        # Handle mouse clicks
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if continue_rect.collidepoint(mouse) and click[0]:
            pygame.time.delay(150)
            return  # Resume game
        elif exit_rect.collidepoint(mouse) and click[0]:
            score = 0
            menu()

        pygame.display.update()
        clock.tick(60)

# --- Bird Class (Player-controlled) ---
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bird_images[0]
        self.rect = self.image.get_rect(center=bird_start_position).inflate(-10, -10)  # Shrink hitbox
        self.image_index = 0
        self.vel = 0
        self.flap = False
        self.alive = True

    def update(self, user_input):
        # Animate bird
        if self.alive:
            self.image_index = (self.image_index + 1) % 30
            self.image = bird_images[self.image_index // 10]

        # Apply gravity
        self.vel += 0.5
        self.vel = min(self.vel, 7)
        self.rect.y += int(self.vel)

        # Tilt effect
        self.image = pygame.transform.rotate(self.image, self.vel * -7)

        # Flap on SPACE key
        if user_input[pygame.K_SPACE] and not self.flap and self.rect.y > 0 and self.alive:
            self.flap = True
            self.vel = -7
        if not user_input[pygame.K_SPACE]:
            self.flap = False

# --- Pipe Class (Obstacle) ---
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, image, pipe_type):
        super().__init__()
        self.pipe_type = pipe_type
        self.image = image
        self.rect = self.image.get_rect()
        if pipe_type == 'top':
            self.rect.bottomleft = (x, y)
        else:
            self.rect.topleft = (x, y)

        # Used to track scoring
        self.enter, self.exit, self.passed = False, False, False

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

        # Scoring logic
        global score
        if self.pipe_type == 'bottom':
            if bird_start_position[0] > self.rect.left and not self.passed:
                self.enter = True
            if bird_start_position[0] > self.rect.right and not self.passed:
                self.exit = True
            if self.enter and self.exit and not self.passed:
                self.passed = True
                score += 1

# --- Food Class (Collectible Item) ---
class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = random.choice(food_images)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# --- Portal Class (Theme Change Trigger) ---
class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = portal_image
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# --- Basic Quit Event Handling ---
def quit_game():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

# How To Play screen
def how_to_play_screen():
    viewing = True
    while viewing:
        quit_game()
        window.blit(normal_background, (0, 0))

        # Buttons and header
        play_rect = play_btn_image.get_rect(center=(win_width // 2 + 100, 610))
        exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 610))
        howto_rect = how_to_play_btn_image2.get_rect(center=(win_width // 2, 100))

        window.blit(how_to_play_image, (win_width // 2 - how_to_play_image.get_width() // 2, win_height // 2 - 250))
        window.blit(play_btn_image, play_rect.topleft)
        window.blit(exit_btn_image, exit_rect.topleft)
        window.blit(how_to_play_btn_image2, howto_rect.topleft)

        # Click detection
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if play_rect.collidepoint(mouse) and click[0]:
            main()
        elif exit_rect.collidepoint(mouse) and click[0]:
            return

        pygame.display.update()
        clock.tick(60)

# --- Main Game Loop ---
def main():
    global score, best_score

    # Sprite groups
    bird = pygame.sprite.GroupSingle(Bird())
    pipes = pygame.sprite.Group()
    foods = pygame.sprite.Group()
    portal = pygame.sprite.Group()

    pipe_timer = 0
    mood_state = 0
    current_background = normal_background
    portal_active = False
    portal_spawn_score = None

    while True:
        user_input = pygame.key.get_pressed()

        # Input Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and pause_btn_rect.collidepoint(pygame.mouse.get_pos()):
                    pause_game()

        # Draw elements
        window.blit(current_background, (0, 0))
        window.blit(pause_btn_image, pause_btn_rect.topleft)

        pipes.draw(window)
        foods.draw(window)
        portal.draw(window)
        bird.draw(window)

        # Display Score
        score_text = font.render(f'Score: {score}', True, pygame.Color(23, 35, 58))
        window.blit(score_text, (190, 50))

        # Update sprites if bird is alive
        if bird.sprite.alive:
            pipes.update()
            foods.update()
            portal.update()
        bird.update(user_input)

        # Check for collisions or out-of-bounds
        if bird.sprite.rect.top <= 0 or bird.sprite.rect.bottom >= win_height:
            bird.sprite.alive = False
        if pygame.sprite.spritecollide(bird.sprite, pipes, False):
            bird.sprite.alive = False

        # Handle Game Over
        if not bird.sprite.alive:
            if score > best_score:
                best_score = score

            while True:
                quit_game()
                window.blit(current_background, (0, 0))
                pipes.draw(window)
                foods.draw(window)
                portal.draw(window)
                bird.draw(window)

                # Show game over panel and buttons
                window.blit(game_over_image, (win_width // 2 - game_over_image.get_width() // 2, win_height // 2 - 250))
                play_rect = play_btn_image.get_rect(center=(win_width // 2 + 100, 510))
                exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 510))
                window.blit(play_btn_image, play_rect.topleft)
                window.blit(exit_btn_image, exit_rect.topleft)

                # Draw current and best score
                curr_text = big_font.render(f"{score}", True, (23, 35, 58))
                best_text = big_font.render(f"{best_score}", True, (23, 35, 58))
                spacing = 140
                total_width = curr_text.get_width() + spacing + best_text.get_width()
                start_x = (win_width - total_width) // 2
                y_position = win_height // 2 - 20
                window.blit(curr_text, (start_x, y_position))
                window.blit(best_text, (start_x + curr_text.get_width() + spacing, y_position))

                pygame.display.update()

                # Handle button clicks
                mouse = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()
                if play_rect.collidepoint(mouse) and click[0]:
                    pygame.time.delay(150)
                    score = 0
                    main()
                    return
                elif exit_rect.collidepoint(mouse) and click[0]:
                    score = 0
                    menu()

        # Check for food collection
        if pygame.sprite.spritecollide(bird.sprite, foods, True):
            score += 1

        # Check for portal entry
        if pygame.sprite.spritecollide(bird.sprite, portal, True):
            mood_state = (mood_state + 1) % 4
            current_background = [normal_background, happy_background, sad_background, angy_background][mood_state]
            portal_active = False
            portal_spawn_score = None

        # Spawn pipes, food, and portal
        if pipe_timer <= 0 and bird.sprite.alive:
            x_pipe = win_width
            top_pipe_height = random.randint(50, win_height - pipe_gap - 150)
            bottom_pipe_y = top_pipe_height + pipe_gap

            # Select mood-specific pipe images
            top_img, bot_img = (top_normal_pipe_image, bottom_normal_pipe_image) if mood_state == 0 else \
                (top_happy_pipe_image, bottom_happy_pipe_image) if mood_state == 1 else \
                    (top_sad_pipe_image, bottom_sad_pipe_image) if mood_state == 2 else \
                        (top_angry_pipe_image, bottom_angry_pipe_image)

            pipes.add(Pipe(x_pipe, top_pipe_height, top_img, 'top'))
            pipes.add(Pipe(x_pipe, bottom_pipe_y, bot_img, 'bottom'))

            if random.random() < 0.5:
                foods.add(Food(x_pipe + 60, top_pipe_height + pipe_gap // 2))

            if score != 0 and score % 2 == 0 and not portal_active and portal_spawn_score != score:
                portal.add(Portal(x_pipe + 80, top_pipe_height + pipe_gap // 2))
                portal_active = True
                portal_spawn_score = score

            pipe_timer = random.randint(150, 220)

        pipe_timer -= 1
        pygame.display.update()
        clock.tick(60)

# --- Main Menu Loop ---
def menu():
    global game_stopped

    start_rect = start_btn_image.get_rect(center=(win_width // 2, 420))
    howto_rect = how_to_play_btn_image1.get_rect(center=(win_width // 2, 500))
    exit_rect = exit_btn_image.get_rect(center=(win_width // 2,580))
    title_rect = title_image.get_rect(center=(win_width // 2, 110))

    while game_stopped:
        quit_game()
        window.blit(normal_background, (0, 0))

        # Draw menu items
        window.blit(title_image, title_rect.topleft)
        window.blit(quickie_image, (win_width // 2 - 115, 130))
        window.blit(start_btn_image, start_rect.topleft)
        window.blit(how_to_play_btn_image1, howto_rect.topleft)
        window.blit(exit_btn_image, exit_rect.topleft)

        # Detect clicks
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

# --- Launch the Game ---
menu()
