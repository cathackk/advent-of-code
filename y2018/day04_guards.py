from collections import Counter
from typing import Iterable
from typing import List
from typing import NamedTuple
from typing import Optional

from utils import dgroupby
from utils import maxk
from utils import parse_line
from utils import strip_line


class Event(NamedTuple):
    guard_no: int
    asleep: range

    @property
    def duration(self) -> int:
        return len(self.asleep)


def load_events(fn: str) -> Iterable[Event]:
    guard_no: Optional[int] = None
    asleep_since: Optional[int] = None

    for line in sorted(open(fn)):
        # [1518-03-06 23:47] Guard #1009 begins shift
        dt, what = parse_line(line, '[', '] ', '\n')
        minute = int(dt.split(':')[1])

        if what.startswith("Guard #"):
            assert asleep_since is None
            guard_no = int(strip_line(what, "Guard #", " begins shift"))
        elif what == "falls asleep":
            assert guard_no is not None
            asleep_since = minute
        elif what == "wakes up":
            assert guard_no is not None
            assert asleep_since < minute
            yield Event(guard_no, range(asleep_since, minute))
            asleep_since = None
        else:
            raise KeyError(what)


def part_1(events: List[Event]) -> int:
    sleep_durations = dgroupby(events, key=lambda e: e.guard_no, value=lambda e: e.duration)
    sleepy_guard_no, total_asleep = maxk(
        sleep_durations.keys(),
        key=lambda g: sum(sleep_durations[g])
    )
    print(f"... guard #{sleepy_guard_no} spends {total_asleep} minutes asleep")

    sleepy_minute, minute_count = Counter(
        minute
        for e in events
        if e.guard_no == sleepy_guard_no
        for minute in e.asleep
    ).most_common(1)[0]
    print(f"... guard #{sleepy_guard_no} sleeps the most "
          f"during minute 00:{sleepy_minute} (x{minute_count})")

    result = sleepy_guard_no * sleepy_minute
    print(f"part 1: result = {sleepy_guard_no} * {sleepy_minute} = {result}")
    return result


def part_2(events: List[Event]) -> int:
    (sleepy_guard_no, sleepy_minute), minute_count = Counter(
        (e.guard_no, minute)
        for e in events
        for minute in e.asleep
    ).most_common(1)[0]
    print(f"... guard #{sleepy_guard_no} sleeps the most "
          f"during minute 00:{sleepy_minute} (x{minute_count})")

    result = sleepy_guard_no * sleepy_minute
    print(f"part 2: result = {sleepy_guard_no} * {sleepy_minute} = {result}")
    return result


if __name__ == '__main__':
    events_ = list(load_events("data/04-input.txt"))
    part_1(events_)
    part_2(events_)
