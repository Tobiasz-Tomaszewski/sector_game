from ScreenClasses import *
from GameLogicClassesAndHandlers import *

pygame.init()

# Starting the mixer
pygame.mixer.init()

# Loading the song
pygame.mixer.music.load("assets/game_soundtrack.mp3")

# Setting the volume
pygame.mixer.music.set_volume(0.25)

# Start playing the song
pygame.mixer.music.play(loops=-1)

#global height, width
height, width = 1280, 720
screen = pygame.display.set_mode((height, width))
centre = screen.get_width() / 2, screen.get_height() / 2

clock = pygame.time.Clock()
running = True
dt = 0
player = Player(centre, 75, 15, curve_nr=8, path_deviation=10, player_speed=100)
obstacle_handler = ObstacleHandler(180, 320, 100)
game = Game(player, obstacle_handler)
text_handler = TextHandler(40)
pause = PauseScreen()
losing_screen = LosingScreen()
difficulty_handler = DifficultyHandler()
difficulty_screen = ChooseDifficultyScreen(difficulty_handler)
menu = Menu(difficulty_handler)
screen_handler = ScreenHandler(game, menu, pause, losing_screen, difficulty_screen)
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    screen_handler.draw_screen(text_handler, screen, dt)
    screen_handler.handle_events(dt, events)
    screen_handler.change_screen()
    if screen_handler.current_screen == game:
        screen_handler.game.detect_collision()

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000


pygame.quit()
