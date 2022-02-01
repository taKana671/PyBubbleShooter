import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from unittest import TestCase, main, mock


from pybubble_shooter import ImageFiles, SoundFiles, Score, Shooter


class ChargeTestCase(TestCase):
    """Tests for charge method of Shooter class
    """

    def setUp(self):
        mock.patch('pybubble_shooter.Shooter.create_launcher').start()
        mock.patch('pybubble_shooter.Shooter.create_sound').start()
        mock.patch('pybubble_shooter.Shooter.initialize_game').start()
        mock.patch('pybubble_shooter.pygame.font.SysFont').start()

        self.mock_bullet_class = mock.patch('pybubble_shooter.Bullet').start()
        self.mock_get_bubble = mock.patch('pybubble_shooter.Shooter.get_bubble').start()

        self.mock_kill = mock.MagicMock(return_value=None)
        self.mock_bullet = mock.MagicMock()
        self.mock_bullet.kill = self.mock_kill
        self.screen = mock.MagicMock()
        self.dropping = mock.MagicMock()
        self.score = mock.MagicMock(spec=Score)

        self.bullets = [
            mock.MagicMock(**{'file.path': 'test_red.png', 'color': 'red'}),
            mock.MagicMock(**{'file.path': 'test_blue.png', 'color': 'blue'})
        ]

    def tearDown(self):
        mock.patch.stopall()

    def test_charge_next_bullet_is_not_None(self):
        """next_bubble is not None.
        """
        mock_next_bullet = mock.MagicMock(**{'file.path': 'test.png', 'color': 'red'})
        self.mock_get_bubble.return_value = self.mock_bullet
        shooter = Shooter(self.screen, self.dropping, self.score)

        with mock.patch.object(shooter, 'next_bullet', mock_next_bullet, create=True):
            shooter.charge()
            self.mock_get_bubble.assert_called_once()
            self.mock_kill.assert_not_called()
            self.mock_bullet_class.assert_called_once_with(
                mock_next_bullet.file.path, mock_next_bullet.color, shooter)
            self.assertEqual(shooter.next_bullet, self.mock_bullet)

    def test_charge_next_bullet_is_none(self):
        """next_bullet is None and bullet is not None.
        """
        self.mock_get_bubble.side_effect = self.bullets
        shooter = Shooter(self.screen, self.dropping, self.score)

        with mock.patch.object(shooter, 'next_bullet', None, create=True), \
                mock.patch.object(shooter, 'bullet', self.mock_bullet):
            shooter.charge()
            self.mock_kill.assert_called_once()
            self.assertEqual(self.mock_get_bubble.call_count, 2)
            self.mock_bullet_class.assert_called_once_with(
                self.bullets[0].file.path, self.bullets[0].color, shooter)
            self.assertEqual(shooter.next_bullet, self.bullets[1])

    def test_charge_next_bullet_and_bullet_are_none(self):
        """Both of next_bullet and bullet are None.
        """
        self.mock_get_bubble.side_effect = self.bullets
        shooter = Shooter(self.screen, self.dropping, self.score)

        with mock.patch.object(shooter, 'next_bullet', None, create=True):
            shooter.charge()
            self.mock_kill.assert_not_called()
            self.assertEqual(self.mock_get_bubble.call_count, 2)
            self.mock_bullet_class.assert_called_once_with(
                self.bullets[0].file.path, self.bullets[0].color, shooter)
            self.assertEqual(shooter.next_bullet, self.bullets[1])


if __name__ == '__main__':
    main()