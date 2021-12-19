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
    CHARGE = auto()
    SHOT = auto()


class Shooter:

    def __init__(self, screen, bubble_group):
        self.screen = screen
        self.angle = 90
        self.bubble_group = bubble_group
        self.bubbles = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.create_bubbles(6)
        self.status = Status.READY


    def create_bubbles(self, rows=15):
        for row in range(rows):
            if row % 2 == 0:
                x_start = X_START_POS
            else:
                x_start = X_START_POS + BUBBLE_SIZE / 2
            y = Y_START_POS + BUBBLE_SIZE * row
            for col in range(20):
                index = randint(0, 5)
                # x = X_START_POS + BUBBLE_SIZE * col
                x = x_start + BUBBLE_SIZE * col
                bubble = Bubble(BUBBLES[index], x, y, row, col)
                self.bubbles[row][col] = bubble
        self.charge()
        # index = randint(0, 5)
        # self.bullet = Bullet(BUBBLES[index], 205, 600, self.bubble_group, self)

    def update(self):
        self.draw_arrow()
        if self.status == Status.CHARGE:
            self.charge()
            self.status = Status.READY

    def charge(self):
        index = randint(0, 5)
        # self.bullet = Bullet(BUBBLES[index], 205, 600, self)
        self.bullet = Bullet(BUBBLES[index], 205, 600, self.bubble_group, self)

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
        self.angle -= 2
        if self.angle < 5:
            self.angle = 5

    def move_left(self):
        self.angle += 2
        if self.angle > 175:
            self.angle = 175

    def shoot(self):
        # if self.bullet.status == Status.READY:
        if self.status == Status.READY:
            self.status = Status.SHOT
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
        self.speed_y = -10

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

    # bubble_group = None

    def __init__(self, bubble_kit, x, y, bubble_group, shooter):
    # def __init__(self, bubble_kit, x, y, shooter):
        super().__init__(self.containers)
        self.image = pygame.image.load(bubble_kit.file).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.status = Status.READY
        self.bubble_group = bubble_group
        self.color = bubble_kit.color
        self.shooter = shooter
        self.speed_x = 0
        self.speed_y = 0
        self.row = None
        self.col = None

    def round_up(self, value):
        return int(math.copysign(math.ceil(abs(value)), value))

    def calc_distance(self, bubble):
        point1 = (self.rect.centerx, self.rect.centery)
        point2 = (bubble.rect.centerx, bubble.rect.centery)
        return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

    def shoot(self, angle):
        x = 10 * math.cos(math.radians(angle))
        y = 10 * math.sin(math.radians(angle))
        self.speed_x = self.round_up(x)
        self.speed_y = -self.round_up(y)
        self.status = Status.LAUNCHED

    def move(self):
        self.speed_x = randint(-5, 5)
        self.speed_y = 10

    def update(self):
        if self.status in (Status.LAUNCHED, self.status.MOVE):
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
        if self.status == Status.LAUNCHED:
            if collided := pygame.sprite.spritecollide(self, self.bubble_group, False):
                self.row, self.col = self.find_destination(collided)
                # collided.sort(key=lambda x: (x.row, x.col))
                # bubble = collided[0]

                # if bubble.col > 0 and not self.shooter.bubbles[bubble.row][bubble.col - 1]:
                #     self.row = bubble.row
                #     self.col = bubble.col - 1
                # elif bubble.col < COLS - 1 and not self.shooter.bubbles[bubble.row][bubble.col + 1]:
                #     self.row = bubble.row
                #     self.col = bubble.col - 1
                # elif bubble.row < ROWS - 1:
                #     self.row = bubble.row + 1
                #     self.col = bubble.col

                # print(self.row, self.col)
                # print(self.shooter.bubbles)

                self.shooter.bubbles[self.row][self.col] = self
                if self.row % 2 == 0:
                    x_start = X_START_POS
                else:
                    x_start = X_START_POS + BUBBLE_SIZE / 2
                y = Y_START_POS + BUBBLE_SIZE * self.row
                x = x_start + BUBBLE_SIZE * self.col
                self.rect.centerx = x
                self.rect.centery = y
                self.bubble_group.add(self)
                neighbors = []
                self.check_color(self.row, self.col, neighbors)
                if len(neighbors) >= 3:
                    for row, col in neighbors:
                        bubble = self.shooter.bubbles[row][col]
                        self.shooter.bubbles[row][col] = None
                        bubble.status = Status.MOVE
                        bubble.move()
                else:
                    self.speed_x = 0
                    self.speed_y = 0
                    self.status = Status.STAY

                self.shooter.status = Status.CHARGE

    def find_destination(self, collided):
        collided.sort(key=self.calc_distance)
        print([(b.row, b.col) for b in collided])
        for bubble in collided:
            # 下2か所左右を探す順番をランダムにする！

            if bubble.row % 2 == 0:
                if not self.shooter.bubbles[bubble.row + 1][bubble.col - 1]:
                    return bubble.row + 1, bubble.col - 1
                if not self.shooter.bubbles[bubble.row + 1][bubble.col]:
                    return bubble.row + 1, bubble.col
            else:
                if not self.shooter.bubbles[bubble.row + 1][bubble.col]:
                    return bubble.row + 1, bubble.col
                if not self.shooter.bubbles[bubble.row + 1][bubble.col + 1]:
                    return bubble.row + 1, bubble.col + 1
            if not self.shooter.bubbles[bubble.row][bubble.col - 1]:
                return bubble.row, bubble.col - 1
            if not self.shooter.bubbles[bubble.row][bubble.col + 1]:
                return bubble.row, bubble.col + 1

    def check_color(self, row, col, neighbors):
        if row < 0 or row > ROWS - 1 or col < 0 or col > COLS - 1:
            return
        if self.shooter.bubbles[row][col] is None:
            return
        if self.shooter.bubbles[row][col].color != self.color:
            return
        if (row, col) in neighbors:
            return
        neighbors.append((row, col))

        if row % 2 == 0:
            self.check_color(row - 1, col - 1, neighbors)
            self.check_color(row - 1, col, neighbors)
            self.check_color(row, col - 1, neighbors)
            self.check_color(row, col + 1, neighbors)
            self.check_color(row + 1, col - 1, neighbors)
            self.check_color(row + 1, col, neighbors)
        else:
            self.check_color(row - 1, col, neighbors)
            self.check_color(row - 1, col + 1, neighbors)
            self.check_color(row, col - 1, neighbors)
            self.check_color(row, col + 1, neighbors)
            self.check_color(row + 1, col, neighbors)
            self.check_color(row + 1, col + 1, neighbors)


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    pygame.display.set_caption('PyBubbleShooter')
    bubbles = pygame.sprite.RenderUpdates()
    bullets = pygame.sprite.RenderUpdates()
    Bubble.containers = bubbles
    Bullet.containers = bullets
    # Bullet.bubble_group = bubbles
    # ball = Ball('images/ball_pink.png')
    bubble_shooter = Shooter(screen, bubbles)
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