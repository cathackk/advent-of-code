"""
Advent of Code 2024
Day 15: Warehouse Woes
https://adventofcode.com/2024/day/15
"""

from typing import Iterable, Self

from common.canvas import Canvas
from common.file import relative_path
from common.heading import Heading
from common.iteration import dgroupby_pairs, single_value
from common.rect import Rect
from common.text import line_groups


def part_1(warehouse: 'Warehouse', moves: Iterable[Heading]) -> int:
    """
    You appear back inside your own mini submarine! Each Historian drives their mini submarine in
    a different direction; maybe the Chief has his own submarine down here somewhere as well?

    You look up to see a vast school of lanternfish (y2021/day06_spawn.py) swimming past you.
    On closer inspection, they seem quite anxious, so you drive your mini submarine over to see
    if you can help.

    Because lanternfish populations grow rapidly, they need a lot of food, and that food needs to be
    stored somewhere. That's why these lanternfish have built elaborate warehouse complexes operated
    by robots!

    These lanternfish seem so anxious because they have lost control of the robot that operates one
    of their most important warehouses! It is currently running amok, pushing around boxes in
    the warehouse with no regard for lanternfish logistics **or** lanternfish inventory management
    strategies.

    Right now, none of the lanternfish are brave enough to swim up to an unpredictable robot so they
    could shut it off. However, if you could anticipate the robot's movements, maybe they could find
    a safe option.

    The lanternfish already have a map of the warehouse and a list of movements the robot will
    **attempt** to make (your puzzle input). The problem is that the movements will sometimes fail
    as boxes are shifted around, making the actual movements of the robot difficult to predict.

    For example:

        >>> map_0, moves_0 = input_from_text('''
        ...     ##########
        ...     #..O..O.O#
        ...     #......O.#
        ...     #.OO..O.O#
        ...     #..O@..O.#
        ...     #O#..O...#
        ...     #O..O..O.#
        ...     #.OO.O.OO#
        ...     #....O...#
        ...     ##########
        ...
        ...     <vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
        ...     vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
        ...     ><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
        ...     <<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
        ...     ^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
        ...     ^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
        ...     >^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
        ...     <><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
        ...     ^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
        ...     v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
        ... ''')

    As the robot (`@`) attempts to move, if there are any boxes (`O`) in the way, the robot will
    also attempt to push those boxes. However, if this action would cause the robot or a box to move
    into a wall (`#`), nothing moves instead, including the robot. The initial positions of these
    are shown on the map at the top of the document the lanternfish gave you.

        >>> map_0.bounds.shape
        (10, 10)
        >>> map_0.robot
        (4, 4)
        >>> len(map_0.boxes)
        21
        >>> len(map_0.walls)
        37

    The rest of the document describes the moves (`^` for up, `v` for down, `<` for left, `>` for
    right) that the robot will attempt to make, in order. (The moves form a single giant sequence;
    they are broken into multiple lines just to make copy-pasting easier. Newlines within the move
    sequence should be ignored.)

        >>> moves_0  # doctest: +ELLIPSIS
        [Heading.WEST, Heading.SOUTH, Heading.SOUTH, Heading.EAST, ..., Heading.WEST, Heading.NORTH]
        >>> len(moves_0)
        700

    Here is a smaller example to get started:

        >>> map_1, moves_1 = input_from_text('''
        ...     ########
        ...     #..O.O.#
        ...     ##@.O..#
        ...     #...O..#
        ...     #.#.O..#
        ...     #...O..#
        ...     #......#
        ...     ########
        ...
        ...     <^^>>>vv<v>>v<<
        ... ''')
        >>> map_1.bounds.shape
        (8, 8)
        >>> map_1.robot
        (2, 2)
        >>> len(map_1.boxes)
        6
        >>> moves_1  # doctest: +ELLIPSIS
        [Heading.WEST, Heading.NORTH, Heading.NORTH, Heading.EAST, ..., Heading.WEST, Heading.WEST]
        >>> len(moves_1)
        15

    Were the robot to attempt the given sequence of moves, it would push around the boxes like this:

        >>> map_1.visualize_moves(moves_1)
        Initial state:
        ########
        #..O.O.#
        ##@.O..#
        #...O..#
        #.#.O..#
        #...O..#
        #......#
        ########
        ----------
        Move <:
        ########
        #..O.O.#
        ##@.O..#
        #...O..#
        #.#.O..#
        #...O..#
        #......#
        ########
        ----------
        Move ^:
        ########
        #.@O.O.#
        ##..O..#
        #...O..#
        #.#.O..#
        #...O..#
        #......#
        ########
        ----------
        Move ^:
        ########
        #.@O.O.#
        ##..O..#
        #...O..#
        #.#.O..#
        #...O..#
        #......#
        ########
        ----------
        Move >:
        ########
        #..@OO.#
        ##..O..#
        #...O..#
        #.#.O..#
        #...O..#
        #......#
        ########
        ----------
        Move >:
        ########
        #...@OO#
        ##..O..#
        #...O..#
        #.#.O..#
        #...O..#
        #......#
        ########
        ----------
        Move >:
        ########
        #...@OO#
        ##..O..#
        #...O..#
        #.#.O..#
        #...O..#
        #......#
        ########
        ----------
        Move v:
        ########
        #....OO#
        ##..@..#
        #...O..#
        #.#.O..#
        #...O..#
        #...O..#
        ########
        ----------
        Move v:
        ########
        #....OO#
        ##..@..#
        #...O..#
        #.#.O..#
        #...O..#
        #...O..#
        ########
        ----------
        Move <:
        ########
        #....OO#
        ##.@...#
        #...O..#
        #.#.O..#
        #...O..#
        #...O..#
        ########
        ----------
        Move v:
        ########
        #....OO#
        ##.....#
        #..@O..#
        #.#.O..#
        #...O..#
        #...O..#
        ########
        ----------
        Move >:
        ########
        #....OO#
        ##.....#
        #...@O.#
        #.#.O..#
        #...O..#
        #...O..#
        ########
        ----------
        Move >:
        ########
        #....OO#
        ##.....#
        #....@O#
        #.#.O..#
        #...O..#
        #...O..#
        ########
        ----------
        Move v:
        ########
        #....OO#
        ##.....#
        #.....O#
        #.#.O@.#
        #...O..#
        #...O..#
        ########
        ----------
        Move <:
        ########
        #....OO#
        ##.....#
        #.....O#
        #.#O@..#
        #...O..#
        #...O..#
        ########
        ----------
        Move <:
        ########
        #....OO#
        ##.....#
        #.....O#
        #.#O@..#
        #...O..#
        #...O..#
        ########

    The larger example has many more moves; after the robot has finished those moves, the warehouse
    would look like this:

        >>> print(map_0.run(moves_0))
        ##########
        #.O.O.OOO#
        #........#
        #OO......#
        #OO@.....#
        #O#.....O#
        #O.....OO#
        #O.....OO#
        #OO....OO#
        ##########

    The lanternfish use their own custom Goods Positioning System (GPS for short) to track
    the locations of the boxes. The **GPS coordinate** of a box is equal to 100 times its distance
    from the top edge of the map plus its distance from the left edge of the map. (This process does
    not stop at wall tiles; measure all the way to the edges of the map.)

    So, the box shown below has a distance of `1` from the top edge of the map and `4` from the left
    edge of the map, resulting in a GPS coordinate of `100 * 1 + 4 = 104`.

        #######
        #...O..
        #......

    The lanternfish would like to know the **sum of all boxes' GPS coordinates** after the robot
    finishes moving. In the larger example, the sum of all boxes' GPS coordinates is **`10092`**.

        >>> map_0.run(moves_0).gps_sum()
        10092

    In the smaller example, the sum is **`2028`**.

        >>> map_1.run(moves_1).gps_sum()
        2028

    Predict the motion of the robot and boxes in the warehouse. After the robot is finished moving,
    **what is the sum of all boxes' GPS coordinates?**

        >>> part_1(map_0, moves_0)
        part 1: sum of all boxes' final GPS coordinates is 10092
        10092
    """

    result = warehouse.run(moves).gps_sum()

    print(f"part 1: sum of all boxes' final GPS coordinates is {result}")
    return result


