import itertools
from typing import Generator
from typing import Iterable
from typing import Optional
from typing import Tuple

from utils import exhaust
from utils import last
from utils import lcm
from utils import sgn
from xyz import Point3
from xyz import Vector3


def sgn_v3(v3: Vector3):
    return Vector3(*(sgn(n) for n in v3))


class Body:
    def __init__(self, pos: Point3, vel: Vector3 = None):
        self.pos = pos
        self.vel = vel if vel is not None else Vector3.null()

    def __repr__(self):
        return f'{type(self).__name__}({self.pos!r}, {self.vel!r})'

    def __str__(self):
        return f"pos={self.pos}, vel={self.vel}"

    @property
    def potential_energy(self):
        return sum(abs(v) for v in self.pos)

    @property
    def kinetic_energy(self):
        return sum(abs(v) for v in self.vel)

    @property
    def energy(self):
        return self.potential_energy * self.kinetic_energy

    def only_x(self):
        return Body(Point3(self.pos.x, 0, 0), Vector3(self.vel.x, 0, 0))

    def only_y(self):
        return Body(Point3(0, self.pos.y, 0), Vector3(0, self.vel.y, 0))

    def only_z(self):
        return Body(Point3(0, 0, self.pos.z), Vector3(0, 0, self.vel.z))


SimState = Tuple[Tuple[Point3, Vector3], ...]


def simulate(
        bodies: Iterable[Body],
        steps_limit: int = None,
        debug: bool = False,
        say_each: int = None
) -> Iterable[SimState]:
    bodies = list(bodies)

    step = 0

    def log():
        if debug or (say_each and step % say_each == 0):
            print(f"After {step} steps:")
            print("\n".join(str(b) for b in bodies))
            print()

    log()
    yield tuple((b.pos, b.vel) for b in bodies)

    while not steps_limit or step < steps_limit:
        # 1. adjust velocities based on current positions
        for b1, b2 in itertools.combinations(bodies, 2):
            b1.vel += sgn_v3(b1.pos.to(b2.pos))
            b2.vel += sgn_v3(b2.pos.to(b1.pos))
        # 2. adjust positions based on current velocities
        for b in bodies:
            b.pos += b.vel

        step += 1
        log()
        yield tuple((b.pos, b.vel) for b in bodies)


def simulate_reverse(
        bodies: Iterable[Body],
        steps_limit: int = None,
        debug: bool = False,
        say_each: int = None
) -> Iterable[SimState]:
    bodies = list(bodies)

    step = 0

    def log():
        if debug or (say_each and step % say_each == 0):
            print(f"After {step} reverse-steps:")
            print("\n".join(str(b) for b in bodies))
            print()

    log()
    yield tuple((b.pos, b.vel) for b in bodies)

    while not steps_limit or step < steps_limit:
        # 1. retrace positions based on current velocities
        for b in bodies:
            b.pos -= b.vel
        # 2. retrace velocities based on current positions
        for b1, b2 in itertools.combinations(bodies, 2):
            b1.vel -= sgn_v3(b1.pos.to(b2.pos))
            b2.vel -= sgn_v3(b2.pos.to(b1.pos))

        step += 1
        log()
        yield tuple((b.pos, b.vel) for b in bodies)


def until_repeat(
        simulation: Iterable[SimState]
) -> Generator[SimState, None, Optional[int]]:
    shs = dict()
    for step, state in enumerate(simulation):
        sh = hash(state)
        identical_step = shs.get(sh)
        if identical_step is None:
            shs[sh] = step
            yield step
        else:
            assert identical_step == 0
            return step
    else:
        return None


def until_repeat_steps(bodies: Iterable[Body], debug: bool = False) -> int:
    def log(message = ""):
        if debug:
            print(message)

    bodies = list(bodies)
    sx = exhaust(until_repeat(simulate(b.only_x() for b in bodies)))
    log(f">> sx = {sx}")
    sy = exhaust(until_repeat(simulate(b.only_y() for b in bodies)))
    log(f">> sy = {sy}")
    sz = exhaust(until_repeat(simulate(b.only_z() for b in bodies)))
    log(f">> sz = {sz}")
    ss = lcm(sx, sy, sz)
    log(f">> ss = {ss}")
    return ss


