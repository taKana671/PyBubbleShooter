import pygame
import sys
from pygame.locals import QUIT, K_DOWN, K_RIGHT, K_LEFT, K_UP, KEYDOWN, MOUSEBUTTONDOWN, Rect


SCREEN = Rect(0, 0, 700, 600)
COLOR_GREEN = (0, 100, 0)


class Ball(pygame.sprite.Sprite):

    def __init__(self, file_path):
        super().__init__(self.containers)
        # self.screen = screen
        self.image = pygame.image.load(file_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.centerx = 80
        self.rect.centery = 80


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    pygame.display.set_caption('PyBubbleShooter')
    balls = pygame.sprite.RenderUpdates()
    Ball.containers = balls
    clock = pygame.time.Clock()
    ball = Ball('images/ball_pink.png')


    while True:
        clock.tick(60)
        screen.fill(COLOR_GREEN)

        balls.update()
        balls.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()

if __name__ == '__main__':
    main()