def part_2(warehouse: 'Warehouse', moves: Iterable[Heading]) -> int:
    """
    The lanternfish use your information to find a safe moment to swim in and turn off
    the malfunctioning robot! Just as they start preparing a festival in your honor, reports start
    coming in that a **second** warehouse's robot is also malfunctioning.

    This warehouse's layout is surprisingly similar to the one you just helped. There is one key
    difference: everything except the robot is **twice as wide**! The robot's list of movements
    doesn't change.

    To get the wider warehouse's map, start with your original map and, for each tile,
    make the following changes:

      - If the tile is `#`, the new map contains `##` instead.
      - If the tile is `O`, the new map contains `[]` instead.
      - If the tile is `.`, the new map contains `..` instead.
      - If the tile is `@`, the new map contains `@.` instead.

    This will produce a new warehouse map which is twice as wide and with wide boxes that are
    represented by `[]`. (The robot does not change size.)

    The larger example from before would now look like this:

        >>> map_0, moves_0 = input_from_file('data/15-example.txt')
        >>> map_0_wide = scaled_up(map_0)
        >>> print(map_0_wide)
        ####################
        ##....[]....[]..[]##
        ##............[]..##
        ##..[][]....[]..[]##
        ##....[]@.....[]..##
        ##[]##....[]......##
        ##[]....[]....[]..##
        ##..[][]..[]..[][]##
        ##........[]......##
        ####################
        >>> map_0_wide.bounds.shape
        (20, 10)
        >>> map_0_wide.robot
        (8, 4)
        >>> len(map_0_wide.boxes)
        21

    Because boxes are now twice as wide but the robot is still the same size and speed, boxes can be
    aligned such that they directly push two other boxes at once. For example, consider this
    situation:

        >>> map_1, moves_1 = input_from_text('''
        ...     #######
        ...     #...#.#
        ...     #.....#
        ...     #..OO@#
        ...     #..O..#
        ...     #.....#
        ...     #######
        ...
        ...     <vv<<^^<<^^
        ... ''')
        >>> map_1_wide = scaled_up(map_1)

    After appropriately resizing this map, the robot would push around these boxes as follows:

        >>> map_1_wide.visualize_moves(moves_1)
        Initial state:
        ##############
        ##......##..##
        ##..........##
        ##....[][]@.##
        ##....[]....##
        ##..........##
        ##############
        ----------------
        Move <:
        ##############
        ##......##..##
        ##..........##
        ##...[][]@..##
        ##....[]....##
        ##..........##
        ##############
        ----------------
        Move v:
        ##############
        ##......##..##
        ##..........##
        ##...[][]...##
        ##....[].@..##
        ##..........##
        ##############
        ----------------
        Move v:
        ##############
        ##......##..##
        ##..........##
        ##...[][]...##
        ##....[]....##
        ##.......@..##
        ##############
        ----------------
        Move <:
        ##############
        ##......##..##
        ##..........##
        ##...[][]...##
        ##....[]....##
        ##......@...##
        ##############
        ----------------
        Move <:
        ##############
        ##......##..##
        ##..........##
        ##...[][]...##
        ##....[]....##
        ##.....@....##
        ##############
        ----------------
        Move ^:
        ##############
        ##......##..##
        ##...[][]...##
        ##....[]....##
        ##.....@....##
        ##..........##
        ##############
        ----------------
        Move ^:
        ##############
        ##......##..##
        ##...[][]...##
        ##....[]....##
        ##.....@....##
        ##..........##
        ##############
        ----------------
        Move <:
        ##############
        ##......##..##
        ##...[][]...##
        ##....[]....##
        ##....@.....##
        ##..........##
        ##############
        ----------------
        Move <:
        ##############
        ##......##..##
        ##...[][]...##
        ##....[]....##
        ##...@......##
        ##..........##
        ##############
        ----------------
        Move ^:
        ##############
        ##......##..##
        ##...[][]...##
        ##...@[]....##
        ##..........##
        ##..........##
        ##############
        ----------------
        Move ^:
        ##############
        ##...[].##..##
        ##...@.[]...##
        ##....[]....##
        ##..........##
        ##..........##
        ##############

    This warehouse also uses GPS to locate the boxes. For these larger boxes, distances are measured
    from the edge of the map to the closest edge of the box in question. So, the box shown below has
    a distance of `1` from the top edge of the map and `5` from the left edge of the map, resulting
    in a GPS coordinate of `100 * 1 + 5 = 105`.

        ##########
        ##...[]...
        ##........

    In the scaled-up version of the larger example from above, after the robot has finished all of
    its moves, the warehouse would look like this:

        >>> print(result_0 := map_0_wide.run(moves_0))
        ####################
        ##[].......[].[][]##
        ##[]...........[].##
        ##[]........[][][]##
        ##[]......[]....[]##
        ##..##......[]....##
        ##..[]............##
        ##..@......[].[][]##
        ##......[][]..[]..##
        ####################

    The sum of these boxes' GPS coordinates is **`9021`**:

        >>> result_0.gps_sum()
        9021

    Predict the motion of the robot and boxes in this new, scaled-up warehouse.
    **What is the sum of all boxes' final GPS coordinates?**

        >>> part_2(map_0, moves_0)
        part 2: sum of all boxes' final GPS coordinates is 9021
        9021
    """

    result = scaled_up(warehouse).run(moves).gps_sum()

    print(f"part 2: sum of all boxes' final GPS coordinates is {result}")
    return result


