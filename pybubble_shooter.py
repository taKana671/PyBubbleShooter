import math
import pygame
import sys
from collections import namedtuple
from enum import Enum, auto
from pygame.locals import QUIT, K_DOWN, K_RIGHT, K_LEFT, K_UP, KEYDOWN, MOUSEBUTTONDOWN, Rect
from random import randint

import numpy as np


SCREEN_WIDTH = 526
SCREEN_HEIGHT = 600
SCREEN = Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
ROW_START = 16
COL_START = 15

Y_START_POS = 15
X_START_POS = 16

ROWS = 20
COLS = 17

BUBBLE_SIZE = 30

# arrow
ARROW_START_X = SCREEN_WIDTH // 2
ARROW_START_Y = SCREEN_HEIGHT
# ARROW_START = (ARROW_START_X, ARROW_START_Y)

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


# Coordinates = namedtuple('Coordinates', 'x y')


# class Point(Coordinates):

#     @property
#     def coords(self):
#         return tuple(self)


Point = namedtuple('Point', 'x y')


def round_up(value):
    return int(math.copysign(math.ceil(abs(value)), value))


class Cell:

    def __init__(self, row, col):
        self.bubble = None
        self.row = row
        self.col = col
        self.calculate_center()
        self.calculate_points()

    def calculate_points(self):
        half = BUBBLE_SIZE // 2
        self.left = Point(self.center.x - half, self.center.y)
        self.right = Point(self.center.x + half, self.center.y)

        # self.left_top = Point(self.center.x - half, self.center.y - half)
        # self.right_bottom = Point(self.center.x + half, self.center.y + half)
        # self.right_top = Point(self.center.x + half, self.center.y - half)
        # self.left_bottom = Point(self.center.x - half, self.center.y + half)

    def calculate_center(self):
        if self.row % 2 == 0:
            start = X_START_POS
        else:
            start = X_START_POS + BUBBLE_SIZE // 2
        x = start + BUBBLE_SIZE * self.col
        y = Y_START_POS + BUBBLE_SIZE * self.row
        self.center = Point(x, y)


