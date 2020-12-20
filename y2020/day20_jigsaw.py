"""
Advent of Code 2020
Day 20: Jurassic Jigsaw
https://adventofcode.com/2020/day/20
"""
import math
import re
import itertools
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

from utils import eprint
from utils import parse_line
from utils import picking
from utils import product
from utils import single_value
from utils import string_builder


def part_1(tiles: List['Tile']) -> Tuple[int, 'Image']:
    r"""
    After decoding the satellite messages, you discover that the data actually contains many small
    images created by the satellite's *camera array*. The camera array consists of many cameras;
    rather than produce a single square image, they produce many smaller square image *tiles* that
    need to be *reassembled back into a single image*.

    Each camera in the camera array returns a single monochrome *image tile* with a random unique
    *ID number*. The tiles (your puzzle input) arrived in a random order.

    Worse yet, the camera array appears to be malfunctioning: each image tile has been *rotated and
    flipped to a random orientation*. Your first task is to reassemble the original image by
    orienting the tiles so they fit together.

    To show how the tiles should be reassembled, each tile's image data includes a border that
    should line up exactly with its adjacent tiles. All tiles have this border, and the border
    lines up exactly when the tiles are both oriented correctly. Tiles at the edge of the image
    also have this border, but the outermost edges won't line up with any other tiles.

    For example, suppose you have the following nine tiles:

        >>> example_tiles = tiles_from_text('''
        ...     Tile 2311:  Tile 1951:  Tile 1171:  Tile 1427:  Tile 1489:
        ...     ..##.#..#.  #.##...##.  ####...##.  ###.##.#..  ##.#.#....
        ...     ##..#.....  #.####...#  #..##.#..#  .#..#.##..  ..##...#..
        ...     #...##..#.  .....#..##  ##.#..#.#.  .#.##.#..#  .##..##...
        ...     ####.#...#  #...######  .###.####.  #.#.#.##.#  ..#...#...
        ...     ##.##.###.  .##.#....#  ..###.####  ....#...##  #####...#.
        ...     ##...#.###  .###.#####  .##....##.  ...##..##.  #..#.#.#.#
        ...     .#.#.#..##  ###.##.##.  .#...####.  ...#.#####  ...#.#.#..
        ...     ..#....#..  .###....#.  #.##.####.  .#.####.#.  ##.#...##.
        ...     ###...#.#.  ..#.#..#.#  ####..#...  ..#..###.#  ..##.##.##
        ...     ..###..###  #...##.#..  .....##...  ..##.#..#.  ###.##.#..
        ...
        ...     Tile 2473:  Tile 2971:  Tile 2729:  Tile 3079:
        ...     #....####.  ..#.#....#  ...#.#.#.#  #.#.#####.
        ...     #..#.##...  #...###...  ####.#....  .#..######
        ...     #.##..#...  #.#.###...  ..#.#.....  ..#.......
        ...     ######.#.#  ##.##..#..  ....#..#.#  ######....
        ...     .#...#.#.#  .#####..##  .##..##.#.  ####.#..#.
        ...     .#########  .#..####.#  .#.####...  .#...#.##.
        ...     .###.#..#.  #..#.#..#.  ####.#.#..  #.#####.##
        ...     ########.#  ..####.###  ##.####...  ..#.###...
        ...     ##...##.#.  ..#.#.###.  ##..#.##..  ..#.......
        ...     ..###.#.#.  ...#.#.#.#  #.##...##.  ..#.###...
        ... ''')
        >>> len(example_tiles)
        9

    Tiles have ID, have square size, and four border:

        >>> tile_0 = example_tiles[0]
        >>> tile_0.tile_id, tile_0.size, tile_0.borders
        (2311, 10, ('..##.#..#.', '...#.##..#', '..###..###', '.#####..#.'))
        >>> tile_8 = example_tiles[-1]
        >>> tile_8.tile_id, tile_8.size, tile_8.borders
        (3079, 10, ('#.#.#####.', '.#....#...', '..#.###...', '#..##.#...'))

    Tiles can be rotated and flipped:

        >>> print(tile_0)
        ..##.#..#.
        ##..#.....
        #...##..#.
        ####.#...#
        ##.##.###.
        ##...#.###
        .#.#.#..##
        ..#....#..
        ###...#.#.
        ..###..###
        >>> print(tile_0.rotated_cw())
        .#..#####.
        .#.####.#.
        ###...#..#
        #..#.##..#
        #....#.##.
        ...##.##.#
        .#...#....
        #.#.##....
        ##.###.#.#
        #..##.#...
        >>> print(tile_0.flipped_x())
        ..###..###
        ###...#.#.
        ..#....#..
        .#.#.#..##
        ##...#.###
        ##.##.###.
        ####.#...#
        #...##..#.
        ##..#.....
        ..##.#..#.

    By rotating, flipping, and rearranging them, you can find a square arrangement that causes all
    adjacent borders to line up:

        >>> image = Image.assemble(example_tiles)
        >>> image.width, image.height, image.tiles_size
        (3, 3, 10)
        >>> print(image.draw())
        #...##.#.. ..###..### #.#.#####.
        ..#.#..#.# ###...#.#. .#..######
        .###....#. ..#....#.. ..#.......
        ###.##.##. .#.#.#..## ######....
        .###.##### ##...#.### ####.#..#.
        .##.#....# ##.##.###. .#...#.##.
        #...###### ####.#...# #.#####.##
        .....#..## #...##..#. ..#.###...
        #.####...# ##..#..... ..#.......
        #.##...##. ..##.#..#. ..#.###...
        <BLANKLINE>
        #.##...##. ..##.#..#. ..#.###...
        ##..#.##.. ..#..###.# ##.##....#
        ##.####... .#.####.#. ..#.###..#
        ####.#.#.. ...#.##### ###.#..###
        .#.####... ...##..##. .######.##
        .##..##.#. ....#...## #.#.#.#...
        ....#..#.# #.#.#.##.# #.###.###.
        ..#.#..... .#.##.#..# #.###.##..
        ####.#.... .#..#.##.. .######...
        ...#.#.#.# ###.##.#.. .##...####
        <BLANKLINE>
        ...#.#.#.# ###.##.#.. .##...####
        ..#.#.###. ..##.##.## #..#.##..#
        ..####.### ##.#...##. .#.#..#.##
        #..#.#..#. ...#.#.#.. .####.###.
        .#..####.# #..#.#.#.# ####.###..
        .#####..## #####...#. .##....##.
        ##.##..#.. ..#...#... .####...#.
        #.#.###... .##..##... .####.##.#
        #...###... ..##...#.. ...#..####
        ..#.#....# ##.#.#.... ...##.....
        >>> print("\n".join("  ".join(str(t.tile_id) for t in row) for row in image.tile_rows))
        1951  2311  3079
        2729  1427  2473
        2971  1489  1171

    To check that you've assembled the image correctly, multiply the IDs of the four corner tiles
    together.

        >>> corner_ids = [t.tile_id for t in image.corner_tiles]
        >>> corner_ids
        [1951, 3079, 2971, 1171]
        >>> product(corner_ids)
        20899048083289

    Assemble the tiles into an image. *What do you get if you multiply together the IDs of the four
    corner tiles?*

        >>> result, image = part_1(example_tiles)
        part 1: assembled image has corner tiles 1951 * 3079 * 2971 * 1171 = 20899048083289
        >>> result
        20899048083289
    """

    image = Image.assemble(tiles)
    corner_tiles_ids = [corner_tile.tile_id for corner_tile in image.corner_tiles]
    result = product(corner_tiles_ids)

    corners_text = " * ".join(str(tid) for tid in corner_tiles_ids)
    print(f"part 1: assembled image has corner tiles {corners_text} = {result}")
    return result, image


