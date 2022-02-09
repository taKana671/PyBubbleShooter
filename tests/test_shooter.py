import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from unittest import TestCase, main, mock


from pybubble_shooter import (ImageFiles, SoundFiles, Score, Shooter, Point, Line,
    ROWS, COLS, Cell, BUBBLES)


class ShooterBasicTest(TestCase):
    """Tests for Shooter class
    """
    def setUp(self):
        self.Bullet = mock.patch('pybubble_shooter.Bullet').start()
        self.Bubble = mock.patch('pybubble_shooter.Bubble').start()

        mock.patch('pybubble_shooter.pygame.mixer.Sound').start()
        mock.patch('pybubble_shooter.pygame.font.SysFont').start()

        screen = mock.MagicMock()
        dropping = mock.MagicMock()
        score = mock.MagicMock()
        self.shooter = Shooter(screen, dropping, score)

    def tearDown(self):
        mock.patch.stopall()

    def get_cell(self):
        cell = mock.create_autospec(
            spec=Cell,
            spec_set=True,
            instance=True,
            row=3,
            col=4,
            bubble=object(),
            center=Point(106, 75),
            left=Line(Point(91, 60), Point(91, 90)),
            right=Line(Point(121, 60), Point(121, 90)),
            top=Line(Point(91, 60), Point(121, 60)),
            bottom=Line(Point(91, 90), Point(121, 90))
        )
        return cell


class ChargeTestCase(ShooterBasicTest):
    """tests for charge method
    """

    def setUp(self):
        mock.patch('pybubble_shooter.Shooter.initialize_game').start()
        super().setUp()
        self.mock_get_bubble = mock.patch('pybubble_shooter.Shooter.get_bubble').start()
        self.mock_bullet = mock.MagicMock()
        self.mock_bullet.kill.return_value = None
        self.bullets = [BUBBLES[0], BUBBLES[1]]

    def test_charge_next_bullet_is_not_None(self):
        """when next_bubble is not None.
        """
        now_next_bullet = BUBBLES[0]
        new_next_bullet = BUBBLES[1]
        self.mock_get_bubble.return_value = new_next_bullet
        new_bullet = mock.MagicMock()
        self.Bullet.return_value = new_bullet

        with mock.patch.object(self.shooter, 'next_bullet', now_next_bullet, create=True), \
                mock.patch.object(self.shooter, 'bullet', self.mock_bullet):
            self.shooter.charge()
            self.mock_bullet.kill.assert_not_called()
            self.mock_get_bubble.assert_called_once()
            self.Bullet.assert_called_once_with(
                now_next_bullet.file.path, now_next_bullet.color, self.shooter)
            self.assertEqual(self.shooter.next_bullet, new_next_bullet)
            self.assertEqual(self.shooter.bullet, new_bullet)

    def test_charge_next_bullet_is_none(self):
        """when next_bullet is None and bullet is not None.
        """
        self.mock_get_bubble.side_effect = self.bullets

        with mock.patch.object(self.shooter, 'next_bullet', None, create=True), \
                mock.patch.object(self.shooter, 'bullet', self.mock_bullet):
            self.shooter.charge()
            self.mock_bullet.kill.assert_called_once()
            self.assertEqual(self.mock_get_bubble.call_count, 2)
            self.Bullet.assert_called_once_with(
                self.bullets[0].file.path, self.bullets[0].color, self.shooter)
            self.assertEqual(self.shooter.next_bullet, self.bullets[1])

    def test_charge_next_bullet_and_bullet_are_none(self):
        """when both of next_bullet and bullet are None.
        """
        self.mock_get_bubble.side_effect = self.bullets
        new_bullet = mock.MagicMock()
        self.Bullet.return_value = new_bullet

        with mock.patch.object(self.shooter, 'next_bullet', None, create=True):
            self.shooter.charge()
            self.assertEqual(self.mock_get_bubble.call_count, 2)
            self.Bullet.assert_called_once_with(
                self.bullets[0].file.path, self.bullets[0].color, self.shooter)
            self.assertEqual(self.shooter.next_bullet, self.bullets[1])
            self.assertEqual(self.shooter.bullet, new_bullet)


