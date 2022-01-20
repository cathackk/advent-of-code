"""
Advent of Code 2020
Day 13: Shuttle Search
https://adventofcode.com/2020/day/13
"""

from typing import Iterable

from common.utils import modular_inverse
from common.utils import relative_path


def part_1(start: int, bus_ids: Iterable[int]) -> int:
    """
    A shuttle bus service is available to bring you from the sea port to the airport. Each bus has
    an ID number that also indicates *how often the bus leaves for the airport*.

    Bus schedules are defined based on a *timestamp* that measures the *number of minutes* since
    some fixed reference point in the past. At timestamp `0`, every bus simultaneously departed
    from the sea port. After that, each bus travels to the airport, then various other locations,
    and finally returns to the sea port to repeat its journey forever.

    The time this loop takes a particular bus is also its ID number: the bus with ID `5` departs
    from the sea port at timestamps `0`, `5`, `10`, `15`, and so on. The bus with ID `11` departs
    at `0`, `11`, `22`, `33`, and so on. If you are there when the bus departs, you can ride that
    bus to the airport!

    Your notes (your puzzle input) consist of two lines. The first line is your estimate of the
    *earliest timestamp you could depart on a bus*. The second line lists the bus IDs that are in
    service according to the shuttle company; entries that show `x` must be out of service, so you
    decide to ignore them.

    To save time once you arrive, your goal is to figure out *the earliest bus you can take to the
    airport*. (There will be exactly one such bus.)

    For example, suppose you have the following notes:

        >>> start, buses = data_from_text('''
        ...     939
        ...     7,13,x,x,59,x,31,19
        ... ''')

    Here, the earliest timestamp you could depart is `939`, and the bus IDs in service are `7`,
    `13`, `59`, `31`, and `19`.

        >>> start
        939
        >>> list(buses.keys())
        [7, 13, 59, 31, 19]

    Near timestamp `939`, these bus IDs depart at the times marked D:

        >>> print_timetable(start, buses.keys(), context=10)
        time   bus 7   bus 13  bus 59  bus 31  bus 19
         929      .       .       .       .       .
         930      .       .       .       D       .
         931      D       .       .       .       D
         932      .       .       .       .       .
         933      .       .       .       .       .
         934      .       .       .       .       .
         935      .       .       .       .       .
         936      .       D       .       .       .
         937      .       .       .       .       .
         938      D       .       .       .       .
        >939<     .       .       .       .       .
         940      .       .       .       .       .
         941      .       .       .       .       .
         942      .       .       .       .       .
         943      .       .       .       .       .
         944      .       .      >D<      .       .
         945      D       .       .       .       .
         946      .       .       .       .       .
         947      .       .       .       .       .
         948      .       .       .       .       .
         949      .       D       .       .       .

    The earliest bus you could take is bus ID `59`.

        >>> departure, bus = earliest_departure(start, buses)
        >>> departure, bus
        (944, 59)

    It doesn't depart until timestamp `944`, so you would need to wait `944 - 939 = 5` minutes
    before it departs. Multiplying the bus ID by the number of minutes you'd need to wait gives
    *`295`*.

        >>> wait = departure - start
        >>> wait
        5
        >>> wait * bus
        295

    *What is the ID of the earliest bus you can take to the airport multiplied by the number of
    minutes you'll need to wait for that bus?*

        >>> part_1(start, buses)
        part 1: wait 5 minutes for bus 59 -> result = 295
        295
    """

    departure, bus_id = earliest_departure(start, bus_ids)
    wait_time = departure - start
    result = bus_id * wait_time

    print(f"part 1: wait {wait_time} minutes for bus {bus_id} -> result = {result}")
    return result


