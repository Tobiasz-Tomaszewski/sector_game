import pygame
import math
import numpy as np
from numpy import random
from settings import *


class Player:
    """
    This is player object. It contains all information about the player (such as way they move or alive status) and
    methods related to player behaviour.

    Attributes:
        centre (tuple): The centre of the rotation of the player. It should be the centre of the screen.
        radius (float): The radius of rotation.
        player_radius (float): The radius of a player (player is a circle).
        curve_nr (int, optional): Parameter of a player path. Move curves means more sin waves in the path. Default
        is 0.
        path_deviation (float, optional): Parameter of a player path. Real distance of a player from the center is equal
        to player_radius + sin(some_angle) * path_deviation. Default is 0.
        player_path_resolution (int, optional): Path is being described as a curve
        [0, player_path_resolution] -> player_path
        player_speed (int): Player speed, it is being multiplied by delta time in seconds since last frame.
        is_alive (bool): Indicator whether the player is alive.
        player_path (list[tuple[float, float]]): Approximation of a path that contains possible player positions.
        player_position (tuple): player position

    Methods:
        generate_player_path(): Generates approximation of player path as a list of tuples.
        move(N: float): Changes and returns player_position based on curve [0, player_path_resolution] -> player_path.
        draw_player(screen: pygame.surface.Surface): Draws a player on a provided screen.
        draw_player_path(screen: pygame.surface.Surface): Draws approximation of player path on a provided screen.
    """
    def __init__(self, centre, radius, player_radius, curve_nr=0, path_deviation=0,
                 player_path_resolution=1000, player_speed=40):
        """
        __init__ method of a Player class, it only sets up parameters.

        Args:
            centre (tuple): The center of rotation for the player, typically the center of the screen.
            radius (float): The radius of rotation.
            player_radius (float): The radius of the player, represented as a circle.
            curve_nr (int): A parameter that affects the player's path. Higher values result in more sinusoidal curves.
                            Must be greater than or equal to 0.
            path_deviation (int, optional): A parameter affecting the player's path. The actual distance from the center
                                            is player_radius + sin(some_angle) * path_deviation. Default is 0.
            player_path_resolution (int): Resolution for describing the player's path as a
                                          curve [0, player_path_resolution].
            player_speed (int): The player's speed, multiplied by the delta time in seconds since the last frame.
        """
        self.radius = radius
        self.player_radius = player_radius
        self.centre = centre
        self.is_alive = True
        self.curve_nr = curve_nr
        self.path_deviation = path_deviation
        self.player_path_resolution = player_path_resolution
        self.player_path = self.generate_player_path()
        self.player_position = self.move(0)
        self.player_speed = player_speed

    @staticmethod
    def __polar_to_cartesian(coordinates):
        """
        Simple method to transform polar coordinates to cartesian coordinates.

        Args:
            coordinates (tuple): Coordinates in polar coordinate system.

        Returns:
            tuple: Coordinates in cartesian coordinate system.
        """
        x = coordinates[0] * math.cos(coordinates[1])
        y = coordinates[0] * math.sin(coordinates[1])
        return x, y

    def generate_player_path(self):
        """
        Uses "move" method to create approximation of player path that can be drawn later.

        Returns:
            list[tuple[float, float]]: Path of the player represented as list of tuples.
        """
        player_path = [self.move(i) for i in range(self.player_path_resolution)]
        return player_path

    def move(self, N):
        """
        This method calculates the position of a player for any given float "N" working with mod player_path_resolution
        arithmetics. Player position can be represented as a point on a curve. This method updates player_position as
        well as returns it.

        Args:
            N (float): Point from domain of a curve.

        Returns:
            tuple: New player position in cartesian coordinates.
        """
        N = N % self.player_path_resolution
        phi = 2 * math.pi * (N / self.player_path_resolution)
        r = self.radius + math.sin(self.curve_nr * phi) * self.path_deviation
        player_pos = self.__polar_to_cartesian((r, phi))
        player_pos = player_pos[0] + self.centre[0], player_pos[1] + self.centre[1]
        self.player_position = player_pos
        return self.player_position

    def draw_player(self, screen):
        """
        This method draws player (circle) on a pygame surface.

        Args:
            screen (pygame.surface.Surface): pygame surface to draw on.

        Returns:
            None: None
        """
        pygame.draw.circle(screen, color_palette['player'], self.player_position, self.player_radius)

    def draw_player_path(self, screen):
        """
        This method draws player path on a pygame surface.
        :param screen: pygame surface to draw on.
        :type screen: pygame.surface.Surface
        :return: None
        :rtype: None
        """
        pygame.draw.polygon(screen, color_palette['text'], self.player_path, width=1)


