"""
Advent of Code 2017
Day 20: Particle Swarm
https://adventofcode.com/2017/day/20
"""

from collections import Counter
from typing import Iterable, Iterator, Self

from common.text import parse_line
from common.xyz import Point3, Vector3
from meta.aoc_tools import data_path


def part_1(particles: Iterable['Particle']) -> int:
    """
    Suddenly, the GPU contacts you, asking for help. Someone has asked it to simulate **too many
    particles**, and it won't be able to finish them all in time to render the next frame at this
    rate.

    It transmits to you a buffer (your puzzle input) listing each particle in order (starting with
    particle `0`, then particle `1`, particle `2`, and so on). For each particle, it provides the
    `X`, `Y`, and `Z` coordinates for the particle's position (`p`), velocity (`v`), and
    acceleration (`a`), each in the format `<X,Y,Z>`.

    Each tick, all particles are updated simultaneously. A particle's properties are updated in the
    following order:

      - Increase the `X` velocity by the `X` acceleration.
      - Increase the `Y` velocity by the `Y` acceleration.
      - Increase the `Z` velocity by the `Z` acceleration.
      - Increase the `X` position by the `X` velocity.
      - Increase the `Y` position by the `Y` velocity.
      - Increase the `Z` position by the `Z` velocity.

    Because of seemingly tenuous rationale involving z-buffering, the GPU would like to know which
    particle will stay closest to position `<0,0,0>` in the long term. Measure this using the
    Manhattan distance, which in this situation is simply the sum of the absolute values of
    a particle's `X`, `Y`, and `Z` position.

    For example, suppose you are only given two particles, both of which stay entirely on the X-axis
    (for simplicity).

        >>> example_particles = particles_from_text('''
        ...     p=<3,0,0>, v=<2,0,0>, a=<-1,0,0>
        ...     p=<4,0,0>, v=<0,0,0>, a=<-2,0,0>
        ... ''')
        >>> example_particles  # doctest: +NORMALIZE_WHITESPACE
        [Particle(pos=Point3(3, 0, 0), vel=Vector3(2, 0, 0), acc=Vector3(-1, 0, 0)),
         Particle(pos=Point3(4, 0, 0), vel=Vector3(0, 0, 0), acc=Vector3(-2, 0, 0))]

    Printing the current states of particles `0` and `1`, the following would take place:

        >>> simulation = simulate(example_particles)
        >>> print(next(simulation))
        (0) p=<3, 0, 0>, v=<2, 0, 0>, a=<-1, 0, 0>
        (1) p=<4, 0, 0>, v=<0, 0, 0>, a=<-2, 0, 0>
        >>> print(next(simulation))
        (0) p=<4, 0, 0>, v=<1, 0, 0>, a=<-1, 0, 0>
        (1) p=<2, 0, 0>, v=<-2, 0, 0>, a=<-2, 0, 0>
        >>> print(next(simulation))
        (0) p=<4, 0, 0>, v=<0, 0, 0>, a=<-1, 0, 0>
        (1) p=<-2, 0, 0>, v=<-4, 0, 0>, a=<-2, 0, 0>
        >>> print(next(simulation))
        (0) p=<3, 0, 0>, v=<-1, 0, 0>, a=<-1, 0, 0>
        (1) p=<-8, 0, 0>, v=<-6, 0, 0>, a=<-2, 0, 0>

    At this point, particle `1` will never be closer to `<0,0,0>` than particle `0`, and so, in the
    long run, particle `0` will stay closest.

    **Which particle will stay closest to position `<0,0,0>`** in the long term?

        >>> part_1(example_particles)
        part 1: closest to origin in the long run is particle number 0
        0
    """

    # simplification: particles closest to the origin is the one with the min acceleration
    particles_dict = dict(enumerate(particles))
    closest_particle_num = min(particles_dict, key=lambda num: abs(particles_dict[num].acc))
    print(f"part 1: closest to origin in the long run is particle number {closest_particle_num}")
    return closest_particle_num


