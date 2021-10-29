from collections import Counter


def load_lines(fn: str) -> list[str]:
    return [line.strip() for line in open(fn)]


def repcode(codes: list[str], most_common: bool) -> str:
    codes = list(codes)
    assert len(codes) > 0
    length = len(codes[0])
    assert all(len(code) == length for code in codes)

    most_common_index = 0 if most_common else -1
    return ''.join(
        Counter(code[k] for code in codes).most_common()[most_common_index][0]
        for k in range(length)
    )


def test_repcode():
    lines = load_lines("data/06-example.txt")
    assert repcode(lines, most_common=True) == "easter"
    assert repcode(lines, most_common=False) == "advent"


def part_1(lines: list[str]) -> str:
    message = repcode(lines, most_common=True)
    print(f"part 1: message is {message!r}")
    return message


def part_2(lines: list[str]) -> str:
    message = repcode(lines, most_common=False)
    print(f"part 2: message is {message!r}")
    return message


if __name__ == '__main__':
    lines_ = load_lines("data/06-input.txt")
    part_1(lines_)
    part_2(lines_)
