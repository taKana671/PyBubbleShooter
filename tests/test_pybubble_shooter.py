import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from unittest import TestCase, main, mock
from pygame.locals import QUIT, MOUSEBUTTONDOWN, KEYDOWN, K_RIGHT, K_LEFT, K_SPACE

from pybubble_shooter import (ImageFiles, SoundFiles, round_up, round, Cell,
    Point, Line, Score, Status)
from pybubble_shooter import main as pybubble_main


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


class ScoreTestCase(TestCase):
    """Tests for Score
    """
    @mock.patch('pybubble_shooter.pygame.font.SysFont')
    def test_add(self, mock_font):
        """Test add method.
        """
        tests = [
            (100, 50),  # (x, added score)
            (118, 150),
            (300, 400),
            (400, 500),
            (450, 550)
        ]
        score = Score(mock.MagicMock())
        for x, expect in tests:
            with self.subTest():
                score.add(x)
                self.assertEqual(score.score, expect)


class MainTestCase(TestCase):
    """Test for main function
    """

    def setUp(self):
        patchers = [
            mock.patch('pybubble_shooter.pygame.display.set_caption'),
            mock.patch('pybubble_shooter.pygame.time'),
            mock.patch('pybubble_shooter.pygame.key.set_repeat'),
        ]
        for patcher in patchers:
            patcher.start()

        mock_set_mode = mock.patch('pybubble_shooter.pygame.display.set_mode').start()
        self.mock_screen = mock.MagicMock()
        mock_set_mode.return_value = self.mock_screen
        mock_Score = mock.patch("pybubble_shooter.Score").start()
        self.mock_score = mock.MagicMock()
        mock_Score.return_value = self.mock_score
        mock_Shooter = mock.patch("pybubble_shooter.Shooter").start()
        self.mock_shooter = mock.MagicMock()
        mock_Shooter.return_value = self.mock_shooter
        mock_StartGame = mock.patch("pybubble_shooter.StartGame").start()
        self.mock_startgame = mock.MagicMock()
        mock_StartGame.return_value = self.mock_startgame
        mock_RetryGame = mock.patch("pybubble_shooter.RetryGame").start()
        self.mock_retrygame = mock.MagicMock()
        mock_RetryGame.return_value = self.mock_retrygame
        self.mock_event_get = mock.patch("pybubble_shooter.pygame.event.get").start()

        self.bubbles = mock.MagicMock()
        self.droppings = mock.MagicMock()
        self.start = mock.MagicMock()
        self.retry = mock.MagicMock()
        mock_renderupdate = mock.patch("pygame.sprite.RenderUpdates").start()
        mock_renderupdate.side_effect = [self.bubbles, self.droppings, self.start, self.retry]

    def tearDown(self):
        mock.patch.stopall()

    def set_dummy_event(self, event_type):
        def dummy_event_get():
            yield mock.MagicMock(type=event_type)
        self.mock_event_get.return_value = dummy_event_get()

    def check_update_called(self, *mock_renders):
        for mock_render in mock_renders:
            with self.subTest():
                mock_render.update.assert_called_once()

    def check_draw_called(self, *mock_renders):
        for mock_render in mock_renders:
            with self.subTest():
                mock_render.draw.assert_called_once_with(self.mock_screen)

    def check_not_called(self, *methods):
        for method in methods:
            with self.subTest():
                method.assert_not_called()

    def test_games_tatus_start(self):
        """Test that start screen is updated when shooter.game status is START.
        """
        self.set_dummy_event(QUIT)

        with mock.patch.object(self.mock_shooter, 'game', Status.START, create=True):
            with self.assertRaises(SystemExit):
                pybubble_main()

        self.check_update_called(self.mock_shooter, self.bubbles, self.start)
        self.check_draw_called(self.bubbles, self.start)
        self.check_not_called(
            self.droppings.draw, self.mock_score.update, self.retry.update, self.retry.draw)

    def test_game_status_play(self):
        """Test that play screen and score are updated
           when shooter.game status is PLAY.
        """
        self.set_dummy_event(QUIT)

        with mock.patch.object(self.mock_shooter, 'game', Status.PLAY, create=True):
            with self.assertRaises(SystemExit):
                pybubble_main()

        self.check_update_called(self.mock_shooter, self.bubbles, self.mock_score)
        self.check_draw_called(self.bubbles, self.droppings)
        self.check_not_called(self.start.update, self.start.draw, self.retry.update, self.retry.draw)

    def test_game_status_gameover(self):
        """Test that retry screen is updated when shooter.game status is gameover.
        """
        self.set_dummy_event(QUIT)

        with mock.patch.object(self.mock_shooter, 'game', Status.GAMEOVER, create=True):
            with self.assertRaises(SystemExit):
                pybubble_main()

        self.check_update_called(self.mock_shooter, self.bubbles, self.retry)
        self.check_draw_called(self.bubbles, self.retry)
        self.check_not_called(
            self.start.update, self.start.draw, self.droppings.draw, self.mock_score.update)

    def test_game_status_win(self):
        """Test that retry screen is updated when shooter.game status is win.
        """
        self.set_dummy_event(QUIT)

        with mock.patch.object(self.mock_shooter, 'game', Status.WIN, create=True):
            with self.assertRaises(SystemExit):
                pybubble_main()

        self.check_update_called(self.mock_shooter, self.bubbles, self.retry)
        self.check_draw_called(self.bubbles, self.retry)
        self.check_not_called(
            self.start.update, self.start.draw, self.droppings.draw, self.mock_score.update)


if __name__ == '__main__':
    main()