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
        mock_load = mock.patch('pybubble_shooter.pygame.image.load').start()
        mock.patch('pybubble_shooter.pygame.transform.scale').start()
        mock.patch('pybubble_shooter.pygame.mixer.Sound').start()
        mock_image = mock.MagicMock()
        mock_image.get_rect.return_value = mock.MagicMock()
        mock_load.convert_alpha.return_value = mock_image

        self.shooter = mock.create_autospec(spec=Shooter, spec_set=True, instance=True)
        self.bubble = BaseBubble('test.png', 'red', Point(300, 300), self.shooter)

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


if __name__ == '__main__':
    main()