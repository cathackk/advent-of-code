"""
Advent of Code 2015
Day 25: Let It Snow
https://adventofcode.com/2015/day/25
"""
from tabulate import tabulate

from common.utils import parse_line
from common.utils import relative_path


def part_1(row: int, column: int) -> int:
    """
    Merry Christmas! Santa is booting up his weather machine; looks like you might get a white
    Christmas after all.

    The weather machine beeps! On the console of the machine is a copy protection message asking you
    to enter a code from the instruction manual. Apparently, it refuses to run unless you give it
    that code. No problem; you'll just look up the code in the--

    "Ho ho ho", Santa ponders aloud. "I can't seem to find the manual."

    You look up the support number for the manufacturer and give them a call. Good thing, too - that
    49th star wasn't going to earn itself.

    "Oh, that machine is quite old!", they tell you. "That model went out of support six minutes
    ago, and we just finished shredding all of the manuals. I bet we can find you the code
    generation algorithm, though."

    After putting you on hold for twenty minutes (your call is **very** important to them, it re-
    minded you repeatedly), they finally find an engineer that remembers how the code system works.

    The codes are printed on an infinite sheet of paper, starting in the top-left corner. The codes
    are filled in by diagonals: starting with the first row with an empty first box, the codes are
    filled in diagonally up and to the right. This process repeats until the infinite paper is
    covered. So, the first few codes are filled in in this order:

       | 1   2   3   4   5   6
    ---+---+---+---+---+---+---+
     1 |  1   3   6  10  15  21
     2 |  2   5   9  14  20
     3 |  4   8  13  19
     4 |  7  12  18
     5 | 11  17
     6 | 16

    For example, the 12th code would be written to row `4`, column `2`:

        >>> index_from_pos(4, 2)
        12

    The 15th code would be written to row `1`, column `5`:

        >>> index_from_pos(1, 5)
        15

    The voice on the other end of the phone continues with how the codes are actually generated.
    The first code is `20151125`. After that, each code is generated by taking the previous one,
    multiplying it by `252533`, and then keeping the remainder from dividing that value by
    `33554393`.

    So, to find the second code (which ends up in row `2`, column `1`), start with the previous
    value, `20151125`. Multiply it by `252533` to get `5088824049625`. Then, divide that by
    `33554393`, which leaves a remainder of `31916031`. That remainder is the second code.

        >>> code_from_index(2)
        31916031

    "Oh!", says the voice. "It looks like we missed a scrap from one of the manuals. Let me read it
    to you." You write down his numbers:

        >>> print_page(rows=6, columns=6)
                   1         2         3         4         5         6
        --  --------  --------  --------  --------  --------  --------
         1  20151125  18749137  17289845  30943339  10071777  33511524
         2  31916031  21629792  16929656   7726640  15514188   4041754
         3  16080970   8057251   1601130   7981243  11661866  16474243
         4  24592653  32451966  21345942   9380097  10600672  31527494
         5     77061  17552253  28094349   6899651   9250759  31663883
         6  33071741   6796745  25397450  24659492   1534922  27995004

    "Now remember", the voice continues, "that's not even all of the first few numbers; for example,
    you're missing the one at 7,1 that would come before 6,2. But, it should be enough to let your--
    oh, it's time for lunch! Bye!" The call disconnects.

    Santa looks nervous. Your puzzle input contains the message on the machine's console.
    **What code do you give the machine?**

        >>> part_1(row=4, column=5)
        part 1: enter the code 10600672
        10600672
    """
    result = code_from_pos(row, column)
    print(f"part 1: enter the code {result}")
    return result


def code_from_pos(row: int, column: int) -> int:
    return code_from_index(index_from_pos(row, column))


def code_from_index(index: int, start=20151125, q=252533, m=33554393) -> int:
    return (start * pow(q, index - 1, m)) % m


def index_from_pos(row: int, column: int) -> int:
    """
        >>> index_from_pos(1, 1)
        1
        >>> index_from_pos(2, 1)
        2
        >>> index_from_pos(1, 2)
        3
        >>> index_from_pos(1, 4)
        10
        >>> index_from_pos(3, 4)
        19
        >>> index_from_pos(5, 2)
        17
    """
    diag = row + column - 2
    offset = (diag * (diag + 1)) // 2
    return offset + column


def print_page(rows: int, columns: int) -> None:
    header = list(range(1, columns + 1))
    data = (
        [row] + [code_from_pos(row, col) for col in range(1, columns + 1)]
        for row in range(1, rows + 1)
    )
    print(tabulate(data, headers=header))


def coordinates_from_file(fn: str) -> tuple[int, int]:
    return coordinates_from_text(open(relative_path(__file__, fn)).readline())


def coordinates_from_text(text: str) -> tuple[int, int]:
    row, col = parse_line(
        text.strip(),
        "To continue, please consult the code grid in the manual.  "
        "Enter the code at row $, column $."
    )

    return int(row), int(col)


if __name__ == '__main__':
    coordinates_ = coordinates_from_file('data/25-input.txt')
    part_1(*coordinates_)
