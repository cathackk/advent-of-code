import math


# pylint: disable=invalid-name)
def program_part1():
    h = 0
    mul = 0

    # set b 57
    # set c b
    # jnz a 2 <- a is always true
    # jnz 1 5
    # skipped: mul b 100
    # skipped: sub b -100_000
    # skipped: set c b
    # skipped: sub c -17_000
    b = 57
    c = 57

    while True:
        # set f 1
        f = 1
        # set d 2
        d = 2

        while True:
            # set e 2
            e = 2

            while True:
                # set g d
                # mul g e
                # sub g b
                g = d * e - b
                mul += 1

                # jnz g 2
                # set f 0
                if g == 0:
                    f = 0

                # sub e -1
                e += 1
                # set g e
                # sub g b
                g = e - b

                # jnz g -8
                if g == 0:
                    break

            # sub d -1
            d += 1
            # set g d
            # sub g b
            g = d - b
            # jnz g -13
            if g == 0:
                break

        # jnz f 2
        # sub h -1
        if f == 0:
            h += 1

        # set g b
        # sub g c
        g = b - c
        # jnz g 2
        # jnz 1 3
        if g == 0:
            return mul

        # sub b -17
        # jnz 1 -23
        b += 17


def program_part2():
    return sum(
        1 for b in range(105_700, 122_700 + 1, 17)
        if any(b % d == 0 for d in range(2, math.ceil(math.sqrt(b))))
    )


def part_1():
    result = program_part1()
    print(f"part 1: {result}")
    return result


def part_2():
    result = program_part2()
    print(f"part 2: {result}")
    return  result

if __name__ == '__main__':
    part_1()
    part_2()