def part_2(image: 'Image', pattern: 'Pattern') -> int:
    r"""
    Now, you're ready to check the image for sea monsters.

    The borders of each tile are not part of the actual image; start by removing them.

    In the example above, the tiles become:

        >>> example_tiles = tiles_from_text('''
        ...     Tile 2311:  Tile 1951:  Tile 1171:  Tile 1427:  Tile 1489:
        ...     ..##.#..#.  #.##...##.  ####...##.  ###.##.#..  ##.#.#....
        ...     ##..#.....  #.####...#  #..##.#..#  .#..#.##..  ..##...#..
        ...     #...##..#.  .....#..##  ##.#..#.#.  .#.##.#..#  .##..##...
        ...     ####.#...#  #...######  .###.####.  #.#.#.##.#  ..#...#...
        ...     ##.##.###.  .##.#....#  ..###.####  ....#...##  #####...#.
        ...     ##...#.###  .###.#####  .##....##.  ...##..##.  #..#.#.#.#
        ...     .#.#.#..##  ###.##.##.  .#...####.  ...#.#####  ...#.#.#..
        ...     ..#....#..  .###....#.  #.##.####.  .#.####.#.  ##.#...##.
        ...     ###...#.#.  ..#.#..#.#  ####..#...  ..#..###.#  ..##.##.##
        ...     ..###..###  #...##.#..  .....##...  ..##.#..#.  ###.##.#..
        ...
        ...     Tile 2473:  Tile 2971:  Tile 2729:  Tile 3079:
        ...     #....####.  ..#.#....#  ...#.#.#.#  #.#.#####.
        ...     #..#.##...  #...###...  ####.#....  .#..######
        ...     #.##..#...  #.#.###...  ..#.#.....  ..#.......
        ...     ######.#.#  ##.##..#..  ....#..#.#  ######....
        ...     .#...#.#.#  .#####..##  .##..##.#.  ####.#..#.
        ...     .#########  .#..####.#  .#.####...  .#...#.##.
        ...     .###.#..#.  #..#.#..#.  ####.#.#..  #.#####.##
        ...     ########.#  ..####.###  ##.####...  ..#.###...
        ...     ##...##.#.  ..#.#.###.  ##..#.##..  ..#.......
        ...     ..###.#.#.  ...#.#.#.#  #.##...##.  ..#.###...
        ... ''')
        >>> len(example_tiles)
        9
        >>> image_assembled = Image.assemble(example_tiles)
        >>> print(image_assembled.draw(borders=False))
        .#.#..#. ##...#.# #..#####
        ###....# .#....#. .#......
        ##.##.## #.#.#..# #####...
        ###.#### #...#.## ###.#..#
        ##.#.... #.##.### #...#.##
        ...##### ###.#... .#####.#
        ....#..# ...##..# .#.###..
        .####... #..#.... .#......
        <BLANKLINE>
        #..#.##. .#..###. #.##....
        #.####.. #.####.# .#.###..
        ###.#.#. ..#.#### ##.#..##
        #.####.. ..##..## ######.#
        ##..##.# ...#...# .#.#.#..
        ...#..#. .#.#.##. .###.###
        .#.#.... #.##.#.. .###.##.
        ###.#... #..#.##. ######..
        <BLANKLINE>
        .#.#.### .##.##.# ..#.##..
        .####.## #.#...## #.#..#.#
        ..#.#..# ..#.#.#. ####.###
        #..####. ..#.#.#. ###.###.
        #####..# ####...# ##....##
        #.##..#. .#...#.. ####...#
        .#.###.. ##..##.. ####.##.
        ...###.. .##...#. ..#..###

    Remove the gaps to form the actual image:

        >>> print(image_assembled.draw(borders=False, gaps=False))
        .#.#..#.##...#.##..#####
        ###....#.#....#..#......
        ##.##.###.#.#..######...
        ###.#####...#.#####.#..#
        ##.#....#.##.####...#.##
        ...########.#....#####.#
        ....#..#...##..#.#.###..
        .####...#..#.....#......
        #..#.##..#..###.#.##....
        #.####..#.####.#.#.###..
        ###.#.#...#.######.#..##
        #.####....##..########.#
        ##..##.#...#...#.#.#.#..
        ...#..#..#.#.##..###.###
        .#.#....#.##.#...###.##.
        ###.#...#..#.##.######..
        .#.#.###.##.##.#..#.##..
        .####.###.#...###.#..#.#
        ..#.#..#..#.#.#.####.###
        #..####...#.#.#.###.###.
        #####..#####...###....##
        #.##..#..#...#..####...#
        .#.###..##..##..####.##.
        ...###...##...#...#..###

    Now, you're ready to search for sea monsters! Because your image is monochrome, a sea monster
    will look like this:

        >>> monster = Pattern.monster()
        >>> print(f"monster pattern:\n{Pattern.monster()}")
        monster pattern:
        ..................#.
        #....##....##....###
        .#..#..#..#..#..#...
        >>> monster.width, monster.height
        (20, 3)

    When looking for this pattern in the image, *the dots can be anything*; only the `#` need to
    match. Also, you might need to rotate or flip your image before it's oriented correctly to find
    sea monsters. In the above image, *after flipping and rotating it* to the appropriate
    orientation, there are *two* sea monsters (marked with `O`):

        >>> image_oriented = image_assembled.rotated_cw().flipped_y()
        >>> image_drawn = image_oriented.draw(borders=False, gaps=False)
        >>> monsters_spotted = list(monster.find_in(image_drawn))
        >>> monsters_spotted
        [(1, 16), (2, 2)]
        >>> image_with_monsters_highlighted = monster.highlight(image_drawn, monsters_spotted)
        >>> print(image_with_monsters_highlighted)
        .####...#####..#...###..
        #####..#..#.#.####..#.#.
        .#.#...#.###...#.##.O#..
        #.O.##.OO#.#.OO.##.OOO##
        ..#O.#O#.O##O..O.#O##.##
        ...#.#..##.##...#..#..##
        #.##.#..#.#..#..##.#.#..
        .###.##.....#...###.#...
        #.####.#.#....##.#..#.#.
        ##...#..#....#..#...####
        ..#.##...###..#.#####..#
        ....#.##.#.#####....#...
        ..##.##.###.....#.##..#.
        #...#...###..####....##.
        .#.##...#.##.#.#.###...#
        #.###.#..####...##..#...
        #.###...#.##...#.##O###.
        .O##.#OO.###OO##..OOO##.
        ..O#.O..O..O.#O##O##.###
        #.#..##.########..#..##.
        #.#####..#.#...##..#....
        #....##..#.#########..##
        #...#.....#..##...###.##
        #..###....##.#...##.##.#

    Determine how rough the waters are in the sea monsters' habitat by counting the number of `#`
    that are *not* part of a sea monster. In the above example, the habitat's water roughness is
    *`273`*.

        >>> sum(1 for c in image_with_monsters_highlighted if c == '#')
        273

    *How many # are not part of a sea monster?*

        >>> part_2(image_assembled, monster)
        part 2: monster was spotted 2 times; there are 273 water tiles without monster
        273
    """

    for image_oriented in image.orientations():
        image_drawn = image_oriented.draw(borders=False, gaps=False)
        matches = list(pattern.find_in(image_drawn))
        if matches:
            image_highlighted = pattern.highlight(image_drawn, matches)
            result = sum(1 for c in image_highlighted if c == '#')
            print(f"part 2: monster was spotted {len(matches)} times; "
                  f"there are {result} water tiles without monster")
            # print(image_highlighted)
            return result
    else:
        print("part 2: monster wasn't spotted")
        return -1


