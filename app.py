import pygame
from pygame.locals import *
import random
import sys

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flapetite')

# Define font
font = pygame.font.SysFont('Arial', 60)  # Changed to Arial for readability

# Define colours
white = (255, 255, 255)
black = (0, 0, 0)

# Define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
game_stopped = True
pipe_gap = 200
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
best_score = 0
pass_pipe = False
mood_state = 0
portal_active = False
portal_spawn_score = None

# Load images
home_bg = pygame.image.load('assets/bg_pup.png')
happy_bg = pygame.image.load('assets/bg_happy.png')
sad_bg = pygame.image.load('assets/bg_sad.png')
angy_bg = pygame.image.load('assets/bg_angry.png')
ground_img = pygame.image.load('assets/ground1.png')
start_btn_image = pygame.image.load('assets/start.png')
how_to_play_btn_image = pygame.image.load('assets/how_to_play.png')
exit_btn_image = pygame.image.load('assets/exit.png')
title_image = pygame.image.load('assets/flapetite.png')
button_img = pygame.image.load('assets/restart.png')
bird_images = [
    pygame.image.load('assets/bird1.png'),
    pygame.image.load('assets/bird2.png'),
    pygame.image.load('assets/bird3.png')
]
food_images = [pygame.image.load(f'assets/food{i}.png') for i in range(1, 11)]
portal_image = pygame.image.load('assets/portal.png')
top_happy_pipe_image = pygame.image.load('assets/popsicle_top.png')
bottom_happy_pipe_image = pygame.image.load('assets/popsicle1.png')
top_sad_pipe_image = pygame.image.load('assets/pipe_sad_top.png')
bottom_sad_pipe_image = pygame.image.load('assets/pipe_sad_bottom.png')
top_angry_pipe_image = pygame.image.load('assets/pipe_angry_top.png')
bottom_angry_pipe_image = pygame.image.load('assets/pipe_angry_bottom.png')

# Function for outputting text with outline
def draw_text(text, font, text_col, outline_col, x, y, centered=False):
    # Render the main text
    img = font.render(text, True, text_col)
    img_rect = img.get_rect()
    
    if centered:
        img_rect.centerx = x
    else:
        img_rect.x = x
    img_rect.y = y

    # Render the outline by drawing the text multiple times with a slight offset
    outline_thickness = 2
    outline_img = font.render(text, True, outline_col)
    for dx in [-outline_thickness, 0, outline_thickness]:
        for dy in [-outline_thickness, 0, outline_thickness]:
            if dx != 0 or dy != 0:  # Skip the center to avoid overwriting main text
                screen.blit(outline_img, (img_rect.x + dx, img_rect.y + dy))
    
    # Draw the main text on top
    screen.blit(img, img_rect)

def reset_game():
    pipe_group.empty()
    food_group.empty()
    portal_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    flappy.vel = 0
    flappy.image = flappy.images[flappy.index]  # Reset bird image to unrotated state
    global score, mood_state, portal_active, portal_spawn_score, flying, game_over
    score = 0
    mood_state = 0
    portal_active = False
    portal_spawn_score = None
    flying = False
    game_over = False
    return score

