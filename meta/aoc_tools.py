import os
import re
from dataclasses import dataclass
from typing import Iterable

from common.file import relative_path
from common.text import parse_line


def year_dirs() -> Iterable[tuple[int, str]]:
    return sorted(
        (int(filename[1:]), filename)
        for filename in os.listdir()
        if os.path.isdir(filename)
        if re.match(r'y\d{4}', filename)
    )


def parse_day_number(filename: str) -> int:
    num, _ = parse_line(filename, "day$_$.py")
    return int(num)


def day_files(path: str) -> Iterable[tuple[int, str]]:
    return sorted(
        (day_number, os.path.join(path, filename))
        for filename in os.listdir(path)
        if re.fullmatch(r'day\d\d_[a-z0-9_]+\.py', filename)
        if (day_number := parse_day_number(filename)) > 0  # ignore template
    )


def data_path(module_path: str, filename: str = 'input.txt') -> str:
    number = parse_day_number(os.path.basename(module_path))
    return relative_path(module_path, f'data/{number:02}-{filename}')


@dataclass(frozen=True, order=True)
class DayDescription:
    year: int
    day: int
    title: str
    path: str
    aoc_url: str

    def __str__(self) -> str:
        return f"{self.path} -- AoC {self.year} Day {self.day}: {self.title}"

    @classmethod
    def from_file(cls, path: str) -> 'DayDescription':
        with open(path) as file:
            # """
            # Advent of Code 2020
            # Day 20: Jurassic Jigsaw
            # https://adventofcode.com/2020/day/20
            # """
            if next(file) != '"""\n':
                raise ValueError(f"missing description in {path}")
            try:
                year, = parse_line(next(file), "Advent of Code $\n")
                day, title = parse_line(next(file), "Day $: $\n")
            except AssertionError as exc:
                raise ValueError(f"description in {path} in unexpected format") from exc

            aoc_url = next(file).strip()
            if aoc_url != f'https://adventofcode.com/{year}/day/{day}':
                raise ValueError(f"unexpected url in {path}")

            if next(file) != '"""\n':
                raise ValueError(f"description missing closing quotes in {path}")

            return cls(year=int(year), day=int(day), title=title, path=path, aoc_url=aoc_url)
