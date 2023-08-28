import pygame
from pygame.math import Vector2

height, width = 1280, 720
screen = pygame.display.set_mode((height, width))
centre = screen.get_width() / 2, screen.get_height() / 2


class Screen:
    def __init__(self):
        self.screen_change = (None, None, None)

    def draw_screen(self, TextHandler, screen, dt):
        raise NotImplementedError()

    def handle_events(self, dt, events):
        raise NotImplementedError()

    def reset_next(self):
        raise NotImplementedError()

    def get_from_prev_screen(self, info):
        raise NotImplementedError()


class Game(Screen):
    def __init__(self, player, obstacle_handler):
        self.player = player
        self.obstacle_handler = obstacle_handler
        self.path_perc = 0
        self.initial_obstacle = False
        self.screen_change = (None, None, None)
        self.score = 0
        self.game_end = False
        self.difficulty = 'easy'

    def create_init_obstacle(self):
        self.obstacle_handler.create_new_obstacle()
        self.initial_obstacle = True

    def change_path_perc(self, val):
        self.path_perc += val

    def draw_screen(self, TextHandler, screen, dt):
        screen.fill("tomato")
        self.player.draw_player(screen)
        self.player.draw_player_path(screen)
        if not self.initial_obstacle:
            self.create_init_obstacle()
        self.obstacle_handler.draw_obstacles(screen)
        self.obstacle_handler.move_all_obstacles(dt)
        self.obstacle_handler.generate_next()
        if self.obstacle_handler.delete_dead_obstacles():
            self.score += 1
        TextHandler.draw_text(screen, str(self.score), 'purple', (100, 100))
        self.check_for_end()

    def handle_events(self, dt, events):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.change_path_perc(dt * self.player.player_speed)
            self.player.move(self.path_perc)
        if keys[pygame.K_LEFT]:
            self.change_path_perc(-dt * self.player.player_speed)
            self.player.move(self.path_perc)
        if keys[pygame.K_l]:
            self.screen_change = (True, 'menu', None)

        for event in events:
            if pygame.KEYUP:
                if keys[pygame.K_ESCAPE]:
                    self.screen_change = (True, 'pause', None)
                if keys[pygame.K_r]:
                    self.restart_game()

    def reset_next(self):
        self.screen_change = (None, None, None)

    def restart_game(self):
        self.player.is_alive = True
        self.player.player_position = self.player.move(0)
        self.obstacle_handler.obstacles = {}
        self.obstacle_handler.last_created_obstacle = None
        self.initial_obstacle = False
        self.path_perc = 0
        self.score = 0
        self.game_end = False

    def detect_collision(self):
        player_circle = pygame.Surface((2*self.player.radius, 2*self.player.radius), pygame.SRCALPHA)
        pygame.draw.circle(player_circle, [255, 255, 255], [self.player.radius, self.player.radius], self.player.player_radius)
        player_pos = Vector2(self.player.player_position)
        player_rect = player_circle.get_rect(center=player_pos)
        player_rect.center = player_pos

        obstacles_original = pygame.Surface((height, width), pygame.SRCALPHA)
        for obstacle in self.obstacle_handler.obstacles.values():
            pygame.draw.polygon(obstacles_original, (0, 0, 255), obstacle.rotate_obstacle(obstacle.start_angle))
        obst = obstacles_original
        pos_blue = Vector2(height / 2, width / 2)
        obstacle_rect = obst.get_rect(center=pos_blue)

        mask_obst = pygame.mask.from_surface(obst)
        mask_player = pygame.mask.from_surface(player_circle)

        offset_ = (obstacle_rect.x - player_rect.x), (obstacle_rect.y - player_rect.y)
        overlap_ = mask_player.overlap(mask_obst, offset_)

        if overlap_:
            self.game_end = True

    def check_for_end(self):
        if self.game_end:
            score = self.score
            self.restart_game()
            self.screen_change = (True, 'lost', score)

    def get_from_prev_screen(self, info):
        if info:
            self.difficulty = info
            difficulty_dict = self.difficulty.difficulties[self.difficulty.current_difficulty]
            self.change_game_settings(difficulty_dict)

    def change_game_settings(self, settings_dict):
        self.restart_game()
        # player settings
        self.player.radius = settings_dict['player']['radius']
        self.player.player_radius = settings_dict['player']['player_radius']
        self.player.curve_nr = settings_dict['player']['curve_nr']
        self.player.path_deviation = settings_dict['player']['path_deviation']
        self.player.player_speed = settings_dict['player']['player_speed']
        # obstacle_handler settings
        self.obstacle_handler.min_angle = settings_dict['obstacle_handler']['min_angle']
        self.obstacle_handler.max_angle = settings_dict['obstacle_handler']['max_angle']
        self.obstacle_handler.distance_between_obstacles = \
            settings_dict['obstacle_handler']['distance_between_obstacles']
        self.player.player_path = self.player.generate_player_path()