class Obstacle:
    """
    Obstacle object represents a single obstacle in a game. Single obstacle is just a sector of a ring. This class
    contains all necessary information needed for creation of such sector, moving it and checking weather it should
    still exist.

    Attributes:
        inner_radius (float): Inner radius of a circle inside the ring - initialized with corner of the screen.
        outer_radius (float): Outer radius of a circle outside the ring - initializes with corner of the screen plus
                              difference between radiuses.
        start_angle (float): Angle of a rotation of the obstacle.
        angle (float): Angle of a sector of an obstacle ring in degrees.
        speed (int, optional): Speed of an obstacle, later multiplied by dt.
        is_alive (bool): Indicator whether the obstacle is alive.

    Methods:
        create_polygon_points(radius: float): Creates list of a points from sector of a circle. Later used to generate
                                              whole obstacle as polygon.
        create_sector_of_the_ring_points(): Creates and returns an obstacle as list of points of some polygon.
        move_obstacle(dt: float): Moves obstacle closer to the center, depends on dt.
        rotate_obstacle(rotation_angle: float): Rotates obstacle (list of points) and returns new polygon.
        draw_obstacle(screen: pygame.surface.Surface): Draws obstacle on a provided pygame screen.
        update_alive_status(): Updates is_alive parameter of obstacle. Dead obstacle should be removed from the memory.
    """
    def __init__(self, start_angle, angle, speed=100):
        """
        __init__ function of a class, it sets up all the parameters.

        Args:
            start_angle (float): Angle (in degrees) of rotation of the obstacle. It should be remembered that Y-axis of
            a screen is "upside down" compared to traditional coordinate system.
            angle (float): Angle (in degrees) of a sector of a ring.
            speed (int): Speed of an obstacle. Later multiplied by dt.

        Returns:
            None
        """
        # Obstacle will start on the edge of the screen.
        self.inner_radius = math.sqrt((centre[0])**2 + (centre[1])**2)
        self.outer_radius = math.sqrt((centre[0])**2 + (centre[1])**2) + 10
        self.start_angle = start_angle
        self.angle = angle
        self.centre = centre
        self.speed = speed
        self.is_alive = True

    def create_polygon_points(self, radius):
        """
        Method used to generate and return approximation of a circle. Center of a circle is object attribute for centre.

        Args:
            radius (float): Radius of generated circle.

        Returns:
            list[tuple[float, float]]: list of points from circle.
        """
        polygon_points = []
        for n in range(0, int(self.angle)):
            x = self.centre[0] + int(radius * math.cos(n * math.pi / 180))
            y = self.centre[1] + int(radius * math.sin(n * math.pi / 180))
            polygon_points.append((x, y))
        return polygon_points

    def create_sector_of_the_ring_points(self):
        """
        This method uses create_polygon_points() method to generate an approximation of sector of a ring as a list of
        tuples.

        Returns:
            list[tuple[float, float]]: Approximation of a sector of a ring - our obstacle.
        """
        outer_points = self.create_polygon_points(self.outer_radius)
        inner_points = self.create_polygon_points(self.inner_radius)[::-1]
        points = outer_points + inner_points + [outer_points[0]]
        return points

    def move_obstacle(self, dt):
        """
        Method used to move an obstacle based on speed attribute and dt.

        Args:
            dt (float): Delta time in seconds since last frame.

        Returns:
            None: None
        """
        self.inner_radius -= self.speed * dt
        self.outer_radius -= self.speed * dt

    def rotate_obstacle(self, rotation_angle):
        """
        Rotates obstacle (list of points) and returns new polygon as list of tuples. It should be remembered that Y-axis
        of pygame screen is "upside down" compared to traditional coordinates system.

        Args:
            rotation_angle (float): Angle (in degrees) of rotation.

        Returns:
            list[tuple[float, float]]: Rotated obstacle
        """
        points_to_be_rotated = self.create_sector_of_the_ring_points()
        points_to_be_rotated = [(x - self.centre[0], y - self.centre[1]) for x, y in points_to_be_rotated]
        rotated_points = []
        rotation_angle = rotation_angle * (math.pi / 180)  # change angle from degrees to radians
        sin_ = math.sin(rotation_angle)
        cos_ = math.cos(rotation_angle)
        rotation_matrix = np.array([[cos_, -sin_],
                                    [sin_, cos_]])
        for point in points_to_be_rotated:
            rotated_points.append(tuple(np.dot(rotation_matrix, np.array(point))))
        rotated_points = [(x + self.centre[0], y + self.centre[1]) for x, y in rotated_points]
        return rotated_points

    def draw_obstacle(self, screen):
        """
        Draws obstacle on a provided pygame screen.

        Args:
            screen (pygame.surface.Surface): Screen that obstacle is being drawn on.

        Returns:
            None: None
        """
        self.update_alive_status()
        if self.is_alive:
            pygame.draw.polygon(screen, color_palette['obstacle'], self.rotate_obstacle(self.start_angle))

    def update_alive_status(self):
        """
            Check whether the radius of inner obstacle is lesser than zero, if yes, changes the "is_alive" parameter to
            True

            Returns:
                None: None
        """
        if self.inner_radius < 0:
            self.is_alive = False