Pos = tuple[int, int]


class Warehouse:
    def __init__(self, robot: Pos, boxes: Iterable[Pos], walls: Iterable[Pos]):
        self.robot = robot
        self.boxes = set(boxes)
        self.walls = set(walls)

        self.bounds = Rect.with_all(self.walls)
        assert self.robot in self.bounds
        assert all(box in self.bounds for box in self.boxes)
        assert self.boxes.isdisjoint(self.walls)

    def gps_sum(self) -> int:
        return sum(x + 100 * y for x, y in self.boxes)

    def run(self, moves: Iterable[Heading]) -> Self:
        robot = self.robot
        boxes = set(self.boxes)

        def try_push(box: Pos, direction: Heading) -> Pos | None:
            while True:
                box += direction
                if box in self.walls:
                    return None
                if box not in boxes:
                    return box

        for heading in moves:
            new_robot = robot + heading
            if new_robot in self.walls:
                pass
            elif new_robot not in boxes:
                robot = new_robot
            elif new_box_pos := try_push(new_robot, heading):
                boxes.remove(new_robot)
                boxes.add(new_box_pos)
                robot = new_robot

        return type(self)(robot=robot, boxes=boxes, walls=self.walls)

    def visualize_moves(self, moves: Iterable[Heading]):
        state = self

        print("Initial state:")
        print(state)

        for move in moves:
            print("-" * (self.bounds.width + 2))
            print(f"Move {move.caret}:")
            state = state.run([move])
            print(state)

    def __str__(self) -> str:
        c = Canvas(bounds=self.bounds)
        c.draw_many((wall, '#') for wall in self.walls)
        self._draw_boxes(c)
        c.draw(self.robot, '@')
        return c.render(empty_char='.')

    def _draw_boxes(self, canvas: Canvas) -> None:
        canvas.draw_many((box, 'O') for box in self.boxes)

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        char_to_positions = dgroupby_pairs(
            (char, (x, y))
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
            if char != '.'
        )
        return cls(
            robot=single_value(char_to_positions['@']),
            boxes=char_to_positions['O'],
            walls=char_to_positions['#'],
        )