class Tile:
    def __init__(self, tile_id: int, pixel_rows: Iterable[str]):
        self.tile_id = tile_id
        self.pixel_rows = list(pixel_rows)

        height = len(self.pixel_rows)
        width = single_value(set(len(row) for row in self.pixel_rows))
        assert width == height
        self.size = width
        assert self.size >= 2

        self.borders = (
            # top row: left-to-right
            self.pixel_rows[0],
            # right column: top-to-bottom
            ''.join(self.pixel_rows[y][-1] for y in range(self.size)),
            # bottom row: left-to_right
            self.pixel_rows[-1],
            # left column: top-to-bottom
            ''.join(self.pixel_rows[y][0] for y in range(self.size))
        )

    def __str__(self):
        return "\n".join(self.pixel_rows)

    @property
    def border_top(self) -> str:
        return self.borders[0]

    @property
    def border_right(self) -> str:
        return self.borders[1]

    @property
    def border_bottom(self) -> str:
        return self.borders[2]

    @property
    def border_left(self) -> str:
        return self.borders[3]

    @classmethod
    def from_lines(cls, lines: Iterable[str]):
        lines_it = iter(lines)
        header = next(lines_it)
        (tile_id,) = parse_line(header, "Tile $:")
        pixels = list(lines_it)
        return cls(int(tile_id), pixels)

    def flipped_x(self) -> 'Tile':
        return type(self)(self.tile_id, self.pixel_rows[::-1])

    def flipped_y(self) -> 'Tile':
        return type(self)(self.tile_id, [row[::-1] for row in self.pixel_rows])

    def rotated_cw(self) -> 'Tile':
        return type(self)(self.tile_id, [
            ''.join(self.pixel_rows[y][x] for y in range(self.size-1, -1, -1))
            for x in range(self.size)
        ])

    def rotated_ccw(self) -> 'Tile':
        return type(self)(self.tile_id, [
            ''.join(self.pixel_rows[y][x] for y in range(self.size))
            for x in range(self.size-1, -1, -1)
        ])

    def orientations(self) -> Iterable['Tile']:
        tile = self
        for _ in range(4):
            yield tile
            yield tile.flipped_x()
            tile = tile.rotated_cw()