class ObstacleHandler(Obstacle):
    """
    Class that contain knowledge about all obstacles and can deal with multiple obstacles at the same time.

    Attributes:
        obstacles (dict): Dictionary that contains all the obstacles that are currently in play.
        min_angle (float): Minimal angle (in degrees) of a randomly generated obstacle.
        max_angle (float): Max angle (in degrees) of a randomly generated obstacle.
                           distance_between_obstacles (int, optional): Distance between two obstacles in pixels.
        last_created_obstacle (str): Name of the obstacle that was created last.
        distance_between_obstacles (int): Distance between two obstacles in pixels.

    Methods:
        add_obstacle(obstacle_name: str, obstacle: Obstacle): Adds obstacle to the "obstacles" dict.
        draw_obstacles(screen: pygame.surface.Surface): Draws all obstacles contained in "obstacles" dict.
        delete_obstacle(obstacle_name: str): Deletes the obstacle from "obstacles" dict based on a name.
        create_available_name(): Creates available name for the new obstacle.
        create_new_obstacle(): Creates new obstacle.
        move_all_obstacles(dt: float): Moves all obstacles closer to the centre.
        generate_next(): Calls "create_new_obstacle" method if obstacles are far enough from each other.
        delete_dead_obstacles(): Checks "obstacles" dict for all dead obstacles and deletes them using "delete_obstacle"
                                 method.
    """
    def __init__(self, min_angle, max_angle, distance_between_obstacles=400):
        """
        __init__ method of ObstacleHandler.

        Args:
            min_angle (float): Minimal angle (in degrees) of a randomly generated obstacle.
            max_angle (float): Max angle (in degrees) of a randomly generated obstacle.
            distance_between_obstacles (int, optional): Distance between two obstacles in pixels.

        Returns:
            None: None
        """
        self.obstacles = {}
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.last_created_obstacle = None
        self.distance_between_obstacles = distance_between_obstacles

    def add_obstacle(self, obstacle_name, obstacle):
        """
        Adds new obstacle to the "obstacles" attribute.

        Args:
            obstacle_name (str): Name of the obstacle.
            obstacle (Obstacle): Obstacle that is being added.

        Returns:
            None: None
        """
        self.obstacles[obstacle_name] = obstacle

    def draw_obstacles(self, screen):
        """
        Draws all obstacles from "obstacles" attribute on a provided screen.

        Args:
            screen (pygame.surface.Surface): Pygame screen that obstacle is being drawn on.

        Returns:
            None: None
        """
        for obstacle in self.obstacles.values():
            obstacle.draw_obstacle(screen)

    def delete_obstacle(self, obstacle_name):
        """
        Deletes obstacle from "obstacles" attribute based on a name.

        Args:
            obstacle_name (str): Name of the obstacle that is being deleted.

        Returns:
            None: None
        """
        return self.obstacles.pop(obstacle_name)

    def create_available_name(self):
        """
        Creates new name for the obstacle. New name is the smallest number (starts from 0) that does not exist yet in
        "obstacles" attribute, converted to the string.

        Returns:
            str: Available name for the new obstacle.
        """
        current_indexes = sorted(int(x) for x in self.obstacles.keys())
        all_indexes = [x for x in range(len(self.obstacles))]
        zipped = zip(current_indexes, all_indexes)
        unused_indexes = [y for x, y in zipped if x != y]
        if unused_indexes:
            return str(min(unused_indexes))
        if not self.obstacles:
            return '0'
        return str(len(self.obstacles))

    def create_new_obstacle(self):
        """
        Initializes instance of Obstacle class. Rotation angle is random, angle of obstacle is random, but no lesser
        than "min_angle" attribute and no bigger than "max_angle" attribute. The method calls "add_obstacle()" method to
        create new obstacle with name created by "create_available_name()" method. It also updates the
        "last_created_obstacle" attribute.

        Returns:
            None: None
        """
        start_angle = random.uniform(low=0, high=360)
        angle = random.uniform(low=self.min_angle, high=self.max_angle)
        name = self.create_available_name()
        self.add_obstacle(name, Obstacle(start_angle, angle))
        self.last_created_obstacle = name

    def move_all_obstacles(self, dt):
        """
        Moves all obstacles in the "obstacles" attribute using "move()" method.

        Returns:
            None: None
        """
        for obstacle in self.obstacles.values():
            obstacle.move_obstacle(dt)

    def generate_next(self):
        """
            Check whether the distance between last created obstacle and the corner of the screen is bigger or equal to
            "distance_between_obstacles" attribute. If yes, calls "create_new_obstacle()" method.

        Returns:
            None: None
        """
        if (self.obstacles[self.last_created_obstacle].outer_radius <
                math.sqrt((centre[0])**2 + (centre[1])**2) - self.distance_between_obstacles):
            self.create_new_obstacle()

    def delete_dead_obstacles(self):
        """
        Deletes all dead obstacles from "obstacles" attribute using "delete_obstacle()" method.

        Returns:
            bool: Information whether some obstacle has been deleted.
        """
        to_delete = []
        for name, obstacle in self.obstacles.items():
            if not obstacle.is_alive:
                to_delete.append(name)
        for dead in to_delete:
            self.delete_obstacle(dead)
        if to_delete:
            return True
        else:
            return False


