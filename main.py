import pygame
from sys import exit
import random

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()

# Window
win_width = 551
win_height = 720
window = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Flapetite")

# Load assets
bird_images = [pygame.image.load("assets/bird_down.png"),
               pygame.image.load("assets/bird_mid.png"),
               pygame.image.load("assets/bird_up.png")]

normal_background = pygame.image.load("assets/background_normal.png")
happy_background = pygame.image.load("assets/background_happy.png")
sad_background = pygame.image.load("assets/background_sad.png")
angy_background = pygame.image.load("assets/background_angry.png")

top_normal_pipe_image = pygame.image.load("assets/pipe_normal_top.png")
bottom_normal_pipe_image = pygame.image.load("assets/pipe_normal_bottom.png")
top_happy_pipe_image = pygame.image.load("assets/pipe_happy_top.png")
bottom_happy_pipe_image = pygame.image.load("assets/pipe_happy_bottom.png")
top_sad_pipe_image = pygame.image.load("assets/pipe_sad_top.png")
bottom_sad_pipe_image = pygame.image.load("assets/pipe_sad_bottom.png")
top_angry_pipe_image = pygame.image.load("assets/pipe_angry_top.png")
bottom_angry_pipe_image = pygame.image.load("assets/pipe_angry_bottom.png")

start_btn_image = pygame.image.load("assets/start.png")
play_btn_image = pygame.image.load("assets/play.png")
how_to_play_btn_image = pygame.image.load("assets/how_to_play.png")
exit_btn_image = pygame.image.load("assets/exit.png")
continue_btn_image = pygame.image.load("assets/continue.png")
title_image = pygame.image.load("assets/flapetite.png")
quickie_image = pygame.image.load("assets/quickie.png")
pause_btn_image = pygame.image.load("assets/pause.png")
pause_image = pygame.image.load("assets/pause_panel.png")
game_over_image = pygame.image.load("assets/game_over_panel.png")

portal_image = pygame.image.load("assets/portal.png")
food_images = [pygame.image.load(f"assets/food{i}.png") for i in range(1, 11)]

scroll_speed = 2
bird_start_position = (100, 250)
score = 0
best_score = 0
font = pygame.font.Font("assets/more_sugar.ttf", 50)
game_stopped = True

pipe_gap = 300

pause_btn_rect = pause_btn_image.get_rect(topleft=(20, 20))

