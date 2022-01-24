from collections import Counter
from itertools import count
from typing import Iterable

from common.iteration import min_all
from common.logging import create_logger
from common.xyz import Point3
from common.xyz import Vector3


class Particle:
    def __init__(self, num: int, pos: Point3, vel: Vector3, acc: Vector3):
        self.num = num
        self.pos = pos
        self.vel = vel
        self.acc = acc

    def __repr__(self):
        return (
            f'{type(self).__name__}('
            f'{self.num!r}, '
            f'pos={self.pos!r}, '
            f'vel={self.vel!r}, '
            f'acc={self.acc!r})'
        )

    def __str__(self):
        return f"n={self.num}, p={self.pos}, v={self.vel}, a={self.acc}"

    def __hash__(self):
        return hash(self.num)

    def step(self) -> 'Particle':
        self.vel += self.acc
        self.pos += self.vel
        return self


def load_particles(fn: str) -> Iterable[Particle]:
    with open(fn) as file:
        for num, line in enumerate(file):
            # 'p=<-201,-1266,-2683>, v=<-29,-181,-382>, a=<2,13,31>'
            pos_part, vel_part, acc_part = line.strip().split(', ')

            pos = Point3(*(int(v) for v in pos_part[3:-1].split(',')))
            vel = Vector3(*(int(v) for v in vel_part[3:-1].split(',')))
            acc = Vector3(*(int(v) for v in acc_part[3:-1].split(',')))

            yield Particle(num, pos, vel, acc)


def manhattan(pos: Point3) -> int:
    return sum(abs(d) for d in pos)


def pos_closest_to_origin(particle: Particle) -> tuple[Point3, int]:
    pos = particle.pos
    vel = particle.vel
    min_pos = pos
    min_pos_step = 0

    for step in count(1):
        vel += particle.acc
        pos += vel
        if manhattan(pos) < manhattan(min_pos):
            min_pos = pos
            min_pos_step = step
        else:
            return min_pos, min_pos_step

    # unreachable
    assert False


def simulate(
        particles: Iterable[Particle],
        idle_steps_limit: int = 10,
        debug: bool = False
) -> int:
    log = create_logger(debug)

    particles = list(particles)
    idle_steps = None

    log(f"step 0 [{len(particles)}]")

    for step in count(1):
        positions = Counter(p.step().pos for p in particles)
        collision_positions = {pos for pos, q in positions.items() if q > 1}
        if collision_positions:
            prev_count = len(particles)
            particles = [p for p in particles if p.pos not in collision_positions]
            collided_count = prev_count - len(particles)
            log(
                f"step {step} [{len(particles)}]: "
                f"collided {collided_count} particles at {len(collision_positions)} positions"
            )
            idle_steps = 0
        else:
            log(f"step {step} [{len(particles)}]")
            if idle_steps is not None:
                idle_steps += 1
                if idle_steps >= idle_steps_limit:
                    return len(particles)

    # unreachable
    assert False


def part_1(fn: str) -> int:
    min_ps = min_all(load_particles(fn), key=lambda p: sum(abs(a) for a in p.acc))
    assert len(min_ps) == 1
    pno = min_ps[0].num
    print(f"part 1: particle closest to origin in the long run is {pno}")
    return pno


def part_2(fn: str):
    result = simulate(load_particles(fn), idle_steps_limit=10)
    print(f"part 2: {result} particles left after all collisions")
    return result


if __name__ == '__main__':
    FILENAME = 'data/20-input.txt'
    part_1(FILENAME)
    part_2(FILENAME)