class DifficultyHandler:
    """
    Class that contains information about currently selected difficulty of the game, as well as all the possible game
    difficulty settings.

    Attributes:
        current_difficulty (str): Name of the currently chosen difficulty.
        difficulties dict: Dictionary of all possible difficulties. Key is the name (str) and value is
                           a property (dict).

    Methods:
        easy_difficulty (property): Dict containing all information needed to generate game on easy difficulty.
        medium_difficulty (property): Dict containing all information needed to generate game on medium difficulty.
        hard_difficulty (property): Dict containing all information needed to generate game on hard difficulty.
        hard_difficulty (property): Dict containing all information needed to generate game on insane difficulty.
    """
    def __init__(self):
        """
        __init__ method for DIfficultyHandler class.

        Returns:
            None: None
        """
        self.current_difficulty = 'easy'
        self.difficulties = {'easy': self.easy_difficulty,
                             'medium': self.medium_difficulty,
                             'hard': self.hard_difficulty,
                             'insane': self.insane_difficulty
                             }

    @property
    def easy_difficulty(self):
        """
        Used to generate easy difficulty settings dict.

        Returns:
            dict: Dict containing easy mode settings.
        """
        easy_difficulty_dict = {'player': {'radius': 100,
                                           'player_radius': 15,
                                           'curve_nr': 0,
                                           'path_deviation': 0,
                                           'player_speed': 400},
                                'obstacle_handler': {'min_angle': 45,
                                                     'max_angle': 270,
                                                     'distance_between_obstacles': 200}}
        return easy_difficulty_dict

    @property
    def medium_difficulty(self):
        """
        Used to generate medium difficulty settings dict.

        Returns:
            dict: Dict containing medium mode settings.
        """
        medium_difficulty_dict = {'player': {'radius': 125,
                                             'player_radius': 15,
                                             'curve_nr': 6,
                                             'path_deviation': 20,
                                             'player_speed': 500},
                                  'obstacle_handler': {'min_angle': 90,
                                                       'max_angle': 300,
                                                       'distance_between_obstacles': 150}}
        return medium_difficulty_dict

    @property
    def hard_difficulty(self):
        """
        Used to generate hard difficulty settings dict.

        Returns:
            dict: Dict containing hard mode settings.
        """
        hard_difficulty_dict = {'player': {'radius': 75,
                                           'player_radius': 15,
                                           'curve_nr': 8,
                                           'path_deviation': 10,
                                           'player_speed': 1000},
                                'obstacle_handler': {'min_angle': 180,
                                                     'max_angle': 320,
                                                     'distance_between_obstacles': 100}}
        return hard_difficulty_dict

    @property
    def insane_difficulty(self):
        """
        Used to generate insane difficulty settings dict.

        Returns:
            dict: Dict containing insane mode settings.
        """
        insane_difficulty_dict = {'player': {'radius': 150,
                                             'player_radius': 10,
                                             'curve_nr': 30,
                                             'path_deviation': 20,
                                             'player_speed': 1500},
                                  'obstacle_handler': {'min_angle': 200,
                                                       'max_angle': 320,
                                                       'distance_between_obstacles': 90}}
        return insane_difficulty_dict

    def change_current_difficulty(self, new_difficulty):
        """
        Used to change the "current_difficulty" attribute.

        Args:
            new_difficulty (dict): New dict with difficulty settings. Must be in the same format as available ones.

        Returns:
            None: None
        """
        self.current_difficulty = new_difficulty


