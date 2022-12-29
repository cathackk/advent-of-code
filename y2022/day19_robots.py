"""
Advent of Code 2022
Day 19: Not Enough Minerals
https://adventofcode.com/2022/day/19
"""

import dataclasses
import functools
import math
from dataclasses import dataclass
from functools import cached_property
from typing import Iterable

from tqdm import tqdm

from common.text import line_groups
from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(blueprints: list['Blueprint'], minutes: int = 24) -> int:
    r"""
    Your scans show that the lava did indeed form obsidian!

    The wind has changed direction enough to stop sending lava droplets toward you, so you and the
    elephants exit the cave. As you do, you notice a collection of geodes around the pond. Perhaps
    you could use the obsidian to create some **geode-cracking robots** and break them open?

    To collect the obsidian from the bottom of the pond, you'll need waterproof **obsidian-
    collecting robots**. Fortunately, there is an abundant amount of clay nearby that you can use to
    make them waterproof.

    In order to harvest the clay, you'll need special-purpose **clay-collecting robots**. To make
    any type of robot, you'll need **ore**, which is also plentiful but in the opposite direction
    from the clay.

    Collecting ore requires **ore-collecting robots** with big drills. Fortunately, **you have
    exactly one ore-collecting robot** in your pack that you can use to kickstart the whole
    operation.

    Each robot can collect 1 of its resource type per minute. It also takes one minute for the robot
    factory (also conveniently from your pack) to construct any type of robot, although it consumes
    the necessary resources available when construction begins.

    The robot factory has many **blueprints** (your puzzle input) you can choose from, but once
    you've configured it with a blueprint, you can't change it. You'll need to work out which
    blueprint is best.

    For example:

        >>> bps = blueprints_from_text('''
        ...     Blueprint 1:
        ...       Each ore robot costs 4 ore.
        ...       Each clay robot costs 2 ore.
        ...       Each obsidian robot costs 3 ore and 14 clay.
        ...       Each geode robot costs 2 ore and 7 obsidian.
        ...
        ...     Blueprint 2:
        ...       Each ore robot costs 2 ore.
        ...       Each clay robot costs 3 ore.
        ...       Each obsidian robot costs 3 ore and 8 clay.
        ...       Each geode robot costs 3 ore and 12 obsidian.
        ... ''')

    (Blueprints have been line-wrapped here for legibility. The robot factory's actual assortment of
    blueprints is provided one blueprint per line.)

    The elephants are starting to look hungry, so you shouldn't take too long; you need to figure
    out which blueprint would maximize the number of opened geodes after **24 minutes** by figuring
    out which robots to build and when to build them.

    Using blueprint 1 in the example above, the largest number of geodes you could open in
    24 minutes is **9**.

        >>> bps[0]  # doctest: +NORMALIZE_WHITESPACE
        Blueprint(number=1, ore_robot_ore_cost=4,
                            clay_robot_ore_cost=2,
                            obsid_robot_ore_cost=3, obsid_robot_clay_cost=14,
                            geode_robot_ore_cost=2, geode_robot_obsid_cost=7)

        >>> bps[0].best_by_geodes(minutes=24)
        9

    However, by using blueprint 2 in the example above, you could do even better: the largest number
    of geodes you could open in 24 minutes is **12**.

        >>> bps[1]  # doctest: +NORMALIZE_WHITESPACE
        Blueprint(number=2, ore_robot_ore_cost=2,
                            clay_robot_ore_cost=3,
                            obsid_robot_ore_cost=3, obsid_robot_clay_cost=8,
                            geode_robot_ore_cost=3, geode_robot_obsid_cost=12)

        >>> bps[1].best_by_geodes(minutes=24)
        12

    Determine the **quality level** of each blueprint by **multiplying that blueprint's ID number**
    with the largest number of geodes that can be opened in 24 minutes using that blueprint. In this
    example, the first blueprint has ID 1 and can open 9 geodes, so its quality level is **9**:

        >>> bps[0].quality_level()
        9

    The second blueprint has ID 2 and can open 12 geodes, so its quality level is **24**:

        >>> bps[1].quality_level()
        24

    Finally, if you **add up the quality levels** of all of the blueprints in the list, you get
    **33**:

        >>> sum(bp.quality_level() for bp in bps)
        33

    Determine the quality level of each blueprint using the largest number of geodes it could
    produce in 24 minutes. **What do you get if you add up the quality level of all of the
    blueprints in your list?**

        >>> part_1(bps)
        part 1: in 24 minutes, sum of blueprint quality levels is 33
        33
    """

    result = sum(
        blueprint.quality_level(minutes)
        for blueprint in tqdm(blueprints, delay=1.0, unit=" blueprints", desc="part 1")
    )

    print(f"part 1: in {minutes} minutes, sum of blueprint quality levels is {result}")
    return result