class WideWarehouse(Warehouse):
    def __init__(self, robot: Pos, boxes: Iterable[Pos], walls: Iterable[Pos]):
        super().__init__(robot, boxes, walls)

        # boxes: positions of the west (left) side of boxes of width 2 `[`
        # these are already validated in super().__init__(), so let's validate the east halves `]`
        boxes_e = {box_w + Heading.EAST for box_w in self.boxes}
        assert all(box_e in self.bounds for box_e in boxes_e)
        assert boxes_e.isdisjoint(self.walls)

    def _draw_boxes(self, canvas: Canvas) -> None:
        canvas.draw_many(
            (pos, char)
            for box_w in self.boxes
            for pos, char in [
                (box_w, '['),
                (box_w + Heading.EAST, ']'),
            ]
        )

    def run(self, moves: Iterable[Heading]) -> Self:
        robot = self.robot
        boxes_w = set(self.boxes)

        def try_push(first_box: Pos, direction: Heading) -> set[Pos] | None:
            to_move_w: set[Pos] = set()

            if first_box in boxes_w:
                layer_w = {first_box}
            elif (first_box_w := first_box + Heading.WEST) in boxes_w:
                layer_w = {first_box_w}
            else:
                assert False

            while layer_w:
                for box_w in list(layer_w):
                    layer_w.clear()
                    new_box_w = box_w + direction
                    new_box_e = new_box_w + Heading.EAST
                    new_box_ww = new_box_w + Heading.WEST

                    # check if there is wall in way
                    if new_box_w in self.walls or new_box_e in self.walls:
                        # cannot move anything -> returning None
                        return None

                    # mark this box as being moved
                    to_move_w.add(box_w)

                    # building new layer
                    if direction is Heading.WEST:
                        if new_box_ww in boxes_w:
                            layer_w.add(new_box_ww)
                    elif direction is Heading.EAST:
                        if new_box_e in boxes_w:
                            layer_w.add(new_box_e)
                    else:
                        # north or south
                        layer_w.update(boxes_w & {new_box_ww, new_box_w, new_box_e})

            return to_move_w

        for heading in moves:
            new_robot = robot + heading
            if new_robot in self.walls:
                pass
            elif new_robot not in boxes_w and new_robot + Heading.WEST not in boxes_w:
                robot = new_robot
            elif (boxes_to_move_w := try_push(new_robot, heading)) is not None:
                boxes_w.difference_update(boxes_to_move_w)
                boxes_w.update(box_w + heading for box_w in boxes_to_move_w)
                robot = new_robot

        return type(self)(robot=robot, boxes=boxes_w, walls=self.walls)