class TextHandler:
    """
    Simple class that is able to write on a screen.

    Attributes:
        font_size (int): Size of a font in pixels.
        font (pygame.font.SysFont, optional): Font to that text is being writen in. Default - comicans.

    Methods:
        draw_text(screen: pygame.surface.Surface, text: str, text_col: tuple, text_position: tuple): Writes text on a
                 provided screen with provided parameters.
    """
    def __init__(self, font_size, font_name='comicsans'):
        """
        __init__ method for TextHandler class.

        Args:
            font_size (int): Size of a font in pixels.
            font_name (str, optional): Font to that text is being writen in. Default - comicans.

        Returns:
            None: None
        """
        self.font_size = font_size
        self.font = pygame.font.SysFont(font_name, self.font_size)

    def draw_text(self, screen, text, text_col, text_position):
        """
        Writes text on a provided screen.

        Args:
            screen (pygame.surface.Surface): Pygame screen that text is being drawn onto.
            text (str): Text that is being drawn.
            text_col (tuple): Color of the text provided in RGB as tuple.
            text_position (tuple): Center position of text that is being drawn.
        """
        text = self.font.render(text, True, text_col)
        text_rect = text.get_rect(center=text_position)
        screen.blit(text, text_rect)


class ScreenHandler:
    """
    ScreenHandler is class that takes care about displaying the proper game screen. It contains knowledge about all
    possible screens, current screen and is responsible for executing its methods.

    Attributes:
        game (ScreenClasses.Game): Instance of a Game class.
        menu (ScreenClasses.Menu): Instance of a Menu class.
        pause (ScreenClasses.PauseScreen): Instance of a PauseScreen class.
        lost (ScreenClasses.LosingScreen): Instance of a LosingScreen class.
        credits (ScreenClasses.CreditsScreen): Instance of a CreditsScreen class.
        current_screen (ScreenClasses.Screen): Current screen. Initial screen is menu.
        difficulty_screen (ScreenClasses.ChooseDifficultyScreen): Instance of a ChooseDifficultyScreen class.
        best_scores (ScreenClasses.BestScoreScreen): Instance of a BestScoreScreen class.
        available_screens (dict): Dictionary containing all possible game screens. Keys of the dict are strings
            representing the name of the screen. It is extremely important that while changing the screen,
            screen_change[1] value exists in this dictionary.

    Methods:
        handle_screen(text_handler: TextHandler, screen: pygame.surface.Surface, dt: float): Executes "handle_screen"
            method of the current screen.
        handle_events(dt: float, events: list): Executes "handle_events" method of the current screen.
        change_screen(): Executes "change_screen" method of the current screen.
    """
    def __init__(self, game, menu, pause, lost, difficulty_screen, credits_screen, best_scores_screen):
        """
        __init__ method of ScreenHandler class.

        Args:
            game (ScreenClasses.Game): Instance of a Game class.
            menu (ScreenClasses.Menu): Instance of a Menu class.
            pause (ScreenClasses.PauseScreen): Instance of a PauseScreen class.
            lost (ScreenClasses.LosingScreen): Instance of a LosingScreen class.
            difficulty_screen (ScreenClasses.ChooseDifficultyScreen): Instance of a ChooseDifficultyScreen class.
            credits_screen (ScreenClasses.CreditsScreen): Instance of a CreditsScreen class.
            best_scores_screen (ScreenClasses.BestScoreScreen): Instance of a BestScoreScreen class.

        Returns:
            None: None
        """
        self.game = game
        self.menu = menu
        self.pause = pause
        self.lost = lost
        self.credits = credits_screen
        self.current_screen = menu
        self.difficulty_screen = difficulty_screen
        self.best_scores = best_scores_screen
        self.available_screens = {'game': self.game,
                                  'menu': self.menu,
                                  'pause': self.pause,
                                  'lost': self.lost,
                                  'difficulty_screen': self.difficulty_screen,
                                  'credits': self.credits,
                                  'best_scores': self.best_scores
                                  }

    def handle_screen(self, text_handler, screen, dt):
        """
        Executes "handle_screen" method of the current screen.

        Args:
            text_handler (TextHandler): Instance of TextHandler class. Is used to write text on screen.
            screen (pygame.surface.Surface): Screen that everything is being drawn on.
            dt (float): Delta time in seconds since last frame.

        Returns:
            None: None
        """
        self.current_screen.handle_screen(text_handler, screen, dt)

    def handle_events(self, dt, events):
        """
        Executes "handle_events" method of the current screen.

        Args:
            dt (float): Delta time in seconds since last frame.
            events (list): Events that happened in a single iteration of pygame "while run" loop - pygame.event.get().

        Returns:
            None: None
        """
        self.current_screen.handle_events(dt, events)

    def change_screen(self):
        """
        Changes the current screen if current_screen.screen_change[0] is True. It also is responsible for passing any
        information to the next screen.

        Returns:
            None: None
        """
        if self.current_screen.screen_change[0]:
            next_screen = self.available_screens[self.current_screen.screen_change[1]]
            pass_from_prev_screen = self.current_screen.screen_change[2]
            self.current_screen.reset_next()
            self.current_screen = next_screen
            self.current_screen.get_from_prev_screen(pass_from_prev_screen)
