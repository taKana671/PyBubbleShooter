import math
import pygame
import random
import sys
from collections import namedtuple
from enum import Enum, auto
from pathlib import Path
from pygame.locals import (QUIT, K_DOWN, K_RIGHT, K_LEFT, K_UP, K_SPACE,
    KEYDOWN, MOUSEBUTTONDOWN, Rect)


Window = namedtuple('Window', 'width height top bottom left right half_width')
WINDOW = Window(526, 600, 0, 600, 0, 526, 526 // 2)

Point = namedtuple('Point', 'x y')
Line = namedtuple('Line', 'start end')


# bubbles
Y_START_POS = 15
X_START_POS = 16
ROWS = 20
COLS = 17
BUBBLE_SIZE = 30
# screen
SCREEN = Rect(0, 0, 526, 650)
# start screen
SURFACE_LEFT = Point(0, 0)
GAME_TITLE = Point(40, 200)
START_Y = 320
GAME_START_BUTTON = Point(WINDOW.half_width, 400)
# game over screen
GAMEOVER_TITLE = Point(130, 200)
FINAL_SCORE = Point(30, 30)
CONTINUE_Y = 280
GAME_RETRY_BUTTON = Point(WINDOW.half_width, 350)


class Files(Enum):

    def __init__(self, name, dir):
        self._name = name
        self._dir = dir

    @property
    def path(self):
        return Path(self._dir, self._name)


class ImageFiles(Files):

    BALL_BLUE = 'ball_blue.png'
    BALL_GREEN = 'ball_green.png'
    BALL_PINK = 'ball_pink.png'
    BALL_PURPLE = 'ball_purple.png'
    BALL_RED = 'ball_red.png'
    BALL_SKY = 'ball_sky.png'
    BUTTON_START = 'button_start.png'

    def __init__(self, name):
        super().__init__(name, 'images')


class SoundFiles(Files):

    FANFARE = 'fanfare.wav'
    SOUND_POP = 'bubble.wav'

    def __init__(self, name):
        super().__init__(name, 'sounds')


class Colors(Enum):

    YELLOW_GREEN = ('yellow_green', (153, 255, 102))
    BLUE = ('blue', (0, 0, 255))
    PINK = ('pink', (255, 102, 255))
    PURPLE = ('purple', (204, 0, 255))
    RED = ('red', (255, 0, 0))
    RIGHT_BLUE = ('sky', (0, 255, 255))
    GREEN = ('green', (0, 100, 0))
    DARK_GREEN = ('dark_green', (0, 80, 0))
    RIGHT_GRAY = ('right_gray', (178, 178, 178))
    WHITE = ('white', (255, 255, 250))
    TRANSPARENT_GREEN = ('transparent_green', (0, 51, 0, 128))

    def __init__(self, color_name, color_code):
        self.color_name = color_name
        self.color_code = color_code


BubbleKit = namedtuple('BubbleKit', 'file color color_code')


BUBBLES = [
    BubbleKit(ImageFiles.BALL_BLUE, Colors.BLUE.color_name, Colors.BLUE.color_code),
    BubbleKit(ImageFiles.BALL_GREEN, Colors.YELLOW_GREEN.color_name, Colors.YELLOW_GREEN.color_code),
    BubbleKit(ImageFiles.BALL_PINK, Colors.PINK.color_name, Colors.PINK.color_code),
    BubbleKit(ImageFiles.BALL_PURPLE, Colors.PURPLE.color_name, Colors.PURPLE.color_code),
    BubbleKit(ImageFiles.BALL_RED, Colors.RED.color_name, Colors.RED.color_code),
    BubbleKit(ImageFiles.BALL_SKY, Colors.RIGHT_BLUE.color_name, Colors.RIGHT_BLUE.color_code)]


class Status(Enum):

    READY = auto()
    STAY = auto()
    MOVE = auto()
    CHARGE = auto()
    SHOT = auto()
    GAMEOVER = auto()
    WIN = auto()
    PLAY = auto()
    START = auto()


def round_up(value):
    return int(math.copysign(math.ceil(abs(value)), value))


def round(value):
    return int((value * 2 + 1) // 2)


class Cell:

    __slots__ = ['bubble', 'row', 'col', 'center',
                 'left', 'right', 'top', 'bottom']

    def __init__(self, row, col):
        self.bubble = None
        self.row = row
        self.col = col
        self.calculate_center()
        self.calculate_sides()

    def calculate_sides(self):
        half = BUBBLE_SIZE // 2
        left_top = Point(self.center.x - half, self.center.y - half)
        right_bottom = Point(self.center.x + half, self.center.y + half)
        right_top = Point(self.center.x + half, self.center.y - half)
        left_bottom = Point(self.center.x - half, self.center.y + half)

        self.left = Line(left_top, left_bottom)
        self.right = Line(right_top, right_bottom)
        self.top = Line(left_top, right_top)
        self.bottom = Line(left_bottom, right_bottom)

    def calculate_center(self):
        if self.row % 2 == 0:
            start = X_START_POS
        else:
            start = X_START_POS + BUBBLE_SIZE // 2
        x = start + BUBBLE_SIZE * self.col
        y = Y_START_POS + BUBBLE_SIZE * self.row
        self.center = Point(x, y)

    def move_bubble(self, move_to):
        if not move_to.bubble:
            self.bubble.rect.centerx = move_to.center.x
            self.bubble.rect.centery = move_to.center.y
            move_to.bubble = self.bubble
            self.bubble = None

    def delete_bubble(self):
        if self.bubble:
            self.bubble = self.bubble.kill()


class Shooter:

    def __init__(self, screen, score, droppings):
        self.droppings_group = droppings
        self.screen = screen
        self.score = score
        self.sysfont = pygame.font.SysFont(None, 30)
        self.cells = [[Cell(row, col) for col in range(COLS)] for row in range(ROWS)]
        self.dest = None
        self.target = None
        self.bullet = None
        self.create_launcher()
        self.create_sound()
        self.initialize_game()
        self.game = Status.START

    def initialize_game(self):
        self.bubbles = BUBBLES[:]
        self.colors_count = len(self.bubbles)
        self.is_increase = False
        self.next_bullet = None
        self.create_bubbles(10)
        self.charge()
        self.status = Status.READY

    def create_launcher(self):
        self.launcher = Point(WINDOW.half_width, WINDOW.height)
        self.launcher_angle = 90
        self.radius = self.get_radius(WINDOW.half_width, WINDOW.height)
        self.limit_angle = round_up(
            self.calculate_angle(WINDOW.height, WINDOW.half_width))
        self.bullet_holder = Point(WINDOW.half_width, 635)
        self.create_rects()

    def create_bubbles(self, rows=15):
        for row in range(rows):
            for cell in self.cells[row]:
                kit = self.get_bubble()
                bubble = Bubble(kit.file.path, kit.color, cell.center, self)
                cell.bubble = bubble

    def create_rects(self):
        self.bars = []
        for i in range(5):
            if i > 0:
                # 105, 210, 315, 420, 525
                self.bars.append(Rect(105 * i, 540, 5, 55))

    def create_sound(self):
        self.fanfare = pygame.mixer.Sound(SoundFiles.FANFARE.path)

    def simulate_shoot_right(self, start, end):
        """Yield lines on which a bullet shot to the right first will move.
           Args:
             start (Point): at where a bullet is shot
             end (Point): where a bullet will collid first with the screen right wall.
        """
        is_stop, line = self._simulate_course(start, end)

        if line:
            yield line
        if not is_stop:
            angle = 90 - self.launcher_angle
            for line in self._simulate_bounce_course(angle, end, is_stop, True):
                yield line

    def simulate_shoot_left(self, start, end):
        """Yield lines on which a bullet shot to the left first will move.
           Args:
             start (Point): at where a bullet is shot
             end (Point): where a bullet will collid first with the screen right wall.
        """
        is_stop, line = self._simulate_course(start, end)

        if line:
            yield line
        if not is_stop:
            angle = self.launcher_angle - 90
            for line in self._simulate_bounce_course(angle, end, is_stop, False):
                yield line

    def simulate_shoot_top(self, start, end):
        """Yield a line on which a bullet shot to the top will move.
           Args:
             start (Point): at where a bullet is shot
             end (Point): where a bullet will collid with the top of the screen.
        """
        _, line = self._simulate_course(start, end, True)

        if line:
            yield line

    def _simulate_bounce_course(self, angle, start, is_stop, to_left):
        """Simulate the bullet moving with repeated bounce to the screen walls.
           Args:
             angle (int): reflection angle
             start (Point): where a bullet will collid with the screen walls
             is_stop (bool): True any more lines are not to be drawn.
             to_left (bool): True if bounce from right to left, False if left to right.
        """
        if not is_stop and to_left:
            if (x := WINDOW.width - self.calculate_height(angle, start.y)) >= 0:
                is_stop, line = self._simulate_course(start, Point(x, 0), True)
                if line:
                    yield line
            else:
                bottom = self.calculate_bottom(angle, WINDOW.width)
                left_pt = Point(0, start.y - bottom)
                is_stop, line = self._simulate_course(start, left_pt)
                if line:
                    yield line
                if not is_stop:
                    yield from self._simulate_bounce_course(angle, left_pt, is_stop, False)

        if not is_stop and not to_left:
            if (x := self.calculate_height(angle, start.y)) <= WINDOW.width:
                is_stop, line = self._simulate_course(start, Point(x, 0), True)
                if line:
                    yield line
            else:
                bottom = self.calculate_bottom(angle, WINDOW.width)
                right_pt = Point(WINDOW.width, start.y - bottom)
                is_stop, line = self._simulate_course(start, right_pt)
                if line:
                    yield line
                if not is_stop:
                    yield from self._simulate_bounce_course(angle, right_pt, is_stop, True)

    def _simulate_course(self, start, end, no_bounce=False):
        """Simulate the movement of a bullet.
           Args:
             start (Point): the end of a line at where a bullet will start moving
             end (Point): the end of a line at which a bullet will stop moving
             no_bounce (bool): True if bullet will shoot to the top
           Returns:
             bool: False if more lines have to be continuingly drawn, otherwise True.
             Line: a line on which a bullet will move
        """
        self.dest, self.target = self.find_destination(start, end)
        if (self.dest and self.target) or (self.dest and no_bounce):
            if cross_point := self.find_cross_point(start, end, self.dest):
                return True, Line(start, cross_point)
            return True, Line(start, self.dest.center)
        elif self.dest and not self.target:
            return False, Line(start, end)
        return True, None

    def set_timer(self, seconds):
        last = pygame.time.get_ticks()
        while True:
            now = pygame.time.get_ticks()
            if now - last >= seconds:
                break

    def quit_game(self):
        if len(self.droppings_group.sprites()) == 0:
            if self.status == Status.WIN:
                self.set_timer(1000)
                self.fanfare.play()
            self.game = self.status

    def draw_setting(self):
        pygame.draw.rect(
            self.screen, Colors.DARK_GREEN.color_code, (0, 600, WINDOW.width, 50))
        pygame.draw.circle(
            self.screen, Colors.DARK_GREEN.color_code, self.launcher, 20)
        pygame.draw.circle(self.screen, self.next_bullet.color_code, self.bullet_holder, 4)

        for bar in self.bars:
            pygame.draw.rect(self.screen, Colors.DARK_GREEN.color_code, bar)

        for num, place in zip(['50', '100', '250', '100', '50'], [49, 140, 250, 350, 460]):
            text = self.sysfont.render(num, True, Colors.RIGHT_GRAY.color_code)
            self.screen.blit(text, (place, 540))

    def update(self):
        if self.game == Status.PLAY:
            self.draw_setting()

            if self.status == Status.READY:
                count = self.count_bubbles()
                if count == 0:
                    self.status = Status.WIN

                if count > 0 and self.bullet.status == Status.STAY:
                    if count <= 20:
                        self.change_bubbles(count)
                    if self.is_increase:
                        self.increase_bubbles(4)
                        self.is_increase = False

                if any(cell.bubble for cell in self.cells[-1]):
                    self.status = Status.GAMEOVER

            if self.status in {Status.WIN, Status.GAMEOVER}:
                self.quit_game()

            if 0 < self.launcher_angle <= self.limit_angle:
                y = WINDOW.height - self.calculate_height(self.launcher_angle, WINDOW.half_width)
                pt = Point(WINDOW.width, y)
                self.course = [line for line in self.simulate_shoot_right(self.launcher, pt)]
            elif self.launcher_angle >= 180 - self.limit_angle:
                y = WINDOW.height - self.calculate_height(180 - self.launcher_angle, WINDOW.half_width)
                pt = Point(0, y)
                self.course = [line for line in self.simulate_shoot_left(self.launcher, pt)]
            else:
                if self.limit_angle < self.launcher_angle <= 90:
                    x = WINDOW.half_width + self.calculate_height(90 - self.launcher_angle, WINDOW.height)
                elif 90 < self.launcher_angle < 180 - self.limit_angle:
                    x = WINDOW.half_width - self.calculate_height(self.launcher_angle - 90, WINDOW.height)
                self.course = [line for line in self.simulate_shoot_top(self.launcher, Point(x, 0))]

            if self.dest:
                for line in self.course:
                    pygame.draw.line(self.screen, Colors.DARK_GREEN.color_code, line.start, line.end, 2)

            if self.status == Status.CHARGE:
                self.charge()
                self.status = Status.READY

    def get_bubble(self):
        return random.choice(self.bubbles)

    def charge(self):
        if not self.next_bullet:
            if self.bullet:
                self.bullet = self.bullet.kill()
            bullet = self.get_bubble()
        else:
            bullet = self.next_bullet

        self.next_bullet = self.get_bubble()
        self.bullet = Bullet(
            bullet.file.path, bullet.color, self)

    def _find_cross_point(self, pt1, pt2, pt3, pt4):
        a0 = pt2.x - pt1.x
        b0 = pt2.y - pt1.y
        a2 = pt4.x - pt3.x
        b2 = pt4.y - pt3.y

        d = a0 * b2 - a2 * b0
        sn = b2 * (pt3.x - pt1.x) - a2 * (pt3.y - pt1.y)
        x = round(pt1.x + a0 * sn / d)
        y = round(pt1.y + b0 * sn / d)

        return Point(x, y)

    def find_cross_point(self, pt1, pt2, cell):
        for line in (cell.bottom, cell.right, cell.left, cell.top):
            if self._is_crossing(pt1, pt2, line.start, line.end):
                pt = self._find_cross_point(pt1, pt2, line.start, line.end)
                x = round((pt.x + cell.center.x) / 2)
                y = round((pt.y + cell.center.y) / 2)
                return Point(x, y)
        return None

    def _is_crossing(self, pt1, pt2, pt3, pt4):
        tc1 = (pt1.x - pt2.x) * (pt3.y - pt1.y) + (pt1.y - pt2.y) * (pt1.x - pt3.x)
        tc2 = (pt1.x - pt2.x) * (pt4.y - pt1.y) + (pt1.y - pt2.y) * (pt1.x - pt4.x)
        td1 = (pt3.x - pt4.x) * (pt1.y - pt3.y) + (pt3.y - pt4.y) * (pt3.x - pt1.x)
        td2 = (pt3.x - pt4.x) * (pt2.y - pt3.y) + (pt3.y - pt4.y) * (pt3.x - pt2.x)

        return tc1 * tc2 < 0 and td1 * td2 < 0

    def is_crossing(self, pt1, pt2, cell):
        if any(self._is_crossing(pt1, pt2, line.start, line.end)
                for line in (cell.bottom, cell.right, cell.left, cell.top)):
            return True
        return False

    def _trace(self, start, end):
        """Follow a simulation line from bottom to top, and yield
           Cell that intersects the simulation line.
           Args:
             start (Point): one end of a simulation line
             end (Point): the another end of a simulation line
        """
        target = None
        step = 1 if start.x >= end.x else -1
        for cells in self.cells[::-1]:
            empty = None
            for cell in cells[::step]:
                if self.is_crossing(start, end, cell):
                    if not cell.bubble and not empty:
                        empty = cell
                    if cell.bubble:
                        target = cell
                        break
            if not target and empty:
                yield empty
            elif target:
                yield target
                break

    def _scan(self, target):
        for cell in self.scan_bubbles(target.row, target.col):
            if not cell.bubble:
                yield cell

    def select_compare_function(self, target, dest):
        if target.center.x <= dest.center.x:
            return lambda target, cell: True if target.center.x <= cell.center.x else False
        else:
            return lambda target, cell: True if target.center.x > cell.center.x else False

    def _find_destination(self, target, dest):
        """Return Cell having no bubble, around the target.
           Arges:
             target (Cell): cell having bubble a bullet will collide with
             dest (Cell):  cell into which a bullet will go enter
        """
        compare_x = self.select_compare_function(target, dest)

        if cancidates := set(cell for cell in self._scan(target) if compare_x(target, cell)):
            candidate = min(
                cancidates,
                key=lambda x: self.calculate_distance(x.center, dest.center))
            return candidate
        return None

    def find_destination(self, start, end):
        """Return a destination Cell into which a bullet go, and
           a target Cell with which the bullet will collid.
           Args:
             start (Point): one end of a simulation line
             end (Point): the another end of a simulation line
        """
        if traced := [cell for cell in self._trace(start, end)]:
            if len(traced) == 1:
                return None, None
            elif not any(cell.bubble for cell in traced):
                return traced[-1], None
            else:
                dest, target = traced[-2:]
                if not any(cell.bubble for cell in self.scan_bubbles(dest.row, dest.col) if cell.bubble):
                    dest = self._find_destination(target, dest)
                return dest, target
        return None, None

    def scan_bubbles(self, row, col):
        if row == 0:
            if row + 1 < ROWS and col - 1 >= 0:
                yield self.cells[row + 1][col - 1]
            if row + 1 < ROWS:
                yield self.cells[row + 1][col]
            if col - 1 >= 0:
                yield self.cells[row][col - 1]
            if col + 1 < COLS:
                yield self.cells[row][col + 1]
        elif row % 2 == 0:
            if row + 1 < ROWS and col - 1 >= 0:
                yield self.cells[row + 1][col - 1]
            if row + 1 < ROWS:
                yield self.cells[row + 1][col]
            if col - 1 >= 0:
                yield self.cells[row][col - 1]
            if col + 1 < COLS:
                yield self.cells[row][col + 1]
            if row - 1 >= 0 and col - 1 >= 0:
                yield self.cells[row - 1][col - 1]
            if row - 1 >= 0:
                yield self.cells[row - 1][col]
        else:
            if row + 1 < ROWS and col + 1 < COLS:
                yield self.cells[row + 1][col + 1]
            if row + 1 < ROWS:
                yield self.cells[row + 1][col]
            if col + 1 < COLS:
                yield self.cells[row][col + 1]
            if col - 1 >= 0:
                yield self.cells[row][col - 1]
            if row - 1 >= 0 and col + 1 < COLS:
                yield self.cells[row - 1][col + 1]
            if row - 1 >= 0:
                yield self.cells[row - 1][col]

    def calculate_distance(self, pt1, pt2):
        return ((pt2.x - pt1.x) ** 2 + (pt2.y - pt1.x) ** 2) ** 0.5

    def get_radius(self, bottom, height):
        return (bottom ** 2 + height ** 2) ** 0.5

    def calculate_angle(self, height, bottom):
        return math.degrees(math.atan2(height, bottom))

    def calculate_height(self, angle, bottom):
        return round_up(math.tan(math.radians(angle)) * bottom)

    def calculate_bottom(self, angle, height):
        return round_up(height / math.tan(math.radians(angle)))

    def move_right(self):
        self.launcher_angle -= 2
        if self.launcher_angle < 5:
            self.launcher_angle = 5

    def move_left(self):
        self.launcher_angle += 2
        if self.launcher_angle > 175:
            self.launcher_angle = 175

    def shoot(self):
        if self.status == Status.READY and self.dest:
            self.status = Status.SHOT
            self.bullet.shoot()

    def increase(self):
        self.is_increase = True

    def increase_bubbles(self, rows):
        for cells in self.cells[::-1]:
            for cell in cells:
                if cell.bubble:
                    if (row := cell.row + rows) < ROWS:
                        move_to = self.cells[row][cell.col]
                        cell.move_bubble(move_to)
        self.create_bubbles(rows)

    def delete_bubbles(self):
        for cells in self.cells:
            for cell in cells:
                cell.delete_bubble()

    def change_bubbles(self, count):
        if self.colors_count > 1:
            self.colors_count -= 1
        self.bubbles = random.sample(BUBBLES, self.colors_count)
        self.next_bullet = None
        self.charge()
        self.status = Status.READY

        if len(self.bubbles) <= 2:
            self.delete_bubbles()
            self.create_bubbles(10)
        else:
            self.increase_bubbles(10)

    def count_bubbles(self):
        total = sum(
            sum(True if cell.bubble else False for cell in cells) for cells in self.cells)
        return total


class Score:

    def __init__(self, screen):
        self.sysfont = pygame.font.SysFont(None, 30)
        self.screen = screen
        self.score = 0

    def add(self, x):
        if x < 105:
            self.score += 50
        elif 110 < x < 210:
            self.score += 100
        elif 215 < x < 315:
            self.score += 250
        elif 320 < x < 420:
            self.score += 100
        elif x > 425:
            self.score += 50

    def update(self):
        text = self.sysfont.render(str(self.score), True, Colors.RIGHT_GRAY.color_code)
        self.screen.blit(text, (10, 615))


class BaseBubble(pygame.sprite.Sprite):

    def __init__(self, file, color, center, shooter):
        super().__init__(self.containers)
        self.image = pygame.image.load(file).convert_alpha()
        self.image = pygame.transform.scale(self.image, (BUBBLE_SIZE, BUBBLE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.centerx = center.x
        self.rect.centery = center.y
        self.speed_x = 0
        self.speed_y = 0
        self.color = color
        self.status = Status.STAY
        self.shooter = shooter
        self.create_sound()

    def create_sound(self):
        self.sound_pop = pygame.mixer.Sound(SoundFiles.SOUND_POP.path)

    def move(self):
        self.speed_x = random.randint(-5, 5)
        self.speed_y = random.randint(-5, 5) or 2

    def update(self):
        if self.status == Status.MOVE:
            self.rect.centerx += self.speed_x
            self.rect.centery += self.speed_y

            if self.rect.left < WINDOW.left:
                self.sound_pop.play()
                self.rect.left = WINDOW.left
                self.speed_x = -self.speed_x

            if self.rect.right > WINDOW.right:
                self.sound_pop.play()
                self.rect.right = WINDOW.right
                self.speed_x = -self.speed_x

            if self.rect.top < WINDOW.top:
                self.sound_pop.play()
                self.rect.top = WINDOW.top
                self.speed_y = -self.speed_y

            if (idx := self.rect.collidelist(self.shooter.bars)) > -1:
                self.sound_pop.play()
                bar = self.shooter.bars[idx]
                if self.rect.left <= bar.right < self.rect.right:
                    self.rect.left = bar.right
                    self.speed_x = -self.speed_x
                if self.rect.right >= bar.left > self.rect.left:
                    self.rect.right = bar.left
                    self.speed_x = -self.speed_x
                if bar.left > self.rect.left and bar.right < self.rect.right:
                    self.rect.bottom = bar.top + 10

            if self.rect.bottom > WINDOW.height:
                self.sound_pop.play()
                self.shooter.score.add(self.rect.centerx)
                self.kill()


class Bubble(BaseBubble):

    def __init__(self, file, color, center, shooter):
        super().__init__(file, color, center, shooter)


class Bullet(BaseBubble):

    def __init__(self, file, color, shooter):
        super().__init__(file, color, shooter.launcher, shooter)
        self.idx = 0

    def decide_positions(self, start, end, compare_position):
        dx = end.x - start.x
        dy = end.y - start.y
        distance = (dx**2 + dy ** 2) ** 0.5
        vx = dx * 10 / distance
        vy = dy * 10 / distance
        x = start.x + vx
        y = start.y + vy

        if compare_position(end, x, y):
            pass_pt = Point(x, y)
            yield pass_pt
            yield from self.decide_positions(pass_pt, end, compare_position)
        else:
            yield self.shooter.dest.center

    def select_func(self, start, end):
        if start.x == end.x:
            return lambda end, x, y: True if end.y < y else False
        elif start.x > end.x:
            return lambda end, x, y: True if x > end.x else False
        else:
            return lambda end, x, y: True if end.x > x else False

    def simulate_course(self):
        """Calculate points which a bullet pass through.The last point in the Shooter.course
           is the cross-point with one of the sides of a Cell. So replace it to the center
           point of the Cell.
        """
        last = self.shooter.course[-1]
        bullet_course = self.shooter.course[:-1] + [Line(last.start, self.shooter.dest.center)]

        for line in bullet_course:
            compare_position = self.select_func(line.start, line.end)
            for pt in self.decide_positions(line.start, line.end, compare_position):
                yield pt

    def shoot(self):
        self.course = [pt for pt in self.simulate_course()]
        self.status = Status.SHOT

    def update(self):
        if self.status == Status.MOVE:
            super().update()

        if self.status == Status.SHOT:
            pt = self.course[self.idx]
            self.rect.centerx = pt.x
            self.rect.centery = pt.y

            if self.rect.left < WINDOW.left:
                self.sound_pop.play()
                self.rect.left = WINDOW.left

            if self.rect.right > WINDOW.right:
                self.sound_pop.play()
                self.rect.right = WINDOW.right

            if self.idx + 1 < len(self.course):
                self.idx += 1
            else:
                self.shooter.dest.bubble = self
                self.sound_pop.play()
                if not self.drop_same_color_bubbles():
                    self.status = Status.STAY
                self.drop_floating_bubbles()
                self.shooter.status = Status.CHARGE

    def drop_bubbles(self, cells):
        for cell in cells:
            # to display dropping bubbles on top of all the other bubbles.
            self.shooter.droppings_group.add(cell.bubble)
            cell.bubble.move()
            cell.bubble.status = Status.MOVE
            cell.bubble = None

    def _get_same_color(self, cell, cells):
        for cell in self.shooter.scan_bubbles(cell.row, cell.col):
            if cell.bubble and cell.bubble.color == self.color:
                if cell not in cells:
                    cells.add(cell)
                    self._get_same_color(cell, cells)

    def drop_same_color_bubbles(self):
        """Drop bubbles that are the same color with a bullet.
           Return False if the same color bubbles are not found.
        """
        cells = set()
        self._get_same_color(self.shooter.dest, cells)
        if len(cells) >= 3:
            self.drop_bubbles(cells)
            return True
        return False

    def _get_floating(self, cell, cells):
        for cell in self.shooter.scan_bubbles(cell.row, cell.col):
            if cell.bubble:
                if cell not in cells:
                    cells.add(cell)
                    self._get_floating(cell, cells)

    def drop_floating_bubbles(self):
        """Get bubbles that are connected to the top to drop them.
        """
        top = [cell for cell in self.shooter.cells[0] if cell.bubble]
        connected = set(top)
        for cell in top:
            self._get_floating(cell, connected)
        bubbles = set(cell for cells in self.shooter.cells for cell in cells if cell.bubble)
        if diff := bubbles - connected:
            self.drop_bubbles(diff)


class StartButton(pygame.sprite.Sprite):

    def __init__(self, file, screen, shooter):
        super().__init__(self.containers)
        self.screen = screen
        self.shooter = shooter
        self.image = pygame.image.load(file).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.create_surface()
        self.set_message_font()
        self.create_texts()

    def create_surface(self):
        self.surface = pygame.Surface(
            (SCREEN.width, SCREEN.height), flags=pygame.SRCALPHA)
        self.surface.fill(Colors.TRANSPARENT_GREEN.color_code)

    def get_font(self):
        for size in range(40, 51):
            yield pygame.font.SysFont(None, size)
        for size in range(50, 41, -1):
            yield pygame.font.SysFont(None, size)

    def set_message_font(self):
        self.idx = -1
        self.fonts = [font for font in self.get_font()]

    def scale_message(self, y, text, color):
        font = self.fonts[self.idx]
        message = font.render(text, True, color)
        x, _ = font.size(text)
        self.screen.blit(message, ((WINDOW.width - x) // 2, y))
        self.idx += 1
        if self.idx >= len(self.fonts):
            self.idx = -1
        pygame.time.wait(100)


class RetryGame(StartButton):

    def __init__(self, file, screen, shooter):
        super().__init__(file, screen, shooter)
        self.rect.centerx = GAME_RETRY_BUTTON.x
        self.rect.centery = GAME_RETRY_BUTTON.y

    def create_texts(self):
        gameover_font = pygame.font.SysFont(None, 60)
        self.gameover = gameover_font.render(
            'GAME OVER', True, Colors.WHITE.color_code)
        self.score_font = pygame.font.SysFont(None, 50)
        self.score = 'Score: {}'
        self.text = 'CONTINUE'

    def update(self):
        self.screen.blit(self.surface, SURFACE_LEFT)
        score = self.score_font.render(
            self.score.format(self.shooter.score.score), True, Colors.WHITE.color_code)
        self.screen.blit(score, FINAL_SCORE)
        if self.shooter.game == Status.GAMEOVER:
            self.screen.blit(self.gameover, GAMEOVER_TITLE)
        self.scale_message(CONTINUE_Y, self.text, Colors.PINK.color_code)

    def click(self, x, y):
        if self.rect.collidepoint(x, y):
            self.shooter.game = Status.PLAY
            self.shooter.delete_bubbles()
            self.shooter.initialize_game()


class StartGame(StartButton):

    def __init__(self, file, screen, shooter):
        super().__init__(file, screen, shooter)
        self.rect.centerx = GAME_START_BUTTON.x
        self.rect.centery = GAME_START_BUTTON.y

    def create_texts(self):
        title_font = pygame.font.SysFont(None, 60)
        self.title = title_font.render(
            'Bubble Shooter Game', True, Colors.WHITE.color_code)
        self.text = 'START'

    def update(self):
        self.screen.blit(self.surface, SURFACE_LEFT)
        self.screen.blit(self.title, GAME_TITLE)
        self.scale_message(START_Y, self.text, Colors.PINK.color_code)

    def click(self, x, y):
        if self.rect.collidepoint(x, y):
            self.shooter.game = Status.PLAY


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    pygame.display.set_caption('PyBubbleShooter')

    bubbles = pygame.sprite.RenderUpdates()
    droppings = pygame.sprite.RenderUpdates()
    start = pygame.sprite.RenderUpdates()
    retry = pygame.sprite.RenderUpdates()

    Bubble.containers = bubbles
    Bullet.containers = bubbles
    StartGame.containers = start
    RetryGame.containers = retry

    score = Score(screen)
    bubble_shooter = Shooter(screen, score, droppings)

    start_game = StartGame(ImageFiles.BUTTON_START.path, screen, bubble_shooter)
    retry_game = RetryGame(ImageFiles.BUTTON_START.path, screen, bubble_shooter)

    clock = pygame.time.Clock()

    bubble_event = pygame.USEREVENT + 1
    # pygame.time.set_timer(bubble_event, 15000)
    pygame.time.set_timer(bubble_event, 60000 * 3)
    pygame.key.set_repeat(100, 100)

    while True:
        clock.tick(60)
        screen.fill(Colors.GREEN.color_code)

        bubble_shooter.update()
        bubbles.update()
        bubbles.draw(screen)

        if bubble_shooter.game == Status.START:
            start.update()
            start.draw(screen)
        elif bubble_shooter.game == Status.PLAY:
            droppings.draw(screen)
            score.update()
        elif bubble_shooter.game in (Status.GAMEOVER, Status.WIN):
            retry.update()
            retry.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == bubble_event:
                bubble_shooter.increase()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if bubble_shooter.game == Status.START:
                    start_game.click(*event.pos)
                if bubble_shooter.game in (Status.WIN, Status.GAMEOVER):
                    retry_game.click(*event.pos)
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    bubble_shooter.move_right()
                if event.key == K_LEFT:
                    bubble_shooter.move_left()
                if event.key == K_SPACE:
                    bubble_shooter.shoot()
        pygame.display.update()


if __name__ == '__main__':
    main()