import math
import pygame
import sys
from collections import namedtuple
from enum import Enum, auto
from pygame.locals import QUIT, K_DOWN, K_RIGHT, K_LEFT, K_UP, KEYDOWN, MOUSEBUTTONDOWN, Rect
from random import randint


# screen
SCREEN = Rect(0, 0, 526, 650)
SCREEN_H = 600
SCREEN_W = 526
# SCREEN = Rect(0, 0, 526, 600)
# SCREEN_H = SCREEN.height
# SCREEN_W = SCREEN.width
HALF_SCREEN_W = SCREEN.width // 2

Y_START_POS = 15
X_START_POS = 16

ROWS = 20
COLS = 17

BUBBLE_SIZE = 30

# color
COLOR_GREEN = (0, 100, 0)
DARK_GREEN = (0, 80, 0)
RIGHT_GRAY = (178, 178, 178)


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


Point = namedtuple('Point', 'x y')
Line = namedtuple('Line', 'start end')


def round_up(value):
    return int(math.copysign(math.ceil(abs(value)), value))


def round(value):
    return int((value * 2 + 1) // 2)


class Cell:

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


class Shooter:

    def __init__(self, screen):
        self.screen = screen
        self.sysfont = pygame.font.SysFont(None, 30)
        self.reflection_angle = None
        self.dest = None
        self.target = None
        self.cells = [[Cell(row, col) for col in range(COLS)] for row in range(ROWS)]
        self.create_launcher()
        self.create_rects()
        self.create_bubbles(10)
        self.status = Status.READY

    def create_launcher(self):
        self.launcher = Point(HALF_SCREEN_W, SCREEN_H)
        self.launcher_angle = 90
        self.radius = self.get_radius(HALF_SCREEN_W, SCREEN_H)
        self.limit_angle = round_up(
            self.calculate_angle(SCREEN_H, HALF_SCREEN_W))

    def create_bubbles(self, rows=15):
        for row in range(rows):
            for col, cell in enumerate(self.cells[row]):
                i = randint(0, 5)
                kit = BUBBLES[i]
                bubble = Bubble(kit.file, kit.color, cell.center, self.bars)
                cell.bubble = bubble
        self.charge()

    def create_rects(self):
        self.bars = []
        for i in range(6):
            if i > 0:
                self.bars.append(Rect(105 * i, 565, 5, 30))

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
            if (x := SCREEN_W - self.calculate_height(angle, start.y)) >= 0:
                is_stop, line = self._simulate_course(start, Point(x, 0), True)
                if line:
                    yield line
            else:
                bottom = self.calculate_bottom(angle, SCREEN_W)
                left_pt = Point(0, start.y - bottom)
                is_stop, line = self._simulate_course(start, left_pt)
                if line:
                    yield line
                if not is_stop:
                    yield from self._simulate_bounce_course(angle, left_pt, is_stop, False)

        if not is_stop and not to_left:
            if (x := self.calculate_height(angle, start.y)) <= SCREEN_W:
                is_stop, line = self._simulate_course(start, Point(x, 0), True)
                if line:
                    yield line
            else:
                bottom = self.calculate_bottom(angle, SCREEN_W)
                right_pt = Point(SCREEN_W, start.y - bottom)
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

    def draw_setting(self):
        pygame.draw.rect(self.screen, DARK_GREEN, (0, 600, SCREEN_W, 50))
        pygame.draw.circle(
            self.screen, DARK_GREEN, self.launcher, 20)

        for bar in self.bars:
            pygame.draw.rect(self.screen, DARK_GREEN, bar)

        for num, place in zip(['50', '100', '250', '100', '50'], [51, 140, 250, 350, 460]):
            text = self.sysfont.render(num, True, RIGHT_GRAY)
            self.screen.blit(text, (place, 540))

    def update(self):
        self.draw_setting()

        if 0 < self.launcher_angle <= self.limit_angle:
            y = SCREEN_H - self.calculate_height(self.launcher_angle, HALF_SCREEN_W)
            pt = Point(SCREEN_W, y)
            self.course = [line for line in self.simulate_shoot_right(self.launcher, pt)]
        elif self.launcher_angle >= 180 - self.limit_angle:
            y = SCREEN_H - self.calculate_height(180 - self.launcher_angle, HALF_SCREEN_W)
            pt = Point(0, y)
            self.course = [line for line in self.simulate_shoot_left(self.launcher, pt)]
        else:
            if self.limit_angle < self.launcher_angle <= 90:
                x = HALF_SCREEN_W + self.calculate_height(90 - self.launcher_angle, SCREEN_H)
            elif 90 < self.launcher_angle < 180 - self.limit_angle:
                x = HALF_SCREEN_W - self.calculate_height(self.launcher_angle - 90, SCREEN_H)
            self.course = [line for line in self.simulate_shoot_top(self.launcher, Point(x, 0))]

        if self.dest:
            for line in self.course:
                pygame.draw.line(self.screen, DARK_GREEN, line.start, line.end, 2)

        if self.status == Status.CHARGE:
            self.charge()
            self.status = Status.READY

    def charge(self):
        i = randint(0, 5)
        kit = BUBBLES[i]
        self.bullet = Bullet(kit.file, kit.color, self.launcher, self)

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
        for line in (cell.bottom, cell.right, cell.left, cell.top):
            if self._is_crossing(pt1, pt2, line.start, line.end):
                return True
        return False

    def _trace(self, pt1, pt2):
        """Yield cells on the simulation line from bottom to top.
           Args:
             pt1 (Point): one end of a simulation line
             pt2 (Point): the another end of a simulation line
        """
        is_stop = False
        for cells in self.cells[::-1]:
            for cell in cells:
                if self.is_crossing(pt1, pt2, cell):
                    yield cell
                    if cell.bubble:
                        is_stop = True
                    break
            if is_stop:
                break

    def _find_destination(self, target, dest):
        """Return Cell having no bubble, around the target.
           Arges:
             target (Cell): having bubble a bullet will collide with
             dest (Cell):  into which a bullet will go enter
        """
        if neighbors := [cell for cell in self.scan_bubbles(target.row, target.col) if not cell.bubble]:
            candidate = min(
                neighbors,
                key=lambda x: self.calculate_distance(x.center, dest.center))
            return candidate
        return None

    def find_destination(self, pt1, pt2):
        """Return a destination Cell into which a bullet go, and
           a target Cell with which the bullet will collid.
           Args:
             pt1 (Point): one end of a simulation line
             pt2 (Point): the another end of a simulation line
        """
        if traced := [cell for cell in self._trace(pt1, pt2)]:
            # print([(c.row, c.col) for c in traced])
            if len(traced) == 1:
                return None, None
            elif not any(cell.bubble for cell in traced):
                return traced[-1], None
            else:
                dest, target = traced[-2:]
                if not any(cell for cell in self.scan_bubbles(dest.row, dest.col) if cell.bubble):
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
        if row % 2 == 0:
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
        # if self.bullet.status == Status.READY:
        if self.status == Status.READY and self.dest:
            self.status = Status.SHOT
            self.bullet.shoot()


class BaseBubble(pygame.sprite.Sprite):

    def __init__(self, file, color, center, bars):
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
        self.bars = bars

    def move(self):
        self.speed_x = randint(-5, 5)
        self.speed_y = 5

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

            if bars := self.rect.collidelist(self.bars):
                print(bars)

            if self.rect.bottom > SCREEN_H:
                self.kill()


class Bubble(BaseBubble):

    def __init__(self, file, color, center, bars):
        super().__init__(file, color, center, bars)


class Bullet(BaseBubble):

    def __init__(self, file, color, center, shooter):
        super().__init__(file, color, center, shooter.bars)
        self.shooter = shooter
        self.idx = 0

    def decide_positions(self, start, end):
        dx = end.x - start.x
        dy = end.y - start.y
        distance = (dx**2 + dy ** 2) ** 0.5
        vx = dx * 10 / distance
        vy = dy * 10 / distance
        x = start.x + vx
        y = start.y + vy

        if self.is_going(x, y):
            pass_pt = Point(x, y)
            yield pass_pt
            yield from self.decide_positions(pass_pt, end)
        else:
            yield self.shooter.dest.center

    def is_going(self, x, y):
        """Override before calling decide_position method.
        """

    def select_func(self, start, end):
        if start.x == end.x:
            return lambda x, y: True if end.y < y else False
        elif start.x > end.x:
            return lambda x, y: True if x > end.x else False
        else:
            return lambda x, y: True if end.x > x else False

    def simulate_course(self):
        last = self.shooter.course[-1]
        bullet_course = self.shooter.course[:-1] + [Line(last.start, self.shooter.dest.center)]

        for line in bullet_course:
            func = self.select_func(line.start, line.end)
            self.is_going = func
            for pt in self.decide_positions(line.start, line.end):
                yield pt

    def shoot(self):
        self.course = [pt for pt in self.simulate_course()]
        self.status = Status.LAUNCHED

    def update(self):
        if self.status == Status.MOVE:
            super().update()

        if self.status == Status.LAUNCHED:
            pt = self.course[self.idx]
            self.rect.centerx = pt.x
            self.rect.centery = pt.y

            if self.rect.left < SCREEN.left:
                self.rect.left = SCREEN.left

            if self.rect.right > SCREEN.right:
                self.rect.right = SCREEN.right

            if self.idx + 1 < len(self.course):
                self.idx += 1
            else:
                self.shooter.dest.bubble = self
                self.status = Status.STAY

                self.drop_same_color_bubbles()
                self.drop_floating_bubbles()
                self.shooter.status = Status.CHARGE

    def drop_bubbles(self, cells):
        for cell in cells:
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
        """Get bubbles that are the same color with a bullet to drop them.
        """
        cells = set()
        self._get_same_color(self.shooter.dest, cells)
        if len(cells) >= 3:
            self.drop_bubbles(cells)

    def _get_floating(self, cell, cells):
        for cell in self.shooter.scan_bubbles(cell.row, cell.col):
            if cell.bubble:
                if cell not in cells:
                    cells.add(cell)
                    self._get_floating(cell, cells)

    def drop_floating_bubbles(self):
        """Get bubbles that are connected to the top to drop them.
        """
        if top := [cell for cell in self.shooter.cells[0] if cell.bubble]:
            connected = set(top)
            for cell in top:
                self._get_floating(cell, connected)
            bubbles = set(cell for cells in self.shooter.cells for cell in cells if cell.bubble)
            diff = bubbles - connected
            self.drop_bubbles(diff)


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    pygame.display.set_caption('PyBubbleShooter')
    bubbles = pygame.sprite.RenderUpdates()
    bullets = pygame.sprite.RenderUpdates()
    Bubble.containers = bubbles
    Bullet.containers = bullets
    bubble_shooter = Shooter(screen)
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