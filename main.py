import pygame
import pygame.gfxdraw
import math

# pygame setup
pygame.init()

global height, width
height, width = 1280, 720

screen = pygame.display.set_mode((height, width))

centre = screen.get_width() / 2, screen.get_height() / 2


class SurfaceHandler:
    def __init__(self):
        self.surfaces = {}

    def create_surface(self, height, width):
        surface_name = self.create_available_name()
        self.add_surface(surface_name, pygame.Surface((height, width), pygame.SRCALPHA))
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


class Obstacle:
    def __init__(self, start_angle, angle, speed = 1):
        # Obstacle will start on the edge of the screen.
        self.inner_radius = math.sqrt((centre[0])**2 + (centre[1])**2)
        self.outer_radius = math.sqrt((centre[0])**2 + (centre[1])**2) + 10
        self.start_angle = start_angle
        self.angle = angle
        self.centre = centre
        self.speed = speed

    def create_polygon_points(self, radius):
        # Start list of polygon points
        polygon_points = [self.centre]
        # Get points on arc
        for n in range(0, int(self.angle)):
            x = self.centre[0] + int(radius * math.cos(n * math.pi / 180))
            y = self.centre[1] + int(radius * math.sin(n * math.pi / 180))
            polygon_points.append((x, y))
        polygon_points.append(self.centre)
        return polygon_points

    def create_sector_of_the_ring_points(self):
        outer_points = self.create_polygon_points(self.outer_radius)
        inner_points = self.create_polygon_points(self.inner_radius)
        return outer_points, inner_points

    def move_obstacle(self):
        self.inner_radius -= self.speed
        self.outer_radius -= self.speed

    def create_sector_of_the_ring(self, SurfaceHandler, ObstacleHandler):
        outer_points, inner_points = self.create_sector_of_the_ring_points()
        SurfaceHandler.create_surface()

        pos1, rad1 = centre, 100
        pos2, rad2 = centre, 110
        surf1 = pygame.Surface((height, width), pygame.SRCALPHA)
        surf2 = pygame.Surface((height, width), pygame.SRCALPHA)
        surf2.blit(surf1, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        if len(self.polygon_points) > 2:
            pygame.draw.polygon(screen, (0, 0, 0), self.polygon_points)

        pygame.draw.circle(surf1, (255, 0, 0, 255), pos1, rad1)
        pygame.draw.circle(surf2, (255, 0, 0, 255), pos2, rad2)
        surf2.blit(surf1, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        screen.blit(surf2, (0, 0))
        surf2.fill(pygame.Color(0, 0, 0, 0))
        surf1.fill(pygame.Color(0, 0, 0, 0))


    def rotate_obstacle(self, rotation_angle):
        pass

    def move_obstacle(self):
        pass

    def draw_obstacle(self, screen):
        pass


class ObstacleHandler:
    def __init__(self):
        pass

    def add_obstacle(self, obstacle):
        pass

    def draw_obstacles(self, screen):
        pass




# Center and radius of pie rchart
cx, cy, r = 100, 320, 75

# Background circle
pygame.draw.circle(screen, (17, 153, 255), (cx, cy), r)




clock = pygame.time.Clock()
running = True
dt = 0
player_pos = pygame.Vector2(0, 0)
pos1, rad1 = centre, 100
pos2, rad2 = centre, 110
surf1 = pygame.Surface((height, width), pygame.SRCALPHA)
surf2 = pygame.Surface((height, width), pygame.SRCALPHA)
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("tomato")
    pygame.draw.circle(screen, "red", player_pos, 40)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt
    if keys[pygame.K_UP]:
        rad1 = rad1 + 1
        rad2 = rad2 + 1
    if keys[pygame.K_DOWN]:
        rad1 = rad1 - 1
        rad2 = rad2 - 1


    test_surface_handler = SurfaceHandler()
    create_test_surface = test_surface_handler.create_surface(height, width)
    pygame.draw.circle(test_surface_handler.get_surface(create_test_surface), (255, 0, 0, 255), pos2, 10)
    screen.blit(test_surface_handler.get_surface(create_test_surface), (0, 0))


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