import os
import os.path
from dataclasses import dataclass
from typing import Iterable

from common.file import relative_path
from common.logging import eprint
from common.text import parse_line


def write_readme(readme_fn: str):
    template_lines = load_template()

    _set_current_path_to_root()

    with open(readme_fn, 'w') as file_out:

        for template_line in template_lines:
            if template_line == '{index}\n':
                file_out.writelines(line + "\n" for line in index_lines())
            else:
                file_out.write(template_line)

    print(f"readme text written to {readme_fn}")


def load_template(template_fn: str = 'readme-template') -> list[str]:
    return open(relative_path(__file__, template_fn)).readlines()


def _set_current_path_to_root() -> None:
    root_dir = os.path.join(os.getcwd(), os.path.dirname(__file__), '..')
    os.chdir(os.path.realpath(root_dir))


def index_lines() -> Iterable[str]:
    years = list(year_dirs())

    yield "## Index"
    yield ""
    for year, _ in years:
        yield f"- [{year}](#{year})"

    for year, year_dir in years:
        yield ""
        yield ""
        yield f"### {year}"
        yield ""
        yield f"([aoc {year} event](https://adventofcode.com/{year}))"
        yield ""

        complete_days_count = 0

        for day, day_path in day_files(year_dir):
            try:
                desc = DayDescription.from_file(day_path)
            except ValueError as exc:
                eprint(f"WARNING: {exc}")
            else:
                assert desc.year == year
                assert desc.day == day
                yield f"- ([aoc]({desc.aoc_url})) Day {desc.day}: [{desc.title}]({desc.path})"
                complete_days_count += 1

        if complete_days_count < 25:
            yield "..."


def year_dirs() -> Iterable[tuple[int, str]]:
    dirs = (
        (int(fn[1:]), fn)
        for fn in os.listdir()
        if os.path.isdir(fn)
        if fn.startswith('y')
    )
    return sorted(dirs, reverse=True)


def day_files(path: str) -> Iterable[tuple[int, str]]:
    def parse_day_number(fn: str) -> int:
        num, _ = parse_line(fn, "day$_$.py")
        return int(num)

    return sorted(
        (parse_day_number(filename), os.path.join(path, filename))
        for filename in os.listdir(path)
        if filename.startswith('day')
        if filename.endswith('.py')
    )


@dataclass(frozen=True, order=True)
class DayDescription:
    year: int
    day: int
    title: str
    path: str
    aoc_url: str

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


if __name__ == '__main__':
    # TODO: use click
    write_readme("README.md")
