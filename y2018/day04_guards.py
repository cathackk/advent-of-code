"""
Advent of Code 2018
Day 4: Repose Record
https://adventofcode.com/2018/day/4
"""

from collections import Counter
from typing import Iterable
from typing import NamedTuple

from common.text import parse_line
from common.utils import some
from meta.aoc_tools import data_path


def part_1(nights: Iterable['NightRecord']) -> int:
    """
    You've sneaked into another supply closet - this time, it's across from the prototype suit
    manufacturing lab. You need to sneak inside and fix the issues with the suit, but there's
    a guard stationed outside the lab, so this is as close as you can safely get.

    As you search the closet for anything that might help, you discover that you're not the first
    person to want to sneak in. Covering the walls, someone has spent an hour starting every
    midnight for the past few months secretly observing this guard post! They've been writing down
    the ID of **the one guard on duty that night** - the Elves seem to have decided that one guard
    was enough for the overnight shift - as well as when they fall asleep or wake up while at their
    post (your puzzle input).

    For example, consider the following records, which have already been organized into
    chronological order:

        >>> example_events = events_from_text('''
        ...     [1518-11-01 00:00] Guard #10 begins shift
        ...     [1518-11-01 00:05] falls asleep
        ...     [1518-11-01 00:25] wakes up
        ...     [1518-11-01 00:30] falls asleep
        ...     [1518-11-01 00:55] wakes up
        ...     [1518-11-01 23:58] Guard #99 begins shift
        ...     [1518-11-02 00:40] falls asleep
        ...     [1518-11-02 00:50] wakes up
        ...     [1518-11-03 00:05] Guard #10 begins shift
        ...     [1518-11-03 00:24] falls asleep
        ...     [1518-11-03 00:29] wakes up
        ...     [1518-11-04 00:02] Guard #99 begins shift
        ...     [1518-11-04 00:36] falls asleep
        ...     [1518-11-04 00:46] wakes up
        ...     [1518-11-05 00:03] Guard #99 begins shift
        ...     [1518-11-05 00:45] falls asleep
        ...     [1518-11-05 00:55] wakes up
        ... ''')

    Timestamps are written using `year-month-day hour:minute format`. The guard falling asleep or
    waking up is always the one whose shift most recently started. Because all asleep/awake times
    are during the midnight hour (`00:00` - `00:59`), only the minute portion (`00` - `59`) is
    relevant for those events.

        >>> example_events  # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
        [Event(time=Timestamp(1518, 11, 1, 0, 0), guard_id=10, what='begins shift'),
         Event(time=Timestamp(1518, 11, 1, 0, 5), guard_id=None, what='falls asleep'),
         Event(time=Timestamp(1518, 11, 1, 0, 25), guard_id=None, what='wakes up'),
         Event(time=Timestamp(1518, 11, 1, 0, 30), guard_id=None, what='falls asleep'),
         Event(time=Timestamp(1518, 11, 1, 0, 55), guard_id=None, what='wakes up'),
         Event(time=Timestamp(1518, 11, 1, 23, 58), guard_id=99, what='begins shift'),
         Event(time=Timestamp(1518, 11, 2, 0, 40), guard_id=None, what='falls asleep'),
         ...
         Event(time=Timestamp(1518, 11, 5, 0, 55), guard_id=None, what='wakes up')]
        >>> example_night_records = list(records_from_events(example_events))
        >>> example_night_records  # doctest: +NORMALIZE_WHITESPACE
        [NightRecord(date=Date(1518, 11, 1), guard_id=10, sleep=[range(5, 25), range(30, 55)]),
         NightRecord(date=Date(1518, 11, 2), guard_id=99, sleep=[range(40, 50)]),
         NightRecord(date=Date(1518, 11, 3), guard_id=10, sleep=[range(24, 29)]),
         NightRecord(date=Date(1518, 11, 4), guard_id=99, sleep=[range(36, 46)]),
         NightRecord(date=Date(1518, 11, 5), guard_id=99, sleep=[range(45, 55)])]


    Visually, these records show that the guards are asleep at these times:

        >>> print_schedule(example_night_records)
        Date   ID   Minute
                    000000000011111111112222222222333333333344444444445555555555
                    012345678901234567890123456789012345678901234567890123456789
        11-01  #10  .....####################.....#########################.....
        11-02  #99  ........................................##########..........
        11-03  #10  ........................#####...............................
        11-04  #99  ....................................##########..............
        11-05  #99  .............................................##########.....

    The columns are Date, which shows the month-day portion of the relevant day; ID, which shows the
    guard on duty that day; and Minute, which shows the minutes during which the guard was asleep
    within the midnight hour. (The Minute column's header shows the minute's ten's digit in the
    first row and the one's digit in the second row.) Awake is shown as `.`, and asleep as `#`.

    Note that guards count as asleep on the minute they fall asleep, and they count as awake on the
    minute they wake up. For example, because Guard #10 wakes up at 00:25 on 1518-11-01, minute 25
    is marked as awake.

    If you can figure out the guard most likely to be asleep at a specific time, you might be able
    to trick that guard into working tonight, so you can have the best chance of sneaking in. You
    have two strategies for choosing the best guard/minute combination.

    **Strategy 1:** Find the guard that has the most minutes asleep. What minute does that guard
    spend asleep the most?

    In the example above, Guard #10 spent the most minutes asleep, a total of `50` minutes
    (`20+25+5`), while Guard #99 only slept for a total of `30` minutes (`10+10+10`).

        >>> slept_per_guard(example_night_records)
        Counter({10: 50, 99: 30})

    Guard #10 was asleep most during minute 24 (on two days, whereas any other minute the guard was
    asleep was only seen on one day).

        >>> slept_per_minute(example_night_records, guard_id=10).most_common(1)
        [(24, 2)]

    While this example listed the entries in chronological order, your entries are in the order you
    found them. You'll need to organize them before they can be analyzed.

    **What is the ID of the guard you chose multiplied by the minute you chose?**

        >>> part_1(example_night_records)
        part 1: guard 10 sleeps the most on minute 24 -> result is 240
        240
    """

    nights_list = list(nights)
    guard_id = slept_per_guard(nights_list).most_common(1)[0][0]
    minute = slept_per_minute(nights_list, guard_id).most_common(1)[0][0]
    result = guard_id * minute
    print(f"part 1: guard {guard_id} sleeps the most on minute {minute} -> result is {result}")
    return result


