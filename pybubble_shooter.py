import math
import pygame
import sys
from pygame.locals import QUIT, K_DOWN, K_RIGHT, K_LEFT, K_UP, KEYDOWN, MOUSEBUTTONDOWN, Rect
from random import randint


SCREEN_WIDTH = 410

SCREEN = Rect(0, 0, SCREEN_WIDTH, 600)
ROW_START = 10
COL_START = 10

Y_START_POS = 10
X_START_POS = 10

ROWS = 30
COLS = 20

BUBBLE_SIZE = 20

# arrow
ARROW_START_X = 205
ARROW_START_Y = 600
ARROW_START = (ARROW_START_X, ARROW_START_Y)

# color
COLOR_GREEN = (0, 100, 0)
DARK_GREEN = (0, 80, 0)

FILES = {
    0: 'images/ball_blue.png',
    1: 'images/ball_green.png',
    2: 'images/ball_pink.png',
    3: 'images/ball_purple.png',
    4: 'images/ball_red.png',
    5: 'images/ball_sky.png'}


class PyBubbleShooter:

    def __init__(self, screen):
        self.screen = screen
        self.angle = 90
        self.bubbles = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.create_bubbles()

    def create_bubbles(self, rows=15):
        for row in range(rows):
            if row % 2 == 0:
                x_start = X_START_POS
            else:
                x_start = X_START_POS + BUBBLE_SIZE / 2
            y = Y_START_POS + BUBBLE_SIZE * row
            for col in range(20):
                key = randint(0, 5)
                x = x_start + BUBBLE_SIZE * col
                bubble = Bubble(FILES[key], x, y, row, col)
                self.bubbles[row][col] = bubble
        key = randint(0, 5)
        self.bullet = Bullet(FILES[key], 205, 600)

    def update(self):
        self.draw_arrow()

    def draw_arrow(self):
        arrow_end = self.get_coordinates()
        arrow_head = self.get_arrow_head(*arrow_end)
        pygame.draw.line(self.screen, DARK_GREEN, ARROW_START, arrow_end, 3)
        pygame.draw.polygon(self.screen, DARK_GREEN, arrow_head)

    def get_arrow_head(self, end_x, end_y, size=10):
        rotation = math.degrees(math.atan2(ARROW_START_Y - end_y, end_x - ARROW_START_X)) + 90
        arrow_head = (
            (end_x + size * math.sin(math.radians(rotation)), end_y + size * math.cos(math.radians(rotation))),
            (end_x + size * math.sin(math.radians(rotation - 120)), end_y + size * math.cos(math.radians(rotation - 120))),
            (end_x + size * math.sin(math.radians(rotation + 120)), end_y + size * math.cos(math.radians(rotation + 120))))
        return arrow_head

    def get_coordinates(self, radius=100):
        x = ARROW_START_X + radius * math.cos(math.radians(self.angle))
        y = ARROW_START_Y - radius * math.sin(math.radians(self.angle))
        return x, y

    def move_right(self):
        self.angle -= 5
        if self.angle < 5:
            self.angle = 5

    def move_left(self):
        self.angle += 5
        if self.angle > 175:
            self.angle = 175

    def shoot(self):
        x, y = self.get_coordinates(100)
        self.bullet.rect.centerx = x
        self.bullet.rect.centery = y



class Bubble(pygame.sprite.Sprite):

    def __init__(self, file_path, x, y, row, col):
        super().__init__(self.containers)
        # self.screen = screen
        self.image = pygame.image.load(file_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.row = row
        self.col = col


class Bullet(pygame.sprite.Sprite):

    def __init__(self, file_path, x, y):
        super().__init__(self.containers)
        self.image = pygame.image.load(file_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        
    def update(self):
        pass



def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    pygame.display.set_caption('PyBubbleShooter')
    bubbles = pygame.sprite.RenderUpdates()
    bullets = pygame.sprite.RenderUpdates()
    Bubble.containers = bubbles
    Bullet.containers = bullets
    # ball = Ball('images/ball_pink.png')
    bubble_shooter = PyBubbleShooter(screen)
    clock = pygame.time.Clock()
    pygame.key.set_repeat(500, 100)

    while True:
        clock.tick(60)
        screen.fill(COLOR_GREEN)

        bubble_shooter.update()
        bubbles.update()
        bubbles.draw(screen)
        bullets.update()
        bullets.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    bubble_shooter.move_right()
                if event.key == K_LEFT:
                    bubble_shooter.move_left()
                if event.key == K_UP:
                    bubble_shooter.shoot()


        pygame.display.update()


if __name__ == '__main__':
    main()

# def draw_arrow(screen, colour, start, end): 
#     pygame.draw.line(screen,colour,start,end,2) 
#     rotation = math.degrees(math.atan2(start[1]-end[1], end[0]-start[0]))+90 
#     pygame.draw.polygon(screen, (255, 0, 0), 
#         ((end[0]+20*math.sin(math.radians(rotation)), end[1]+20*math.cos(math.radians(rotation))),
#         (end[0]+20*math.sin(math.radians(rotation-120)), end[1]+20*math.cos(math.radians(rotation-120))),
#         (end[0]+20*math.sin(math.radians(rotation+120)), end[1]+20*math.cos(math.radians(rotation+120))))) 