class Menu(Screen):
    def __init__(self, difficulty_handler):
        self.menu_options = {'Start New Game': 'game',
                             'Select Difficulty': 'difficulty_screen',
                             'Best Scores': 'other_action',
                             'Credits': 'other_action',
                             }
        self.currently_chosen_index = 0
        self.currently_chosen = list(self.menu_options.keys())[self.currently_chosen_index]
        self.screen_change = (None, None, None)
        self.difficulty = difficulty_handler

    def draw_screen(self, TextHandler, screen, dt):
        screen.fill('tomato')
        text_pos = centre
        text_pos = text_pos[0], text_pos[1] - (TextHandler.font_size * len(self.menu_options.keys()))/2 \
                                + TextHandler.font_size/2
        for option in self.menu_options.keys():
            if option is self.currently_chosen:
                TextHandler.draw_text(screen, option, 'purple', text_pos)
            else:
                TextHandler.draw_text(screen, option, 'red', text_pos)
            text_pos = text_pos[0], text_pos[1] + TextHandler.font_size

    def handle_events(self, dt, events):
        keys = pygame.key.get_pressed()
        for event in events:
            if pygame.KEYUP:
                if keys[pygame.K_UP]:
                    self.currently_chosen_index = (self.currently_chosen_index - 1) % len(self.menu_options)
                    self.currently_chosen = list(self.menu_options.keys())[self.currently_chosen_index]
                if keys[pygame.K_DOWN]:
                    self.currently_chosen_index = (self.currently_chosen_index+ 1) % len(self.menu_options)
                    self.currently_chosen = list(self.menu_options.keys())[self.currently_chosen_index]
                if keys[pygame.K_RETURN]:
                    self.screen_change = (True, self.menu_options[self.currently_chosen], self.difficulty)

    def reset_next(self):
        self.screen_change = (None, None, None)

    def get_from_prev_screen(self, info):
        self.difficulty = info


class PauseScreen(Screen):
    def __init__(self):
        self.screen_change = (None, None, None)

    def draw_screen(self, TextHandler, screen, dt):
        screen.fill("tomato")
        text_pos = centre
        TextHandler.draw_text(screen, "Press 'Y' to resume game, press 'N' to go back to the menu.", 'black', text_pos)

    def handle_events(self, dt, events):
        keys = pygame.key.get_pressed()
        for event in events:
            if pygame.KEYUP:
                if keys[pygame.K_y]:
                    self.screen_change = (True, 'game', None)
                if keys[pygame.K_n]:
                    self.screen_change = (True, 'menu', None)

    def reset_next(self):
        self.screen_change = (None, None, None)

    def get_from_prev_screen(self, info):
        return None


class ChooseDifficultyScreen(Screen):
    def __init__(self, difficulty_handler):
        self.difficulty_handler = difficulty_handler
        self.currently_chosen_index = list(self.difficulty_handler.difficulties.keys()).index(self.difficulty_handler.current_difficulty)
        self.screen_change = (None, None, None)

    def draw_screen(self, TextHandler, screen, dt):
        screen.fill('tomato')
        text_pos = centre
        text_pos = text_pos[0], text_pos[1] - (TextHandler.font_size * len(self.difficulty_handler.difficulties.keys()))/2 \
                                + TextHandler.font_size/2
        for difficulty in self.difficulty_handler.difficulties.keys():
            if difficulty is self.difficulty_handler.current_difficulty:
                TextHandler.draw_text(screen, difficulty, 'purple', text_pos)
            else:
                TextHandler.draw_text(screen, difficulty, 'red', text_pos)
            text_pos = text_pos[0], text_pos[1] + TextHandler.font_size

    def handle_events(self, dt, events):
        keys = pygame.key.get_pressed()
        for event in events:
            if pygame.KEYUP:
                if keys[pygame.K_UP]:
                    self.currently_chosen_index = (self.currently_chosen_index - 1) % len(self.difficulty_handler.difficulties.keys())
                    self.difficulty_handler.current_difficulty = list(self.difficulty_handler.difficulties.keys())[self.currently_chosen_index]
                if keys[pygame.K_DOWN]:
                    self.currently_chosen_index = (self.currently_chosen_index+ 1) % len(self.difficulty_handler.difficulties.keys())
                    self.difficulty_handler.current_difficulty = list(self.difficulty_handler.difficulties.keys())[self.currently_chosen_index]
                if keys[pygame.K_RETURN]:
                    self.screen_change = (True, 'menu', self.difficulty_handler)

    def reset_next(self):
        self.screen_change = (None, None, None)

    def get_from_prev_screen(self, info):
        return None


class LosingScreen(Screen):
    def __init__(self):
        self.screen_change = (None, None, None)
        self.score = None

    def draw_screen(self, TextHandler, screen, dt):
        screen.fill("tomato")
        text_pos = centre
        TextHandler.draw_text(screen, f"You have lost. Your score is {self.score}. Press 'Y' to go back to the menu.",
                              'black', text_pos)

    def handle_events(self, dt, events):
        keys = pygame.key.get_pressed()
        for event in events:
            if pygame.KEYUP:
                if keys[pygame.K_y]:
                    self.screen_change = (True, 'menu', None)

    def reset_next(self):
        self.screen_change = (None, None, None)

    def get_from_prev_screen(self, info):
        self.score = info
