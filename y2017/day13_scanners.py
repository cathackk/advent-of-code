"""
Advent of Code 2017
Day 13: Packet Scanners
https://adventofcode.com/2017/day/13
"""

from itertools import count
from typing import Iterable

from tqdm import tqdm

from common.iteration import sorted_dict
from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(layers: 'Layers') -> int:
    """
    You need to cross a vast **firewall**. The firewall consists of several layers, each with
    a **security scanner** that moves back and forth across the layer. To succeed, you must not be
    detected by a scanner.

    By studying the firewall briefly, you are able to record (in your puzzle input) the **depth** of
    each layer and the **range** of the scanning area for the scanner within it, written as
    `depth: range`. Each layer has a thickness of exactly `1`. A layer at depth `0` begins
    immediately inside the firewall; a layer at depth `1` would start immediately after that.

    For example, suppose you've recorded the following:

        >>> example_layers = layers_from_text('''
        ...     0: 3
        ...     1: 2
        ...     4: 4
        ...     6: 4
        ... ''')
        >>> example_layers
        {0: 3, 1: 2, 4: 4, 6: 4}

    This means that there is a layer immediately inside the firewall (with range `3`), a second
    layer immediately after that (with range `2`), a third layer which begins at depth `4` (with
    range `4`), and a fourth layer which begins at depth `6` (also with range `4`). Visually, it
    might look like this:

        >>> print_layers(example_layers)
         0   1   2   3   4   5   6
        [ ] [ ] ... ... [ ] ... [ ]
        [ ] [ ]         [ ]     [ ]
        [ ]             [ ]     [ ]
                        [ ]     [ ]

    Within each layer, a security scanner moves back and forth within its range. Each security
    scanner starts at the top and moves down until it reaches the bottom, then moves up until it
    reaches the top, and repeats. A security scanner takes **one picosecond** to move one step.
    Drawing scanners as `S`, the first few picoseconds look like this:

        >>> print_layers(example_layers, picosecond=range(4))
        === Picosecond 0: ===
         0   1   2   3   4   5   6
        [S] [S] ... ... [S] ... [S]
        [ ] [ ]         [ ]     [ ]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        === Picosecond 1: ===
         0   1   2   3   4   5   6
        [ ] [ ] ... ... [ ] ... [ ]
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        === Picosecond 2: ===
         0   1   2   3   4   5   6
        [ ] [S] ... ... [ ] ... [ ]
        [ ] [ ]         [ ]     [ ]
        [S]             [S]     [S]
                        [ ]     [ ]
        === Picosecond 3: ===
         0   1   2   3   4   5   6
        [ ] [ ] ... ... [ ] ... [ ]
        [S] [S]         [ ]     [ ]
        [ ]             [ ]     [ ]
                        [S]     [S]

    Your plan is to hitch a ride on a packet about to move through the firewall. The packet will
    travel along the top of each layer, and it moves at **one layer per picosecond**. Each
    picosecond, the packet moves one layer forward (its first move takes it into layer `0`), and
    then the scanners move one step. If there is a scanner at the top of the layer **as your packet
    enters it**, you are **caught**. (If a scanner moves into the top of its layer while you are
    there, you are **not** caught: it doesn't have time to notice you before you leave.) If you were
    to do this in the configuration above, marking your current position with parentheses, your
    passage through the firewall would look like this:

        >>> print_layers_traversal(example_layers)
        === Initial state: ===
         0   1   2   3   4   5   6
        [S] [S] ... ... [S] ... [S]
        [ ] [ ]         [ ]     [ ]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        === Picosecond 0: ===
         0   1   2   3   4   5   6
        (S) [S] ... ... [S] ... [S]
        [ ] [ ]         [ ]     [ ]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        -->
         0   1   2   3   4   5   6
        ( ) [ ] ... ... [ ] ... [ ]
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        === Picosecond 1: ===
         0   1   2   3   4   5   6
        [ ] ( ) ... ... [ ] ... [ ]
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        -->
         0   1   2   3   4   5   6
        [ ] (S) ... ... [ ] ... [ ]
        [ ] [ ]         [ ]     [ ]
        [S]             [S]     [S]
                        [ ]     [ ]
        === Picosecond 2: ===
         0   1   2   3   4   5   6
        [ ] [S] (.) ... [ ] ... [ ]
        [ ] [ ]         [ ]     [ ]
        [S]             [S]     [S]
                        [ ]     [ ]
        -->
         0   1   2   3   4   5   6
        [ ] [ ] (.) ... [ ] ... [ ]
        [S] [S]         [ ]     [ ]
        [ ]             [ ]     [ ]
                        [S]     [S]
        === Picosecond 3: ===
         0   1   2   3   4   5   6
        [ ] [ ] ... (.) [ ] ... [ ]
        [S] [S]         [ ]     [ ]
        [ ]             [ ]     [ ]
                        [S]     [S]
        -->
         0   1   2   3   4   5   6
        [S] [S] ... (.) [ ] ... [ ]
        [ ] [ ]         [ ]     [ ]
        [ ]             [S]     [S]
                        [ ]     [ ]
        === Picosecond 4: ===
         0   1   2   3   4   5   6
        [S] [S] ... ... ( ) ... [ ]
        [ ] [ ]         [ ]     [ ]
        [ ]             [S]     [S]
                        [ ]     [ ]
        -->
         0   1   2   3   4   5   6
        [ ] [ ] ... ... ( ) ... [ ]
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        === Picosecond 5: ===
         0   1   2   3   4   5   6
        [ ] [ ] ... ... [ ] (.) [ ]
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        -->
         0   1   2   3   4   5   6
        [ ] [S] ... ... [S] (.) [S]
        [ ] [ ]         [ ]     [ ]
        [S]             [ ]     [ ]
                        [ ]     [ ]
        === Picosecond 6: ===
         0   1   2   3   4   5   6
        [ ] [S] ... ... [S] ... (S)
        [ ] [ ]         [ ]     [ ]
        [S]             [ ]     [ ]
                        [ ]     [ ]
        -->
         0   1   2   3   4   5   6
        [ ] [ ] ... ... [ ] ... ( )
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]

    In this situation, you are **caught** (`(S)`) in layers `0` and `6`, because your packet entered
    the layer when its scanner was at the top when you entered it. You are **not** caught in layer
    `1`, since the scanner moved into the top of the layer once you were already there.

        >>> list(caught_layers(example_layers))
        [(0, 3), (6, 4)]

    The **severity** of getting caught on a layer is equal to its **depth** multiplied by its
    **range**. (Ignore layers in which you do not get caught.) The severity of the whole trip is the
    sum of these values. In the example above, the trip severity is `0*3 + 6*4 = 24`.

        >>> severity_score(example_layers)
        24

    Given the details of the firewall you've recorded, if you leave immediately,
    **what is the severity of your whole trip**?

        >>> part_1(example_layers)
        part 1: severity score is 24
        24
    """

    result = severity_score(layers)
    print(f"part 1: severity score is {result}")
    return result


