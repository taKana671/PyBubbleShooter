import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from unittest import TestCase, main, mock


from pybubble_shooter import (ImageFiles, SoundFiles, round_up, round, Cell,
    Point, Line)


class FilesTestCase(TestCase):
    """Tests for Files sub classes
    """

    def test_image_files(self):
        """Tests for ImageFiles
        """
        tests = [
            (ImageFiles.BALL_BLUE, Path('images', 'ball_blue.png')),
            (ImageFiles.BALL_GREEN, Path('images', 'ball_green.png')),
            (ImageFiles.BALL_PINK, Path('images', 'ball_pink.png')),
            (ImageFiles.BALL_PURPLE, Path('images', 'ball_purple.png')),
            (ImageFiles.BALL_RED, Path('images', 'ball_red.png')),
            (ImageFiles.BALL_SKY, Path('images', 'ball_sky.png')),
            (ImageFiles.BUTTON_START, Path('images', 'button_start.png')),
        ]
        for image_file, expect in tests:
            with self.subTest(image_file):
                self.assertEqual(image_file.path, expect)

    def test_sound_files(self):
        """Tests for SoundFiles
        """
        tests = [
            (SoundFiles.FANFARE, Path('sounds', 'fanfare.wav')),
            (SoundFiles.SOUND_POP, Path('sounds', 'bubble.wav'))
        ]
        for sound_file, expect in tests:
            with self.subTest(sound_file):
                self.assertEqual(sound_file.path, expect)


class RoundTestCase(TestCase):
    """Tests for round functions
    """

    def test_round_up(self):
        """Tests for round_up
        """
        tests = [
            (356.005, 357),
            (189.6, 190),
            (268.001, 269),
            (-123.1, -124),
            (-567.07, -568)
        ]
        for test, expect in tests:
            with self.subTest(test):
                result = round_up(test)
                self.assertEqual(result, expect)

    def test_round(self):
        """Tests for round
        """
        tests = [
            (356.005, 356),
            (189.6, 190),
            (268.001, 268),
            (-123.1, -123),
            (-567.07, -567),
            (-564.7, -565)
        ]
        for test, expect in tests:
            with self.subTest(test):
                result = round(test)
                self.assertEqual(result, expect)


class CellTestCase(TestCase):
    """Tests for Cell
    """

    def test_odd_row(self):
        """Tests for calculate_sides and calculate_center
        """
        tests = [
            (1, 3),  # row is odd number.
            (2, 3)   # row is even number.
        ]
        expects = [
            dict(center=Point(121, 45),
                 left=Line(Point(106, 30), Point(106, 60)),
                 right=Line(Point(136, 30), Point(136, 60)),
                 top=Line(Point(106, 30), Point(136, 30)),
                 bottom=Line(Point(106, 60), Point(136, 60))),
            dict(center=Point(106, 75),
                 left=Line(Point(91, 60), Point(91, 90)),
                 right=Line(Point(121, 60), Point(121, 90)),
                 top=Line(Point(91, 60), Point(121, 60)),
                 bottom=Line(Point(91, 90), Point(121, 90)))
        ]
        for (row, col), expect in zip(tests, expects):
            cell = Cell(row, col)
            self.assertEqual(cell.center, expect['center'])
            self.assertEqual(cell.left, expect['left'])
            self.assertEqual(cell.right, expect['right'])
            self.assertEqual(cell.top, expect['top'])
            self.assertEqual(cell.bottom, expect['bottom'])

    def test_move_bubble_not_none(self):
        """Test for move_bubbles when move_to is not None.
        """
        mock_bubble = mock.MagicMock(**{'rect.centerx': 100, 'rect.centery': 250})
        mock_move_to = mock.MagicMock(**{'center.x': 150, 'center.y': 300, 'bubble': None})

        cell = Cell(2, 3)
        with mock.patch.object(cell, 'bubble', mock_bubble):
            cell.move_bubble(mock_move_to)
            self.assertEqual(cell.bubble, None)
            self.assertEqual(mock_bubble.rect.centerx, mock_move_to.center.x)
            self.assertEqual(mock_bubble.rect.centery, mock_move_to.center.y)
            self.assertEqual(mock_move_to.bubble, mock_bubble)

    def test_move_to_is_none(self):
        """Test for move_bubbles when move_to is None.
        """
        mock_bubble = mock.MagicMock(**{'rect.centerx': 100, 'rect.centery': 250})
        mock_moveto_bubble = mock.MagicMock()
        mock_move_to = mock.MagicMock(
            **{'center.x': 150, 'center.y': 300, 'bubble': mock_moveto_bubble})

        cell = Cell(2, 3)
        with mock.patch.object(cell, 'bubble', mock_bubble):
            cell.move_bubble(mock_move_to)
            self.assertEqual(cell.bubble, mock_bubble)
            self.assertEqual(mock_bubble.rect.centerx, 100)
            self.assertEqual(mock_bubble.rect.centery, 250)
            self.assertEqual(mock_move_to.bubble, mock_moveto_bubble)

    def test_delete_bubble(self):
        """Test for delete_bubble
        """
        mock_bubble = mock.MagicMock()
        mock_bubble.kill.return_value = None

        cell = Cell(3, 5)
        with mock.patch.object(cell, 'bubble', mock_bubble):
            cell.delete_bubble()
            self.assertEqual(cell.bubble, None)


if __name__ == '__main__':
    main()