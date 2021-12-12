import pygame
import sys
from pygame.locals import QUIT, K_DOWN, K_RIGHT, K_LEFT, K_UP, KEYDOWN, MOUSEBUTTONDOWN, Rect
from random import randint


SCREEN_WIDTH = 410

SCREEN = Rect(0, 0, SCREEN_WIDTH, 600)
ROW_START = 10
COL_START = 10

BUBBLE_SIZE = 20

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
        self.line_x = SCREEN_WIDTH / 2
        self.line_y = 15 * BUBBLE_SIZE
        self.bubbles = [[0 for _ in range(20)] for _ in range(15)]
        self.create_bubbles()

    def create_bubbles(self):
        for row in range(15):
            if row % 2 == 0:
                col_start = COL_START
            else:
                col_start = COL_START + BUBBLE_SIZE / 2
            row_start = ROW_START + BUBBLE_SIZE * row
            for col in range(20):
                key = randint(0, 5)
                Bubble(
                    FILES[key], col_start + BUBBLE_SIZE * col, row_start)
                self.bubbles[row][col] = 1
        key = randint(0, 5)
        Bubble(
            FILES[key], 205, 580)

    def update(self):
        # pygame.draw.line(self.screen, DARK_GREEN, (205, 570), (205, 360), 3)
        pygame.draw.lines(self.screen, DARK_GREEN, False, [(205, 570), (self.line_x, self.line_y)], 3)
        # pygame.draw.lines(self.screen, DARK_GREEN, False, [(205, 570), (205, 360), (20, 360)], 3)

    def move_right(self):
        self.line_x += BUBBLE_SIZE
        if self.line_x > SCREEN_WIDTH:
            self.line_y += BUBBLE_SIZE
            if self.line_y > 550:
                self.line_y -= BUBBLE_SIZE
        if self.line_x < 0:
            self.line_y -= BUBBLE_SIZE

    def move_left(self):
        self.line_x -= BUBBLE_SIZE
        if self.line_x < 0:
            self.line_y += BUBBLE_SIZE
            if self.line_y > 550:
                self.line_y -= BUBBLE_SIZE
        if self.line_x > SCREEN_WIDTH:
            self.line_y -= BUBBLE_SIZE


class Bubble(pygame.sprite.Sprite):

    def __init__(self, file_path, x, y):
        super().__init__(self.containers)
        # self.screen = screen
        self.image = pygame.image.load(file_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    pygame.display.set_caption('PyBubbleShooter')
    bubbles = pygame.sprite.RenderUpdates()
    Bubble.containers = bubbles
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
                    print('up')


        pygame.display.update()


if __name__ == '__main__':
    main()