def tiles_from_file(fn: str) -> List[Tile]:
    return list(tiles_from_lines(open(fn)))


def tiles_from_text(text: str) -> List[Tile]:
    return list(tiles_from_lines(text.strip().split("\n")))


def tiles_from_lines(lines: Iterable[str]) -> Iterable[Tile]:
    buffers: List[List[str]] = []

    # trailing empty line to force flush the last part
    lines = itertools.chain(lines, [""])
    for line in lines:
        line = line.strip()

        if line:
            parts = re.split(r' {2,}', line)
            if not buffers:
                buffers.extend(([part] for part in parts))
            else:
                if len(buffers) != len(parts):
                    raise ValueError(f"line parts count mismatch: {len(buffers)} vs {len(parts)}")
                for part, buffer in zip(parts, buffers):
                    buffer.append(part)

        elif buffers:
            # flush buffer
            yield from (
                Tile.from_lines(buffer)
                for buffer in buffers
            )
            buffers.clear()


class Image:
    def __init__(self, tile_rows: Iterable[Iterable[Tile]]):
        self.tile_rows = [list(row) for row in tile_rows]
        self.height = len(self.tile_rows)
        assert self.height >= 1
        self.width = single_value(set(len(row) for row in self.tile_rows))
        assert self.width >= 1
        self.tiles_size = single_value(set(tile.size for row in self.tile_rows for tile in row))

    def __str__(self):
        return self.draw()

    @string_builder()
    def draw(self, borders: bool = True, gaps: bool = True) -> str:
        range_y = range(self.tiles_size) if borders else range(1, self.tiles_size-1)
        slice_x = slice(0, self.tiles_size) if borders else slice(1, self.tiles_size-1)
        gap_char = " " if gaps else ""

        for tile_row_index, tile_row in enumerate(self.tile_rows):
            if gaps and tile_row_index >= 1:
                yield ""  # blank separator line
            for pixel_y in range_y:
                yield gap_char.join(
                    tile.pixel_rows[pixel_y][slice_x]
                    for tile in tile_row
                )

    def flipped_x(self) -> 'Image':
        return type(self)(
            [tile.flipped_x() for tile in tile_row]
            for tile_row in reversed(self.tile_rows)
        )

    def flipped_y(self) -> 'Image':
        return type(self)(
            [tile.flipped_y() for tile in reversed(tile_row)]
            for tile_row in self.tile_rows
        )

    def rotated_cw(self) -> 'Image':
        return type(self)(
            [self.tile_rows[y][x].rotated_cw() for y in range(self.height-1, -1, -1)]
            for x in range(self.width)
        )

    def rotated_ccw(self) -> 'Image':
        return type(self)(
            [self.tile_rows[y][x].rotated_ccw() for y in range(self.height)]
            for x in range(self.width-1, -1, -1)
        )

    def orientations(self) -> Iterable['Image']:
        image = self
        for _ in range(4):
            yield image
            yield image.flipped_x()
            image = image.rotated_cw()


    @classmethod
    def assemble(cls, tiles: Iterable[Tile]) -> Optional['Image']:
        tiles = list(tiles)

        side_length = int(math.sqrt(len(tiles)))
        if side_length * side_length != len(tiles):
            raise ValueError(f"can only assemble square images; "
                             f"given non-square number of tiles: {len(tiles)}")

        # go through tiles, try to use each as top-left corner in all of its orientations
        for tile_ix, (starting_tile, remaining_tiles) in enumerate(picking(tiles)):
            for orientation_ix, top_left_tile in enumerate(starting_tile.orientations()):
                eprint(f"tile={tile_ix+1}/{len(tiles)}, orn={orientation_ix+1}/8")
                solution = cls.solve(top_left_tile, remaining_tiles, side_length)
                if solution:
                    return solution

        return None

    @classmethod
    def solve(
            cls,
            top_left_tile: Tile,
            tiles: Iterable[Tile],
            side_length: int
    ) -> Optional['Image']:
        # given top-left-corner, tiles pool and side size (image being square)
        # try building the first row from left-to-right,
        # then adding more rows below
        # if this all goes well, we are done!

        tiles_pool = {tile.tile_id: tile for tile in tiles}
        rows: List[List[Tile]] = [[top_left_tile]]

        def matches_rows(tile: Tile):
            current_row = rows[-1]
            prev_row = rows[-2] if len(rows) >= 2 else None
            return (
                # if there are any tiles in the current row,
                # -> right border of the rightmost one must match the left border of the given tile
                (not current_row or current_row[-1].border_right == tile.border_left)
                # if there is a row top of this one,
                # -> bottom border of the tile above the current position must match the top border
                #    of the given tile
                and (not prev_row or prev_row[len(current_row)].border_bottom == tile.border_top)
            )

        while tiles_pool:
            if len(rows[-1]) == side_length:
                rows.append([])

            matching_tiles = set(
                tile_oriented
                for tile in tiles_pool.values()
                for tile_oriented in tile.orientations()
                if matches_rows(tile_oriented)
            )

            if not matching_tiles:
                # no solution for given top-left corner found
                return None

            # only supporting single solutions
            matching_tile = single_value(matching_tiles)
            del tiles_pool[matching_tile.tile_id]
            rows[-1].append(matching_tile)

        assert len(rows) == side_length
        assert all(len(row) == side_length for row in rows)
        return cls(rows)

    @property
    def corner_tiles(self) -> List[Tile]:
        row_indexes = [0, self.height - 1] if self.height > 1 else [0]
        col_indexes = [0, self.width - 1] if self.width > 1 else [0]
        return [
            self.tile_rows[row][col]
            for row, col in itertools.product(row_indexes, col_indexes)
        ]