def part_2(nights: Iterable['NightRecord']) -> int:
    """
    **Strategy 2:** Of all guards, which guard is most frequently asleep on the same minute?

    In the example above, Guard #99 spent minute 45 asleep more than any other guard or minute -
    three times in total. (In all other cases, any guard spent any minute asleep at most twice.)

        >>> example_records = records_from_file('data/04-example.txt')
        >>> slept_per_guard_minute(example_records).most_common(2)
        [((99, 45), 3), ((10, 24), 2)]

    **What is the ID of the guard you chose multiplied by the minute you chose?**

        >>> part_2(example_records)
        part 2: guard 99 sleeps the most on minute 45 -> result is 4455
        4455
    """

    guard_id, minute = slept_per_guard_minute(nights).most_common(1)[0][0]
    result = guard_id * minute
    print(f"part 2: guard {guard_id} sleeps the most on minute {minute} -> result is {result}")
    return result


class Date(NamedTuple):
    year: int
    month: int
    day: int

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.year!r}, {self.month!r}, {self.day!r})'

    def __str__(self) -> str:
        return format(self, 'y-m-d')

    def __format__(self, format_spec) -> str:
        if format_spec == 'y-m-d':
            return f"{self.year}-{self.month:02}-{self.day:02}"
        elif format_spec == 'm-d':
            return f"{self.month:02}-{self.day:02}"
        else:
            raise ValueError(format_spec)


class Timestamp(NamedTuple):
    year: int
    month: int
    day: int
    hour: int
    minute: int

    def __repr__(self) -> str:
        tn = type(self).__name__
        return f'{tn}({self.year!r}, {self.month!r}, {self.day!r}, {self.hour!r}, {self.minute!r})'

    @classmethod
    def from_str(cls, string: str) -> 'Timestamp':
        year, month, day, hour, minute = parse_line(string, "$-$-$ $:$")
        return Timestamp(int(year), int(month), int(day), int(hour), int(minute))

    @property
    def date(self) -> Date:
        return Date(self.year, self.month, self.day)


