#!/usr/bin/env python3

from importlib import import_module

import click
from click.exceptions import Exit

from meta.aoc_tools import day_files
from meta.aoc_tools import DayDescription
from meta.aoc_tools import year_dirs


# pylint: disable=unused-argument
def parse_year_dir(ctx: click.Context, param, value: int) -> str:
    try:
        year_dir = next(y_dir for y, y_dir in year_dirs() if y == value)
        ctx.ensure_object(dict)
        ctx.obj['year_dir'] = year_dir
        return year_dir

    except StopIteration as stop:
        click.echo(f">> year {value} not found", err=True)
        raise Exit(1) from stop


# pylint: disable=unused-argument
def parse_day_paths(ctx: click.Context, param, value) -> list[str]:
    year_dir = ctx.obj['year_dir']

    if value == 'all':
        return [d_filename for _, d_filename in day_files(year_dir)]

    day = int(value)
    try:
        return [next(d_filename for d, d_filename in day_files(year_dir) if d == day)]
    except StopIteration as stop:
        click.echo(f">> day {day} not found in {year_dir}", err=True)
        raise Exit(1) from stop


@click.command()
@click.option(
    '--year', '-y', 'year_dir', type=int, callback=parse_year_dir, required=True
)
# TODO: multiple days
@click.option(
    '--day', '-d', 'day_paths', type=click.UNPROCESSED, callback=parse_day_paths, required=True
)
@click.option(
    '--input', '-i', 'input_path', type=click.Path(exists=True), help="override default input path"
)
@click.option(
    '--show-description/--no-show-description', default=True
)
def run(year_dir: str, day_paths: list[str], input_path: str, show_description: bool):

    for day_path in day_paths:
        module_name = day_path.removesuffix('.py').replace('/', '.')
        module = import_module(module_name)

        if show_description:
            day_description = DayDescription.from_file(day_path)
            click.echo(f">> running {day_description}", err=True)

        try:
            if not input_path:
                module.main()
            else:
                module.main(input_path)

        except AttributeError as exc:
            click.echo(f">> {exc}", err=True)
            raise Exit(1) from exc


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    run()
