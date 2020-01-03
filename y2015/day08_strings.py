def part_1(lines):
    ll = sum(len(line) for line in lines)
    strings = [eval(line) for line in lines]
    sl = sum(len(s) for s in strings)
    print(f"{ll} - {sl} = {ll - sl}")


def part_2(lines):
    ll = sum(len(line) for line in lines)
    ell = sum(
        2 + sum(
            2 if c in '\\"' else 1
            for c in line
        )
        for line in lines
    )
    print(f"{ell} - {ll} = {ell - ll}")


if __name__ == '__main__':
    lines = [line.strip() for line in open("data/08-input.txt")]
    # part_1(lines)
    part_2(lines)

