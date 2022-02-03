import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from unittest import TestCase, main, mock


from pybubble_shooter import ImageFiles, SoundFiles, Score, Shooter, Point, Line


class ShooterBasicTest(TestCase):
    """Tests for Shooter class
    """
    def setUp(self):
        mock.patch('pybubble_shooter.Shooter.create_launcher').start()
        mock.patch('pybubble_shooter.Shooter.create_sound').start()
        mock.patch('pybubble_shooter.Shooter.initialize_game').start()
        mock.patch('pybubble_shooter.pygame.font.SysFont').start()

        screen = mock.MagicMock()
        dropping = mock.MagicMock()
        score = mock.MagicMock(spec=Score)
        self.shooter = Shooter(screen, dropping, score)

    def tearDown(self):
        mock.patch.stopall()


class ChargeTestCase(ShooterBasicTest):
    """Test charge method
    """

    def setUp(self):
        super().setUp()
        self.mock_bullet_class = mock.patch('pybubble_shooter.Bullet').start()
        self.mock_get_bubble = mock.patch('pybubble_shooter.Shooter.get_bubble').start()
        self.mock_kill = mock.MagicMock(return_value=None)
        self.mock_bullet = mock.MagicMock()
        self.mock_bullet.kill = self.mock_kill

        self.bullets = [
            mock.MagicMock(**{'file.path': 'test_red.png', 'color': 'red'}),
            mock.MagicMock(**{'file.path': 'test_blue.png', 'color': 'blue'})
        ]

    def test_charge_next_bullet_is_not_None(self):
        """when next_bubble is not None.
        """
        mock_next_bullet = mock.MagicMock(**{'file.path': 'test.png', 'color': 'red'})
        self.mock_get_bubble.return_value = self.mock_bullet

        with mock.patch.object(self.shooter, 'next_bullet', mock_next_bullet, create=True):
            self.shooter.charge()
            self.mock_get_bubble.assert_called_once()
            self.mock_kill.assert_not_called()
            self.mock_bullet_class.assert_called_once_with(
                mock_next_bullet.file.path, mock_next_bullet.color, self.shooter)
            self.assertEqual(self.shooter.next_bullet, self.mock_bullet)

    def test_charge_next_bullet_is_none(self):
        """when next_bullet is None and bullet is not None.
        """
        self.mock_get_bubble.side_effect = self.bullets

        with mock.patch.object(self.shooter, 'next_bullet', None, create=True), \
                mock.patch.object(self.shooter, 'bullet', self.mock_bullet):
            self.shooter.charge()
            self.mock_kill.assert_called_once()
            self.assertEqual(self.mock_get_bubble.call_count, 2)
            self.mock_bullet_class.assert_called_once_with(
                self.bullets[0].file.path, self.bullets[0].color, self.shooter)
            self.assertEqual(self.shooter.next_bullet, self.bullets[1])

    def test_charge_next_bullet_and_bullet_are_none(self):
        """when both of next_bullet and bullet are None.
        """
        self.mock_get_bubble.side_effect = self.bullets

        with mock.patch.object(self.shooter, 'next_bullet', None, create=True):
            self.shooter.charge()
            self.mock_kill.assert_not_called()
            self.assertEqual(self.mock_get_bubble.call_count, 2)
            self.mock_bullet_class.assert_called_once_with(
                self.bullets[0].file.path, self.bullets[0].color, self.shooter)
            self.assertEqual(self.shooter.next_bullet, self.bullets[1])


class FindCrossPointTestCase(ShooterBasicTest):
    """Test find_cross_point method
    """

    def setUp(self):
        super().setUp()
        center = Point(106, 75)
        left = Line(Point(91, 60), Point(91, 90))
        right = Line(Point(121, 60), Point(121, 90))
        top = Line(Point(91, 60), Point(121, 60))
        bottom = Line(Point(91, 90), Point(121, 90))
        self.mock_cell = mock.MagicMock(
            center=center, left=left, bottom=bottom, right=right, top=top)

    def test_helper_find_cross_point(self):
        """Test return values from _find_cross_point method."""
        tests = [(Point(0, 0), Point(0, 3), Point(1, 10), Point(3, -1)),
                 (Point(4, 0), Point(0, 6), Point(0, 2), Point(2, 3))]
        expects = [Point(0, 16), Point(2, 3)]

        for test, expect in zip(tests, expects):
            with self.subTest(test):
                result = self.shooter._find_cross_point(*test)
                self.assertEqual(result, expect)

    def test_not_find_cross_point(self):
        """find_cross_point must return none if no sides of a cell
           intersect line segment pt1pt2.
        """
        with mock.patch('pybubble_shooter.Shooter._is_crossing') as mock_is_crossing:
            mock_is_crossing.side_effect = [False for _ in range(4)]
            result = self.shooter.find_cross_point(Point(600, 255), Point(0, 300), self.mock_cell)
            self.assertEqual(result, None)

    def test_find_cross_point_successfully(self):
        """find_cross_point must return Point if at least one side of a cell
           intersect line segment pt1pt2.
        """
        pt1 = Point(600, 255)
        pt2 = Point(70, 0)

        with mock.patch('pybubble_shooter.Shooter._is_crossing') as mock_is_crossing, \
                mock.patch('pybubble_shooter.Shooter._find_cross_point') as mock_find_cross_point:
            mock_is_crossing.side_effect = [False, True, False, False]
            mock_find_cross_point.return_value = Point(100, 60)
            result = self.shooter.find_cross_point(pt1, pt2, self.mock_cell)
            self.assertEqual(result, Point(103, 68))
            self.assertEqual(mock_is_crossing.call_count, 2)
            mock_find_cross_point.assert_called_once_with(
                pt1, pt2, self.mock_cell.right.start, self.mock_cell.right.end)


if __name__ == '__main__':
    main()