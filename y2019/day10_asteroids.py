import math
from typing import Iterable

from xy import Point
from xy import Vector


def load_points(fn) -> list[Point]:
    with open(fn) as f:
        return sorted(
            Point(x, y)
            for y, line in enumerate(f)
            for x, c in enumerate(line.strip())
            if c != '.'
        )


def best_base(asteroids: list[Point]) -> Point:
    return max(asteroids, key=lambda c: seen_count(c, asteroids))


def seen_count(base: Point, asteroids: list[Point]) -> int:
    return sum(1 for _ in gen_seen(base, asteroids))


def gen_seen(base: Point, asteroids: Iterable[Point]) -> Iterable[Point]:
    asteroids = list(asteroids)
    asteroids_set = set(asteroids)
    return (
        asteroid
        for asteroid in asteroids
        if asteroid != base and can_be_seen(base, asteroid, asteroids_set)
    )


def can_be_seen(base: Point, target: Point, asteroids: set[Point]) -> bool:
    return not any(obstacles(base, target, asteroids))


def obstacles(base: Point, target: Point, asteroids: set[Point]) -> Iterable[Point]:
    n = (target - base).normalize()
    c = base + n
    while True:
        if c == target:
            return
        if c in asteroids:
            yield c
        c += n


def rotate_laser(
        base: Point,
        asteroids: Iterable[Point],
        debug: bool = False
) -> Iterable[Point]:

    asteroids_left = set(asteroids)
    asteroids_left.remove(base)  # we are not going to shoot ourselves!

    def angle(asteroid: Point) -> float:
        return (asteroid - base).angle()

    round_no = 0
    vaporized_no = 0

    while asteroids_left:
        round_no += 1
        seen = set(gen_seen(base, asteroids_left))

        for vaporized in sorted(seen, key=angle):
            vaporized_no += 1
            if debug:
                print(
                    f"{round_no:2} / {vaporized_no:3}: "
                    f"vaporizing asteroid at {vaporized} "
                    f"(angle={round(180*angle(vaporized)/math.pi, 1)})"
                )
            yield vaporized

        asteroids_left.difference_update(seen)


def test_load_points():
    points = load_points('data/10-example-1.txt')
    assert points == [
        Point(0, 2),
        Point(1, 0), Point(1, 2),
        Point(2, 2),
        Point(3, 2), Point(3, 4),
        Point(4, 0), Point(4, 2), Point(4, 3), Point(4, 4)
    ]


def test_vector_normalize():
    assert Vector(2, 4).normalize() == Vector(1, 2)
    assert Vector(-1, -1).normalize() == Vector(-1, -1)
    assert Vector(-6, 3).normalize() == Vector(-2, 1)
    assert Vector(45, 18).normalize() == Vector(5, 2)
    assert Vector(3, 7).normalize() == Vector(3, 7)
    assert Vector(3, -7).normalize() == Vector(3, -7)
    assert Vector(-3, 7).normalize() == Vector(-3, 7)
    assert Vector(-3, -7).normalize() == Vector(-3, -7)
    assert Vector(1, 0).normalize() == Vector(1, 0)
    assert Vector(0, 2).normalize() == Vector(0, 1)
    assert Vector(0, -4).normalize() == Vector(0, -1)
    try:
        Vector(0, 0).normalize()
        assert False
    except ZeroDivisionError:
        pass


def test_vector_angle():
    assert Vector(0, -1).angle() == 0
    assert Vector(1, 0).angle() == math.pi/2
    assert Vector(0, 1).angle() == math.pi
    assert Vector(-1, 0).angle() == 3*math.pi/2
    assert Vector(1, 1).angle() == 3*math.pi/4


def test_can_be_seen():
    assert can_be_seen(Point(0, 0), Point(1, 1), set()) is True
    assert can_be_seen(Point(0, 0), Point(2, 2), {Point(1, 1)}) is False
    assert can_be_seen(Point(0, 0), Point(6, 6), {Point(4, 4)}) is False
    assert can_be_seen(Point(0, 0), Point(2, 3), {Point(1, 1)}) is True
    assert can_be_seen(Point(0, 2), Point(2, 2), {Point(1, 2)}) is False
    assert can_be_seen(Point(1, 0), Point(2, 3), {Point(1, 0), Point(1, 1), Point(2, 3)}) is True


def test_gen_seen():
    asteroids = load_points('data/10-example-1.txt')
    assert list(gen_seen(Point(0, 2), asteroids)) == [
        Point(1, 0), Point(1, 2),
        Point(3, 4),
        Point(4, 0), Point(4, 3), Point(4, 4)
    ]


def test_best_bases():
    expected = [
        ('data/10-example-1.txt', Point(3, 4), 8),
        ('data/10-example-2.txt', Point(5, 8), 33),
        ('data/10-example-3.txt', Point(1, 2), 35),
        ('data/10-example-4.txt', Point(6, 3), 41),
        ('data/10-example-5.txt', Point(11, 13), 210)
    ]
    for fn, expected_base, expected_seen in expected:
        asteroids = load_points(fn)
        base = best_base(asteroids)
        assert base == expected_base
        seen = seen_count(base, asteroids)
        assert seen == expected_seen
        print(f">>>> passed test_best_bases: {fn}")


def test_rotate_laser():
    asteroids = load_points('data/10-example-5.txt')
    base = best_base(asteroids)
    assert base == Point(11, 13)

    vaporized = list(rotate_laser(base, asteroids))
    assert len(vaporized) == 299

    assert vaporized[0] == Point(11, 12)
    assert vaporized[1] == Point(12, 1)
    assert vaporized[2] == Point(12, 2)
    assert vaporized[9] == Point(12, 8)
    assert vaporized[19] == Point(16, 0)
    assert vaporized[49] == Point(16, 9)
    assert vaporized[99] == Point(10, 16)
    assert vaporized[198] == Point(9, 6)
    assert vaporized[199] == Point(8, 2)
    assert vaporized[200] == Point(10, 9)
    assert vaporized[-1] == Point(11, 1)


def tests():
    for test in [
        test_load_points,
        test_vector_normalize,
        test_vector_angle,
        test_can_be_seen,
        test_gen_seen,
        test_best_bases,
        test_rotate_laser,
    ]:
        test()
        print(f">> passed {test.__name__}")

    print("passed all tests")
    print()


def main():
    asteroids = load_points('data/10-input.txt')
    base = best_base(asteroids)
    seen = seen_count(base, asteroids)
    print(f"best base is at {base}, it can see {seen} asteroids")

    vaporized = list(rotate_laser(base, asteroids, debug=False))
    print(f"the 200th vaporized asteroid is at {vaporized[199]}")


if __name__ == '__main__':
    main()
