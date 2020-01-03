def next_row(row: str) -> str:
    """
    >>> next_row('..^^.')
    '.^^^^'
    >>> next_row('.^^^^')
    '^^..^'
    """
    rowx = '.'+row+'.'
    return ''.join(
        '^' if (rowx[k] != rowx[k+2]) else '.'
        for k in range(len(row))
    )


def safe_tiles_count(row0: str, height: int) -> int:
    safe_tiles = 0
    row = row0
    for _ in range(height):
        safe_tiles += sum(1 for c in row if c != '^')
        row = next_row(row)
    return safe_tiles


def part_1(row0: str, height: int = 40) -> int:
    safe_tiles = safe_tiles_count(row0, height)
    print(f"part 1: {safe_tiles} safe tiles in {height} rows")
    return safe_tiles


def part_2(row0: str, height: int = 400_000) -> int:
    safe_tiles = safe_tiles_count(row0, height)
    print(f"part 2: {safe_tiles} safe tiles in {height} rows")
    return safe_tiles


if __name__ == '__main__':
    first_row = open("data/18-input.txt").readline().strip()
    part_1(first_row)
    part_2(first_row)