def part_2(layers: 'Layers') -> int:
    """
    Now, you need to pass through the firewall without being caught - easier said than done.

    You can't control the speed of the packet, but you can **delay** it any number of picoseconds.
    For each picosecond you delay the packet before beginning your trip, all security scanners move
    one step. You're not in the firewall during this time; you don't enter layer `0` until you stop
    delaying the packet.

    In the example above, if you delay `10` picoseconds, you won't get caught:

        >>> example_layers = layers_from_file(data_path(__file__, 'example.txt'))
        >>> print_layers_traversal(example_layers, delay=10)
        === State after delaying: ===
         0   1   2   3   4   5   6
        [ ] [S] ... ... [ ] ... [ ]
        [ ] [ ]         [ ]     [ ]
        [S]             [S]     [S]
                        [ ]     [ ]
        === Picosecond 10: ===
         0   1   2   3   4   5   6
        ( ) [S] ... ... [ ] ... [ ]
        [ ] [ ]         [ ]     [ ]
        [S]             [S]     [S]
                        [ ]     [ ]
        -->
         0   1   2   3   4   5   6
        ( ) [ ] ... ... [ ] ... [ ]
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        === Picosecond 11: ===
         0   1   2   3   4   5   6
        [ ] ( ) ... ... [ ] ... [ ]
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        -->
         0   1   2   3   4   5   6
        [S] (S) ... ... [S] ... [S]
        [ ] [ ]         [ ]     [ ]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        === Picosecond 12: ===
         0   1   2   3   4   5   6
        [S] [S] (.) ... [S] ... [S]
        [ ] [ ]         [ ]     [ ]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        -->
         0   1   2   3   4   5   6
        [ ] [ ] (.) ... [ ] ... [ ]
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        === Picosecond 13: ===
         0   1   2   3   4   5   6
        [ ] [ ] ... (.) [ ] ... [ ]
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        -->
         0   1   2   3   4   5   6
        [ ] [S] ... (.) [ ] ... [ ]
        [ ] [ ]         [ ]     [ ]
        [S]             [S]     [S]
                        [ ]     [ ]
        === Picosecond 14: ===
         0   1   2   3   4   5   6
        [ ] [S] ... ... ( ) ... [ ]
        [ ] [ ]         [ ]     [ ]
        [S]             [S]     [S]
                        [ ]     [ ]
        -->
         0   1   2   3   4   5   6
        [ ] [ ] ... ... ( ) ... [ ]
        [S] [S]         [ ]     [ ]
        [ ]             [ ]     [ ]
                        [S]     [S]
        === Picosecond 15: ===
         0   1   2   3   4   5   6
        [ ] [ ] ... ... [ ] (.) [ ]
        [S] [S]         [ ]     [ ]
        [ ]             [ ]     [ ]
                        [S]     [S]
        -->
         0   1   2   3   4   5   6
        [S] [S] ... ... [ ] (.) [ ]
        [ ] [ ]         [ ]     [ ]
        [ ]             [S]     [S]
                        [ ]     [ ]
        === Picosecond 16: ===
         0   1   2   3   4   5   6
        [S] [S] ... ... [ ] ... ( )
        [ ] [ ]         [ ]     [ ]
        [ ]             [S]     [S]
                        [ ]     [ ]
        -->
         0   1   2   3   4   5   6
        [ ] [ ] ... ... [ ] ... ( )
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]

    Because all smaller delays would get you caught, the fewest number of picoseconds you would need
    to delay to get through safely is `10`.

        >>> target_delay(example_layers)
        10

    **What is the fewest number of picoseconds** that you need to delay the packet to pass through
    the firewall without being caught?

        >>> part_2(example_layers)
        part 2: wait 10 picoseconds to avoid being caught
        10
    """

    result = target_delay(layers)
    print(f"part 2: wait {result} picoseconds to avoid being caught")
    return result