class Shooter:

    def __init__(self, screen, bubble_group):
        self.screen = screen
        self.angle = 90
        self.dest = None
        self.target = None
        self.bubble_group = bubble_group
        self.targets = [[Cell(row, col) for col in range(COLS)] for row in range(ROWS)]
        self.create_variables()
        self.create_bubbles(5)
        self.status = Status.READY

    def create_variables(self):
        self.launcher = Point(SCREEN.width // 2, SCREEN.height)
        self.radius = self.get_radius(SCREEN.width // 2, SCREEN.height)
        self.limit_angle = round_up(
            self.calculate_angle(SCREEN.height, SCREEN.width // 2))

    def create_bubbles(self, rows=15):
        for row in range(rows):
            for col, cell in enumerate(self.targets[row]):
                i = randint(0, 5)
                bubble = Bubble(BUBBLES[i], cell.center, row, col)
                cell.bubble = bubble
        self.charge()

    def recursive_from_right(self, angle, start):
        if (x := SCREEN.width - self.calculate_height(angle, start.y)) >= 0:
            _ = self.find_destination(start, Point(x, 0))
            return

        bottom = self.calculate_bottom(angle, SCREEN.width)
        end_left = Point(0, start.y - bottom)
        if self.find_destination(start, end_left):
            return

        if (x := self.calculate_height(angle, end_left.y)) <= SCREEN.width:
            self.find_destination(end_left, Point(x, 0))
            return

        bottom = self.calculate_bottom(angle, SCREEN.width)
        end_right = Point(SCREEN.width, end_left.y - bottom)
        if self.find_destination(end_left, end_right):
            return

        self.recursive_from_right(angle, end_right)

    def recursive_from_left(self, angle, start):

        if (x := self.calculate_height(angle, start.y)) <= SCREEN.width:
            self.find_destination(start, Point(x, 0))
            return

        bottom = self.calculate_bottom(angle, SCREEN.width)
        end_right = Point(SCREEN.width, start.y - bottom)
        if self.find_destination(start, end_right):
            return

        if (x := SCREEN.width - self.calculate_height(angle, end_right.y)) >= 0:
            _ = self.find_destination(end_right, Point(x, 0))
            return

        bottom = self.calculate_bottom(angle, SCREEN.width)
        end_left = Point(0, end_right.y - bottom)
        if self.find_destination(end_right, end_left):
            return

        self.recursive_from_left(angle, end_left)

    def find_destination(self, start, end):
        """Return False if more lines are to be continuingly drawn.
        """
        self.dest, self.target = self.check_targets(start, end)
        if self.dest and not self.target:
            pygame.draw.line(self.screen, DARK_GREEN, start, end, 2)
            return False
        if self.dest and self.target:
            cross_point = self.find_cross_point(start, end, self.dest.left, self.dest.right)
            pygame.draw.line(self.screen, DARK_GREEN, start, cross_point, 2)
        return True

    def update(self):
        if 0 < self.angle <= self.limit_angle:
            y = SCREEN.height - self.calculate_height(self.angle, SCREEN.width // 2)
            end = Point(SCREEN.width, y)
            if not self.find_destination(self.launcher, end):
                self.recursive_from_right(90 - self.angle, end)

        if self.limit_angle < self.angle <= 90:
            x = SCREEN.width // 2 + self.calculate_height(90 - self.angle, SCREEN.height)
            end = Point(x, 0)
            _ = self.find_destination(self.launcher, end)

        if 90 < self.angle < 180 - self.limit_angle:
            x = SCREEN.width // 2 - self.calculate_height(self.angle - 90, SCREEN.height)
            end = Point(x, 0)
            _ = self.find_destination(self.launcher, end)

        if self.angle >= 180 - self.limit_angle:
            y = SCREEN.height - self.calculate_height(180 - self.angle, SCREEN.width // 2)
            end = Point(0, y)
            if not self.find_destination(self.launcher, end):
                self.recursive_from_left(self.angle - 90, end)

        if self.status == Status.CHARGE:
            self.charge()
            self.status = Status.READY

    def charge(self):
        i = randint(0, 5)
        # self.bullet = Bullet(BUBBLES[index], 205, 600, self)
        self.bullet = Bullet(BUBBLES[i], SCREEN.width // 2, SCREEN.height, self.bubble_group, self)

    def find_cross_point(self, pt1, pt2, pt3, pt4):
        a0 = pt2.x - pt1.x
        b0 = pt2.y - pt1.y
        a2 = pt4.x - pt3.x
        b2 = pt4.y - pt3.y

        d = a0 * b2 - a2 * b0
        sn = b2 * (pt3.x - pt1.x) - a2 * (pt3.y - pt1.y)
        x = pt1.x + a0 * sn / d
        y = pt1.y + b0 * sn / d

        return Point(x, y)

    def is_crossing(self, pt1, pt2, pt3, pt4):
        tc1 = (pt1.x - pt2.x) * (pt3.y - pt1.y) + (pt1.y - pt2.y) * (pt1.x - pt3.x)
        tc2 = (pt1.x - pt2.x) * (pt4.y - pt1.y) + (pt1.y - pt2.y) * (pt1.x - pt4.x)
        td1 = (pt3.x - pt4.x) * (pt1.y - pt3.y) + (pt3.y - pt4.y) * (pt3.x - pt1.x)
        td2 = (pt3.x - pt4.x) * (pt2.y - pt3.y) + (pt3.y - pt4.y) * (pt3.x - pt2.x)

        return tc1 * tc2 < 0 and td1 * td2 < 0

    def check_targets(self, pt1, pt2):
        dest = None
        for row, cells in zip(range(ROWS - 1, -1, -1), self.targets[::-1]):
            for col, cell in enumerate(cells):
                if self.is_crossing(pt1, pt2, cell.left, cell.right):
                    if not cell.bubble:
                        dest = cell
                    else:
                        return dest, cell

        return dest, None

    def get_radius(self, bottom, height):
        return (bottom ** 2 + height ** 2) ** 0.5

    def calculate_angle(self, height, bottom):
        return math.degrees(math.atan2(height, bottom))

    def calculate_height(self, angle, bottom):
        return round_up(math.tan(math.radians(angle)) * bottom)

    def calculate_bottom(self, angle, height):
        return round_up(height / math.tan(math.radians(angle)))

    def get_coordinates(self):
        x = ARROW_START_X + self.radius * math.cos(math.radians(self.angle))
        y = ARROW_START_Y - self.radius * math.sin(math.radians(self.angle))
        return Point(x, y)

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

    def __init__(self, bubble_kit, center, row, col):
        super().__init__(self.containers)
        # self.screen = screen
        self.image = pygame.image.load(bubble_kit.file).convert_alpha()
        self.image = pygame.transform.scale(self.image, (BUBBLE_SIZE, BUBBLE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.centerx = center.x
        self.rect.centery = center.y
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
        self.image = pygame.transform.scale(self.image, (BUBBLE_SIZE, BUBBLE_SIZE))
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
        self.random_generator = np.random.default_rng()

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

                self.shooter.targets[self.row][self.col] = self
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
                        bubble = self.shooter.targets[row][col]
                        self.shooter.targets[row][col] = None
                        bubble.status = Status.MOVE
                        bubble.move()
                else:
                    self.speed_x = 0
                    self.speed_y = 0
                    self.status = Status.STAY

                self.shooter.status = Status.CHARGE

    def find_destination(self, collided):
        print([(b.row, b.col) for b in collided])
        for bubble in collided:
            func = self.check_even_rows if bubble.row % 2 == 0 else self.check_odd_rows
            for number in self.random_generator.permutation(4):
                new_row, new_col = func(bubble.row, bubble.col, number)
                if new_row and new_col:
                    return new_row, new_col

    def check_even_rows(self, row, col, number):
        if number == 0:
            if row < ROWS - 1 and col > 0:
                if not self.shooter.targets[row + 1][col - 1]:
                    return row + 1, col - 1
            return None, None
        elif number == 1:
            if row < ROWS - 1:
                if not self.shooter.targets[row + 1][col]:
                    return row + 1, col
            return None, None
        elif number == 2:
            if col > 0:
                if not self.shooter.targets[row][col - 1]:
                    return row, col - 1
            return None, None
        elif number == 3:
            if col < COLS - 1:
                if not self.shooter.targets[row][col + 1]:
                    return row, col + 1
            return None, None

    def check_odd_rows(self, row, col, number):
        if number == 0:
            if row < ROWS - 1:
                if not self.shooter.targets[row + 1][col]:
                    return row + 1, col + 1
            return None, None
        elif number == 1:
            if row < ROWS - 1 and col < COLS - 1:
                if not self.shooter.targets[row + 1][col + 1]:
                    return row + 1, col
            return None, None
        elif number == 2:
            if col > 0:
                if not self.shooter.targets[row][col - 1]:
                    return row, col - 1
            return None, None
        elif number == 3:
            if col < COLS - 1:
                if not self.shooter.targets[row][col + 1]:
                    return row, col + 1
            return None, None

    def check_color(self, row, col, neighbors):
        if row < 0 or row > ROWS - 1 or col < 0 or col > COLS - 1:
            return
        if self.shooter.targets[row][col] is None:
            return
        if self.shooter.targets[row][col].color != self.color:
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