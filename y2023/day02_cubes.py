"""
Advent of Code 2023
Day 2: Cube Conundrum
https://adventofcode.com/2023/day/2
"""
import math
from typing import Iterable, Literal

from common.file import relative_path
from common.iteration import dgroupby_pairs
from common.text import parse_line

Color = Literal['red', 'green', 'blue']
CubeSet = dict[Color, int]
Game = list[CubeSet]
Games = dict[int, Game]


def part_1(games: Games) -> int:
    """
    You're launched high into the atmosphere! The apex of your trajectory just barely reaches
    the surface of a large island floating in the sky. You gently land in a fluffy pile of leaves.
    It's quite cold, but you don't see much snow. An Elf runs over to greet you.

    The Elf explains that you've arrived at **Snow Island** and apologizes for the lack of snow.
    He'll be happy to explain the situation, but it's a bit of a walk, so you have some time. They
    don't get many visitors up here; would you like to play a game in the meantime?

    As you walk, the Elf shows you a small bag and some cubes which are either red, green, or blue.
    Each time you play this game, he will hide a secret number of cubes of each color in the bag,
    and your goal is to figure out information about the number of cubes.

    To get information, once a bag has been loaded with cubes, the Elf will reach into the bag, grab
    a handful of random cubes, show them to you, and then put them back in the bag. He'll do this
    a few times per game.

    You play several games and record the information from each game (your puzzle input). Each game
    is listed with its ID number (like the `11` in `Game 11: ...`) followed by a semicolon-separated
    list of subsets of cubes that were revealed from the bag (like `3 red, 5 green, 4 blue`).

    For example, the record of a few games might look like this:

        >>> games_ = games_from_text('''
        ...     Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
        ...     Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
        ...     Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
        ...     Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
        ...     Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green
        ... ''')
        >>> len(games_)
        5

    In game 1, three sets of cubes are revealed from the bag (and then put back again). The first
    set is 3 blue cubes and 4 red cubes; the second set is 1 red cube, 2 green cubes, and 6 blue
    cubes; the third set is only 2 green cubes.

        >>> games_[1]
        [{'blue': 3, 'red': 4}, {'red': 1, 'green': 2, 'blue': 6}, {'green': 2}]

    The Elf would first like to know which games would have been possible if the bag contained
    **only 12 red cubes, 13 green cubes, and 14 blue cubes**?

        >>> inventory: CubeSet = {'red': 12, 'green': 13, 'blue': 14}

    In the example above, games 1, 2, and 5 would have been **possible** if the bag had been loaded
    with that configuration.

        >>> [game_id for game_id, game in games_.items() if is_game_possible(game, inventory)]
        [1, 2, 5]

    However, game 3 would have been **impossible** because at one point the Elf showed you 20 red
    cubes at once.

        >>> is_game_possible(games_[3], inventory)
        False

    Similarly, game 4 would also have been **impossible** because the Elf showed you 15 blue cubes
    at once.

        >>> is_game_possible(games_[4], inventory)
        False

    If you add up the IDs of the games that would have been possible, you get **`8`**.

        >>> sum(game_id for game_id, game in games_.items() if is_game_possible(game, inventory))
        8

    Determine which games would have been possible if the bag had been loaded with only 12 red
    cubes, 13 green cubes, and 14 blue cubes. **What is the sum of the IDs of those games?**

        >>> part_1(games_)
        part 1: sum of possible game IDs is 8
        8
    """

    inventory: CubeSet = {'red': 12, 'green': 13, 'blue': 14}
    result = sum(game_id for game_id, game in games.items() if is_game_possible(game, inventory))

    print(f"part 1: sum of possible game IDs is {result}")
    return result


def part_2(games: Games) -> int:
    """
    The Elf says they've stopped producing snow because they aren't getting any **water**! He isn't
    sure why the water stopped; however, he can show you how to get to the water source to check it
    out for yourself. It's just up ahead!

    As you continue your walk, the Elf poses a second question: in each game you played, what is
    the **fewest number of cubes of each color** that could have been in the bag to make the game
    possible?

    Again consider the example games from earlier:

        >>> games_ = games_from_text('''
        ...     Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
        ...     Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
        ...     Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
        ...     Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
        ...     Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green
        ... ''')

    - In game 1, the game could have been played with as few as 4 red, 2 green, and 6 blue cubes.
      If any color had even one fewer cube, the game would have been impossible.

        >>> min_cube_set(games_[1])
        {'blue': 6, 'red': 4, 'green': 2}

    - Game 2 could have been played with a minimum of 1 red, 3 green, and 4 blue cubes.

        >>> min_cube_set(games_[2])
        {'blue': 4, 'green': 3, 'red': 1}

    - Game 3 must have been played with at least 20 red, 13 green, and 6 blue cubes.

        >>> min_cube_set(games_[3])
        {'green': 13, 'blue': 6, 'red': 20}

    - Game 4 required at least 14 red, 3 green, and 15 blue cubes.

        >>> min_cube_set(games_[4])
        {'green': 3, 'red': 14, 'blue': 15}

    - Game 5 needed no fewer than 6 red, 3 green, and 2 blue cubes in the bag.

        >>> min_cube_set(games_[5])
        {'red': 6, 'blue': 2, 'green': 3}

    The **power** of a set of cubes is equal to the numbers of red, green, and blue cubes multiplied
    together.

        >>> [set_power(min_cube_set(game)) for game in games_.values()]
        [48, 12, 1560, 630, 36]
        >>> sum(_)
        2286

    For each game, find the minimum set of cubes that must have been present.
    **What is the sum of the power of these sets?**

        >>> part_2(games_)
        part 2: sum of powers of minimum cube sets is 2286
        2286
    """

    result = sum(set_power(min_cube_set(game)) for game in games.values())

    print(f"part 2: sum of powers of minimum cube sets is {result}")
    return result


def is_game_possible(game: Game, inventory: CubeSet) -> bool:
    return all(
        inventory.get(color, 0) >= amount
        for draw in game
        for color, amount in draw.items()
    )


def min_cube_set(game: Game) -> CubeSet:
    return {
        color: max(amounts)
        for color, amounts in dgroupby_pairs(
            cube
            for draw in game
            for cube in draw.items()
        ).items()
    }


def set_power(cube_set: CubeSet) -> int:
    return math.prod(cube_set.values())


def games_from_file(fn: str) -> Games:
    return dict(games_from_lines(open(relative_path(__file__, fn))))


def games_from_text(text: str) -> Games:
    return dict(games_from_lines(text.strip().splitlines()))


def games_from_lines(lines: Iterable[str]) -> Iterable[tuple[int, Game]]:
    return (game_from_line(line.strip()) for line in lines)


def game_from_line(line: str) -> tuple[int, Game]:

    def parse_cube(cube: str) -> tuple[Color, int]:
        # '3 blue'
        amount, color = cube.split(' ')
        return color, int(amount)  # type: ignore

    # 'Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green'
    game_id, body = parse_line(line, 'Game $: $')
    return int(game_id), [
        dict(parse_cube(cube) for cube in draw.split(', '))
        for draw in body.split('; ')
    ]


def main(input_fn: str = 'data/02-input.txt') -> tuple[int, int]:
    games = games_from_file(input_fn)
    result_1 = part_1(games)
    result_2 = part_2(games)
    return result_1, result_2


if __name__ == '__main__':
    main()