def test_1a():
    bodies = [
        Body(Point3(-1, 0, 2)),
        Body(Point3(2, -10, -7)),
        Body(Point3(4, -8, 8)),
        Body(Point3(3, 5, -1))
    ]
    r = list(simulate(bodies, steps_limit=10))
    assert len(r) == 11
    assert r[1] == (
        (Point3( 2, -1,  1), Vector3( 3, -1, -1)),
        (Point3( 3, -7, -4), Vector3( 1,  3,  3)),
        (Point3( 1, -7,  5), Vector3(-3,  1, -3)),
        (Point3( 2,  2,  0), Vector3(-1, -3,  1)),
    )
    assert r[2] == (
        (Point3( 5, -3, -1), Vector3( 3, -2, -2)),
        (Point3( 1, -2,  2), Vector3(-2,  5,  6)),
        (Point3( 1, -4, -1), Vector3( 0,  3, -6)),
        (Point3( 1, -4,  2), Vector3(-1, -6,  2)),
    )
    assert r[3] == (
        (Point3( 5, -6, -1), Vector3( 0, -3,  0)),
        (Point3( 0,  0,  6), Vector3(-1,  2,  4)),
        (Point3( 2,  1, -5), Vector3( 1,  5, -4)),
        (Point3( 1, -8,  2), Vector3( 0, -4,  0)),
    )
    assert r[4] == (
        (Point3( 2, -8,  0), Vector3(-3, -2,  1)),
        (Point3( 2,  1,  7), Vector3( 2,  1,  1)),
        (Point3( 2,  3, -6), Vector3( 0,  2, -1)),
        (Point3( 2, -9,  1), Vector3( 1, -1, -1)),
    )
    assert r[5] == (
        (Point3(-1, -9,  2), Vector3(-3, -1,  2)),
        (Point3( 4,  1,  5), Vector3( 2,  0, -2)),
        (Point3( 2,  2, -4), Vector3( 0, -1,  2)),
        (Point3( 3, -7, -1), Vector3( 1,  2, -2)),
    )
    assert r[6] == (
        (Point3(-1, -7,  3), Vector3( 0,  2,  1)),
        (Point3( 3,  0,  0), Vector3(-1, -1, -5)),
        (Point3( 3, -2,  1), Vector3( 1, -4,  5)),
        (Point3( 3, -4, -2), Vector3( 0,  3, -1)),
    )
    assert r[7] == (
        (Point3( 2, -2,  1), Vector3( 3,  5, -2)),
        (Point3( 1, -4, -4), Vector3(-2, -4, -4)),
        (Point3( 3, -7,  5), Vector3( 0, -5,  4)),
        (Point3( 2,  0,  0), Vector3(-1,  4,  2)),
    )
    assert r[8] == (
        (Point3( 5,  2, -2), Vector3( 3,  4, -3)),
        (Point3( 2, -7, -5), Vector3( 1, -3, -1)),
        (Point3( 0, -9,  6), Vector3(-3, -2,  1)),
        (Point3( 1,  1,  3), Vector3(-1,  1,  3)),
    )
    assert r[9] == (
        (Point3( 5,  3, -4), Vector3( 0,  1, -2)),
        (Point3( 2, -9, -3), Vector3( 0, -2,  2)),
        (Point3( 0, -8,  4), Vector3( 0,  1, -2)),
        (Point3( 1,  1,  5), Vector3( 0,  0,  2)),
    )
    assert r[10] == (
        (Point3( 2,  1, -3), Vector3(-3, -2,  1)),
        (Point3( 1, -8,  0), Vector3(-1,  1,  3)),
        (Point3( 3, -6,  1), Vector3( 3,  2, -3)),
        (Point3( 2,  0,  4), Vector3( 1, -1, -1)),
    )

    assert sum(b.energy for b in bodies) == 179

    print("passed test_1a")


def test_1b():
    bodies = [
        Body(Point3(-8,-10, 0)),
        Body(Point3( 5,  5,10)),
        Body(Point3( 2, -7, 3)),
        Body(Point3( 9, -8,-3)),
    ]

    last_state = last(simulate(bodies, steps_limit=100))

    assert last_state == (
        (Point3(  8, -12, -9), Vector3(-7,   3,  0)),
        (Point3( 13,  16, -3), Vector3( 3, -11, -5)),
        (Point3(-29, -11, -1), Vector3(-3,   7,  4)),
        (Point3( 16, -13, 23), Vector3( 7,   1,  1)),
    )
    assert sum(b.energy for b in bodies) == 1940
    print("passed test_1b")


def test_2a():
    bodies = [
        Body(Point3(-1, 0, 2)),
        Body(Point3(2, -10, -7)),
        Body(Point3(4, -8, 8)),
        Body(Point3(3, 5, -1))
    ]
    assert until_repeat_steps(bodies) == 2772
    print("passed test_2a")


def test_2b():
    bodies = [
        Body(Point3(-8,-10, 0)),
        Body(Point3( 5,  5,10)),
        Body(Point3( 2, -7, 3)),
        Body(Point3( 9, -8,-3)),
    ]
    assert until_repeat_steps(bodies) == 4686774924
    print("passed test_2b")


def test_reverse():
    bodies = [
        Body(Point3(-1, 0, 2)),
        Body(Point3(2, -10, -7)),
        Body(Point3(4, -8, 8)),
        Body(Point3(3, 5, -1))
    ]

    states_f = list(simulate(bodies, steps_limit=2772))
    states_b = list(simulate_reverse(bodies, steps_limit=2772))

    assert len(states_f) == len(states_b) == 2773
    assert states_f[0] == states_b[0]
    assert states_f[0] == states_f[-1]
    assert states_b[0] == states_b[-1]

    assert states_f[1] == states_b[-2]
    assert states_f[2] == states_b[-3]
    assert states_f[1000] == states_b[-1001]

    print("passed test_reverse")


def tests():
    test_1a()
    test_1b()
    test_2a()
    test_2b()
    test_reverse()
    print()


def part_1(steps=1000):
    bodies = [
        Body(Point3(-1, -4, 0)),
        Body(Point3(4, 7, -1)),
        Body(Point3(-14, -10, 9)),
        Body(Point3(1, 2, 17)),
    ]
    last(simulate(bodies, steps_limit=steps))
    total_energy = sum(b.energy for b in bodies)
    print(f"part 1: total energy after {steps} steps is {total_energy}")


def part_2():
    bodies = [
        Body(Point3(-1, -4, 0)),
        Body(Point3(4, 7, -1)),
        Body(Point3(-14, -10, 9)),
        Body(Point3(1, 2, 17)),
    ]
    ss = until_repeat_steps(bodies, debug=True)
    print(f"part 2: simulation will repeat after {ss} steps")


if __name__ == '__main__':
    tests()
    part_1()
    part_2()
