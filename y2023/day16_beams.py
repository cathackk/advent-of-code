"""
Advent of Code 2023
Day 16: The Floor Will Be Lava
https://adventofcode.com/2023/day/16
"""

from typing import Iterable, Self

from tqdm import tqdm

from common.file import relative_path
from common.heading import Heading
from common.iteration import dgroupby_pairs_set
from common.rect import Rect


def part_1(map_: 'Map') -> int:
    r"""
    With the beam of light completely focused **somewhere**, the reindeer leads you deeper still
    into the Lava Production Facility. At some point, you realize that the steel facility walls have
    been replaced with cave, and the doorways are just cave, and the floor is cave, and you're
    pretty sure this is actually just a giant cave.

    Finally, as you approach what must be the heart of the mountain, you see a bright light in
    a cavern up ahead. There, you discover that the beam of light you so carefully focused is
    emerging from the cavern wall closest to the facility and pouring all of its energy into
    a contraption on the opposite side.

    Upon closer inspection, the contraption appears to be a flat, two-dimensional square grid
    containing **empty space** (`.`), **mirrors** (`/` and `\`) and **splitters** (`|` and `-`).

    The contraption is aligned so that most of the beam bounces around the grid, but each tile on
    the grid converts some of the beam's light into **heat** to melt the rock in the cavern.

    You note the layout of the contraption (your puzzle input). For example:

        >>> example = Map.from_file('data/16-example.txt')
        >>> print(example)
        ·|···\····
        |·-·\·····
        ·····|-···
        ········|·
        ··········
        ·········\
        ····/·\\··
        ·-·-/··|··
        ·|····-|·\
        ··//·|····

    The beam enters the top-left corner from the left and heading to the **right**.
    Then, its behavior depends on what it encounters as it moves:

      - If the beam encounters **empty space** (`.`), it continues in the same direction.
      - If the beam encounters a **mirror** (`/` or `\`), the beam is reflected 90 degrees depending
        on the angle of the mirror. For instance, a rightward-moving beam that encounters a `/`
        mirror would continue **upward** in the mirror's column, while a rightward-moving beam that
        encounters a `\` mirror would continue **downward** from the mirror's column.
      - If the beam encounters the **pointy end of a splitter** (`|` or `-`), the beam passes
        through the splitter as if the splitter were **empty space**. For instance, a rightward-
        moving beam that encounters a `-` splitter would continue in the same direction.
      - If the beam encounters the **flat side of a splitter** (`|` or `-`), the beam is **split
        into two beams** going in each of the two directions the splitter's pointy ends are
        pointing. For instance, a rightward-moving beam that encounters a `|` splitter would split
        into two beams: one that continues **upward** from the splitter's column and one that
        continues **downward** from the splitter's column.

    Beams do not interact with other beams; a tile can have many beams passing through it at the
    same time. A tile is **energized** if that tile has at least one beam pass through it, reflect
    in it, or split in it.

    In the above example, here is how the beam of light bounces around the contraption:

        >>> print(format(example, 'arrows'))
        >|<<<\····
        |v-·\^····
        ·v···|->>>
        ·v···v^·|·
        ·v···v^···
        ·v···v^··\
        ·v··/2\\··
        <->-/vv|··
        ·|<<<2-|·\
        ·v//·|·v··

    Beams are only shown on empty tiles; arrows indicate the direction of the beams. If a tile
    contains beams moving in multiple directions, the number of distinct directions is shown
    instead. Here is the same diagram but instead only showing whether a tile is **energized** (`#`)
    or not (`·`):

        >>> print(format(example, 'energized'))
        ######····
        ·#···#····
        ·#···#####
        ·#···##···
        ·#···##···
        ·#···##···
        ·#··####··
        ########··
        ·#######··
        ·#···#·#··

    Ultimately, in this example, **`46`** tiles become **energized**.

        >>> example.energized_count()
        46

    The light isn't energizing enough tiles to produce lava; to debug the contraption, you need to
    start by analyzing the current situation. With the beam starting in the top-left heading right,
    **how many tiles end up being energized?**

        >>> part_1(example)
        part 1: there are 46 energized tiles
        46
    """

    result = map_.energized_count()

    print(f"part 1: there are {result} energized tiles")
    return result


