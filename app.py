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
flying = False
game_over = False

# Load images
bg = pygame.image.load('assets/bg.png')
ground_img = pygame.image.load('assets/ground.png')


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 3):
            img = pygame.image.load(f'assets/quickie{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel = 0
        self.clicked = False

    def update(self):

        # Gravity
        if flying == True:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)
        
        if game_over == False:
        # Jump Motion
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # Handles the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # Rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -70) # can be -90

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

    # Draw the ground
    screen.blit(ground_img, (ground_scroll, 768))

    # Check if bird has hit the ground
    if flappy.rect.bottom >= 768 and flying:
        game_over = True
        flying = False

    if game_over == False:
    # Scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False 
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
        
    pygame.display.update()

pygame.quit()