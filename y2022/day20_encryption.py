"""
Advent of Code 2022
Day 20: Grove Positioning System
https://adventofcode.com/2022/day/20
"""

from typing import Iterable

from tqdm import tqdm

from common.chain import Circle
from common.file import relative_path


def part_1(numbers: list[int]) -> int:
    """
    It's finally time to meet back up with the Elves. When you try to contact them, however, you get
    no reply. Perhaps you're out of range?

    You know they're headed to the grove where the star fruit grows, so if you can figure out where
    that is, you should be able to meet back up with them.

    Fortunately, your handheld device has a file (your puzzle input) that contains the grove's
    coordinates! Unfortunately, the file is **encrypted** - just in case the device were to fall
    into the wrong hands.

    Maybe you can decrypt it?

    When you were still back at the camp, you overheard some Elves talking about coordinate file
    encryption. The main operation involved in decrypting the file is called **mixing**.

    The encrypted file is a list of numbers. To **mix** the file, move each number forward or
    backward in the file a number of positions equal to the value of the number being moved.
    The list is **circular**, so moving a number off one end of the list wraps back around to the
    other end as if the ends were connected.

    For example, to move the `1` in a sequence like `4, 5, 6, 1, 7, 8, 9`, the `1` moves one
    position forward:

        >>> moved([4, 5, 6, 1, 7, 8, 9], 1)
        [1, 8, 9, 4, 5, 6, 7]

    To move the `-2` in a sequence like `4, -2, 5, 6, 7, 8, 9`, the -2 moves two positions backward,
    wrapping around:

        >>> moved([4, -2, 5, 6, 7, 8, 9], -2)
        [-2, 9, 4, 5, 6, 7, 8]

    The numbers should be moved **in the order they originally appear** in the encrypted file.
    Numbers moving around during the mixing process do not change the order in which the numbers are
    moved.

    Consider this encrypted file:

        >>> nums = [1,  2, -3, 3, -2, 0, 4]

    Mixing this file proceeds as follows:

        >>> nums_mixed = mixed(nums, logging=True)
        Initial arrangement:
        1, 2, -3, 3, -2, 0, 4
        1 moves between 2 and -3:
        1, -3, 3, -2, 0, 4, 2
        2 moves between -3 and 3:
        2, 3, -2, 0, 4, 1, -3
        -3 moves between -2 and 0:
        -3, 0, 4, 1, 2, 3, -2
        3 moves between 0 and 4:
        3, 4, 1, 2, -2, -3, 0
        -2 moves between 4 and 1:
        -2, 1, 2, -3, 0, 3, 4
        0 does not move:
        0, 3, 4, -2, 1, 2, -3
        4 moves between -3 and 0:
        4, 0, 3, -2, 1, 2, -3
        >>> nums_mixed
        [4, 0, 3, -2, 1, 2, -3]

    Then, the grove coordinates can be found by looking at the 1000th, 2000th, and 3000th numbers
    after the value `0`, wrapping around the list as necessary. In the above example, the 1000th
    number after `0` is **`4`**, the 2000th is **`-3`**, and the 3000th is **`2`**; adding these
    together produces **`3`**.

        >>> (coors := grove_coordinates(nums_mixed))
        (4, -3, 2)
        >>> sum(coors)
        3

    Mix your encrypted file exactly once.
    **What is the sum of the three numbers that form the grove coordinates?**

        >>> part_1(nums)
        part 1: grove coordinates are (4, -3, 2) -> sum is 3
        3
    """

    coordinates = grove_coordinates(mixed(numbers))
    result = sum(coordinates)

    print(f"part 1: grove coordinates are {coordinates} -> sum is {result}")
    return result


