import pygame
from pygame.math import Vector2
from settings import *
import ast
import GameLogicClassesAndHandlers


class Screen:
    """
    This is abstract class. Its purpose is to clarify all attributes and methods the screen should have in order to
    work properly with other screens.

    Attributes:
        screen_change (tuple): Contains info about changing the screen.

    Methods:
        handle_screen(TextHandler, pygame.surface.Surface, float): Deals with all action that takes places in a single
        frame of main pygame loop.
        handle_events(float, list): Handles player events. Should have an event or other condition that can change
        current screen.
        reset_next(): Sets screen_change parameter to (None, None, None).
        get_from_prev_screen(Any): Is used to pass any type of information to the next screen.
    """
    def __init__(self):
        """
        All screens should have "screen_change" attribute. It's a tuple containing three information:
        screen_change[0] - (bool), True if screen should be changed. False otherwise.
        screen_change[1] - (string), name of the next screen that should be displayed after the current one
                           (if screen_change[0] is True). ScreenHandler object is responsible for dealing with switching
                           the screens and supported screens are stored there in "available_screens" attribute.
        screen_change[2] - (any), any kind of information we want to pass to the next screen. For example game screen
                           can pass information about the score to the pause screen, so it can be displayed there.
        Parameters
        ---------
        :param screen_change: Contains information responsible for changing current screen.
        :type screen_change: tuple
        """
        self.screen_change = (None, None, None)

    def handle_screen(self, TextHandler, screen, dt):
        """
        This method handles all actions that happens in a single frame in a "while run" pygame loop. It includes screen
        logic as well as drawing objects.

        Args:
            TextHandler (GameLogicClassesAndHandlers.TextHandler): instance of TextHandler object. This parameter allows
            the screen to write things down and contain information such as font style and size.
            screen (pygame.surface.Surface): pygame screen that game screen is being drawn on.
            dt (float): Delta time in seconds since last frame.

        Returns:
            None: None
        """
        raise NotImplementedError()

    def handle_events(self, dt, events):
        """
        This method is responsible for handling all events that take place on the screen, such as pressing a key. This
        includes event that changes the scree, so "handle_events" should have action that updates "screen_change"
        attribute.

        Args:
            dt (float): Delta time in seconds since last frame.
            events (list): Events that happened in a single iteration of pygame "while run" loop - pygame.event.get().

        Returns:
            None: None
        """
        raise NotImplementedError()

    def reset_next(self):
        """
        This method sets the "screen_change" attribute to (None, None, None). It should be called after changing
        the screen, so it changes only once and awaits another action that will change the screen.

        Returns:
            None: None
        """
        raise NotImplementedError()

    def get_from_prev_screen(self, info):
        """
        This method gets some information (such as game score) from previous screen to the current one.

        Args:
            info (Any): Anything that is necessary from the previous screen.

        Returns:
            Any: Anything that is necessary from the previous screen.
        """
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
        self.difficulty = GameLogicClassesAndHandlers.DifficultyHandler()

    def create_init_obstacle(self):
        self.obstacle_handler.create_new_obstacle()
        self.initial_obstacle = True

    def change_path_perc(self, val):
        self.path_perc += val

    def handle_screen(self, TextHandler, screen, dt):
        screen.fill(color_palette['background'])
        self.player.draw_player(screen)
        self.player.draw_player_path(screen)
        if not self.initial_obstacle:
            self.create_init_obstacle()
        self.obstacle_handler.draw_obstacles(screen)
        self.obstacle_handler.move_all_obstacles(dt)
        self.obstacle_handler.generate_next()
        if self.obstacle_handler.delete_dead_obstacles():
            self.score += 1
        TextHandler.draw_text(screen, str(self.score), color_palette['text'], (width / 2, TextHandler.font_size))
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

        obstacles_original = pygame.Surface((width, height), pygame.SRCALPHA)
        for obstacle in self.obstacle_handler.obstacles.values():
            pygame.draw.polygon(obstacles_original, (0, 0, 255), obstacle.rotate_obstacle(obstacle.start_angle))
        obst = obstacles_original
        pos_blue = Vector2(width / 2, height / 2)
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
            f = open('scores.txt')
            s = f.read()
            f.close()
            scores = ast.literal_eval(s)
            if scores[self.difficulty.current_difficulty] < score:
                f = open('scores.txt', 'w')
                scores[self.difficulty.current_difficulty] = score
                f.write(str(scores))
                f.close()
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
                             'Best Scores': 'best_scores',
                             'Credits': 'credits',
                             }
        self.currently_chosen_index = 0
        self.currently_chosen = list(self.menu_options.keys())[self.currently_chosen_index]
        self.screen_change = (None, None, None)
        self.difficulty = difficulty_handler

    def handle_screen(self, TextHandler, screen, dt):
        screen.fill(color_palette['background'])
        text_pos = centre
        text_pos = text_pos[0], text_pos[1] - (TextHandler.font_size * len(self.menu_options.keys()))/2 \
                                + TextHandler.font_size/2
        for option in self.menu_options.keys():
            if option is self.currently_chosen:
                TextHandler.draw_text(screen, option, color_palette['selected text'], text_pos)
            else:
                TextHandler.draw_text(screen, option, color_palette['text'], text_pos)
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

    def handle_screen(self, TextHandler, screen, dt):
        screen.fill(color_palette['background'])
        text_pos = centre
        TextHandler.draw_text(screen, "Press 'Y' to resume game, press 'N' to go back to the menu.",
                              color_palette['text'], text_pos)

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

    def handle_screen(self, TextHandler, screen, dt):
        screen.fill(color_palette['background'])
        text_pos = centre
        text_pos = text_pos[0], text_pos[1] - (TextHandler.font_size * len(self.difficulty_handler.difficulties.keys()))/2 \
                                + TextHandler.font_size/2
        for difficulty in self.difficulty_handler.difficulties.keys():
            if difficulty is self.difficulty_handler.current_difficulty:
                TextHandler.draw_text(screen, difficulty, color_palette['selected text'], text_pos)
            else:
                TextHandler.draw_text(screen, difficulty, color_palette['text'], text_pos)
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

    def handle_screen(self, TextHandler, screen, dt):
        screen.fill(color_palette['background'])
        text_pos = centre
        TextHandler.draw_text(screen, f"You have lost. Your score is {self.score}. Press 'Y' to go back to the menu.",
                              color_palette['text'], text_pos)

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


