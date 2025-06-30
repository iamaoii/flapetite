# --- Import Libraries ---
import pygame
from sys import exit
import random
import speech_recognition as sr
import threading
import queue

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
angry_background = pygame.image.load("assets/background_angry.png")

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
food_images = [pygame.image.load(f"assets/food{i}.png") for i in range(1, 11)]

# --- Game Constants and Initial Values ---
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

# --- Pause Button Rect ---
pause_btn_rect = pause_btn_image.get_rect(topleft=(20, 20))

# --- Voice Recognition Thread ---
def voice_recognition_thread():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True  # Enable dynamic thresholding for faster speech detection
    recognizer.energy_threshold = 4000  # Adjust for microphone sensitivity
    with sr.Microphone() as source:
        print("Voice recognition thread started. Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        print("Listening for voice commands (say 'start', 'jump', 'pause', etc.)...")
        while True:
            try:
                audio = recognizer.listen(source, timeout=0.1)
                command = recognizer.recognize_google(audio).lower()
                print(f"Recognized command: {command}")
                command_queue.put(command)
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                print("Could not understand audio.")
                continue
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error in voice thread: {e}")
                continue

# Start voice recognition in a separate thread
threading.Thread(target=voice_recognition_thread, daemon=True).start()

# --- Pause Game Menu ---
def pause_game():
    global score
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse = event.pos
                    continue_rect = continue_btn_image.get_rect(center=(win_width // 2 + 100, 510))
                    exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 510))
                    if continue_rect.collidepoint(mouse):
                        paused = False
                    elif exit_rect.collidepoint(mouse):
                        score = 0
                        paused = False
                        game_stopped = True
                        menu()

        # Process voice commands
        try:
            command = command_queue.get_nowait()
            print(f"Pause menu received command: {command}")
            if command == "continue":
                paused = False
            elif command == "exit":
                score = 0
                paused = False
                game_stopped = True
                menu()
        except queue.Empty:
            pass

        # Draw pause panel and buttons
        window.blit(pause_image, (win_width // 2 - pause_image.get_width() // 2, win_height // 2 - pause_image.get_height() // 2))
        continue_rect = continue_btn_image.get_rect(center=(win_width // 2 + 100, 510))
        exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 510))
        window.blit(continue_btn_image, continue_rect.topleft)
        window.blit(exit_btn_image, exit_rect.topleft)

        pygame.display.update()
        clock.tick(60)

# --- Bird Class ---
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
                    print("Jump command detected, triggering flap")
                    self.voice_jump = True
            except queue.Empty:
                pass

            if ((user_input[pygame.K_SPACE] and not self.space_pressed) or 
                (pygame.mouse.get_pressed()[0] == 1 and not self.clicked) or 
                (self.voice_jump and not self.clicked)) and self.rect.y > 0:
                self.clicked = pygame.mouse.get_pressed()[0] == 1 or self.voice_jump
                self.space_pressed = user_input[pygame.K_SPACE]
                self.vel = -10
                print(f"Bird flapping: vel={self.vel}, y={self.rect.y}")
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

# --- Pipe Class ---
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

# --- Food Class ---
class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = random.choice(food_images)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# --- Portal Class ---
class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = portal_image
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# --- How to Play Screen ---
def how_to_play_screen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse = event.pos
                    play_rect = play_btn_image.get_rect(center=(win_width // 2 + 100, 610))
                    exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 610))
                    if play_rect.collidepoint(mouse):
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
                        menu()
                        return

        # Process voice commands
        try:
            command = command_queue.get_nowait()
            print(f"How to play screen received command: {command}")
            if command == "play":
                main()
                return
            elif command == "exit":
                menu()
                return
        except queue.Empty:
            pass

        window.blit(normal_background, (0, 0))
        play_rect = play_btn_image.get_rect(center=(win_width // 2 + 100, 610))
        exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 610))
        howto_rect = how_to_play_btn_image2.get_rect(center=(win_width // 2, 100))

        window.blit(how_to_play_image, (win_width // 2 - how_to_play_image.get_width() // 2, win_height // 2 - 250))
        window.blit(play_btn_image, play_rect.topleft)
        window.blit(exit_btn_image, exit_rect.topleft)
        window.blit(how_to_play_btn_image2, howto_rect.topleft)

        pygame.display.update()
        clock.tick(60)

# --- Main Game Loop ---
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
                pause_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and pause_btn_rect.collidepoint(event.pos) and game_started:
                    pause_game()

        # Process voice commands
        try:
            command = command_queue.get_nowait()
            print(f"Main loop received command: {command}")
            if command == "pause" and game_started:
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
                bird.sprite.alive = False
            if pygame.sprite.spritecollide(bird.sprite, pipes, False):
                bird.sprite.alive = False

        # Handle game over
        if not bird.sprite.alive and game_started:
            if score > best_score:
                best_score = score
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
                                score = 0
                                main()
                                return
                            elif exit_rect.collidepoint(mouse):
                                score = 0
                                game_stopped = True
                                menu()
                                return

                # Process voice commands
                try:
                    command = command_queue.get_nowait()
                    print(f"Game over screen received command: {command}")
                    if command == "play":
                        score = 0
                        main()
                        return
                    elif command == "exit":
                        score = 0
                        game_stopped = True
                        menu()
                        return
                except queue.Empty:
                    pass

                window.blit(current_background, (0, 0))
                pipes.draw(window)
                foods.draw(window)
                portal.draw(window)
                bird.draw(window)

                # Show game over panel
                window.blit(game_over_image, (win_width // 2 - game_over_image.get_width() // 2, win_height // 2 - 250))
                play_rect = play_btn_image.get_rect(center=(win_width // 2 + 100, 510))
                exit_rect = exit_btn_image.get_rect(center=(win_width // 2 - 100, 510))
                window.blit(play_btn_image, play_rect.topleft)
                window.blit(exit_btn_image, exit_rect.topleft)

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

        # Check for portal entry
        if game_started and pygame.sprite.spritecollide(bird.sprite, portal, True):
            available_moods = [i for i in range(4) if i != mood_state]
            mood_state = random.choice(available_moods)
            current_background = [normal_background, happy_background, sad_background, angry_background][mood_state]
            portal_active = False
            portal_spawn_score = None

        pygame.display.update()
        clock.tick(60)

# --- Main Menu Loop ---
def menu():
    global game_stopped
    game_stopped = True
    start_rect = start_btn_image.get_rect(center=(win_width // 2, 420))
    howto_rect = how_to_play_btn_image1.get_rect(center=(win_width // 2, 500))
    exit_rect = exit_btn_image.get_rect(center=(win_width // 2, 580))
    title_rect = title_image.get_rect(center=(win_width // 2, 110))

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
                        pygame.quit()
                        exit()

        # Process voice commands
        try:
            command = command_queue.get_nowait()
            print(f"Main menu received command: {command}")
            if command == "start":
                game_stopped = False
                main()
            elif command == "how to play":
                how_to_play_screen()
            elif command == "exit":
                pygame.quit()
                exit()
        except queue.Empty:
            pass

        window.blit(normal_background, (0, 0))
        window.blit(title_image, title_rect.topleft)
        window.blit(quickie_image, (win_width // 2 - 115, 130))
        window.blit(start_btn_image, start_rect.topleft)
        window.blit(how_to_play_btn_image1, howto_rect.topleft)
        window.blit(exit_btn_image, exit_rect.topleft)

        pygame.display.update()
        clock.tick(60)

# --- Launch the Game ---
menu()