def pause_game():
    paused = True

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and pause_btn_rect.collidepoint(pygame.mouse.get_pos()):
                    paused = False

        window.blit(pause_image, (win_width // 2 - pause_image.get_width() // 2, win_height // 2 - pause_image.get_height() // 2))

        # Buttons
        continue_rect = continue_btn_image.get_rect(center=(win_width // 2 + 100, 510))  # Resume on left
        exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 510))     # Exit on right

        window.blit(continue_btn_image, continue_rect.topleft)
        window.blit(exit_btn_image, exit_rect.topleft)

        # Get mouse input here
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if continue_rect.collidepoint(mouse) and click[0]:
            pygame.time.delay(150)
            return  # Resume game
        elif exit_rect.collidepoint(mouse) and click[0]:
            pygame.quit()
            exit()

        pygame.display.update()
        clock.tick(60)

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bird_images[0]
        self.rect = self.image.get_rect(center=bird_start_position).inflate(-10, -10)
        self.image_index = 0
        self.vel = 0
        self.flap = False
        self.alive = True

    def update(self, user_input):
        if self.alive:
            self.image_index = (self.image_index + 1) % 30
            self.image = bird_images[self.image_index // 10]

        self.vel += 0.5
        if self.vel > 7:
            self.vel = 7
        self.rect.y += int(self.vel)

        self.image = pygame.transform.rotate(self.image, self.vel * -7)

        if user_input[pygame.K_SPACE] and not self.flap and self.rect.y > 0 and self.alive:
            self.flap = True
            self.vel = -7
        if not user_input[pygame.K_SPACE]:
            self.flap = False

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

        self.enter, self.exit, self.passed = False, False, False

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

        global score
        if self.pipe_type == 'bottom':
            if bird_start_position[0] > self.rect.left and not self.passed:
                self.enter = True
            if bird_start_position[0] > self.rect.right and not self.passed:
                self.exit = True
            if self.enter and self.exit and not self.passed:
                self.passed = True
                score += 1

class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = random.choice(food_images)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = portal_image
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

def quit_game():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

def how_to_play_screen():
    viewing = True
    while viewing:
        quit_game()
        window.blit(normal_background, (0, 0))

        lines = [
            "HOW TO PLAY:",
            "Press SPACE to flap",
            "Avoid the pipes",
            "Collect food (+2 points)",
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

def main():
    global score, best_score

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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and pause_btn_rect.collidepoint(pygame.mouse.get_pos()):
                    pause_game()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and pause_btn_rect.collidepoint(pygame.mouse.get_pos()):
                    pause_game()

        window.blit(current_background, (0, 0))
        window.blit(pause_btn_image, pause_btn_rect.topleft)

        pipes.draw(window)
        foods.draw(window)
        portal.draw(window)
        bird.draw(window)

        score_text = font.render(f'Score: {score}', True, pygame.Color(23, 35, 58))
        window.blit(score_text, (190, 50))

        if bird.sprite.alive:
            pipes.update()
            foods.update()
            portal.update()
        bird.update(user_input)

        if bird.sprite.rect.top <= 0 or bird.sprite.rect.bottom >= win_height:
            bird.sprite.alive = False

        if pygame.sprite.spritecollide(bird.sprite, pipes, False):
            bird.sprite.alive = False

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

                # Game over image
                window.blit(game_over_image, (win_width // 2 - game_over_image.get_width() // 2, win_height // 2 - 250))

                # Buttons
                play_rect = play_btn_image.get_rect(center=(win_width // 2 + 100, 510))  # Shifted left
                exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 510))  # Shifted right

                window.blit(play_btn_image, play_rect.topleft)
                window.blit(exit_btn_image, exit_rect.topleft)

                # Score text
                curr_text = font.render(f"{score}", True, (23, 35, 58))
                best_text = font.render(f"{best_score}", True, (23, 35, 58))

                spacing = 140  # Space between texts
                total_width = curr_text.get_width() + spacing + best_text.get_width()
                start_x = (win_width - total_width) // 2
                y_position = win_height // 2 + 5

                window.blit(curr_text, (start_x, y_position))
                window.blit(best_text, (start_x + curr_text.get_width() + spacing, y_position))

                pygame.display.update()

                # Get mouse status
                mouse = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()

                # Button click handling
                if play_rect.collidepoint(mouse) and click[0]:
                    pygame.time.delay(150)
                    score = 0
                    return
                elif exit_rect.collidepoint(mouse) and click[0]:
                    pygame.quit()
                    exit()

        if pygame.sprite.spritecollide(bird.sprite, foods, True):
            score += 1

        if pygame.sprite.spritecollide(bird.sprite, portal, True):
            mood_state = (mood_state + 1) % 4
            current_background = [normal_background, happy_background, sad_background, angy_background][mood_state]
            portal_active = False
            portal_spawn_score = None

        if pipe_timer <= 0 and bird.sprite.alive:
            x_pipe = win_width
            top_pipe_height = random.randint(50, win_height - pipe_gap - 150)
            bottom_pipe_y = top_pipe_height + pipe_gap

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

def menu():
    global game_stopped

    start_rect = start_btn_image.get_rect(center=(win_width // 2, 420))
    howto_rect = how_to_play_btn_image.get_rect(center=(win_width // 2, 500))
    exit_rect = exit_btn_image.get_rect(center=(win_width // 2,580))
    title_rect = title_image.get_rect(center=(win_width // 2, 110))

    while game_stopped:
        quit_game()
        window.blit(normal_background, (0, 0))

        window.blit(title_image, title_rect.topleft)
        window.blit(quickie_image, (win_width // 2 - 115, 130))
        window.blit(start_btn_image, start_rect.topleft)
        window.blit(how_to_play_btn_image, howto_rect.topleft)
        window.blit(exit_btn_image, exit_rect.topleft)

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

menu()
