import pygame
import pygame.gfxdraw
import math
import numpy as np
from numpy import random


# pygame setup
pygame.init()

global height, width
height, width = 1280, 720
screen = pygame.display.set_mode((height, width))
centre = screen.get_width() / 2, screen.get_height() / 2


class Player:
    def __init__(self, centre, radius, curve_nr=0, path_deviation=0,
                 player_path_resolution=100):
        self.radius = radius
        self.centre = centre
        self.is_alive = True
        self.curve_nr = curve_nr
        self.path_deviation = path_deviation
        self.player_path_resolution = player_path_resolution
        self.player_path = self.generate_player_path()
        self.player_position = self.move(0)

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
        pygame.draw.circle(screen, 'yellow', self.player_position, 10)

    def draw_player_path(self, screen):
        pygame.draw.polygon(screen, 'black', self.player_path, width=1)

    def check_alive_status(self, ObstacleHandler):
        pass


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
    def __init__(self, min_angle, max_angle, distance_between_obstacles = 400):
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


class Game:
    def __init__(self, player, obstacle_handler):
        self.player = player
        self.obstacle_handler = obstacle_handler
        self.path_perc = 0

    def create_init_obstacle(self):
        self.obstacle_handler.create_new_obstacle()

    def change_path_perc(self, val):
        self.path_perc += val

    def draw_game_screen(self, screen, dt):
        screen.fill("tomato")
        self.player.draw_player(screen)
        self.player.draw_player_path(screen)
        self.obstacle_handler.draw_obstacles(screen)
        self.obstacle_handler.move_all_obstacles(dt)
        self.obstacle_handler.generate_next()
        self.obstacle_handler.delete_dead_obstacles()

    def handle_events(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.change_path_perc(dt * 40)
            self.player.move(self.path_perc)
        if keys[pygame.K_LEFT]:
            self.change_path_perc(-dt * 40)
            self.player.move(self.path_perc)


clock = pygame.time.Clock()
running = True
dt = 0
player = Player(centre, 100, curve_nr=8, path_deviation=10)
obstacle_handler = ObstacleHandler(45, 270, 200)
game = Game(player, obstacle_handler)
game.create_init_obstacle()
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    game.draw_game_screen(screen, dt)
    game.handle_events(dt)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000


pygame.quit()