def how_to_play_screen():
    viewing = True
    while viewing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                viewing = False

        screen.blit(home_bg, (0, 0))
        lines = [
            "HOW TO PLAY:",
            "Click mouse to flap",
            "Avoid the pipes",
            "Collect food (+2 points)",
            "Every 2 points: a portal appears",
            "Enter the portal to change theme",
            "Press ESC to return"
        ]
        for idx, line in enumerate(lines):
            text_surf = font.render(line, True, white)
            screen.blit(text_surf, (50, 100 + idx * 40))

        pygame.display.update()
        clock.tick(fps)

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = bird_images
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying and not game_over:
            # Apply gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

            # Jump
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # Handle animation
            flap_cooldown = 5
            self.counter += 1
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            # Rotate the bird based on velocity
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        elif game_over:
            # Point the bird at the ground
            self.image = pygame.transform.rotate(self.images[self.index], -90)
        else:
            # Reset bird image to unrotated state when not flying and not game over
            self.image = self.images[self.index]

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        if mood_state == 0:
            self.image = top_happy_pipe_image if position == 1 else bottom_happy_pipe_image
        elif mood_state == 1:
            self.image = top_sad_pipe_image if position == 1 else bottom_sad_pipe_image
        else:
            self.image = top_angry_pipe_image if position == 1 else bottom_angry_pipe_image
        self.rect = self.image.get_rect()
        if position == 1:
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]
        self.passed = False

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = random.choice(food_images)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = portal_image
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()
food_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# Create menu buttons
start_button = Button(screen_width // 2 - start_btn_image.get_width() // 2, 250, start_btn_image)
how_to_play_button = Button(screen_width // 2 - how_to_play_btn_image.get_width() // 2, 320, how_to_play_btn_image)
exit_button = Button(screen_width // 2 - exit_btn_image.get_width() // 2, 390, exit_btn_image)
restart_button = Button(screen_width // 2 - button_img.get_width() // 2, screen_height // 2 + 50, button_img)
title_rect = title_image.get_rect(center=(screen_width // 2, 60))

def menu():
    global game_stopped, flying, game_over
    while game_stopped:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(home_bg, (0, 0))
        screen.blit(title_image, title_rect.topleft)
        screen.blit(bird_images[1], (screen_width // 2 - bird_images[1].get_width() // 2, 130))
        start_button.draw()
        how_to_play_button.draw()
        exit_button.draw()

        if start_button.draw():
            pygame.time.delay(150)
            game_stopped = False
            # Do not set flying = True here to prevent immediate jump
        elif how_to_play_button.draw():
            pygame.time.delay(150)
            how_to_play_screen()
        elif exit_button.draw():
            pygame.quit()
            sys.exit()

        pygame.display.update()
        clock.tick(fps)

run = True
current_background = happy_bg

while run:
    clock.tick(fps)

    if game_stopped:
        menu()
    else:
        # Draw background
        screen.blit(current_background, (0, 0))

        pipe_group.draw(screen)
        food_group.draw(screen)
        portal_group.draw(screen)
        bird_group.draw(screen)
        bird_group.update()

        # Draw and scroll the ground
        screen.blit(ground_img, (ground_scroll, 768))

        # Update background based on mood
        current_background = [happy_bg, sad_bg, angy_bg][mood_state]

        # Check the score
        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
                and not pass_pipe:
                pass_pipe = True
            if pass_pipe and bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

        # Check for food collision
        if pygame.sprite.spritecollide(flappy, food_group, True):
            score += 2

        # Check for portal collision
        if pygame.sprite.spritecollide(flappy, portal_group, True):
            mood_state = (mood_state + 1) % 3
            portal_active = False
            portal_spawn_score = None
            pipe_group.empty()  # Clear pipes to update with new mood images

        # Draw score and best score during gameplay with outline
        draw_text(f'Score: {score}', font, white, black, screen_width // 2, 20, centered=True)
        draw_text(f'Best: {best_score}', font, white, black, screen_width // 2, 80, centered=True)

        # Look for collision
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True
        if flappy.rect.bottom >= 768:
            game_over = True
            flying = False

        if flying and not game_over:
            # Generate new pipes
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
                top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)
                if random.random() < 0.5:
                    food_x = screen_width + 60
                    food_y = int(screen_height / 2) + pipe_height
                    food_group.add(Food(food_x, food_y))
                if score != 0 and score % 2 == 0 and not portal_active and portal_spawn_score != score:
                    portal_x = screen_width + 80
                    portal_y = int(screen_height / 2) + pipe_height
                    portal_group.add(Portal(portal_x, portal_y))
                    portal_active = True
                    portal_spawn_score = score
                last_pipe = time_now

            pipe_group.update()
            food_group.update()
            portal_group.update()

            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0

        # Check for game over and show game over screen
        if game_over:
            if score > best_score:
                best_score = score
            # Draw game over screen with centered text and outline
            draw_text(f'Score: {score}', font, white, black, screen_width // 2, screen_height // 2 - 50, centered=True)
            draw_text(f'Best: {best_score}', font, white, black, screen_width // 2, screen_height // 2, centered=True)
            if restart_button.draw():
                game_stopped = True
                score = reset_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
                flying = True

    pygame.display.update()

pygame.quit()