Layer = tuple[int, int]
Layers = dict[int, int]


# region logic

def caught_layers(layers: Layers, delay: int = 0) -> Iterable[Layer]:
    for layer in layers.items():
        ldepth, lrange = layer
        scanner_round = 2 * (lrange - 1)
        if (ldepth + delay) % scanner_round == 0:
            yield layer


def severity_score(layers: Layers, delay: int = 0) -> int:
    return sum(d * r for d, r in caught_layers(layers, delay))


def target_delay(layers: Layers) -> int:
    # naive solution - works fine for small inputs (takes 3 seconds to compute the given input)
    for delay in tqdm(count(0), unit=" picoseconds", unit_scale=True, delay=0.5):
        if not any(caught_layers(layers, delay)):
            return delay

    # unreachable
    assert False

# endregion


# region printing

def print_layers(layers: Layers, picosecond: None | int | range = None) -> None:
    if picosecond is None:
        # print layers without any scanners in it
        _print_layers_single(layers, picosecond=None)

    elif isinstance(picosecond, int):
        # print layers + scanners at a single moment
        _print_layers_single(
            layers,
            picosecond=picosecond,
            header_text=f"=== Picosecond {picosecond}: ==="
        )

    elif isinstance(picosecond, range):
        # print layers + scanners in a range of moments
        for psec in picosecond:
            _print_layers_single(
                layers,
                picosecond=psec,
                header_text=f"=== Picosecond {psec}: ==="
            )

    else:
        raise TypeError(type(picosecond))


def print_layers_traversal(layers: Layers, delay: int = 0) -> None:
    _print_layers_single(
        layers,
        picosecond=delay,
        header_text=f"=== {'State after delaying' if delay > 0 else 'Initial state'}: ==="
    )
    for packet_at in range(max(layers) + 1):
        picosecond = packet_at + delay
        _print_layers_single(
            layers,
            picosecond=picosecond,
            packet_at=packet_at,
            header_text=f"=== Picosecond {picosecond}: ==="
        )
        _print_layers_single(
            layers,
            picosecond=picosecond + 1,
            packet_at=packet_at,
            header_text="-->"
        )


def _print_layers_single(
    layers: Layers,
    picosecond: None | int,
    packet_at: None | int = None,
    header_text: None | str = None
) -> None:

    # header
    if header_text is not None:
        print(header_text)

    # layer numbers header
    layers_count = max(layers) + 1
    print(" ".join(f" {layer} " for layer in range(layers_count)).rstrip())

    # rows
    # - where each scanner at?
    scanner_positions = {
        layer: (d_1 := depth - 1) - abs(picosecond % (2 * d_1) - d_1)
        for layer, depth in layers.items()
    } if picosecond is not None else {}

    # - what to print in each position of the grid
    def scanner_str(layer_: int, depth_: int) -> str:
        if layer_ in layers:
            return "S" if scanner_positions.get(layer_, -1) == depth_ else " "
        else:
            return "." if depth_ == 0 else " "

    def padding_str(layer_: int, depth_: int) -> str:
        if packet_at == layer_ and depth_ == 0:
            return "()"
        elif layer_ not in layers:
            return ".." if depth_ == 0 else "  "
        elif depth_ < layers[layer_]:
            return "[]"
        else:
            return "  "

    def pos_str(layer_: int, depth_: int):
        scanner = scanner_str(layer_, depth_)
        pad_left, pad_right = tuple(padding_str(layer_, depth_))
        return pad_left + scanner + pad_right

    # the actual printing, row by row
    max_depth = max(layers.values())
    for depth in range(max_depth):
        print(" ".join(pos_str(layer, depth) for layer in range(layers_count)).rstrip())


# endregion


# region input

def layers_from_text(text: str) -> Layers:
    return sorted_dict(layers_from_lines(text.strip().splitlines()))


def layers_from_file(fn: str) -> Layers:
    return sorted_dict(layers_from_lines(open(fn)))


def layers_from_lines(lines: Iterable[str]) -> Iterable[Layer]:
    for line in lines:
        l_depth, l_range = parse_line(line.strip(), "$: $")
        yield int(l_depth), int(l_range)

# endregion


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    layers = layers_from_file(input_path)
    result_1 = part_1(layers)
    result_2 = part_2(layers)
    return result_1, result_2


if __name__ == '__main__':
    main()