class FindCrossPointTestCase(ShooterBasicTest):
    """tests for find_cross_point method
    """

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
        mock_cell = self.get_cell()

        with mock.patch('pybubble_shooter.Shooter._is_crossing') as mock_is_crossing:
            mock_is_crossing.side_effect = [False for _ in range(4)]
            result = self.shooter.find_cross_point(Point(600, 255), Point(0, 300), mock_cell)
            self.assertEqual(result, None)

    def test_find_cross_point_successfully(self):
        """find_cross_point must return Point if at least one side of a cell
           intersect line segment pt1pt2.
        """
        pt1 = Point(600, 255)
        pt2 = Point(70, 0)
        mock_cell = self.get_cell()

        with mock.patch('pybubble_shooter.Shooter._is_crossing') as mock_is_crossing, \
                mock.patch('pybubble_shooter.Shooter._find_cross_point') as mock_helper_find:
            mock_is_crossing.side_effect = [False, True, False, False]
            mock_helper_find.return_value = Point(100, 60)
            result = self.shooter.find_cross_point(pt1, pt2, mock_cell)
            self.assertEqual(result, Point(103, 68))
            self.assertEqual(mock_is_crossing.call_count, 2)
            mock_helper_find.assert_called_once_with(
                pt1, pt2, mock_cell.right.start, mock_cell.right.end)


class IsCrossingTestCase(ShooterBasicTest):
    """tests for is_crossing method
    """

    def test_helper_is_crossing(self):
        """Test return values from _is_crossing method.
        """
        tests = [
            [Point(0, 0), Point(1, 1), Point(0, 1), Point(1, 0)],
            [Point(0, 0), Point(1, 1), Point(0, 2), Point(3, 2)],
            [Point(0, 0), Point(2, 0), Point(0, 1), Point(1, 0)]]
        expects = [True, False, False]

        for test, expect in zip(tests, expects):
            with self.subTest(test):
                result = self.shooter._is_crossing(*test)
                self.assertEqual(result, expect)

    def test_is_crossing_false(self):
        """Test that is_crossing returns False
           if no lines intersect line segment pt1pt2.
        """
        mock_cell = self.get_cell()

        with mock.patch('pybubble_shooter.Shooter._is_crossing') as mock_is_crossing:
            mock_is_crossing.side_effect = [False for _ in range(4)]
            result = self.shooter.is_crossing(Point(0, 1), Point(1, 0), mock_cell)
            self.assertEqual(result, False)

    def test_is_crossing_true(self):
        """Test that is_crossing returns True
           if at least one line intersects line segment pt1pt2.
        """
        mock_cell = self.get_cell()

        with mock.patch('pybubble_shooter.Shooter._is_crossing') as mock_is_crossing:
            mock_is_crossing.side_effect = [False, True]
            result = self.shooter.is_crossing(Point(0, 1), Point(1, 0), mock_cell)
            self.assertEqual(result, True)


# class FindDestinationTestCase(ShooterBasicTest):
#     """tests for find_destination methods
#     """

#     def test_trace_start_x(self):
#         """Test _trace method when start.x >= end.x.
#         """
#         cells = [
#             [mock.MagicMock(row=row, col=col, bubble=None) for col in range(5)] for row in range(3)]
#         start, end = Point(263, 600), Point(0, 400)
#         expects = [(2, 1), (1, 0), (0, 0)]

#         with mock.patch.object(self.shooter, 'cells', cells), \
#                 mock.patch('pybubble_shooter.Shooter.is_crossing') as mock_is_crossing:
#             mock_is_crossing.side_effect = [
#                 False, True, True, False, False,
#                 True, True, False, False, False,
#                 True, False, False, False, False]

#             traced = [cell for cell in self.shooter._trace(start, end)]
#             self.assertEqual(len(traced), len(expects))
#             for cell, expect in zip(traced, expects):
#                 with self.subTest():
#                     self.assertEqual((cell.row, cell.col), expect)

#     def test_trace_end_x(self):
#         """Test _trace method when start.x < end.x.
#         """
#         cells = [
#             [mock.MagicMock(row=row, col=col, bubble=None) for col in range(5)] for row in range(3)]
#         start, end = Point(0, 600), Point(400, 0)
#         expects = [(2, 2), (1, 3), (0, 4)]

