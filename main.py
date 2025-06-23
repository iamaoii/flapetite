import pygame
from sys import exit
import random

pygame.init()
clock = pygame.time.Clock()

# Window
win_height = 720
win_width = 551
window = pygame.display.set_mode((win_width, win_height))

# Images
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

# Game
scroll_speed = 1
bird_start_position = (100, 250)
score = 0
font = pygame.font.SysFont('Segoe', 26)
game_stopped = True


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
        if self.alive:
            self.image_index += 1
        if self.image_index >= 30:
            self.image_index = 0
        self.image = bird_images[self.image_index // 10]

        self.vel += 0.5
        if self.vel > 7:
            self.vel = 7
        if self.rect.y < 500:
            self.rect.y += int(self.vel)
        if self.vel == 0:
            self.flap = False

        self.image = pygame.transform.rotate(self.image, self.vel * -7)

        if user_input[pygame.K_SPACE] and not self.flap and self.rect.y > 0 and self.alive:
            self.flap = True
            self.vel = -7


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, image, pipe_type):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.enter, self.exit, self.passed = False, False, False
        self.pipe_type = pipe_type

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

        global score
        if self.pipe_type == 'bottom':
            if bird_start_position[0] > self.rect.topleft[0] and not self.passed:
                self.enter = True
            if bird_start_position[0] > self.rect.topright[0] and not self.passed:
                self.exit = True
            if self.enter and self.exit and not self.passed:
                self.passed = True
                score += 1


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = coin_image
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


class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ground_image
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


def quit_game():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


def main():
    global score

    bird = pygame.sprite.GroupSingle()
    bird.add(Bird())

    pipes = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    portal = pygame.sprite.Group()

    x_pos_ground, y_pos_ground = 0, 520
    ground = pygame.sprite.Group()
    ground.add(Ground(x_pos_ground, y_pos_ground))

    pipe_timer = 0
    is_night = False
    current_background = skyline_image
    portal_active = False
    portal_spawn_score = None

    run = True
    while run:
        quit_game()
        user_input = pygame.key.get_pressed()

        # Draw
        window.fill((0, 0, 0))
        window.blit(current_background, (0, 0))
        pipes.draw(window)
        coins.draw(window)
        portal.draw(window)
        ground.draw(window)
        bird.draw(window)

        # Score display
        score_text = font.render('Score: ' + str(score), True, pygame.Color(255, 255, 255))
        window.blit(score_text, (20, 20))

        # Update
        if bird.sprite.alive:
            pipes.update()
            coins.update()
            portal.update()
            ground.update()
        bird.update(user_input)

        # Collisions
        if pygame.sprite.spritecollide(bird.sprite, pipes, False) or \
           pygame.sprite.spritecollide(bird.sprite, ground, False):
            bird.sprite.alive = False
            window.blit(game_over_image, (win_width // 2 - game_over_image.get_width() // 2,
                                          win_height // 2 - game_over_image.get_height() // 2))
            if user_input[pygame.K_r]:
                score = 0
                break

        # Coin collection
        if pygame.sprite.spritecollide(bird.sprite, coins, True):
            score += 2

        # Portal collision - switch mode
        if pygame.sprite.spritecollide(bird.sprite, portal, True):
            is_night = not is_night
            current_background = night_background_image if is_night else skyline_image
            portal_active = False
            portal_spawn_score = None

        # Pipe/Coin/Portal spawning
        if pipe_timer <= 0 and bird.sprite.alive:
            x_pipe = 550
            y_top = random.randint(-600, -480)
            gap = random.randint(90, 130)
            y_bottom = y_top + gap + bottom_pipe_image.get_height()

            top_img = red_pipe_top_image if is_night else top_pipe_image
            bot_img = red_pipe_bottom_image if is_night else bottom_pipe_image

            pipes.add(Pipe(x_pipe, y_top, top_img, 'top'))
            pipes.add(Pipe(x_pipe, y_bottom, bot_img, 'bottom'))

            # Random coin chance
            if random.random() < 0.5:
                coin_x = x_pipe + top_img.get_width() // 2
                coin_y = y_top + top_img.get_height() + gap // 2
                coins.add(Coin(coin_x, coin_y))

            # Spawn portal immediately after reaching new 5-point milestone
            if score != 0 and score % 2 == 0 and not portal_active and portal_spawn_score != score:
                portal_x = x_pipe + 80
                portal_y = y_top + top_img.get_height() + gap // 2
                portal.add(Portal(portal_x, portal_y))
                portal_active = True
                portal_spawn_score = score

            pipe_timer = random.randint(180, 250)

        pipe_timer -= 1
        clock.tick(60)
        pygame.display.update()


def menu():
    global game_stopped
    while game_stopped:
        quit_game()
        window.fill((0, 0, 0))
        window.blit(skyline_image, (0, 0))
        window.blit(ground_image, (0, 520))
        window.blit(bird_images[0], (100, 250))
        window.blit(start_image, (win_width // 2 - start_image.get_width() // 2,
                                  win_height // 2 - start_image.get_height() // 2))
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            main()
        pygame.display.update()


menu()