class CreditsScreen(Screen):
    def __init__(self, credits_list):
        self.screen_change = (None, None, None)
        self.credits_list = credits_list

    def handle_screen(self, TextHandler, screen, dt):
        screen.fill(color_palette['background'])
        credits_list = ["Press 'Y' to go back"] + self.credits_list
        text_pos = centre
        text_pos = text_pos[0], text_pos[1] - (TextHandler.font_size * len(credits_list))/2 + TextHandler.font_size/2
        for text in credits_list:
            TextHandler.draw_text(screen, text, color_palette['text'], text_pos)
            text_pos = text_pos[0], text_pos[1] + TextHandler.font_size + 5

    def handle_events(self, dt, events):
        keys = pygame.key.get_pressed()
        for event in events:
            if pygame.KEYUP:
                if keys[pygame.K_y]:
                    self.screen_change = (True, 'menu', None)

    def reset_next(self):
        self.screen_change = (None, None, None)

    def get_from_prev_screen(self, info):
        return None


class BestScoreScreen(Screen):
    def __init__(self):
        self.screen_change = (None, None, None)
        f = open('scores.txt')
        self.scores = f.read()
        f.close()
        self.scores = ast.literal_eval(self.scores)

    def handle_screen(self, TextHandler, screen, dt):
        screen.fill(color_palette['background'])
        text_pos = centre
        text_pos = text_pos[0], text_pos[1] - (TextHandler.font_size * (len(credits_list)+2))/2 + TextHandler.font_size/2
        TextHandler.draw_text(screen, "Press 'Y' to go back", color_palette['text'], text_pos)
        text_pos = text_pos[0], text_pos[1] + TextHandler.font_size + 5
        TextHandler.draw_text(screen, "Best Scores:", color_palette['text'], text_pos)
        text_pos = text_pos[0], text_pos[1] + TextHandler.font_size + 5
        for difficulty, score in self.scores.items():
            TextHandler.draw_text(screen, f"{difficulty}: {score}", color_palette['text'], text_pos)
            text_pos = text_pos[0], text_pos[1] + TextHandler.font_size + 5

    def handle_events(self, dt, events):
        keys = pygame.key.get_pressed()
        for event in events:
            if pygame.KEYUP:
                if keys[pygame.K_y]:
                    self.screen_change = (True, 'menu', None)

    def reset_next(self):
        self.screen_change = (None, None, None)

    def update_best_scores(self):
        f = open('scores.txt')
        self.scores = f.read()
        f.close()
        self.scores = ast.literal_eval(self.scores)

    def get_from_prev_screen(self, info):
        self.update_best_scores()
