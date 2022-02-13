import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from unittest import TestCase, main, mock


from pybubble_shooter import (BaseBubble, Score, Shooter, Point, Line,
    ROWS, COLS, Cell, BUBBLES, Status)


class BasicTest(TestCase):

    def setUp(self):
        BaseBubble.containers = mock.MagicMock()
        mock.patch('pybubble_shooter.pygame.image.load').start()
        mock.patch('pybubble_shooter.pygame.mixer.Sound').start()
        mock.patch('pybubble_shooter.pygame.transform.scale').start()
        mock.patch('pybubble_shooter.pygame.sprite.Sprite.kill').start()

    def tearDown(self):
        mock.patch.stopall()

    def get_cell(self, bubble):
        cell = mock.create_autospec(
            spec=Cell,
            spec_set=True,
            instance=True,
            row=3,
            col=4,
            bubble=bubble,
            center=Point(106, 75),
            left=Line(Point(91, 60), Point(91, 90)),
            right=Line(Point(121, 60), Point(121, 90)),
            top=Line(Point(91, 60), Point(121, 60)),
            bottom=Line(Point(91, 90), Point(121, 90))
        )
        return cell


class BaseBubbleTestCase(BasicTest):
    """Tests for BaseBubble class.
    """

    def setUp(self):
        super().setUp()
        mock_score = mock.patch('pybubble_shooter.Score', speck=True).start()
        self.bar = mock.MagicMock()
        shooter = mock.create_autospec(
            spec=Shooter, instance=True, bars=[self.bar], score=mock_score)
        self.bubble = BaseBubble('test.png', 'red', Point(300, 300), shooter)
        self.bubble.status = Status.MOVE

    def reset_bubble_rect(self, left, right, top, bottom, collide):
        self.bubble.rect.configure_mock(
            **dict(left=left, right=right, top=top, bottom=bottom))
        self.bubble.rect.collidelist.return_value = collide

    def test_move(self):
        """Test that speed_y is 2 if random.randint returns 0.
        """
        tests = [
            [(3, -2), (3, -2)],
            [(0, 4), (0, 4)],
            [(-4, 0), (-4, 2)]
        ]
        with mock.patch('pybubble_shooter.random.randint') as mock_randint:
            for return_values, expect in tests:
                with self.subTest():
                    mock_randint.side_effect = return_values
                    self.bubble.move()
                    self.assertEqual(
                        (self.bubble.speed_x, self.bubble.speed_y), expect)

    def test_update_left(self):
        """Test that rect.left and speed_x are changed
           when rect.left < WINDOW.left.
        """
        self.reset_bubble_rect(left=-10, right=20, top=200, bottom=230, collide=-1)

        with mock.patch.object(self.bubble, 'speed_x', -3), \
                mock.patch.object(self.bubble, 'speed_y', 3):
            self.bubble.update()
            self.assertEqual((self.bubble.rect.centerx, self.bubble.rect.centery), (297, 303))
            self.assertEqual((self.bubble.speed_x, self.bubble.speed_y), (3, 3))
            self.assertEqual(self.bubble.rect.left, 0)
            self.bubble.sound_pop.play.assert_called_once()

    def test_update_right(self):
        """Test that rect.right and speed_x are changed
           when rect.right > WINDOW.right.
        """
        self.reset_bubble_rect(left=506, right=536, top=200, bottom=230, collide=-1)

        with mock.patch.object(self.bubble, 'speed_x', 3), \
                mock.patch.object(self.bubble, 'speed_y', 3):
            self.bubble.update()
            self.assertEqual((self.bubble.rect.centerx, self.bubble.rect.centery), (303, 303))
            self.assertEqual((self.bubble.speed_x, self.bubble.speed_y), (-3, 3))
            self.bubble.sound_pop.play.assert_called_once()
            self.assertEqual(self.bubble.rect.right, 526)

    def test_update_top(self):
        """Test that rect.top and speed_y are changed
           when rect.top < WINDOW.top.
        """
        self.reset_bubble_rect(left=200, right=230, top=-5, bottom=25, collide=-1)

        with mock.patch.object(self.bubble, 'speed_x', 3), \
                mock.patch.object(self.bubble, 'speed_y', -3):
            self.bubble.update()
            self.assertEqual((self.bubble.rect.centerx, self.bubble.rect.centery), (303, 297))
            self.bubble.sound_pop.play.assert_called_once()
            self.assertEqual(self.bubble.rect.top, 0)
            self.assertEqual((self.bubble.speed_x, self.bubble.speed_y), (3, 3))

    def test_update_bottom(self):
        """Test update method when rect.bottom > WINDOW.height.
        """
        self.reset_bubble_rect(left=200, right=230, top=575, bottom=605, collide=-1)

        with mock.patch.object(self.bubble, 'speed_x', -3), \
                mock.patch.object(self.bubble, 'speed_y', 3):
            self.bubble.update()
            self.assertEqual((self.bubble.rect.centerx, self.bubble.rect.centery), (297, 303))
            self.bubble.sound_pop.play.assert_called_once()
            self.bubble.kill.assert_called_once()
            self.bubble.shooter.score.add.assert_called_once()

    def test_update_collid_left(self):
        """Test update method when rect.left <= bar.right < rect.right.
        """
        self.reset_bubble_rect(left=200, right=230, top=550, bottom=580, collide=0)
        self.bar.configure_mock(**dict(right=203, left=198))

        with mock.patch.object(self.bubble, 'speed_x', -3), \
                mock.patch.object(self.bubble, 'speed_y', 3):
            self.bubble.update()
            self.assertEqual((self.bubble.rect.centerx, self.bubble.rect.centery), (297, 303))
            self.bubble.sound_pop.play.assert_called_once()
            self.assertEqual(self.bubble.rect.left, 203)
            self.assertEqual((self.bubble.speed_x, self.bubble.speed_y), (3, 3))

    def test_update_collid_right(self):
        """Test update method when rect.right >= bar.left > rect.left.
        """
        self.reset_bubble_rect(left=200, right=230, top=550, bottom=580, collide=0)
        self.bar.configure_mock(**dict(right=233, left=228))

        with mock.patch.object(self.bubble, 'speed_x', 3), \
                mock.patch.object(self.bubble, 'speed_y', 3):
            self.bubble.update()
            self.assertEqual((self.bubble.rect.centerx, self.bubble.rect.centery), (303, 303))
            self.bubble.sound_pop.play.assert_called_once()
            self.assertEqual(self.bubble.rect.right, 228)
            self.assertEqual((self.bubble.speed_x, self.bubble.speed_y), (-3, 3))


if __name__ == '__main__':
    main()