def part_2(particles: Iterable['Particle']):
    """
    To simplify the problem further, the GPU would like to remove any particles that **collide**.
    Particles collide if their positions ever **exactly match**. Because particles are updated
    simultaneously, **more than two particles** can collide at the same time and place. Once
    particles collide, they are removed and cannot collide with anything else after that tick.

    For example:

        >>> example_particles = particles_from_text('''
        ...     p=<-6,0,0>, v=< 3,0,0>, a=< 0,0,0>
        ...     p=<-4,0,0>, v=< 2,0,0>, a=< 0,0,0>
        ...     p=<-2,0,0>, v=< 1,0,0>, a=< 0,0,0>
        ...     p=< 3,0,0>, v=<-1,0,0>, a=< 0,0,0>
        ... ''')
        >>> simulation = simulate(example_particles)
        >>> print(next(simulation))
        (0) p=<-6, 0, 0>, v=<3, 0, 0>, a=<0, 0, 0>
        (1) p=<-4, 0, 0>, v=<2, 0, 0>, a=<0, 0, 0>
        (2) p=<-2, 0, 0>, v=<1, 0, 0>, a=<0, 0, 0>
        (3) p=<3, 0, 0>, v=<-1, 0, 0>, a=<0, 0, 0>
        >>> print(next(simulation))
        (0) p=<-3, 0, 0>, v=<3, 0, 0>, a=<0, 0, 0>
        (1) p=<-2, 0, 0>, v=<2, 0, 0>, a=<0, 0, 0>
        (2) p=<-1, 0, 0>, v=<1, 0, 0>, a=<0, 0, 0>
        (3) p=<2, 0, 0>, v=<-1, 0, 0>, a=<0, 0, 0>
        >>> print(next(simulation))
        (0) p=<0, 0, 0>, v=<3, 0, 0>, a=<0, 0, 0>
        (1) p=<0, 0, 0>, v=<2, 0, 0>, a=<0, 0, 0>
        (2) p=<0, 0, 0>, v=<1, 0, 0>, a=<0, 0, 0>
        (3) p=<1, 0, 0>, v=<-1, 0, 0>, a=<0, 0, 0>
        >>> print(next(simulation))
        (0) ---destroyed by collision---
        (1) ---destroyed by collision---
        (2) ---destroyed by collision---
        (3) p=<0, 0, 0>, v=<-1, 0, 0>, a=<0, 0, 0>

    In this example, particles `0`, `1`, and `2` are simultaneously destroyed. On the next tick,
    particle `3` passes through unharmed.

    **How many particles are left** after all collisions are resolved?

        >>> part_2(example_particles)
        part 2: 1 particles left after all collisions
        1
    """
    result = len(after_collisions(simulate(particles)).particles)
    print(f"part 2: {result} particles left after all collisions")
    return result


class Particle:
    def __init__(self, pos: Point3, vel: Vector3, acc: Vector3):
        self.pos = pos
        self.vel = vel
        self.acc = acc

    def __repr__(self) -> str:
        tn = type(self).__name__
        return f'{tn}(pos={self.pos!r}, vel={self.vel!r}, acc={self.acc!r})'

    def step(self) -> Self:
        new_vel = self.vel + self.acc
        new_pos = self.pos + new_vel
        return type(self)(pos=new_pos, vel=new_vel, acc=self.acc)

    def __str__(self) -> str:
        return f"p={self.pos:<>}, v={self.vel:<>}, a={self.acc:<>}"

    @classmethod
    def from_str(cls, line: str) -> Self:
        # 'p=<-201,-1266,-2683>, v=<-29,-181,-382>, a=<2,13,31>'
        vals = [int(val) for val in parse_line(line.strip(), "p=<$,$,$>, v=<$,$,$>, a=<$,$,$>")]
        assert len(vals) == 9
        return cls(pos=Point3(*vals[:3]), vel=Vector3(*vals[3:6]), acc=Vector3(*vals[6:]))


class RunState:
    def __init__(self, particles: Iterable[tuple[int, Particle | None]]):
        # both surviving and destroyed
        self._all_particles = dict(particles)
        # only surviving
        self.particles = {num: p for num, p in self._all_particles.items() if p is not None}

    def has_collision(self) -> bool:
        return len(self._all_particles) > len(self.particles)

    def __str__(self) -> str:
        destroyed_text = "---destroyed by collision---"
        return "\n".join(
            f"({num}) {particle or destroyed_text}"
            for num, particle in self._all_particles.items()
        )

    def next_state(self) -> Self:
        # count have many particles are at each position
        position_counter = Counter(p.pos for p in self.particles.values())
        # positions with more than one particle -> those will be destroyed
        collision_positions = {pos for pos, pcount in position_counter.items() if pcount > 1}

        return type(self)(
            (num, particle.step() if particle.pos not in collision_positions else None)
            for num, particle in self.particles.items()
        )


def simulate(particles: Iterable[Particle]) -> Iterator[RunState]:
    state = RunState(enumerate(particles))
    while True:
        yield state
        state = state.next_state()


def after_collisions(simulation: Iterator[RunState], wait_steps: int = 10) -> RunState:
    steps_since_last_collision: int | None = None

    for state in simulation:
        if state.has_collision():
            steps_since_last_collision = 0
        elif steps_since_last_collision is not None:
            steps_since_last_collision += 1
            if steps_since_last_collision >= wait_steps:
                return state

    raise ValueError("simulation ended prematurely")


def particles_from_text(text: str) -> list[Particle]:
    return list(particles_from_lines(text.strip().splitlines()))


def particles_from_file(fn: str) -> list[Particle]:
    return list(particles_from_lines(open(fn)))


def particles_from_lines(lines: Iterable[str]) -> Iterable[Particle]:
    return (Particle.from_str(line) for line in lines)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    particles = particles_from_file(input_path)
    result_1 = part_1(particles)
    result_2 = part_2(particles)
    return result_1, result_2


if __name__ == '__main__':
    main()