def scaled_up(warehouse: Warehouse) -> WideWarehouse:
    assert not isinstance(warehouse, WideWarehouse)
    robot_x, robot_y = warehouse.robot
    return WideWarehouse(
        robot=(robot_x * 2, robot_y),
        boxes=((x * 2, y) for x, y in warehouse.boxes),
        walls=(wall for x, y in warehouse.walls for wall in [(x * 2, y), (x * 2 + 1, y)]),
    )


def input_from_file(fn: str) -> tuple[Warehouse, list[Heading]]:
    return input_from_lines(open(relative_path(__file__, fn)))


def input_from_text(text: str) -> tuple[Warehouse, list[Heading]]:
    return input_from_lines(text.strip().splitlines())


def input_from_lines(lines: Iterable[str]) -> tuple[Warehouse, list[Heading]]:
    lines_warehouse, lines_moves = line_groups(lines)
    warehouse = Warehouse.from_lines(lines_warehouse)
    moves = [Heading.from_caret(c) for line in lines_moves for c in line]
    return warehouse, moves


def main(input_fn: str = 'data/15-input.txt') -> tuple[int, int]:
    warehouse, moves = input_from_file(input_fn)
    result_1 = part_1(warehouse, moves)
    result_2 = part_2(warehouse, moves)
    return result_1, result_2


if __name__ == '__main__':
    main()
