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
    def __init__(self, centre, radius, speed=1, curve_nr=0, path_deviation=0):
        self.radius = radius
        self.centre = centre
        self.speed = speed
        self.is_alive = True
        self.player_path = self.generate_player_path(curve_nr, path_deviation)
        self.player_position = self.player_path[0]

    @staticmethod
    def _polar_to_cartesian(coordinates):
        x = coordinates[0] * math.cos(coordinates[1])
        y = coordinates[0] * math.sin(coordinates[1])
        return x, y

    def generate_player_path(self, curve_nr, path_deviation):
        phi = np.array([i * (math.pi / 180) for i in range(360)])
        r = np.array([self.radius + math.sin(curve_nr * phi[i]) * path_deviation for i in range(360)])
        x_list = []
        y_list = []
        for x, y in zip(r, phi):
            cart = self._polar_to_cartesian((x, y))
            x_list.append(cart[0])
            y_list.append(cart[1])
        x_list = [x + height / 2 for x in x_list]
        y_list = [y + width / 2 for y in y_list]
        player_path = [pygame.Vector2(x, y) for x, y in zip(x_list, y_list)]
        return player_path

    def move_clockwise(self):
        current_index = self.player_path.index(self.player_position)
        next_index = (current_index + 1) % len(self.player_path)
        self.player_position = self.player_path[next_index]

    def move_counterclockwise(self):
        current_index = self.player_path.index(self.player_position)
        next_index = current_index - 1
        self.player_position = self.player_path[next_index]

    def draw_player(self, screen):
        pygame.draw.circle(screen, "yellow", self.player_position, 10)

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

    def create_polygon_points(self, radius):
        # Start list of polygon points
        polygon_points = []
        # Get points on arc
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

    def create_sector_of_the_ring(self, SurfaceHandler, ObstacleHandler):
        points = self.create_sector_of_the_ring_points()
        surface_id = SurfaceHandler.create_surface()
        surface = SurfaceHandler.get_surface(surface_id)

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

    def draw_obstacle(self, SurfaceHandler):
        SurfaceHandler.create_surface()


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


# Center and radius of pie rchart
cx, cy, r = 100, 320, 75

# Background circle
pygame.draw.circle(screen, (17, 153, 255), (cx, cy), r)




clock = pygame.time.Clock()
running = True
dt = 0
pos1, rad1 = centre, 100
pos2, rad2 = centre, 110
surf1 = pygame.Surface((height, width), pygame.SRCALPHA)
surf2 = pygame.Surface((height, width), pygame.SRCALPHA)
player = Player(centre, 100, curve_nr=4, path_deviation=40)
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
    keys = pygame.key.get_pressed()
    if keys[pygame.K_p]:
        player.move_clockwise()
    if keys[pygame.K_l]:
        player.move_counterclockwise()
    if keys[pygame.K_UP]:
        rad1 = rad1 + 1
        rad2 = rad2 + 1
    if keys[pygame.K_DOWN]:
        rad1 = rad1 - 1
        rad2 = rad2 - 1



    pygame.draw.circle(surf1, (255, 0, 0, 255), pos1, rad1)
    pygame.draw.circle(surf2, (255, 0, 0, 255), pos2, rad2)
    surf2.blit(surf1, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    screen.blit(surf2, (0, 0))
    surf2.fill(pygame.Color(0, 0, 0, 0))
    surf1.fill(pygame.Color(0, 0, 0, 0))



####    if len(p) > 2:
####        pygame.draw.polygon(screen, (0, 0, 0), p)
    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()