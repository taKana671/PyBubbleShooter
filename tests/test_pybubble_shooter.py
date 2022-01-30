import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from unittest import TestCase, main, mock

from pybubble_shooter import ImageFiles, SoundFiles, round_up, round


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


if __name__ == '__main__':
    main()