def part_2(map_: 'Map') -> int:
    r"""
    As you try to work out what might be wrong, the reindeer tugs on your shirt and leads you to
    a nearby control panel. There, a collection of buttons lets you align the contraption so that
    the beam enters from any edge tile and heading away from that edge. (You can choose either of
    two directions for the beam if it starts on a corner; for instance, if the beam starts in
    the bottom-right corner, it can start heading either left or upward.)

    So, the beam could start on:

      - any tile in the top row (heading downward),
      - any tile in the bottom row (heading upward),
      - any tile in the leftmost column (heading right),
      - or any tile in the rightmost column (heading left).

    To produce lava, you need to find the configuration that energizes **as many tiles as possible**

    In the above example, this can be achieved by starting the beam in the fourth tile from the left
    in the top row:

        >>> example = Map.from_file('data/16-example.txt')
        >>> print(format(example, 'arrows@3,0,v'))
        ·|<2<\····
        |v-v\^····
        ·v·v·|->>>
        ·v·v·v^·|·
        ·v·v·v^···
        ·v·v·v^··\
        ·v·v/2\\··
        <-2-/vv|··
        ·|<<<2-|·\
        ·v//·|·v··

    Using this configuration, **`51`** tiles are energized:

        >>> example.energized_count(((3, 0), Heading.SOUTH))
        51
        >>> print(format(example, 'energized@3,0,v'))
        ·#####····
        ·#·#·#····
        ·#·#·#####
        ·#·#·##···
        ·#·#·##···
        ·#·#·##···
        ·#·#####··
        ########··
        ·#######··
        ·#···#·#··

    Find the initial beam configuration that energizes the largest number of tiles;
    **how many tiles are energized in that configuration?**

        >>> part_2(example)
        part 2: up to 51 tiles can be energized
        51
    """

    result = max(
        map_.energized_count(start)
        for start in tqdm(
            map_.beam_starts(),
            total=2 * (map_.bounds.height + map_.bounds.width),
            unit=" starts",
            delay=1.0,
        )
    )

    print(f"part 2: up to {result} tiles can be energized")
    return result


Pos = tuple[int, int]
Standing = tuple[Pos, Heading]


REFLECTIONS: dict[str, dict[Heading, list[Heading]]] = {
    '/': {
        Heading.NORTH: [Heading.EAST],
        Heading.EAST: [Heading.NORTH],
        Heading.SOUTH: [Heading.WEST],
        Heading.WEST: [Heading.SOUTH],
    },
    '\\': {
        Heading.NORTH: [Heading.WEST],
        Heading.WEST: [Heading.NORTH],
        Heading.SOUTH: [Heading.EAST],
        Heading.EAST: [Heading.SOUTH],
    },
    '|': {
        Heading.EAST: [Heading.NORTH, Heading.SOUTH],
        Heading.WEST: [Heading.NORTH, Heading.SOUTH],
    },
    '-': {
        Heading.NORTH: [Heading.EAST, Heading.WEST],
        Heading.SOUTH: [Heading.EAST, Heading.WEST],
    },
}


class Map:
    def __init__(self, tiles: Iterable[tuple[Pos, str]]):
        self.tiles = dict(tiles)
        self.bounds = Rect.with_all(self.tiles)

    def beams(self, initial: Standing = ((0, 0), Heading.EAST)) -> Iterable[Standing]:
        stack: list[Standing] = [initial]
        seen: set[Standing] = set()

        while stack:
            standing = stack.pop()
            if standing in seen:
                continue

            yield standing
            seen.add(standing)

            pos, heading = standing
            tile = self.tiles.get(pos, '')
            new_headings = REFLECTIONS.get(tile, {}).get(heading, [heading])
            stack.extend(
                (new_pos, new_h)
                for new_h in new_headings
                if (new_pos := new_h.move(pos)) in self.bounds
            )

    def beam_starts(self) -> Iterable[Standing]:
        b = self.bounds
        yield from (((x, b.top_y), Heading.SOUTH) for x in b.range_x())
        yield from (((b.right_x, y), Heading.WEST) for y in b.range_y())
        yield from (((x, b.bottom_y), Heading.NORTH) for x in b.range_x())
        yield from (((b.left_x, y), Heading.EAST) for y in b.range_y())

    def energized_count(self, initial: Standing = ((0, 0), Heading.EAST)) -> int:
        return len({pos for pos, _ in self.beams(initial)})

    def __str__(self) -> str:
        return format(self)

    def __format__(self, format_spec: str) -> str:
        if '@' in format_spec:
            try:
                style, standing_part = format_spec.split('@')
                x, y, h = standing_part.split(',')
                initial_standing = (int(x), int(y)), Heading.from_caret(h)
            except ValueError as error:
                raise ValueError(f"unsupported format string {format_spec!r}") from error

        else:
            style = format_spec or ''
            initial_standing = (0, 0), Heading.EAST

        if style not in ['', 'arrows', 'energized']:
            raise ValueError(f'unsupported format string {format_spec!r}')

        if style:
            beams_map: dict[Pos, set[Heading]] = dgroupby_pairs_set(self.beams(initial_standing))
        else:
            beams_map = {}

        def char(pos: Pos) -> str:
            match style:
                case 'arrows':
                    if pos in self.tiles:
                        return self.tiles[pos]
                    elif pos not in beams_map:
                        return '·'
                    elif len(pos_headings := beams_map[pos]) == 1:
                        single_heading, = pos_headings
                        return single_heading.caret
                    else:
                        return str(len(pos_headings))
                case 'energized':
                    return '#' if pos in beams_map else '·'
                case None | '':
                    return self.tiles.get(pos, '·')
                case _ as not_supported:
                    raise ValueError(f"unsupported format string {not_supported!r}")

        return '\n'.join(
            ''.join(char((x, y)) for x in self.bounds.range_x())
            for y in self.bounds.range_y()
        )

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        return cls(
            ((x, y), char)
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
            if char != '.'
        )


def main(input_fn: str = 'data/16-input.txt') -> tuple[int, int]:
    map_ = Map.from_file(input_fn)
    result_1 = part_1(map_)
    result_2 = part_2(map_)
    return result_1, result_2


if __name__ == '__main__':
    main()