def part_2(numbers: list[int], decryption_key: int = 811589153) -> int:
    """
    The grove coordinate values seem nonsensical. While you ponder the mysteries of Elf encryption,
    you suddenly remember the rest of the decryption routine you overheard back at camp.

    First, you need to apply the **decryption key**, `811589153`. Multiply each number by the
    decryption key before you begin; this will produce the actual list of numbers to mix.

    Second, you need to mix the list of numbers **ten times**. The order in which the numbers are
    mixed does not change during mixing; the numbers are still moved in the order they appeared in
    the original, pre-mixed list.

    Using the same example as above:

        >>> nums = numbers_from_file('data/20-example.txt')
        >>> nums_decrypted = [num * 811589153 for num in nums]
        >>> nums_mixed = mixed(nums_decrypted, rounds=10, logging=True)
        Initial arrangement:
        811589153, 1623178306, -2434767459, 2434767459, -1623178306, 0, 3246356612
        After 1 round of mixing:
        3246356612, -1623178306, 2434767459, 1623178306, 811589153, 0, -2434767459
        After 2 rounds of mixing:
        3246356612, -2434767459, -1623178306, 811589153, 0, 2434767459, 1623178306
        After 3 rounds of mixing:
        3246356612, 1623178306, -1623178306, -2434767459, 0, 811589153, 2434767459
        After 4 rounds of mixing:
        3246356612, -1623178306, 0, 1623178306, -2434767459, 811589153, 2434767459
        After 5 rounds of mixing:
        3246356612, 2434767459, 0, 811589153, -1623178306, 1623178306, -2434767459
        After 6 rounds of mixing:
        3246356612, -2434767459, 1623178306, 2434767459, 0, 811589153, -1623178306
        After 7 rounds of mixing:
        3246356612, 0, -2434767459, 2434767459, 1623178306, -1623178306, 811589153
        After 8 rounds of mixing:
        3246356612, 811589153, -2434767459, 2434767459, -1623178306, 0, 1623178306
        After 9 rounds of mixing:
        3246356612, 2434767459, -1623178306, 0, 811589153, 1623178306, -2434767459
        After 10 rounds of mixing:
        3246356612, -1623178306, 2434767459, 811589153, 0, -2434767459, 1623178306
        >>> nums_mixed
        [3246356612, -1623178306, 2434767459, 811589153, 0, -2434767459, 1623178306]

    The grove coordinates can still be found in the same way. Here, the 1000th number after `0` is
    **`811589153`**, the 2000th is **`2434767459`**, and the 3000th is **`-1623178306`**;
    adding these together produces **`1623178306`**:

        >>> (coors := grove_coordinates(nums_mixed))
        (811589153, 2434767459, -1623178306)
        >>> sum(coors)
        1623178306

    Apply the decryption key and mix your encrypted file ten times.
    **What is the sum of the three numbers that form the grove coordinates?**

        >>> part_2(nums)
        part 2: grove coordinates are (811589153, 2434767459, -1623178306) -> sum is 1623178306
        1623178306
    """

    numbers_decrypted = [num * decryption_key for num in numbers]
    coordinates = grove_coordinates(mixed(numbers_decrypted, rounds=10))
    result = sum(coordinates)

    print(f"part 2: grove coordinates are {coordinates} -> sum is {result}")
    return result


def moved(numbers: Iterable[int], number_to_move: int) -> list[int]:
    # the same procedure is used in mixed(), but it's not called for optimization reasons
    circle = Circle(numbers)
    circle.shift_to_value(number_to_move)
    circle.pop(0)
    circle.insert(steps=number_to_move - 1, value=number_to_move)
    return list(circle)


def mixed(numbers: Iterable[int], rounds: int = 1, logging: bool = False) -> list[int]:
    assert rounds >= 1

    circle = Circle(numbers)
    # by keeping this, we don't need to search for values
    links_in_original_order = list(circle.links())

    if logging:
        print("Initial arrangement:")
        print(", ".join(str(v) for v in circle))

    for round_ in tqdm(range(1, rounds + 1), delay=1.0, unit=" rounds"):
        for link_index, link_to_move in enumerate(links_in_original_order):
            # potentially unsafe operation, but I know what I'm doing :)
            circle.current_link = link_to_move
            number = circle.pop(0)
            circle.insert(steps=number - 1, value=number)
            # the link was recreated, the list needs to be updated,
            # otherwise it would contain only orphans after the first round
            links_in_original_order[link_index] = circle.current_link

            if logging and rounds == 1:
                if number != 0:
                    print(f"{circle[0]} moves between {circle[-1]} and {circle[1]}:")
                else:
                    print(f"{circle[0]} does not move:")
                print(", ".join(str(v) for v in circle))

        if logging and rounds > 1:
            noun = "rounds" if round_ > 1 else "round"
            print(f"After {round_} {noun} of mixing:")
            print(", ".join(str(v) for v in circle))

    return list(circle)


def grove_coordinates(
    numbers: list[int],
    key_value: int = 0,
    key_positions: tuple[int, ...] = (1000, 2000, 3000)
) -> tuple[int, ...]:
    key_index = numbers.index(key_value)
    return tuple(numbers[(key_index + pos) % len(numbers)] for pos in key_positions)


def numbers_from_file(fn: str) -> list[int]:
    return [int(line.strip()) for line in open(relative_path(__file__, fn))]


def main(input_fn: str = 'data/20-input.txt') -> tuple[int, int]:
    numbers = numbers_from_file(input_fn)
    result_1 = part_1(numbers)
    result_2 = part_2(numbers)
    return result_1, result_2


if __name__ == '__main__':
    main()
