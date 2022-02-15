import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from unittest import TestCase, main, mock


from pybubble_shooter import (BaseBubble, Score, Shooter, Point, Line,
    ROWS, COLS, Cell, BUBBLES, Status, Bullet)


class BasicTest(TestCase):

    def setUp(self):
        BaseBubble.containers = mock.MagicMock()
        mock.patch('pybubble_shooter.pygame.image.load').start()
        mock.patch('pybubble_shooter.pygame.mixer.Sound').start()
        mock.patch('pybubble_shooter.pygame.transform.scale').start()
        mock.patch('pybubble_shooter.pygame.sprite.Sprite.kill').start()

    def tearDown(self):
        mock.patch.stopall()

    def reset_rect(self, target_mock, left, right, top, bottom, collide=None):
        target_mock.rect.configure_mock(
            **dict(left=left, right=right, top=top, bottom=bottom))
        if collide is not None:
            target_mock.rect.collidelist.return_value = collide

    def get_cell(self, bubble=None):
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
        mock_score = mock.create_autospec(spec=Score, speck_set=True, instance=True)
        self.bar = mock.MagicMock()
        shooter = mock.create_autospec(
            spec=Shooter, instance=True, bars=[self.bar], score=mock_score)
        self.bubble = BaseBubble('test.png', 'red', Point(300, 300), shooter)
        self.bubble.status = Status.MOVE

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
        self.reset_rect(self.bubble, -10, 20, 200, 230, collide=-1)

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
        self.reset_rect(self.bubble, 506, 536, 200, 230, collide=-1)

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
        self.reset_rect(self.bubble, 200, 230, -5, 25, collide=-1)

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
        self.reset_rect(self.bubble, 200, 230, 575, 605, collide=-1)

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
        self.reset_rect(self.bubble, 200, 230, 550, 580, collide=0)
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
        self.reset_rect(self.bubble, 200, 230, 550, 580, collide=0)
        self.bar.configure_mock(**dict(right=233, left=228))

        with mock.patch.object(self.bubble, 'speed_x', 3), \
                mock.patch.object(self.bubble, 'speed_y', 3):
            self.bubble.update()
            self.assertEqual((self.bubble.rect.centerx, self.bubble.rect.centery), (303, 303))
            self.bubble.sound_pop.play.assert_called_once()
            self.assertEqual(self.bubble.rect.right, 228)
            self.assertEqual((self.bubble.speed_x, self.bubble.speed_y), (-3, 3))


class BulletTestCase(BasicTest):

    def setUp(self):
        super().setUp()
        self.shooter = mock.create_autospec(spec=Shooter, launcher=Point(300, 300), instance=True)
        self.bullet = Bullet('test.png', 'red', self.shooter)

    def test_decide_position(self):
        """Test decides position method.
        """
        cell = self.get_cell()
        self.shooter.dest = cell
        tests = [
            (Point(2, 20), Point(2, 0)),
            (Point(15, 0), Point(0, 20)),
            (Point(0, 0), Point(4, 3))
        ]
        expects = [
            [Point(2.0, 10.0), cell.center],
            [Point(x=9.0, y=8.0), Point(x=3.0, y=16.0), Point(x=106, y=75)],
            [Point(x=106, y=75)]
        ]
        for (start, end), expect in zip(tests, expects):
            result = [pt for pt in self.bullet.decide_positions(start, end, self.bullet.select_func(start, end))]
            self.assertEqual(result, expect)

    def test_simulate_course(self):
        """Test that in simulate_course method the last line
           in shooter.course is replaced.
        """
        cell = self.get_cell()
        course = [Line(Point(263, 600), Point(0, 500)), Line(Point(0, 500), Point(526, 300))]
        self.shooter.configure_mock(**dict(dest=cell, course=course))
        mock_func = mock.Mock()
        expect_select_func_args = [
            mock.call(Point(263, 600), Point(0, 500)),
            mock.call(Point(0, 500), Point(106, 75))
        ]
        expect_decide_positions_args = [
            mock.call(Point(263, 600), Point(0, 500), mock_func),
            mock.call(Point(0, 500), Point(106, 75), mock_func)
        ]
        with mock.patch('pybubble_shooter.Bullet.select_func', return_value=mock_func) as mock_select_func, \
                mock.patch('pybubble_shooter.Bullet.decide_positions') as mock_decide_positions:
            _ = [pt for pt in self.bullet.simulate_course()]
            self.assertEqual(mock_select_func.call_args_list, expect_select_func_args)
            self.assertEqual(mock_decide_positions.call_args_list, expect_decide_positions_args)

    @mock.patch('pybubble_shooter.Bullet.drop_floating_bubbles')
    @mock.patch('pybubble_shooter.Bullet.drop_same_color_bubbles')
    def test_bullet_update_left(self, mock_drop_color, mock_floating):
        """Test update method when bullet.rect.left < WINDOW.left.
        """
        cell = self.get_cell()
        self.shooter.configure_mock(**dict(dest=cell, status=Status.SHOT))
        course = [Point(1, 1), Point(2, 2), Point(3, 3)]
        self.reset_rect(self.bullet, -10, 20, 200, 230)

        with mock.patch.object(self.bullet, 'course', course, create=True), \
                mock.patch.object(self.bullet, 'status', Status.SHOT):
            self.bullet.update()
            self.assertEqual((self.bullet.rect.centerx, self.bullet.rect.centery), (1, 1))
            self.bullet.sound_pop.play.assert_called_once()
            self.assertEqual(self.bullet.rect.left, 0)
            self.assertEqual(self.bullet.idx, 1)


if __name__ == '__main__':
    main()