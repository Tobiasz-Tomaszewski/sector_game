import pygame
import pygame.gfxdraw
import math
import numpy as np


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


class SurfaceHandler:
    def __init__(self, screen):
        self.surfaces = {}
        self.screen = screen
        self.height = screen.get_height()
        self.width = screen.get_width()

    def create_surface(self):
        surface_name = self.create_available_name()
        surface = pygame.Surface((self.height, self.width), pygame.SRCALPHA)
        self.add_surface(surface_name, surface)
        return surface_name

    def add_surface(self, surface_name, surface):
        self.surfaces[surface_name] = surface

    def get_surface(self, surface_name):
        return self.surfaces[surface_name]

    def create_available_name(self):
        current_indexes = sorted(int(x) for x in self.surfaces.keys())
        all_indexes = [x for x in range(len(self.surfaces))]
        zipped = zip(current_indexes, all_indexes)
        unused_indexes = [y for x, y in zipped if x != y]
        if unused_indexes:
            return str(min(unused_indexes))
        return '0'

    def delete_surface(self, surface_name):
        return self.surfaces.pop(surface_name)


class Obstacle:
    def __init__(self, start_angle, angle, speed=1):
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

    def move_obstacle(self):
        self.inner_radius -= self.speed
        self.outer_radius -= self.speed

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


class ObstacleHandler:
    def __init__(self):
        self.obstacles = {}

    def add_obstacle(self, obstacle_name, obstacle):
        self.obstacles[obstacle_name] = obstacle

    def draw_obstacles(self, screen):
        pass

    def delete_obstacle(self, obstacle_name):
        return self.obstacles.pop(obstacle_name)

    def create_available_name(self):
        current_indexes = sorted(int(x) for x in self.obstacles.keys())
        all_indexes = [x for x in range(len(self.obstacles))]
        zipped = zip(current_indexes, all_indexes)
        unused_indexes = [y for x, y in zipped if x != y]
        if unused_indexes:
            return str(min(unused_indexes))
        return '0'


clock = pygame.time.Clock()
running = True
dt = 0
player = Player(centre, 100, curve_nr=4, path_deviation=20)
obstacle = Obstacle(40, 300)
path_perc = 0
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("tomato")
    player.draw_player(screen)
    player.draw_player_path(screen)
    obstacle.draw_obstacle(screen)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_p]:
        path_perc += dt * 40
        player.move(path_perc)
    if keys[pygame.K_l]:
        path_perc -= dt * 40
        player.move(path_perc)

    obstacle.move_obstacle()

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()