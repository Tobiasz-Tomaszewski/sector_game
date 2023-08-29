import settings
from ScreenClasses import *
from GameLogicClassesAndHandlers import *

pygame.init()

# Starting the mixer
pygame.mixer.init()

# Loading the song
pygame.mixer.music.load("game_soundtrack.mp3")

# Setting the volume
pygame.mixer.music.set_volume(0.25)

# Start playing the song
pygame.mixer.music.play(loops=-1)

width, height = 1280, 720
screen = pygame.display.set_mode((width, height))
centre = screen.get_width() / 2, screen.get_height() / 2

# Load sound images
sound_on_selected = pygame.image.load('Sound_icons/Sound_on_selected.png').convert_alpha()
sound_on_not_selected = pygame.image.load('Sound_icons/Sound_on_not_selected.png').convert_alpha()
sound_off_selected = pygame.image.load('Sound_icons/Sound_off_selected.png').convert_alpha()
sound_off_not_selected = pygame.image.load('Sound_icons/Sound_off_not_selected.png').convert_alpha()

sound_on_selected_rect = sound_on_selected.get_rect()
sound_on_selected_rect.topleft = (0, 0)
sound_on_not_selected_rect = sound_on_not_selected.get_rect()
sound_on_not_selected_rect.topleft = (0, 0)
sound_off_selected_rect = sound_off_selected.get_rect()
sound_off_selected_rect.topleft = (0, 0)
sound_off_not_selected_rect = sound_off_not_selected.get_rect()
sound_off_not_selected_rect.topleft = (0, 0)

clock = pygame.time.Clock()
running = True
music_play = True
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
credits_screen = CreditsScreen(settings.credits_list)
best_scores_screen = BestScoreScreen()
screen_handler = ScreenHandler(game,
                               menu,
                               pause,
                               losing_screen,
                               difficulty_screen,
                               credits_screen,
                               best_scores_screen)
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if 0 <= mouse[0] <= 75 and 0 <= mouse[1] <= 75 and music_play:
                pygame.mixer.music.pause()
                music_play = False
            elif 0 <= mouse[0] <= 75 and 0 <= mouse[1] <= 75 and (not music_play):
                pygame.mixer.music.unpause()
                music_play = True

    screen_handler.draw_screen(text_handler, screen, dt)
    screen_handler.handle_events(dt, events)
    screen_handler.change_screen()
    if screen_handler.current_screen == game:
        screen_handler.game.detect_collision()

    mouse = pygame.mouse.get_pos()

    if 0 <= mouse[0] <= 75 and 0 <= mouse[1] <= 75 and music_play:
        screen.blit(sound_on_selected, sound_on_selected_rect)
    elif 0 <= mouse[0] <= 75 and 0 <= mouse[1] <= 75 and (not music_play):
        screen.blit(sound_off_selected, sound_off_selected_rect)
    elif music_play:
        screen.blit(sound_on_not_selected, sound_on_not_selected_rect)
    elif not music_play:
        screen.blit(sound_off_not_selected, sound_off_not_selected_rect)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000


pygame.quit()
