import pygame
import math
import numpy as np
from numpy import random

height, width = 1280, 720
screen = pygame.display.set_mode((height, width))
centre = screen.get_width() / 2, screen.get_height() / 2

class Player:
    def __init__(self, centre, radius, player_radius, curve_nr=0, path_deviation=0,
                 player_path_resolution=100, player_speed = 40):
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
    def _polar_to_cartesian(coordinates):
        x = coordinates[0] * math.cos(coordinates[1])
        y = coordinates[0] * math.sin(coordinates[1])
        return x, y

    def generate_player_path(self):
        player_path = [self.move(i) for i in range(self.player_path_resolution)]
        return player_path

    def move(self, N):
        N = N % self.player_path_resolution
        phi = 2 * math.pi * (N / self.player_path_resolution)
        r = self.radius + math.sin(self.curve_nr * phi) * self.path_deviation
        player_pos = self._polar_to_cartesian((r, phi))
        player_pos = player_pos[0] + self.centre[0], player_pos[1] + self.centre[1]
        self.player_position = player_pos
        return self.player_position

    def draw_player(self, screen):
        pygame.draw.circle(screen, 'yellow', self.player_position, self.player_radius)

    def draw_player_path(self, screen):
        pygame.draw.polygon(screen, 'black', self.player_path, width=1)


class Obstacle:
    def __init__(self, start_angle, angle, speed=100):
        # Obstacle will start on the edge of the screen.
        self.inner_radius = math.sqrt((centre[0])**2 + (centre[1])**2)
        self.outer_radius = math.sqrt((centre[0])**2 + (centre[1])**2) + 10
        self.start_angle = start_angle
        self.angle = angle
        self.centre = centre
        self.speed = speed
        self.is_alive = True

    def create_polygon_points(self, radius):
        polygon_points = []
        for n in range(0, int(self.angle)):
            x = self.centre[0] + int(radius * math.cos(n * math.pi / 180))
            y = self.centre[1] + int(radius * math.sin(n * math.pi / 180))
            polygon_points.append((x, y))
        return polygon_points

    def create_sector_of_the_ring_points(self):
        outer_points = self.create_polygon_points(self.outer_radius)
        inner_points = self.create_polygon_points(self.inner_radius)[::-1]
        points = outer_points + inner_points + [outer_points[0]]
        return points

    def move_obstacle(self, dt):
        self.inner_radius -= self.speed * dt
        self.outer_radius -= self.speed * dt

    def rotate_obstacle(self, rotation_angle):
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
        self.update_alive_status()
        if self.is_alive:
            pygame.draw.polygon(screen, 'blue', self.rotate_obstacle(self.start_angle))

    def update_alive_status(self):
        if self.inner_radius < 0:
            self.is_alive = False


class ObstacleHandler(Obstacle):
    def __init__(self, min_angle, max_angle, distance_between_obstacles=400):
        self.obstacles = {}
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.last_created_obstacle = None
        self.distance_between_obstacles = distance_between_obstacles

    def add_obstacle(self, obstacle_name, obstacle):
        self.obstacles[obstacle_name] = obstacle

    def draw_obstacles(self, screen):
        for obstacle in self.obstacles.values():
            obstacle.draw_obstacle(screen)

    def delete_obstacle(self, obstacle_name):
        return self.obstacles.pop(obstacle_name)

    def create_available_name(self):
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
        start_angle = random.uniform(low=0, high=360)
        angle = random.uniform(low=self.min_angle, high=self.max_angle)
        name = self.create_available_name()
        self.add_obstacle(name, Obstacle(start_angle, angle))
        self.last_created_obstacle = name

    def move_all_obstacles(self, dt):
        for obstacle in self.obstacles.values():
            obstacle.move_obstacle(dt)

    def generate_next(self):
        if (self.obstacles[self.last_created_obstacle].outer_radius <
                math.sqrt((centre[0])**2 + (centre[1])**2) - self.distance_between_obstacles):
            self.create_new_obstacle()

    def delete_dead_obstacles(self):
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
    def __init__(self):
        self.current_difficulty = 'easy'
        self.difficulties = {'easy': self.easy_difficulty,
                             'medium': self.medium_difficulty,
                             'hard': self.hard_difficulty}

    @property
    def easy_difficulty(self):
        easy_difficulty_dict = {'player': {'radius': 100,
                                           'player_radius': 15,
                                           'curve_nr': 0,
                                           'path_deviation': 0,
                                           'player_speed': 40},
                                'obstacle_handler': {'min_angle': 45,
                                                     'max_angle': 270,
                                                     'distance_between_obstacles': 200}}
        return easy_difficulty_dict

    @property
    def medium_difficulty(self):
        medium_difficulty_dict = {'player': {'radius': 125,
                                             'player_radius': 15,
                                             'curve_nr': 6,
                                             'path_deviation': 20,
                                             'player_speed': 50},
                                  'obstacle_handler': {'min_angle': 90,
                                                       'max_angle': 300,
                                                       'distance_between_obstacles': 150}}
        return medium_difficulty_dict

    @property
    def hard_difficulty(self):
        hard_difficulty_dict = {'player': {'radius': 75,
                                           'player_radius': 15,
                                           'curve_nr': 8,
                                           'path_deviation': 10,
                                           'player_speed': 100},
                                'obstacle_handler': {'min_angle': 180,
                                                     'max_angle': 320,
                                                     'distance_between_obstacles': 100}}
        return hard_difficulty_dict

    def change_current_difficulty(self, new_difficulty):
        self.current_difficulty = new_difficulty


class TextHandler:
    def __init__(self, font_size, font_name='comicsans'):
        self.font_size = font_size
        self.font = pygame.font.SysFont(font_name, self.font_size)

    def draw_text(self, screen, text, text_col, text_position):
        text = self.font.render(text, True, text_col)
        text_rect = text.get_rect(center=text_position)
        screen.blit(text, text_rect)


class ScreenHandler:
    def __init__(self, game, menu, pause, lost):
        self.game = game
        self.menu = menu
        self.pause = pause
        self.lost = lost
        self.current_screen = menu
        self.available_screens = {'game': self.game,
                                  'menu': self.menu,
                                  'pause': self.pause,
                                  'lost': self.lost}

    def draw_screen(self, TextHandler, screen, dt):
        self.current_screen.draw_screen(TextHandler, screen, dt)

    def handle_events(self, dt, events):
        self.current_screen.handle_events(dt, events)

    def change_screen(self):
        if self.current_screen.screen_change[0]:
            next_screen = self.available_screens[self.current_screen.screen_change[1]]
            pass_from_prev_screen = self.current_screen.screen_change[2]
            self.current_screen.reset_next()
            self.current_screen = next_screen
            self.current_screen.get_from_prev_screen(pass_from_prev_screen)
