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
        reset_next(): Sets "screen_change" parameter to (None, None, None).
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
        """
        self.screen_change = (None, None, None)

    def handle_screen(self, text_handler, screen, dt):
        """
        This method handles all actions that happens in a single frame in a "while run" pygame loop. It includes screen
        logic as well as drawing objects.

        Args:
            text_handler (GameLogicClassesAndHandlers.TextHandler): instance of TextHandler object. This parameter allows
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
    """
    This is one of the most important class in the project. It combines information from Player class and
    ObstacleHandler class to create the game logic. This class also fills the role of game screen, so it does have
    all necessary Screen methods and screen_change attribute.

    Attributes:
        player (GameLogicClassesAndHandlers.Player): Instance of Player class. It contains all information about the
            player.
        obstacle_handler (GameLogicClassesAndHandlers.ObstacleHandler): Instance of ObstacleHandler object. It contains
            all information about current obstacles, can generate and draw new obstacles.
        path_perc (float): Percentage of the path that tells where the player is currently located in the relation to
            the path. Is used as argument passed to "move" method.
        initial_obstacle (bool): Logical value used to initialize the creation of the obstacles.
        screen_change (tuple): Screen class attribute.
        score (int): Score of the player. It is calculated based on the number of obstacles that reach the end.
        game_end (bool): Logical value that indicates whether the player has lost.
        difficulty (GameLogicClassesAndHandlers.DifficultyHandler): Instance of DifficultyHandler class. Contains all
            information needed to create new game.

    Methods:
        create_init_obstacle(): Initializes the process of generating obstacles.
        change_path_perc(val: float): Changes the player position by changing the "path_perc" attribute.
        handle_screen(text_handler: GameLogicClassesAndHandlers.TextHandler, screen: pygame.surface.Surface, dt: float):
            Deals with all action that takes places in a single frame of main pygame loop. This method must be
            implemented for all screens.
        handle_events(dt: float, events: list): Handles player events. Should have an event or other condition that can
        change current screen. This method must be implemented for all screens.
        reset_next(): Sets "screen_change" parameter to (None, None, None). This method must be implemented for all
            screens.
        restart_game(): Performs all actions necessary to consider the current instance of Game class to be "new".
        detect_collision(): Is responsible for collision logic.
        check_for_end(): Checks if a game ended, if yes performs all actions necessary at the end of the game.
        get_from_prev_screen(Any): Is used to pass any type of information to the next screen. This method must be
            implemented for all screens.
        change_game_settings(dict): Changes the game difficulty settings. The dict passed as an argument should be
            an attribute of DifficultyHandler object
    """
    def __init__(self, player, obstacle_handler):
        """
        __init__ method of Game class.

        Args:
            player (GameLogicClassesAndHandlers.Player): Instance of Player class. It contains all information about the
                player.
            obstacle_handler (GameLogicClassesAndHandlers.ObstacleHandler): Instance of ObstacleHandler object. It contains
                all information about current obstacles, can generate and draw new obstacles.
        """
        self.player = player
        self.obstacle_handler = obstacle_handler
        self.path_perc = 0
        self.initial_obstacle = False
        self.screen_change = (None, None, None)
        self.score = 0
        self.game_end = False
        self.difficulty = GameLogicClassesAndHandlers.DifficultyHandler()

    def create_init_obstacle(self):
        """
        Initializes the process of generating obstacles by creating the new obstacle. Changes "initial_obstacle" value
        to True, so the process is not repeated.

        Returns:
            None: None
        """
        self.obstacle_handler.create_new_obstacle()
        self.initial_obstacle = True

    def change_path_perc(self, val):
        """
        Changes value of "path_perc" attribute by value passed in the argument.

        Args:
            val (float): Value that is added to "path_perc" attribute.

        Returns:
            None: None
        """
        self.path_perc += val

    def handle_screen(self, text_handler, screen, dt):
        """
        Deals with all action that takes places in a single frame of main pygame loop. For details check comments in the
        code.

        Args:
            text_handler (GameLogicClassesAndHandlers.TextHandler): Instance of TextHandler class. Is used to deal with
                text.
            screen (pygame.surface.Surface): Screen that the object are being drawn on.
            dt (float): Delta time in seconds since last frame.

        Returns:
            None: None
        """
        # Fill the screen with the color specified in setting file.
        screen.fill(color_palette['background'])
        # Draw player related attributes.
        self.player.draw_player(screen)
        self.player.draw_player_path(screen)
        # Initialize the creation of obstacle in case it was not done yet.
        if not self.initial_obstacle:
            self.create_init_obstacle()
        # Perform obstacle related actions, such as drawing, generating, moving.
        self.obstacle_handler.draw_obstacles(screen)
        self.obstacle_handler.move_all_obstacles(dt)
        self.obstacle_handler.generate_next()
        # Deletion of obstacles that reached an end. Increasing player score in case obstacle was removed.
        if self.obstacle_handler.delete_dead_obstacles():
            self.score += 1
        # Draw player score
        text_handler.draw_text(screen, str(self.score), color_palette['text'], (width / 2, text_handler.font_size))
        # Check if the game should be finished.
        self.check_for_end()

    def handle_events(self, dt, events):
        """
        This method is responsible for handling all events that take place on the screen, such as pressing a key. This
        includes event that changes the scree, so "handle_events" should have action that updates "screen_change"
        attribute. For details check comments in the code.

        Args:
            dt (float): Delta time in seconds since last frame.
            events (list): Events that happened in a single iteration of pygame "while run" loop - pygame.event.get().

        Returns:
            None: None
        """
        keys = pygame.key.get_pressed()
        # Player moves are binded to right and left arrows.
        if keys[pygame.K_RIGHT]:
            self.change_path_perc(dt * self.player.player_speed)
            self.player.move(self.path_perc)
        if keys[pygame.K_LEFT]:
            self.change_path_perc(-dt * self.player.player_speed)
            self.player.move(self.path_perc)

        for event in events:
            if pygame.KEYUP:
                # Escape key changes the current screen to the pause screen.
                if keys[pygame.K_ESCAPE]:
                    self.screen_change = (True, 'pause', None)
                # Game can be restarted with 'r' key.
                if keys[pygame.K_r]:
                    self.restart_game()

    def reset_next(self):
        """
        This method sets the "screen_change" attribute to (None, None, None). It should be called after changing
        the screen, so it changes only once and awaits another action that will change the screen.

        Returns:
            None: None
        """
        self.screen_change = (None, None, None)

    def restart_game(self):
        """
        Performs all actions necessary to consider the current instance of Game class to be "new". This includes:

        Returns:
            None: None
        """
        self.player.is_alive = True
        self.player.player_position = self.player.move(0)
        self.obstacle_handler.obstacles = {}
        self.obstacle_handler.last_created_obstacle = None
        self.initial_obstacle = False
        self.path_perc = 0
        self.score = 0
        self.game_end = False

    def detect_collision(self):
        """
        Is responsible for collision logic. It uses "overlap" method of pygame.Mask object. In case the collision
        between player and obstacle happens, the "game_end" is set to True.

        Returns:
            None: None
        """
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
        """
        Check if game ended, based on "game_end" attribute. If yes, overwrites the file with best scores, restarts the
        game status and changes "screen_change", so the loosing screen can be displayed.

        Returns:
            None: None
        """
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
        """
        Gets information about game difficulty. This information is passed from menu screen. Menu screen gets this
        information from ChooseDifficultyScreen class.

        Args:
            info (GameLogicClassesAndHandlers.DifficultyHandler): Information about the game difficulty.

        Returns:
            None: None
        """
        if info:
            self.difficulty = info
            difficulty_dict = self.difficulty.difficulties[self.difficulty.current_difficulty]
            self.change_game_settings(difficulty_dict)

    def change_game_settings(self, settings_dict):
        """
        Restarts the game and changes the attributes of a player and obstacle handler in order to impact game
            difficulty.

        Args:
            settings_dict (dict): Dictionary containing all game difficulty info. Those dictionaries have specific
                format and are stored in DifficultyHandler properties.

        Returns:
            None: None
        """
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
        self.menu_options = {'Start Game': 'game',
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

    def handle_screen(self, text_handler, screen, dt):
        screen.fill(color_palette['background'])
        text_pos = centre
        text_pos = text_pos[0], text_pos[1] - (text_handler.font_size * len(self.difficulty_handler.difficulties.keys())) / 2 \
                                + text_handler.font_size / 2
        for difficulty in self.difficulty_handler.difficulties.keys():
            if difficulty is self.difficulty_handler.current_difficulty:
                text_handler.draw_text(screen, difficulty, color_palette['selected text'], text_pos)
            else:
                text_handler.draw_text(screen, difficulty, color_palette['text'], text_pos)
            text_pos = text_pos[0], text_pos[1] + text_handler.font_size

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