#         with mock.patch.object(self.shooter, 'cells', cells), \
#                 mock.patch('pybubble_shooter.Shooter.is_crossing') as mock_is_crossing:
#             mock_is_crossing.side_effect = [
#                 False, False, True, True, False,
#                 False, True, True, False, False,
#                 True, False, False, False, False]

#             traced = [cell for cell in self.shooter._trace(start, end)]
#             self.assertEqual(len(traced), len(expects))
#             for cell, expect in zip(traced, expects):
#                 with self.subTest():
#                     self.assertEqual((cell.row, cell.col), expect)

#     def test_trace_no_empty(self):
#         """Test _trace method when all of the cells have bubble.
#         """
#         cells = [
#             [mock.MagicMock(row=row, col=col, bubble=object()) for col in range(5)] for row in range(3)]
#         start, end = Point(0, 600), Point(400, 0)
#         expects = [(2, 2)]

#         with mock.patch.object(self.shooter, 'cells', cells), \
#                 mock.patch('pybubble_shooter.Shooter.is_crossing') as mock_is_crossing:
#             mock_is_crossing.side_effect = [
#                 False, False, True, True, False,
#                 False, True, True, False, False,
#                 True, False, False, False, False]

#             traced = [cell for cell in self.shooter._trace(start, end)]
#             self.assertEqual(len(traced), len(expects))
#             for cell, expect in zip(traced, expects):
#                 with self.subTest():
#                     self.assertEqual((cell.row, cell.col), expect)

#     def test_trace_target(self):
#         """Test _trace method when target is found.
#         """
#         cells = [
#             [mock.MagicMock(row=row, col=col, bubble=object() if row <= 1 else None) for col in range(5)] for row in range(3)]
#         start, end = Point(263, 600), Point(0, 400)
#         expects = [(2, 1), (1, 0)]

#         with mock.patch.object(self.shooter, 'cells', cells), \
#                 mock.patch('pybubble_shooter.Shooter.is_crossing') as mock_is_crossing:
#             mock_is_crossing.side_effect = [
#                 False, True, True, False, False,
#                 True, True, False, False, False,
#                 True, False, False, False, False]

#             traced = [cell for cell in self.shooter._trace(start, end)]
#             self.assertEqual(len(traced), len(expects))
#             for cell, expect in zip(traced, expects):
#                 with self.subTest():
#                     self.assertEqual((cell.row, cell.col), expect)

#     def test_scan_bubbles(self):
#         """Test scan_bubbles method.
#         """
#         cells = [
#             [mock.MagicMock(row=row, col=col) for col in range(17)] for row in range(20)]
#         tests = [
#             (0, 0), (0, 5), (0, 16),
#             (2, 0), (2, 5), (2, 16),
#             (3, 0), (3, 5), (3, 16)]
#         expects = [
#             [(1, 0), (0, 1)],
#             [(1, 4), (1, 5), (0, 4), (0, 6)],
#             [(1, 15), (1, 16), (0, 15)],
#             [(3, 0), (2, 1), (1, 0)],
#             [(3, 4), (3, 5), (2, 4), (2, 6), (1, 4), (1, 5)],
#             [(3, 15), (3, 16), (2, 15), (1, 15), (1, 16)],
#             [(4, 1), (4, 0), (3, 1), (2, 1), (2, 0)],
#             [(4, 6), (4, 5), (3, 6), (3, 4), (2, 6), (2, 5)],
#             [(4, 16), (3, 15), (2, 16)]]

#         with mock.patch.object(self.shooter, 'cells', cells):
#             for test, expect in zip(tests, expects):
#                 result = [(cell.row, cell.col) for cell in self.shooter.scan_bubbles(*test)]
#                 self.assertEqual(len(result), len(expect))
#                 self.assertEqual(result, expect)

#     def test_scan(self):
#         """Test _scan method.
#         """
#         cell_with_bubble = [(0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 1)]
#         cells = [
#             [mock.MagicMock(row=row, col=col, bubble=object() if (row, col) in cell_with_bubble else None) for col in range(17)] for row in range(20)]
#         target = cells[1][1]