def part_2(blueprints: list['Blueprint'], minutes: int = 32, max_blueprints: int = 3) -> int:
    """
    While you were choosing the best blueprint, the elephants found some food on their own, so
    you're not in as much of a hurry; you figure you probably have **32 minutes** before the wind
    changes direction again and you'll need to get out of range of the erupting volcano.

    Unfortunately, one of the elephants **ate most of your blueprint list**! Now, only the first
    three blueprints in your list are intact.

    In 32 minutes, the largest number of geodes blueprint 1 (from the example above) can open is
    **`56`**. One way to achieve that is:

        >>> bps = blueprints_from_file(data_path(__file__, 'example.txt'))

        >>> bps[0].best_by_geodes(minutes=32)
        56
        >>> bps[1].best_by_geodes(minutes=32)
        62

        >>> part_2(bps)
        part 2: in 32 minutes, product of max geodes of the first 2 blueprints is 3472
        3472
    """

    remaining_blueprints = blueprints[:max_blueprints]
    result = math.prod(
        blueprint.best_by_geodes(minutes)
        for blueprint in tqdm(remaining_blueprints, delay=1.0, unit=" blueprints", desc="part 2")
    )

    print(
        f"part 2: in {minutes} minutes, "
        f"product of max geodes of the first {len(remaining_blueprints)} blueprints is {result}"
    )
    return result


SO_MUCH = 9999


# TODO: rewrite using some nicer structures without repeating **with comparable performance**


@dataclass(frozen=True)
class State:
    minutes_remaining: int = dataclasses.field(hash=False, compare=False)
    robots_ore: int = 1
    robots_clay: int = 0
    robots_obsid: int = 0
    robots_geode: int = 0
    stock_ore: int = 0
    stock_clay: int = 0
    stock_obsid: int = 0
    stock_geode: int = 0

    def __str__(self) -> str:
        def fv(value: int) -> str:
            return str(value) if value < SO_MUCH else "*"

        robots = ":".join(str(v) for v in [self.robots_ore, self.robots_clay, self.robots_obsid, self.robots_geode])
        stocks = ":".join([fv(self.stock_ore), fv(self.stock_clay), fv(self.stock_obsid), str(self.stock_geode)])
        return f"minutes={self.minutes_remaining}, robots={robots}, stock={stocks}"

    def next_ore(self, max_ore: int, spent_ore: int = 0) -> int:
        if self.stock_ore == SO_MUCH:
            return SO_MUCH
        if self.robots_ore >= max_ore:
            return SO_MUCH
        next_stock = self.stock_ore + self.robots_ore - spent_ore
        return next_stock if next_stock <= max_ore * (self.minutes_remaining - 2) else SO_MUCH

    def next_clay(self, max_clay: int, spent_clay: int = 0) -> int:
        if self.stock_clay == SO_MUCH:
            return SO_MUCH
        if self.robots_clay >= max_clay:
            return SO_MUCH
        next_stock = self.stock_clay + self.robots_clay - spent_clay
        return next_stock if next_stock <= max_clay * (self.minutes_remaining - 4) else SO_MUCH

    def next_obsid(self, max_obsid: int, spent_obsid: int = 0) -> int:
        if self.stock_obsid == SO_MUCH:
            return SO_MUCH
        if self.robots_obsid >= max_obsid:
            return SO_MUCH
        next_stock = self.stock_obsid + self.robots_obsid - spent_obsid
        return next_stock if next_stock <= max_obsid * (self.minutes_remaining - 2) else SO_MUCH

    def next_geode(self) -> int:
        return self.stock_geode + self.robots_geode


