import pygame
import pygame.gfxdraw
import math

# pygame setup
pygame.init()


height, width = 1280, 720

screen = pygame.display.set_mode((height, width))

centre = screen.get_width() / 2, screen.get_height() / 2


class Obstacle:
    def __init__(self, inner_radius, outer_radius, start_angle, angle):
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.start_angle = start_angle
        self.angle = angle
        self.centre = centre

    def get_polygon_points(self):
        # Start list of polygon points
        polygon_points = [self.centre]
        # Get points on arc
        for n in range(0, int(self.angle)):
            x = self.centre[0] + int(r * math.cos(n * math.pi / 180))
            y = self.centre[1] + int(r * math.sin(n * math.pi / 180))
            polygon_points.append((x, y))
        polygon_points.append(self.centre)
        return polygon_points

    def create_pseudo_sector_of_the_ring(self):
        pos1, rad1 = centre, 100
        pos2, rad2 = centre, 110
        surf1 = pygame.Surface((height, width), pygame.SRCALPHA)
        surf2 = pygame.Surface((height, width), pygame.SRCALPHA)
        surf2.blit(surf1, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)


    def move_obstacle(self):
        pass

    def draw_obstacle(self, screen):
        pass


class ObstacleHandler:
    def __init__(self):
        pass

    def add_obstacle(self):
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
player_pos = pygame.Vector2(centre[0], centre[1])
pos1, rad1 = centre, 100
pos2, rad2 = centre, 110
surf1 = pygame.Surface((height, width), pygame.SRCALPHA)
surf2 = pygame.Surface((height, width), pygame.SRCALPHA)
surf2.blit(surf1, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
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