#         with mock.patch.object(self.shooter, 'cells', cells):
#             result = [(cell.row, cell.col) for cell in self.shooter._scan(target)]
#             self.assertEqual(result, [(2, 2)])

#     def test_helper_find_destination(self):
#         """Test _find_destination method.
#         """
#         cells = [
#             [Cell(row=row, col=col) for col in range(17)] for row in range(20)]
#         for row, col in [(0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]:
#             cells[row][col].bubble = object()
#         target = cells[1][1]
#         tests = (cells[3][2], cells[3][1], cells[3][0])
#         expects = [(2, 2), (2, 2), (2, 1)]

#         with mock.patch.object(self.shooter, 'cells', cells):
#             for dest, expect in zip(tests, expects):
#                 result = self.shooter._find_destination(target, dest)
#                 self.assertEqual((result.row, result.col), expect)

#     def test_helper_not_find_destination(self):
#         """Test _find_destination method.
#         """
#         cells = [
#             [Cell(row=row, col=col) for col in range(17)] for row in range(20)]
#         for row, col in [(0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 1), (2, 2)]:
#             cells[row][col].bubble = object()
#         target = cells[1][1]
#         tests = (cells[3][2], cells[3][1], cells[3][0])

#         with mock.patch.object(self.shooter, 'cells', cells):
#             for dest in tests:
#                 result = self.shooter._find_destination(target, dest)
#                 self.assertEqual(result, None)

#     def test_find_destination_traced_one_cell(self):
#         """Test find_destination method when _trace yield one cell.
#         """
#         start, end = Point(263, 600), Point(0, 400)

#         def _trace(start, end):
#             yield mock.MagicMock()

#         with mock.patch('pybubble_shooter.Shooter._trace') as mock_trace:
#             mock_trace.return_value = _trace(start, end)
#             dest, target = self.shooter.find_destination(start, end)
#             self.assertEqual((dest, target), (None, None))

#     def test_find_destination_dest(self):
#         """Test find_destination method when dest is found and target is None.
#         """
#         start, end = Point(263, 600), Point(0, 400)

#         def _trace(start, end):
#             for row, col in [(5, 3), (4, 2), (3, 1), (2, 0)]:
#                 yield mock.MagicMock(row=row, col=col, bubble=None)

#         with mock.patch('pybubble_shooter.Shooter._trace') as mock_trace:
#             mock_trace.return_value = _trace(start, end)
#             dest, target = self.shooter.find_destination(start, end)
#             self.assertEqual((dest.row, dest.col, target), (2, 0, None))

#     def test_find_destination_dest_changed(self):
#         """Test find_destination method when dest is changed by _find_destination
#         """
#         changed_dest = mock.MagicMock()
#         cells = [
#             mock.MagicMock(row=5, col=3, bubble=None),
#             mock.MagicMock(row=4, col=2, bubble=None),
#             mock.MagicMock(row=2, col=0, bubble=mock.MagicMock())]
#         start, end = Point(263, 600), Point(0, 400)
#         mock_dest, mock_target = cells[-2:]

#         def _trace(start, end):
#             for cell in cells:
#                 yield cell

#         def scan_bubbles(row, col):
#             for _ in range(6):
#                 yield mock.MagicMock(bubble=None)

#         with mock.patch('pybubble_shooter.Shooter._trace') as mock_trace, \
#                 mock.patch('pybubble_shooter.Shooter.scan_bubbles') as mock_scan_bubble, \
#                 mock.patch('pybubble_shooter.Shooter._find_destination') as mock_helper_find_destination:
#             mock_trace.return_value = _trace(start, end)
#             mock_scan_bubble.return_value = scan_bubbles(4, 2)
#             mock_helper_find_destination.return_value = changed_dest
#             dest, target = self.shooter.find_destination(start, end)
#             self.assertEqual((dest, target), (changed_dest, mock_target))
#             mock_helper_find_destination.assert_called_once_with(mock_target, mock_dest)