class Event:
    def __init__(self, time: Timestamp, guard_id: int | None, what: str):
        self.time = time
        self.guard_id = guard_id
        self.what = what

    def __repr__(self) -> str:
        tn = type(self).__name__
        return f'{tn}(time={self.time!r}, guard_id={self.guard_id!r}, what={self.what!r})'

    def __lt__(self, other) -> bool:
        if not isinstance(other, type(self)):
            raise TypeError(type(other))
        return self.time < other.time

    @property
    def date(self) -> Date:
        return self.time.date

    @classmethod
    def from_str(cls, line: str) -> 'Event':
        # [1518-11-01 00:00] Guard #10 begins shift
        # [1518-11-01 00:05] falls asleep

        ts_str, action = parse_line(line, "[$] $")
        time = Timestamp.from_str(ts_str)
        if action.startswith("Guard #"):
            guard_id, what = parse_line(action, "Guard #$ $")
            return cls(time, int(guard_id), what)
        else:
            return cls(time, None, action)


class NightRecord:
    def __init__(self, date: Date, guard_id: int, sleep: Iterable[range]):
        self.date = date
        self.guard_id = guard_id
        self.sleep = list(sleep)

    def __repr__(self) -> str:
        tn = type(self).__name__
        return f'{tn}(date={self.date!r}, guard_id={self.guard_id!r}, sleep={self.sleep!r})'

    def minutes_asleep(self) -> Iterable[int]:
        return (
            minute
            for sleep_range in self.sleep
            for minute in sleep_range
        )

    def is_asleep(self, minute: int):
        assert minute in range(60)
        return any(minute in r for r in self.sleep)

    @property
    def sleep_time(self) -> int:
        return sum(len(r) for r in self.sleep)

    def __str__(self) -> str:
        sleep = "".join("#" if self.is_asleep(minute) else "." for minute in range(60))
        return f"{self.date:m-d}  #{self.guard_id:02}  {sleep}"


def print_schedule(records: Iterable[NightRecord]) -> None:
    print("Date   ID   Minute")
    print("            000000000011111111112222222222333333333344444444445555555555")
    print("            012345678901234567890123456789012345678901234567890123456789")
    print("\n".join(str(record) for record in records))


def slept_per_guard(records: Iterable[NightRecord]) -> Counter[int]:
    guard_sleep: Counter[int] = Counter()
    for record in records:
        guard_sleep[record.guard_id] += record.sleep_time
    return guard_sleep


def slept_per_minute(records: Iterable[NightRecord], guard_id: int) -> Counter[int]:
    return Counter(
        minute
        for record in records
        if record.guard_id == guard_id
        for minute in record.minutes_asleep()
    )


def slept_per_guard_minute(records: Iterable[NightRecord]) -> Counter[tuple[int, int]]:
    return Counter(
        (record.guard_id, minute)
        for record in records
        for minute in record.minutes_asleep()
    )


def events_from_text(text: str) -> list[Event]:
    return sorted(events_from_lines(text.strip().splitlines()))


def events_from_file(fn: str) -> list[Event]:
    return sorted(events_from_lines(open(fn)))


def events_from_lines(lines: Iterable[str]) -> Iterable[Event]:
    return (Event.from_str(line.strip()) for line in lines)


def records_from_file(fn: str) -> list[NightRecord]:
    return list(records_from_events(events_from_file(fn)))


def records_from_events(events: Iterable[Event]) -> Iterable[NightRecord]:
    current_date: Date | None = None
    current_guard_id: int | None = None
    current_sleeps: list[range] = []
    last_sleep_minute: int | None = None
    last_timestamp: Timestamp | None = None

    for event in events:
        if last_timestamp:
            assert event.time > last_timestamp

        last_timestamp = event.time

        if event.guard_id is not None:
            assert event.what == "begins shift"

            if current_sleeps:
                yield NightRecord(some(current_date), some(current_guard_id), current_sleeps)
                current_sleeps = []

            current_guard_id = event.guard_id
            current_date = None

        else:
            assert event.time.hour == 0
            current_date = event.date

            if event.what == "falls asleep":
                assert last_sleep_minute is None
                last_sleep_minute = event.time.minute
            elif event.what == "wakes up":
                wake_up_minute = event.time.minute
                current_sleeps.append(range(some(last_sleep_minute), wake_up_minute))
                last_sleep_minute = None
            else:
                raise ValueError(event.what)

    if current_sleeps:
        yield NightRecord(some(current_date), some(current_guard_id), current_sleeps)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    records = records_from_file(input_path)
    result_1 = part_1(records)
    result_2 = part_2(records)
    return result_1, result_2


if __name__ == '__main__':
    main()
