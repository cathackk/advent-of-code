"""
Advent of Code 2023
Day 6: Wait For It
https://adventofcode.com/2023/day/6
"""

import math
from typing import Iterable

from common.bsrange import BSRange
from common.file import relative_path
from common.text import parse_line


def part_1(races: Iterable['Race']) -> int:
    """
    The ferry quickly brings you across Island Island. After asking around, you discover that there
    is indeed normally a large pile of sand somewhere near here, but you don't see anything besides
    lots of water and the small island where the ferry has docked.

    As you try to figure out what to do next, you notice a poster on a wall near the ferry dock.
    "Boat races! Open to the public! Grand prize is an all-expenses-paid trip to **Desert Island**!"
    That must be where the sand comes from! Best of all, the boat races are starting in just a few
    minutes.

    You manage to sign up as a competitor in the boat races just in time. The organizer explains
    that it's not really a traditional race - instead, you will get a fixed amount of time during
    which your boat has to travel as far as it can, and you win if your boat goes the farthest.

    As part of signing up, you get a sheet of paper (your puzzle input) that lists the **time**
    allowed for each race and also the best **distance** ever recorded in that race. To guarantee
    you win the grand prize, you need to make sure you **go farther in each race** than the current
    record holder.

    The organizer brings you over to the area where the boat races are held. The boats are much
    smaller than you expected - they're actually **toy boats**, each with a big button on top.
    Holding down the button **charges the boat**, and releasing the button **allows the boat to
    move**. Boats move faster if their button was held longer, but time spent holding the button
    counts against the total race time. You can only hold the button at the start of the race, and
    boats don't move until the button is released.

    For example:

        >>> races_ = races_from_text('''
        ...     Time:      7  15   30
        ...     Distance:  9  40  200
        ... ''')
        >>> races_
        [(7, 9), (15, 40), (30, 200)]

    This document describes three races:

      - The first race lasts 7 milliseconds. The record distance in this race is 9 millimeters.
      - The second race lasts 15 milliseconds. The record distance in this race is 40 millimeters.
      - The third race lasts 30 milliseconds. The record distance in this race is 200 millimeters.

    Your toy boat has a starting speed of **zero millimeters per millisecond**. For each whole
    millisecond you spend at the beginning of the race holding down the button, the boat's speed
    increases by **one millimeter per millisecond**.

    So, because the first race lasts 7 milliseconds, you only have a few options:

      - Don't hold the button at all (that is, hold it for **`0` milliseconds**) at the start of the
        race. The boat won't move; it will have traveled **`0` millimeters** by the end of the race.

        >>> travel_distance(0, 7)
        0

      - Hold the button for **`1` millisecond** at the start of the race. Then, the boat will travel
        at a speed of `1` millimeter per millisecond for 6 milliseconds, reaching a total distance
        traveled of **`6` millimeters**.

        >>> travel_distance(1, 7)
        6

      - Hold the button for **`2` ms**, giving the boat a speed of `2` mm/ms.
        It will then get 5 ms to move, reaching a total distance of **`10` mm**.

        >>> travel_distance(2, 7)
        10

      - Hold the button for **`3` ms**.
        After its remaining 4 ms of travel time, the boat will have gone **`12` mm**.

        >>> travel_distance(3, 7)
        12

      - Hold the button for **`4` ms**.
        After its remaining 3 ms of travel time, the boat will have gone **`12` mm**.

        >>> travel_distance(4, 7)
        12

      - Hold the button for **`5` ms**, causing the boat to travel a total of **`10` mm**.

        >>> travel_distance(5, 7)
        10

      - Hold the button for **`6` ms**, causing the boat to travel a total of **`6` mm**.

        >>> travel_distance(6, 7)
        6

      - Hold the button for **`7` ms**. That's the entire duration of the race. You never let go of
        the button. The boat can't move until you let go of the button. Please make sure you let go
        of the button so the boat gets to move. **`0` millimeters**.

        >>> travel_distance(7, 7)
        0

    Since the current record for this race is 9 millimeters, there are actually **`4`** different
    ways you could win: you could hold the button for `2`, `3`, `4`, or `5` milliseconds at
    the start of the race.

        >>> [t for t in range(7) if travel_distance(t, 7) > 9]
        [2, 3, 4, 5]

    In the second race, you could hold the button for at least `4` milliseconds and at most `11`
    milliseconds and beat the record, a total of **`8`** different ways to win.

        >>> [t for t in range(15) if travel_distance(t, 15) > 40]
        [4, 5, 6, 7, 8, 9, 10, 11]
        >>> winning_range(race_time=15, distance_to_beat=40)
        range(4, 12)
        >>> len(_)
        8

    In the third race, you could hold the button for at least `11` milliseconds and no more than
    `19` milliseconds and still beat the record, a total of **`9`** ways you could win.

        >>> winning_range(*races_[2])
        range(11, 20)
        >>> len(_)
        9

    To see how much margin of error you have, determine the **number of ways you can beat the
    record** in each race; in this example, if you multiply these values together, you get **`288`**

        >>> math.prod(len(winning_range(*race)) for race in races_)
        288

    Determine the number of ways you could beat the record in each race.
    **What do you get if you multiply these numbers together?**

        >>> part_1(races_)
        part 1: you can win the races in 288 ways
        288
    """

    result = math.prod(len(winning_range(*race)) for race in races)

    print(f"part 1: you can win the races in {result} ways")
    return result