#     def test_find_destination_dest_not_changed(self):
#         """Test find_destination method when dest is not changed by _find_destination.
#         """
#         changed_dest = mock.MagicMock()
#         cells = [
#             mock.MagicMock(row=5, col=3, bubble=None),
#             mock.MagicMock(row=4, col=2, bubble=None),
#             mock.MagicMock(row=2, col=0, bubble=mock.MagicMock())]
#         start, end = Point(263, 600), Point(0, 400)
#         mock_dest, mock_target = cells[-2:]

#         def _trace(start, end):
#             for cell in cells:
#                 yield cell

#         def scan_bubbles(row, col):
#             for i in range(6):
#                 if i == 3:
#                     yield mock.MagicMock(bubble=mock.MagicMock())
#                 else:
#                     yield mock.MagicMock(bubble=None)

#         with mock.patch('pybubble_shooter.Shooter._trace') as mock_trace, \
#                 mock.patch('pybubble_shooter.Shooter.scan_bubbles') as mock_scan_bubble, \
#                 mock.patch('pybubble_shooter.Shooter._find_destination') as mock_helper_find_destination:
#             mock_trace.return_value = _trace(start, end)
#             mock_scan_bubble.return_value = scan_bubbles(4, 2)
#             mock_helper_find_destination.return_value = changed_dest
#             dest, target = self.shooter.find_destination(start, end)
#             self.assertEqual((dest, target), (mock_dest, mock_target))
#             mock_helper_find_destination.assert_not_called()

#     def test_find_destination_dest_trace_no_cell(self):
#         """Test find_destination method when _trace yield no cells.
#         """
#         start, end = Point(263, 600), Point(0, 400)

#         def _trace(start, end):
#             for i in range(3):
#                 if i > 3:
#                     yield mock.MagicMock()

#         with mock.patch('pybubble_shooter.Shooter._trace') as mock_trace:
#             mock_trace.return_value = _trace(start, end)
#             dest, target = self.shooter.find_destination(start, end)
#             self.assertEqual((dest, target), (None, None))


# class ChangeBubblesTestCase(ShooterBasicTest):
#     """tests for change_bubbles
#     """

#     def create_cell(self, row, col, bubble):
#         return mock.create_autospec(
#             spec=Cell, spec_set=True, instance=True, row=row, col=col, bubble=bubble)

#     def test_delete_bubbles(self):
#         """Test delete_bubbles method.
#         """
#         mock_bubble = mock.MagicMock()
#         mock_bubble.kill.return_value = None
#         cells = [[Cell(r, c) for c in range(5)] for r in range(5)]
#         for row in cells:
#             for cell in row:
#                 cell.bubble = mock_bubble
#         with mock.patch.object(self.shooter, 'cells', cells):
#             self.shooter.delete_bubbles()

#         self.assertEqual(mock_bubble.kill.call_count, 25)
#         self.assertTrue(not any(cell.bubble for row in cells for cell in row))

#     def test_increase_bubbles(self):
#         """Test increase_bubbles method.
#         """
#         cells = [[self.create_cell(r, c, object() if r < 3 else None) for c in range(COLS)] for r in range(ROWS)]

#         with mock.patch('pybubble_shooter.Shooter.create_bubbles') as mock_create_bubbles, \
#                 mock.patch.object(self.shooter, 'cells', cells):
#             self.shooter.increase_bubbles(3)
#             for i, row in enumerate(cells):
#                 for j, mock_cell in enumerate(row):
#                     with self.subTest():
#                         if i < 3:
#                             mock_cell.move_bubble.assert_called_once_with(cells[i + 3][j])
#                         else:
#                             mock_cell.move_bubble.assert_not_called()
#             mock_create_bubbles.assert_called_once_with(3)

    # @mock.patch('pybubble_shooter.Shooter.charge')
    # @mock.patch('pybubble_shooter.Shooter.delete_bubbles')
    # @mock.patch('pybubble_shooter.Shooter.create_bubbles')
    # @mock.patch('pybubble_shooter.Shooter.increase_bubbles')
    # def test_colors_count_more_than_one(self, mock_incerase_bubbles, mock_create_bubbles,
    #                                     mock_delete_bubbles, mock_charge):
    #     with mock.patch.object()
        


if __name__ == '__main__':
    main()