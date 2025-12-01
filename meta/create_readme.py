#!/usr/bin/env python3

import os
import os.path
from typing import Iterable

from common.file import relative_path
from common.logging import eprint
from meta.aoc_tools import day_files, DayDescription, year_dirs


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


def days_count(year: int) -> int:
    if year < 2015:
        raise IndexError("year out of range")
    return 25 if year < 2025 else 12


def index_lines() -> Iterable[str]:
    # years in reverse order
    years = list(year_dirs())[::-1]

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

        prev_day = 0
        for day, day_path in day_files(year_dir):
            try:
                desc = DayDescription.from_file(day_path)
            except ValueError as exc:
                eprint(f"WARNING: {exc}")
            else:
                assert desc.year == year
                assert desc.day == day
                assert day > prev_day
                if day > prev_day + 1:
                    yield "- ..."
                prev_day = day
                yield f"- ([aoc]({desc.aoc_url})) Day {desc.day}: [{desc.title}]({desc.path})"

        if prev_day < days_count(year):
            yield "- ..."


if __name__ == '__main__':
    # TODO: use click
    write_readme("README.md")
