import asyncio
import platform
import pygame
from sys import exit
import random
import speech_recognition as sr
import threading
import queue
import math

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init()  # Initialize the mixer for audio
clock = pygame.time.Clock()

# Set Window Properties
win_width = 551
win_height = 720
window = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Flapetite")

# Load Bird Animation Frames
bird_images = [pygame.image.load("assets/bird_down.png"),
               pygame.image.load("assets/bird_mid.png"),
               pygame.image.load("assets/bird_up.png")]

# Load Backgrounds for Mood States
normal_background = pygame.image.load("assets/background_normal.png")
happy_background = pygame.image.load("assets/background_happy.png")
sad_background = pygame.image.load("assets/background_sad.png")
angry_background = pygame.image.load("assets/background_angry.png")

# Load Pipe Images for Each Mood
top_normal_pipe_image = pygame.image.load("assets/pipe_normal_top.png")
bottom_normal_pipe_image = pygame.image.load("assets/pipe_normal_bottom.png")
top_happy_pipe_image = pygame.image.load("assets/pipe_happy_top.png")
bottom_happy_pipe_image = pygame.image.load("assets/pipe_happy_bottom.png")
top_sad_pipe_image = pygame.image.load("assets/pipe_sad_top.png")
bottom_sad_pipe_image = pygame.image.load("assets/pipe_sad_bottom.png")
top_angry_pipe_image = pygame.image.load("assets/pipe_angry_top.png")
bottom_angry_pipe_image = pygame.image.load("assets/pipe_angry_bottom.png")

# Load UI Button and Panel Assets
start_btn_image = pygame.image.load("assets/start.png")
play_btn_image = pygame.image.load("assets/play.png")
how_to_play_btn_image1 = pygame.image.load("assets/how_to_play1.png")
how_to_play_btn_image2 = pygame.image.load("assets/how_to_play2.png")
exit_btn_image = pygame.image.load("assets/exit.png")
continue_btn_image = pygame.image.load("assets/continue.png")
title_image = pygame.image.load("assets/flapetite.png")
quickie_image = [pygame.image.load("assets/quickie.png"),
                 pygame.image.load("assets/quickie1.png"),
                 pygame.image.load("assets/quickie2.png")]
pause_btn_image = pygame.image.load("assets/pause.png")
how_to_play_image = pygame.image.load("assets/how_to_play_panel.png")
pause_image = pygame.image.load("assets/pause_panel.png")
game_over_image = pygame.image.load("assets/game_over_panel.png")

# Load Gameplay Sprites
portal_image = pygame.image.load("assets/portal.png")
food_images = [pygame.image.load(f"assets/food{i}.png") for i in range(1, 11)]

# Load Audio Files
background_music = pygame.mixer.Sound("assets/audio/bg_music.mp3")
flap_sounds = [
    pygame.mixer.Sound("assets/audio/flap.wav"),
    pygame.mixer.Sound("assets/audio/flap1.wav"),
    pygame.mixer.Sound("assets/audio/flap2.wav"),
    pygame.mixer.Sound("assets/audio/flap3.wav")
]
score_sound = pygame.mixer.Sound("assets/audio/score.wav")
food_eat_sound = pygame.mixer.Sound("assets/audio/food_eat_sound.wav")
portal_sound = pygame.mixer.Sound("assets/audio/warp.wav")
game_over_sound = pygame.mixer.Sound("assets/audio/game_over.wav")
button_click = pygame.mixer.Sound("assets/audio/button_click.wav")
button_hover = pygame.mixer.Sound("assets/audio/hover.wav")

# Start background music once at game startup
background_music.play(loops=-1)  # Loop indefinitely

# Game Constants and Initial Values
scroll_speed = 3
bird_start_position = (100, 350)
score = 0
best_score = 0
font = pygame.font.Font("assets/more_sugar.ttf", 50)
big_font = pygame.font.Font("assets/more_sugar.ttf", 90)
small_font = pygame.font.Font("assets/more_sugar.ttf", 30)
game_stopped = True
pipe_gap = 200
command_queue = queue.Queue()

# Pause Button Rect
pause_btn_rect = pause_btn_image.get_rect(topleft=(20, 20))