@dataclass(frozen=True)
class Blueprint:
    number: int
    ore_robot_ore_cost: int
    clay_robot_ore_cost: int
    obsid_robot_ore_cost: int
    obsid_robot_clay_cost: int
    geode_robot_ore_cost: int
    geode_robot_obsid_cost: int

    def __str__(self) -> str:
        return (
            f"Number: {self.number}, "
            f"Ore: {self.ore_robot_ore_cost} O, "
            f"Clay: {self.clay_robot_ore_cost} O, "
            f"Obsid: {self.obsid_robot_ore_cost} O + {self.obsid_robot_clay_cost} C, "
            f"Geode: {self.geode_robot_ore_cost} O + {self.geode_robot_obsid_cost} B"
        )

    @cached_property
    def max_ore_cost(self) -> int:
        return max(
            self.ore_robot_ore_cost,
            self.clay_robot_ore_cost,
            self.obsid_robot_ore_cost,
            self.geode_robot_ore_cost,
        )

    @property
    def max_clay_cost(self) -> int:
        return self.obsid_robot_clay_cost

    @property
    def max_obsid_cost(self) -> int:
        return self.geode_robot_obsid_cost

    @classmethod
    def from_line(cls, line: str) -> 'Blueprint':
        pattern = (
            "Blueprint $: "
            "Each ore robot costs $ ore. "
            "Each clay robot costs $ ore. "
            "Each obsidian robot costs $ ore and $ clay. "
            "Each geode robot costs $ ore and $ obsidian."
        )
        num, ore_ore, clay_ore, obs_ore, obs_clay, geode_ore, geode_obs = parse_line(line, pattern)
        return cls(
            number=int(num),
            ore_robot_ore_cost=int(ore_ore),
            clay_robot_ore_cost=int(clay_ore),
            obsid_robot_ore_cost=int(obs_ore),
            obsid_robot_clay_cost=int(obs_clay),
            geode_robot_ore_cost=int(geode_ore),
            geode_robot_obsid_cost=int(geode_obs),
        )

    def create_nothing(self, state: State) -> State:
        return dataclasses.replace(
            state,
            minutes_remaining=state.minutes_remaining - 1,
            stock_ore=state.next_ore(max_ore=self.max_ore_cost),
            stock_clay=state.next_clay(max_clay=self.max_clay_cost),
            stock_obsid=state.next_obsid(max_obsid=self.max_obsid_cost),
            stock_geode=state.next_geode(),
        )

    def can_create_ore_robot(self, state: State) -> bool:
        return (
            state.stock_ore >= self.ore_robot_ore_cost and
            state.robots_ore < self.max_ore_cost
        )

    def create_ore_robot(self, state: State) -> State:
        return dataclasses.replace(
            state,
            minutes_remaining=state.minutes_remaining - 1,
            robots_ore=state.robots_ore + 1,
            stock_ore=state.next_ore(max_ore=self.max_ore_cost, spent_ore=self.ore_robot_ore_cost),
            stock_clay=state.next_clay(max_clay=self.max_clay_cost),
            stock_obsid=state.next_obsid(max_obsid=self.max_obsid_cost),
            stock_geode=state.next_geode(),
        )

    def can_create_clay_robot(self, state: State) -> bool:
        return (
            state.stock_ore >= self.clay_robot_ore_cost and
            state.robots_clay < self.max_clay_cost
        )

    def create_clay_robot(self, state: State) -> State:
        return dataclasses.replace(
            state,
            minutes_remaining=state.minutes_remaining - 1,
            robots_clay=state.robots_clay + 1,
            stock_ore=state.next_ore(max_ore=self.max_ore_cost, spent_ore=self.clay_robot_ore_cost),
            stock_clay=state.next_clay(max_clay=self.max_clay_cost),
            stock_obsid=state.next_obsid(max_obsid=self.max_obsid_cost),
            stock_geode=state.next_geode(),
        )

    def can_create_obsid_robot(self, state: State) -> bool:
        return (
            state.stock_ore >= self.obsid_robot_ore_cost and
            state.stock_clay >= self.obsid_robot_clay_cost and
            state.robots_obsid < self.max_obsid_cost
        )

    def create_obsid_robot(self, state: State) -> State:
        return dataclasses.replace(
            state,
            minutes_remaining=state.minutes_remaining - 1,
            robots_obsid=state.robots_obsid + 1,
            stock_ore=state.next_ore(max_ore=self.max_ore_cost, spent_ore=self.obsid_robot_ore_cost),
            stock_clay=state.next_clay(max_clay=self.max_clay_cost, spent_clay=self.obsid_robot_clay_cost),
            stock_obsid=state.next_obsid(max_obsid=self.max_obsid_cost),
            stock_geode=state.next_geode(),
        )

    def can_create_geode_robot(self, state: State) -> bool:
        return (
            state.stock_ore >= self.geode_robot_ore_cost and
            state.stock_obsid >= self.geode_robot_obsid_cost
        )

    def create_geode_robot(self, state: State) -> State:
        return dataclasses.replace(
            state,
            minutes_remaining=state.minutes_remaining - 1,
            robots_geode=state.robots_geode + 1,
            stock_ore=state.next_ore(max_ore=self.max_ore_cost, spent_ore=self.geode_robot_ore_cost),
            stock_clay=state.next_clay(max_clay=self.max_clay_cost),
            stock_obsid=state.next_obsid(max_obsid=self.max_obsid_cost, spent_obsid=self.geode_robot_obsid_cost),
            stock_geode=state.next_geode(),
        )

    def next_states(self, state: State) -> Iterable[State]:
        assert state.minutes_remaining > 0

        # always produce geode robot if possible
        if self.can_create_geode_robot(state):
            yield self.create_geode_robot(state)
            return

        # produce ore robot
        if (can_ore := self.can_create_ore_robot(state)):
            yield self.create_ore_robot(state)

        # produce clay robot
        if (can_clay := self.can_create_clay_robot(state)):
            yield self.create_clay_robot(state)

        # produce obsidian robot
        if (can_obsid := self.can_create_obsid_robot(state)):
            yield self.create_obsid_robot(state)

        # wait if there is at least one type of robot (apart from geode) that can't be created
        if not (can_ore and can_clay and can_obsid):
            yield self.create_nothing(state)

    @functools.lru_cache()
    def best_by_geodes(self, minutes: int) -> int:
        layer = {State(minutes_remaining=minutes)}
        visited: set[State] = set()

        for minute in range(minutes):
            next_layer = set()

            for old_state in layer:
                for new_state in self.next_states(old_state):
                    if new_state not in visited:
                        next_layer.add(new_state)
                        visited.add(new_state)

            layer = next_layer

        return max(s.stock_geode for s in layer)

    def quality_level(self, minutes: int = 24) -> int:
        return self.number * self.best_by_geodes(minutes)


def blueprints_from_file(fn: str) -> list[Blueprint]:
    return list(blueprints_from_lines(open(fn)))


def blueprints_from_text(text: str) -> list[Blueprint]:
    lines = (' '.join(group) for group in line_groups(text.strip().splitlines()))
    return list(blueprints_from_lines(lines))


def blueprints_from_lines(lines: Iterable[str]) -> Iterable[Blueprint]:
    return (Blueprint.from_line(line.strip()) for line in lines)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    blueprints = blueprints_from_file(input_path)
    result_1 = part_1(blueprints)
    result_2 = part_2(blueprints)
    return result_1, result_2


if __name__ == '__main__':
    main()
