import math
import pygame
import sys
from collections import namedtuple
from enum import Enum, auto
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


BubbleKit = namedtuple('BubbleKit', 'file color')

BUBBLES = [
    BubbleKit('images/ball_blue.png', 'blue'),
    BubbleKit('images/ball_green.png', 'green'),
    BubbleKit('images/ball_pink.png', 'pink'),
    BubbleKit('images/ball_purple.png', 'purple'),
    BubbleKit('images/ball_red.png', 'red'),
    BubbleKit('images/ball_sky.png', 'sky'),
]


class Status(Enum):

    LAUNCHED = auto()
    READY = auto()
    STAY = auto()
    MOVE = auto()


class PyBubbleShooter:

    def __init__(self, screen, bubble_group):
        self.screen = screen
        self.angle = 90
        self.bubble_group = bubble_group
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
                index = randint(0, 5)
                x = x_start + BUBBLE_SIZE * col
                bubble = Bubble(BUBBLES[index], x, y, row, col)
                self.bubbles[row][col] = bubble
        index = randint(0, 5)
        self.bullet = Bullet(BUBBLES[index], 205, 600, self.bubble_group)

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
        if self.bullet.status == Status.READY:
            self.bullet.shoot(self.angle)


class Bubble(pygame.sprite.Sprite):

    def __init__(self, bubble_kit, x, y, row, col):
        super().__init__(self.containers)
        # self.screen = screen
        self.image = pygame.image.load(bubble_kit.file).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.row = row
        self.col = col
        self.speed_x = None
        self.speed_y = None
        self.color = bubble_kit.color
        self.status = Status.STAY 

    def move(self):
        self.speed_x = randint(-5, 5)
        self.speed_y = randint(-5, 5)

    def update(self):
        if self.status == Status.MOVE:
            self.rect.centerx += self.speed_x
            self.rect.centery += self.speed_y
            if self.rect.left < SCREEN.left:
                self.rect.left = SCREEN.left
                self.speed_x = -self.speed_x

            if self.rect.right > SCREEN.right:
                self.rect.right = SCREEN.right
                self.speed_x = -self.speed_x

            if self.rect.top < SCREEN.top:
                self.rect.top = SCREEN.top
                self.speed_y = -self.speed_y


class Bullet(pygame.sprite.Sprite):

    def __init__(self, bubble_kit, x, y, bubbles):
        super().__init__(self.containers)
        self.image = pygame.image.load(bubble_kit.file).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.status = Status.READY
        self.bubbles = bubbles
        self.color = bubble_kit.color
        self.speed_x = None
        self.speed_y = None

    def round_up(self, value):
        return int(math.copysign(math.ceil(abs(value)), value))

    def shoot(self, angle):
        x = 10 * math.cos(math.radians(angle))
        y = 10 * math.sin(math.radians(angle))
        self.speed_x = self.round_up(x)
        self.speed_y = -self.round_up(y)
        self.status = Status.LAUNCHED

    def update(self):
        if self.status == Status.LAUNCHED:
            self.rect.centerx += self.speed_x
            self.rect.centery += self.speed_y
            if self.rect.left < SCREEN.left:
                self.rect.left = SCREEN.left
                self.speed_x = -self.speed_x

            if self.rect.right > SCREEN.right:
                self.rect.right = SCREEN.right
                self.speed_x = -self.speed_x

            if self.rect.top < SCREEN.top:
                self.rect.top = SCREEN.top
                self.speed_y = -self.speed_y

            if collided_bubbles := pygame.sprite.spritecollide(self, self.bubbles, False):
                self.speed_x = randint(-5, 5)
                self.speed_y = -self.speed_y

                for collided_bubble in collided_bubbles:
                    print(collided_bubble.row, collided_bubble.col)
                    collided_bubble.status = Status.MOVE
                    collided_bubble.move()

    # def check_collide(self, collided_bubble):
    #     for bubble in collided_bubble:
    #         if bubble.collor == self.color:
    #             yield bubble


    # def check_matrix(self, bubble):
    #     row = bubble.row
    #     col = bubble.col
    #     while row < 
    # 最初にぶつかったバブルと同じrowで左右に連続しているもののカラムインデックスを調べる。
    #　一段上に行き、そのカラムと同じか左右に連続しているものを調べる。
    # さらに上にいって調べる
    # 最初にぶつかったカラムの下の方向にも調べる。
    # 再帰？

        

            



def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    pygame.display.set_caption('PyBubbleShooter')
    bubbles = pygame.sprite.RenderUpdates()
    bullets = pygame.sprite.RenderUpdates()
    Bubble.containers = bubbles
    Bullet.containers = bullets
    # ball = Ball('images/ball_pink.png')
    bubble_shooter = PyBubbleShooter(screen, bubbles)
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