# Voice Recognition Thread
def voice_recognition_thread():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True  # Enable dynamic thresholding for faster speech detection
    recognizer.energy_threshold = 4000  # Adjust for microphone sensitivity
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        while True:
            try:
                audio = recognizer.listen(source, timeout=0.1)
                command = recognizer.recognize_google(audio).lower()
                command_queue.put(command)
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                continue
            except Exception:
                continue

# Start voice recognition in a separate thread
threading.Thread(target=voice_recognition_thread, daemon=True).start()

# Pause Game Menu
def pause_game():
    global score
    paused = True
    continue_hover_played = False
    exit_hover_played = False
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                button_click.play()  # Play button click sound on ESC
                paused = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse = event.pos
                    continue_rect = continue_btn_image.get_rect(center=(win_width // 2 + 100, 510))
                    exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 510))
                    if continue_rect.collidepoint(mouse):
                        button_click.play()  # Play button click sound
                        paused = False
                    elif exit_rect.collidepoint(mouse):
                        button_click.play()  # Play button click sound
                        score = 0
                        paused = False
                        game_stopped = True
                        menu()

        # Process voice commands
        try:
            command = command_queue.get_nowait()
            if command == "continue":
                button_click.play()  # Play button click sound
                paused = False
            elif command == "exit":
                button_click.play()  # Play button click sound
                score = 0
                paused = False
                game_stopped = True
                menu()
        except queue.Empty:
            pass

        # Check for mouse hover on buttons
        mouse_pos = pygame.mouse.get_pos()
        continue_btn = continue_btn_image
        exit_btn = exit_btn_image
        button_scale = 1.1  # 10% larger when hovered
        continue_rect = continue_btn_image.get_rect(center=(win_width // 2 + 100, 510))
        exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 510))

        if continue_rect.collidepoint(mouse_pos):
            if not continue_hover_played:
                button_hover.play()  # Play hover sound
                continue_hover_played = True
            continue_btn = pygame.transform.scale(continue_btn_image,
                                                 (int(continue_btn_image.get_width() * button_scale),
                                                  int(continue_btn_image.get_height() * button_scale)))
            continue_rect = continue_btn.get_rect(center=(win_width // 2 + 100, 510))
        else:
            continue_hover_played = False

        if exit_rect.collidepoint(mouse_pos):
            if not exit_hover_played:
                button_hover.play()  # Play hover sound
                exit_hover_played = True
            exit_btn = pygame.transform.scale(exit_btn_image,
                                              (int(exit_btn_image.get_width() * button_scale),
                                               int(exit_btn_image.get_height() * button_scale)))
            exit_rect = exit_btn.get_rect(center=(win_width // 2 - 100, 510))
        else:
            exit_hover_played = False

        # Draw pause panel and buttons
        window.blit(pause_image, (win_width // 2 - pause_image.get_width() // 2, win_height // 2 - pause_image.get_height() // 2))
        window.blit(continue_btn, continue_rect.topleft)
        window.blit(exit_btn, exit_rect.topleft)

        pygame.display.update()
        clock.tick(60)

# Bird Class
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = bird_images
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=bird_start_position).inflate(-10, -10)
        self.vel = 0
        self.clicked = False
        self.space_pressed = False
        self.voice_jump = False
        self.alive = True

    def update(self, user_input, game_started):
        if self.alive:
            # Handle animation
            flap_cooldown = 5
            self.counter += 1
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index = (self.index + 1) % len(self.images)
                self.image = self.images[self.index]

            # Apply gravity only if game has started
            if game_started:
                self.vel += 0.5
                if self.vel > 8:
                    self.vel = 8
                if self.rect.bottom < win_height:
                    self.rect.y += int(self.vel)

            # Flap on SPACE key, mouse click, or voice "jump" (single tap)
            try:
                command = command_queue.get_nowait()
                if command == "jump":
                    self.voice_jump = True
            except queue.Empty:
                pass

            if ((user_input[pygame.K_SPACE] and not self.space_pressed) or 
                (pygame.mouse.get_pressed()[0] == 1 and not self.clicked) or 
                (self.voice_jump and not self.clicked)) and self.rect.y > 0:
                self.clicked = pygame.mouse.get_pressed()[0] == 1 or self.voice_jump
                self.space_pressed = user_input[pygame.K_SPACE]
                self.vel = -10
                random.choice(flap_sounds).play()  # Play random flap sound
            if not user_input[pygame.K_SPACE]:
                self.space_pressed = False
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
            if self.voice_jump:
                self.voice_jump = False

            # Rotate bird based on velocity
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            # When dead, point downward
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < win_height:
                self.rect.y += int(self.vel)
            self.image = pygame.transform.rotate(self.images[self.index], -90)

# Pipe Class
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
                score_sound.play()  # Play score sound for passing pipes

# Food Class
class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = random.choice(food_images)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# Portal Class
class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = portal_image
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# How to Play Screen
def how_to_play_screen():
    play_hover_played = False
    exit_hover_played = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                button_click.play()  # Play button click sound on ESC
                menu()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse = event.pos
                    play_rect = play_btn_image.get_rect(center=(win_width // 2 + 100, 610))
                    exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 610))
                    if play_rect.collidepoint(mouse):
                        button_click.play()  # Play button click sound
                        # Wait for mouse release before starting game
                        while pygame.mouse.get_pressed()[0]:
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    pygame.quit()
                                    exit()
                            pygame.display.update()
                            clock.tick(60)
                        main()
                        return
                    elif exit_rect.collidepoint(mouse):
                        button_click.play()  # Play button click sound
                        menu()
                        return

        # Process voice commands
        try:
            command = command_queue.get_nowait()
            if command == "play":
                button_click.play()  # Play button click sound
                main()
                return
            elif command == "exit":
                button_click.play()  # Play button click sound
                menu()
                return
        except queue.Empty:
            pass

        # Check for mouse hover on buttons
        mouse_pos = pygame.mouse.get_pos()
        play_btn = play_btn_image
        exit_btn = exit_btn_image
        button_scale = 1.1  # 10% larger when hovered
        play_rect = play_btn_image.get_rect(center=(win_width // 2 + 100, 610))
        exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 610))

        if play_rect.collidepoint(mouse_pos):
            if not play_hover_played:
                button_hover.play()  # Play hover sound
                play_hover_played = True
            play_btn = pygame.transform.scale(play_btn_image,
                                              (int(play_btn_image.get_width() * button_scale),
                                               int(play_btn_image.get_height() * button_scale)))
            play_rect = play_btn.get_rect(center=(win_width // 2 + 100, 610))
        else:
            play_hover_played = False

        if exit_rect.collidepoint(mouse_pos):
            if not exit_hover_played:
                button_hover.play()  # Play hover sound
                exit_hover_played = True
            exit_btn = pygame.transform.scale(exit_btn_image,
                                              (int(exit_btn_image.get_width() * button_scale),
                                               int(exit_btn_image.get_height() * button_scale)))
            exit_rect = exit_btn.get_rect(center=(win_width // 2 - 100, 610))
        else:
            exit_hover_played = False

        # Draw elements
        window.blit(normal_background, (0, 0))
        howto_rect = how_to_play_btn_image2.get_rect(center=(win_width // 2, 100))
        window.blit(how_to_play_image, (win_width // 2 - how_to_play_image.get_width() // 2, win_height // 2 - 250))
        window.blit(play_btn, play_rect.topleft)
        window.blit(exit_btn, exit_rect.topleft)
        window.blit(how_to_play_btn_image2, howto_rect.topleft)

        pygame.display.update()
        clock.tick(60)

# Main Game Loop
def main():
    global score, best_score, game_stopped
    bird = pygame.sprite.GroupSingle(Bird())
    pipes = pygame.sprite.Group()
    foods = pygame.sprite.Group()
    portal = pygame.sprite.Group()

    pipe_timer = 0
    mood_state = 0
    current_background = normal_background
    portal_active = False
    portal_spawn_score = None
    game_started = False  # Wait for user input to start game
    game_over_played = False  # Flag to ensure game over sound plays once

    # Clear command queue and reset input states
    while not command_queue.empty():
        command_queue.get()
    bird.sprite.clicked = False
    bird.sprite.space_pressed = False
    bird.sprite.voice_jump = False

    while True:
        user_input = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and game_started:
                button_click.play()  # Play button click sound on ESC
                pause_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and pause_btn_rect.collidepoint(event.pos) and game_started:
                    button_click.play()  # Play button click sound
                    pause_game()

        # Process voice commands
        try:
            command = command_queue.get_nowait()
            if command == "pause" and game_started:
                button_click.play()  # Play button click sound
                pause_game()
            elif command == "jump":
                game_started = True  # Start game on "jump" voice command
        except queue.Empty:
            pass

        # Check for start inputs (spacebar, click, or voice "jump")
        if not game_started:
            if user_input[pygame.K_SPACE] or (pygame.mouse.get_pressed()[0] == 1 and not bird.sprite.clicked):
                game_started = True

        # Draw elements
        window.blit(current_background, (0, 0))
        if game_started:
            window.blit(pause_btn_image, pause_btn_rect.topleft)
        pipes.draw(window)
        foods.draw(window)
        portal.draw(window)
        bird.draw(window)

        # Display score
        score_text = font.render(f'Score: {score}', True, pygame.Color(23, 35, 58))
        window.blit(score_text, (190, 50))

        # Display start prompt if game hasn't started
        if not game_started:
            # Split text into two lines
            line1 = small_font.render("Press SPACE, Click,", True, pygame.Color(23, 35, 58))
            line2 = small_font.render("or Say 'Jump' to Start", True, pygame.Color(23, 35, 58))
            line3 = font.render("GET READY...", True, pygame.Color(23, 35, 58))

            # Centered x positions
            x = (win_width - line1.get_width()) // 2
            x3 = (win_width - line3.get_width()) // 2

            # Y position
            y = 500

            # Draw each line
            window.blit(line1, (x, y))
            window.blit(line2, (x, y + line1.get_height() + 5))
            window.blit(line3, (x3, 150))

        # Update sprites
        if game_started and bird.sprite.alive:
            pipes.update()
            foods.update()
            portal.update()
        bird.update(user_input, game_started)

        # Check collisions
        if game_started:
            if bird.sprite.rect.top <= 0 or bird.sprite.rect.bottom >= win_height:
                if bird.sprite.alive:
                    bird.sprite.alive = False
                    game_over_sound.play()  # Play game over sound
                    game_over_played = True
            if pygame.sprite.spritecollide(bird.sprite, pipes, False):
                if bird.sprite.alive:
                    bird.sprite.alive = False
                    game_over_sound.play()  # Play game over sound
                    game_over_played = True

        # Handle game over
        if not bird.sprite.alive and game_started:
            if score > best_score:
                best_score = score
            play_hover_played = False
            exit_hover_played = False
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            mouse = event.pos
                            play_rect = play_btn_image.get_rect(center=(win_width // 2 + 100, 510))
                            exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 510))
                            if play_rect.collidepoint(mouse):
                                button_click.play()  # Play button click sound
                                score = 0
                                main()
                                return
                            elif exit_rect.collidepoint(mouse):
                                button_click.play()  # Play button click sound
                                score = 0
                                game_stopped = True
                                menu()
                                return

                # Process voice commands
                try:
                    command = command_queue.get_nowait()
                    if command == "play":
                        button_click.play()  # Play button click sound
                        score = 0
                        main()
                        return
                    elif command == "exit":
                        button_click.play()  # Play button click sound
                        score = 0
                        game_stopped = True
                        menu()
                        return
                except queue.Empty:
                    pass

                # Check for mouse hover on buttons
                mouse_pos = pygame.mouse.get_pos()
                play_btn = play_btn_image
                exit_btn = exit_btn_image
                button_scale = 1.1  # 10% larger when hovered
                play_rect = play_btn_image.get_rect(center=(win_width // 2 + 100, 510))
                exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 510))

                if play_rect.collidepoint(mouse_pos):
                    if not play_hover_played:
                        button_hover.play()  # Play hover sound
                        play_hover_played = True
                    play_btn = pygame.transform.scale(play_btn_image,
                                                     (int(play_btn_image.get_width() * button_scale),
                                                      int(play_btn_image.get_height() * button_scale)))
                    play_rect = play_btn.get_rect(center=(win_width // 2 + 100, 510))
                else:
                    play_hover_played = False

                if exit_rect.collidepoint(mouse_pos):
                    if not exit_hover_played:
                        button_hover.play()  # Play hover sound
                        exit_hover_played = True
                    exit_btn = pygame.transform.scale(exit_btn_image,
                                                     (int(exit_btn_image.get_width() * button_scale),
                                                      int(exit_btn_image.get_height() * button_scale)))
                    exit_rect = exit_btn.get_rect(center=(win_width // 2 - 100, 510))
                else:
                    exit_hover_played = False

                # Draw game over elements
                window.blit(current_background, (0, 0))
                pipes.draw(window)
                foods.draw(window)
                portal.draw(window)
                bird.draw(window)

                # Show game over panel
                window.blit(game_over_image, (win_width // 2 - game_over_image.get_width() // 2, win_height // 2 - 250))
                window.blit(play_btn, play_rect.topleft)
                window.blit(exit_btn, exit_rect.topleft)

                # Draw scores
                curr_text = big_font.render(f"{score}", True, (23, 35, 58))
                best_text = big_font.render(f"{best_score}", True, (23, 35, 58))
                spacing = 140
                total_width = curr_text.get_width() + spacing + best_text.get_width()
                start_x = (win_width - total_width) // 2
                y_position = win_height // 2 - 20
                window.blit(curr_text, (start_x, y_position))
                window.blit(best_text, (start_x + curr_text.get_width() + spacing, y_position))

                pygame.display.update()
                clock.tick(60)

        # Spawn pipes, food, and portal only if game has started
        if game_started and pipe_timer <= 0 and bird.sprite.alive:
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

            if score > 0 and score % 10 == 0 and not portal_active and portal_spawn_score != score:
                portal.add(Portal(x_pipe + 80, top_pipe_height + pipe_gap // 2))
                portal_active = True
                portal_spawn_score = score

            pipe_timer = random.randint(150, 220)

        if game_started:
            pipe_timer -= 1

        # Check for food collection
        if game_started and pygame.sprite.spritecollide(bird.sprite, foods, True):
            score += 1
            food_eat_sound.play()  # Play food eat sound

        # Check for portal entry
        if game_started and pygame.sprite.spritecollide(bird.sprite, portal, True):
            available_moods = [i for i in range(4) if i != mood_state]
            mood_state = random.choice(available_moods)
            current_background = [normal_background, happy_background, sad_background, angry_background][mood_state]
            portal_active = False
            portal_spawn_score = None
            portal_sound.play()  # Play portal sound

        pygame.display.update()
        clock.tick(60)

# Main Menu Loop
def menu():
    global game_stopped
    game_stopped = True
    start_rect = start_btn_image.get_rect(center=(win_width // 2, 420))
    howto_rect = how_to_play_btn_image1.get_rect(center=(win_width // 2, 500))
    exit_rect = exit_btn_image.get_rect(center=(win_width // 2, 580))
    title_rect = title_image.get_rect(center=(win_width // 2, 110))

    # Animation variables for title
    animation_time = 0
    base_title_scale = 1.0
    title_scale_amplitude = 0.05  # 5% scale variation
    title_animation_speed = 0.05   # Speed of pulsing animation

    # Animation variables for quickie
    quickie_index = 0
    quickie_counter = 0
    flap_cooldown = 5  # Match Bird class animation speed
    quickie_hover_played = False  # Flag for hover sound (optional)

    # Hover sound flags for buttons
    start_hover_played = False
    howto_hover_played = False
    exit_hover_played = False

    # Clear command queue to avoid stale commands
    while not command_queue.empty():
        command_queue.get()

    while game_stopped:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse = event.pos
                    if start_rect.collidepoint(mouse):
                        button_click.play()  # Play button click sound
                        # Wait for mouse release before starting game
                        while pygame.mouse.get_pressed()[0]:
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    pygame.quit()
                                    exit()
                            pygame.display.update()
                            clock.tick(60)
                        game_stopped = False
                        main()
                    elif howto_rect.collidepoint(mouse):
                        button_click.play()  # Play button click sound
                        # Wait for mouse release before going to how to play
                        while pygame.mouse.get_pressed()[0]:
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    pygame.quit()
                                    exit()
                            pygame.display.update()
                            clock.tick(60)
                        how_to_play_screen()
                    elif exit_rect.collidepoint(mouse):
                        button_click.play()  # Play button click sound
                        pygame.quit()
                        exit()

        # Process voice commands
        try:
            command = command_queue.get_nowait()
            if command == "start":
                button_click.play()  # Play button click sound
                game_stopped = False
                main()
            elif command == "how to play":
                button_click.play()  # Play button click sound
                how_to_play_screen()
            elif command == "exit":
                button_click.play()  # Play button click sound
                pygame.quit()
                exit()
        except queue.Empty:
            pass

        # Update animation time for title
        animation_time += title_animation_speed

        # Calculate title scale for pulsing effect
        title_scale = base_title_scale + title_scale_amplitude * math.sin(animation_time)
        scaled_title = pygame.transform.scale(title_image,
                                             (int(title_image.get_width() * title_scale),
                                              int(title_image.get_height() * title_scale)))
        scaled_title_rect = scaled_title.get_rect(center=(win_width // 2, 110))

        # Check for mouse hover on quickie
        mouse_pos = pygame.mouse.get_pos()
        quickie_rect = quickie_image[quickie_index].get_rect(topleft=(win_width // 2 - 90, 190))
        if quickie_rect.collidepoint(mouse_pos):
            # Uncomment the following block to add hover sound
            # if not quickie_hover_played:
            #     button_hover.play()  # Play hover sound
            #     quickie_hover_played = True
            # Animate quickie
            quickie_counter += 1
            if quickie_counter > flap_cooldown:
                quickie_counter = 0
                quickie_index = (quickie_index + 1) % len(quickie_image)
        else:
            # Reset to static image
            quickie_index = 0
            quickie_counter = 0
            quickie_hover_played = False  # Reset hover sound flag

        # Check for mouse hover on buttons
        start_btn = start_btn_image
        howto_btn = how_to_play_btn_image1
        exit_btn = exit_btn_image
        button_scale = 1.1  # 10% larger when hovered

        if start_rect.collidepoint(mouse_pos):
            if not start_hover_played:
                button_hover.play()  # Play hover sound
                start_hover_played = True
            start_btn = pygame.transform.scale(start_btn_image,
                                               (int(start_btn_image.get_width() * button_scale),
                                                int(start_btn_image.get_height() * button_scale)))
            start_rect = start_btn.get_rect(center=(win_width // 2, 420))
        else:
            start_hover_played = False

        if howto_rect.collidepoint(mouse_pos):
            if not howto_hover_played:
                button_hover.play()  # Play hover sound
                howto_hover_played = True
            howto_btn = pygame.transform.scale(how_to_play_btn_image1,
                                               (int(how_to_play_btn_image1.get_width() * button_scale),
                                                int(how_to_play_btn_image1.get_height() * button_scale)))
            howto_rect = howto_btn.get_rect(center=(win_width // 2, 500))
        else:
            howto_hover_played = False

        if exit_rect.collidepoint(mouse_pos):
            if not exit_hover_played:
                button_hover.play()  # Play hover sound
                exit_hover_played = True
            exit_btn = pygame.transform.scale(exit_btn_image,
                                              (int(exit_btn_image.get_width() * button_scale),
                                               int(exit_btn_image.get_height() * button_scale)))
            exit_rect = exit_btn.get_rect(center=(win_width // 2, 580))
        else:
            exit_hover_played = False

        # Draw elements
        window.blit(normal_background, (0, 0))
        window.blit(scaled_title, scaled_title_rect.topleft)
        window.blit(quickie_image[quickie_index], quickie_rect.topleft)
        window.blit(start_btn, start_rect.topleft)
        window.blit(howto_btn, howto_rect.topleft)
        window.blit(exit_btn, exit_rect.topleft)

        pygame.display.update()
        clock.tick(60)

# Launch the Game
if platform.system() == "Emscripten":
    async def main_async():
        menu()
        await asyncio.sleep(0)
    asyncio.ensure_future(main_async())
else:
    if __name__ == "__main__":
        menu()