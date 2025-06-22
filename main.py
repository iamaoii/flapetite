import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

# Window
win_height = 936
win_width = 836
screen = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption('Flapetite')

# Define game variables
ground_scroll = 0
scroll_speed = 4

# Load images
bg = pygame.image.load('assets/bg.png')
ground_img = pygame.image.load('assets/ground.png')


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'assets/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):

        # Handles the animation
        self.counter += 1
        flap_cooldown = 5

        if self.counter > flap_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
        self.image = self.images[self.index]

bird_group = pygame.sprite.Group()

flappy = Bird(100, int(win_height / 2))

bird_group.add(flappy)


run = True
while run:

    clock.tick(fps)

    # Draw background
    screen.blit(bg, (0, 0))

    # Draw bird
    bird_group.draw(screen)
    bird_group.update()

    # Draw and scroll ground
    screen.blit(ground_img, (ground_scroll, 768))
    ground_scroll -= scroll_speed
    if abs(ground_scroll) > 35:
        ground_scroll = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False 

    pygame.display.update()

pygame.quit()