def part_2(bus_offsets: dict[int, int]) -> int:
    """
    The shuttle company is running a contest: one gold coin for anyone that can find the earliest
    timestamp such that the first bus ID departs at that time and each subsequent listed bus ID
    departs at that subsequent minute. (The first line in your input is no longer relevant.)

    For example, suppose you have the same list of bus IDs as above:

        >>> buses = bus_offsets_from_line('7,13,x,x,59,x,31,19')

    An `x` in the schedule means there are no constraints on what bus IDs must depart at that time.

    This means you are looking for the earliest timestamp (called `t`) such that:

        - Bus ID `7` departs at timestamp `t`.
        - Bus ID `13` departs one minute after timestamp `t`.
        - There are no requirements on departures at two or three minutes after `t`.
        - Bus ID `59` departs four minutes after `t`.
        - There are no requirements on departures at five minutes after `t`.
        - Bus ID `31` departs six minutes after `t`.
        - Bus ID `19` departs seven minutes after `t`.

        >>> buses
        {7: 0, 13: 1, 59: 4, 31: 6, 19: 7}

    The only bus departures that matter are the listed bus IDs at their specific offsets from `t`.
    Those bus IDs can depart at other times, and other bus IDs can depart at those times. For
    example, in the list above, because bus ID `19` must depart seven minutes after the timestamp
    at which bus ID `7` departs, bus ID `7` will always also be departing with bus ID `19` at seven
    minutes after timestamp `t`.

    In this example, the earliest timestamp at which this occurs is `1068781`:

        >>> earliest_offset_departures(buses)
        1068781
        >>> print_timetable(start=_, end=_+7, bus_ids=buses.keys(), context=8)
        time       bus 7   bus 13  bus 59  bus 31  bus 19
         1068773      .       .       .       .       .
         1068774      D       .       .       .       .
         1068775      .       .       .       .       .
         1068776      .       .       .       .       .
         1068777      .       .       .       .       .
         1068778      .       .       .       .       .
         1068779      .       .       .       .       .
         1068780      .       .       .       .       .
        >1068781<    >D<      .       .       .       .
         1068782      .       D       .       .       .
         1068783      .       .       .       .       .
         1068784      .       .       .       .       .
         1068785      .       .       D       .       .
         1068786      .       .       .       .       .
         1068787      .       .       .       D       .
         1068788      D       .       .       .       D
         1068789      .       .       .       .       .
         1068790      .       .       .       .       .
         1068791      .       .       .       .       .
         1068792      .       .       .       .       .
         1068793      .       .       .       .       .
         1068794      .       .       .       .       .
         1068795      D       D       .       .       .
         1068796      .       .       .       .       .

    In the above example, bus ID `7` departs at timestamp `1068788` (seven minutes after t). This
    is fine; the only requirement on that minute is that bus ID `19` departs then, and it does.

    Here are some other examples:

        >>> earliest_offset_departures(bus_offsets_from_line('17,x,13,19'))
        3417
        >>> earliest_offset_departures(bus_offsets_from_line('67,7,59,61'))
        754018
        >>> earliest_offset_departures(bus_offsets_from_line('67,x,7,59,61'))
        779210
        >>> earliest_offset_departures(bus_offsets_from_line('67,7,x,59,61'))
        1261476
        >>> earliest_offset_departures(bus_offsets_from_line('1789,37,47,1889'))
        1202161486

    However, with so many bus IDs in your list, surely the actual earliest timestamp will be larger
    than `100000000000000`!

    *What is the earliest timestamp such that all of the listed bus IDs depart at offsets matching
    their positions in the list?*

        >>> part_2(buses)
        part 2: earliest timestamp with matching offset departures is 1068781
        1068781
    """

    result = earliest_offset_departures(bus_offsets)

    print(f"part 2: earliest timestamp with matching offset departures is {result}")
    return result


def data_from_text(text: str) -> tuple[int, dict[int, int]]:
    return data_from_lines(text.strip().splitlines())


def data_from_file(fn: str) -> tuple[int, dict[int, int]]:
    return data_from_lines(relative_path(__file__, fn))


def data_from_lines(lines: Iterable[str]) -> tuple[int, dict[int, int]]:
    lines = list(lines)
    assert len(lines) == 2

    start = int(lines[0].strip())
    buses = bus_offsets_from_line(lines[1].strip())

    return start, buses


def bus_offsets_from_line(line: str) -> dict[int, int]:
    return {
        int(bus_id): offset
        for offset, bus_id in enumerate(line.split(","))
        if bus_id != "x"
    }


def print_timetable(start: int, bus_ids: Iterable[int], context: int, end: int = None):
    """ Visualize departures in readable timetable. """

    bus_ids = list(bus_ids)
    if end is None:
        end = start

    # header
    time_val_width = len(str(end))
    time_col_width = max(4, time_val_width + 2)
    time_header_pad = " " * (time_col_width-4)
    print("  ".join(["time" + time_header_pad] + [f"bus {bus_id:<2}" for bus_id in bus_ids]))

    # rows
    found_departing = False
    for time in range(start - context, end + context + 1):
        if time >= start and not found_departing and any(time % bus_id == 0 for bus_id in bus_ids):
            departure_text = "  >D< "
            found_departing = True
        else:
            departure_text = "   D  "

        time_text = f">{time:{time_val_width}}<" if time == start else f" {time} "
        departure_texts = [
            departure_text if time % bus_id == 0 else "   .  "
            for bus_id in bus_ids
        ]
        print("  ".join([time_text] + departure_texts).rstrip())


def earliest_departure(start: int, bus_ids: Iterable[int]) -> tuple[int, int]:
    return min(
        (start + (-start % bus_id), bus_id)
        for bus_id in bus_ids
    )


def earliest_offset_departures(bus_offsets: dict[int, int]) -> int:
    return find_divrem(
        (bus_id, -offset % bus_id)
        for bus_id, offset in bus_offsets.items()
    )


def find_divrem(divrems: Iterable[tuple[int, int]]) -> int:
    # lowest number L which follows each rule so far
    # rule := (L % div == rem)
    # after dividing L by `div`, you get remainder `rem`
    lowest = 0

    # lowest number that can be added to L and still suffice all rules
    # (product of all `div`s so far)
    prod = 1

    # we'll go through the rules one by one, modifying the two values above
    for div, rem in divrems:
        # target_rem = (rem - lowest) % div
        # k = next(x for x in range(div) if (x * prod) % div == target_rem)
        # lowest += k * prod
        lowest += prod * divide(rem - lowest, prod, div)
        prod *= div

    return lowest


def divide(x, y, base) -> int:
    return (x * modular_inverse(y, base)) % base


if __name__ == '__main__':
    start_, buses_offsets_ = data_from_file("data/13-input.txt")
    assert len(buses_offsets_) == 9

    part_1(start_, buses_offsets_.keys())
    part_2(buses_offsets_)