Pos = Tuple[int, int]


class Pattern:
    def __init__(self, pixel_rows: Iterable[str]):
        self.pixel_rows = list(pixel_rows)
        self.height = len(self.pixel_rows)
        self.width = single_value(set(len(row) for row in self.pixel_rows))

    def __str__(self):
        return "\n".join(self.pixel_rows)

    @classmethod
    def monster(cls):
        return Pattern.from_text('''
            ..................#.
            #....##....##....###
            .#..#..#..#..#..#...
        ''')

    @classmethod
    def from_text(cls, text: str):
        return cls(
            line.strip()
            for line in text.strip().split("\n")
        )

    def find_in(self, drawn_image: str) -> Iterable[Pos]:
        image_lines = drawn_image.split("\n")

        def is_match(ix, iy):
            return all(
                image_pixel == '#'
                for pattern_line, image_line in zip(self.pixel_rows, image_lines[iy:])
                for pattern_pixel, image_pixel in zip(pattern_line, image_line[ix:])
                if pattern_pixel == '#'
            )

        image_height = len(image_lines)
        image_width = single_value(set(len(line) for line in image_lines))

        return (
            (x, y)
            for x in range(image_width - self.width + 1)
            for y in range(image_height - self.height + 1)
            if is_match(x, y)
        )

    def highlight(self, drawn_image: str, matches: Iterable[Pos], hchr: str = 'O') -> str:
        image_pixels = [list(line) for line in drawn_image.split("\n")]

        for mx, my in matches:
            pixels_to_highlight = (
                (px, py)
                for px in range(self.width)
                for py in range(self.height)
                if self.pixel_rows[py][px] == '#'
            )
            for px, py in pixels_to_highlight:
                image_pixels[my+py][mx+px] = hchr

        return "\n".join("".join(row) for row in image_pixels)


if __name__ == '__main__':
    tiles_ = tiles_from_file("data/20-input.txt")
    result_1, image_ = part_1(tiles_)
    part_2(image_, Pattern.monster())