def part_2(single_race: 'Race') -> int:
    """
    As the race is about to start, you realize the piece of paper with race times and record
    distances you got earlier actually just has very bad kerning. There's really **only one race** -
    ignore the spaces between the numbers on each line.

    So, the example from before:

        >>> single_race_ = single_race_from_text('''
        ...     Time:      7  15   30
        ...     Distance:  9  40  200
        ... ''')

    ...now instead means this:

        Time:      71530
        Distance:  940200

        >>> single_race_
        (71530, 940200)

    Now, you have to figure out how many ways there are to win this single race. In this example,
    the race lasts for **`71530` milliseconds** and the record distance you need to beat is
    **`940200` millimeters**. You could hold the button anywhere from `14` to `71516` milliseconds
    and beat the record, a total of **`71503`** ways!

        >>> winning_range(*single_race_)
        range(14, 71517)
        >>> len(_)
        71503

    **How many ways can you beat the record in this one much longer race?**

        >>> part_2(single_race_)
        part 2: you can win the big race in 71503 ways
        71503
    """

    result = len(winning_range(*single_race))

    print(f"part 2: you can win the big race in {result} ways")
    return result


def travel_distance(hold_time: int, race_time: int) -> int:
    assert 0 <= hold_time <= race_time
    return (race_time - hold_time) * hold_time


def winning_range(race_time: int, distance_to_beat: int) -> range:
    # find the minimal value for which the race can be won using binary search
    min_range = BSRange(0, race_time // 2)
    while not min_range.has_single_value():
        pivot = min_range.mid
        assert pivot is not None
        win = travel_distance(pivot - 1, race_time) > distance_to_beat
        if win:
            min_range.upper = pivot
        else:
            min_range.lower = pivot

    min_value = min_range.single_value
    # maximal value is symmetric to the minimal one
    max_value = race_time - min_value

    return range(min_value, max_value + 1)


Race = tuple[int, int]


def races_from_file(fn: str) -> list[Race]:
    return list(races_from_lines(open(relative_path(__file__, fn))))


def races_from_text(text: str) -> list[Race]:
    return list(races_from_lines(text.strip().splitlines()))


def races_from_lines(lines: Iterable[str]) -> Iterable[Race]:
    time_line, distance_line = lines
    times_str, = parse_line(time_line.strip(), 'Time: $')
    distances_str, = parse_line(distance_line.strip(), 'Distance: $')
    return zip(
        (int(t) for t in times_str.split()),
        (int(d) for d in distances_str.split()),
    )


def single_race_from_file(fn: str) -> Race:
    return single_race_from_lines(open(relative_path(__file__, fn)))


def single_race_from_text(text: str) -> Race:
    return single_race_from_lines(text.strip().splitlines())


def single_race_from_lines(lines: Iterable[str]) -> Race:
    time_line, distance_line = lines
    times_str, = parse_line(time_line.strip(), 'Time: $')
    distances_str, = parse_line(distance_line.strip(), 'Distance: $')
    return (
        int(times_str.replace(' ', '')),
        int(distances_str.replace(' ', '')),
    )


def main(input_fn: str = 'data/06-input.txt') -> tuple[int, int]:
    result_1 = part_1(races_from_file(input_fn))
    result_2 = part_2(single_race_from_file(input_fn))
    return result_1, result_2


if __name__ == '__main__':
    main()
