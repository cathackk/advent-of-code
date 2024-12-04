"""
Advent of Code 2023
Day 19: Aplenty
https://adventofcode.com/2023/day/19
"""

from dataclasses import dataclass
from math import prod
from typing import Iterable, Iterator, Self

from common.file import relative_path
from common.text import line_groups, parse_line


def part_1(factory: 'Factory', parts: list['Part']) -> int:
    """
    The Elves of Gear Island are thankful for your help and send you on your way. They even have
    a hang glider that someone stole from Desert Island; since you're already going that direction,
    it would help them a lot if you would use it to get down there and return it to them.

    As you reach the bottom of the **relentless avalanche of machine parts**, you discover that
    they're already forming a formidable heap. Don't worry, though - a group of Elves is already
    here organizing the parts, and they have a **system**.

    To start, each part is rated in each of four categories:

      - `x`: E**x**tremely cool looking
      - `m`: **M**usical (it makes a noise when you hit it)
      - `a`: **A**erodynamic
      - `s`: **S**hiny

    Then, each part is sent through a series of **workflows** that will ultimately **accept** or
    **reject** the part. Each workflow has a name and contains a list of **rules**; each rule
    specifies a condition and where to send the part if the condition is true. The first rule that
    matches the part being considered is applied immediately, and the part moves on to the
    destination described by the rule. (The last rule in each workflow has no condition and always
    applies if reached.)

    Consider the following workflow:

        >>> example_wf = Workflow.from_line('ex{x>10:one,m<20:two,a>30:R,A}')
        >>> example_wf.name
        'ex'
        >>> len(example_wf.rules)
        4

    If workflow `ex` was considering a specific part, it would perform the following steps in order:

      - If the part's `x` is more than `10`, send the part to the workflow named `one`:

        >>> example_wf.rules[0]
        Rule(condition=Condition('x', '>', 10), target='one')
        >>> str(_)
        'x>10:one'


      - Otherwise, if the part's `m` is less than `20`, send the part to the workflow named `two`:

        >>> example_wf.rules[1]
        Rule(condition=Condition('m', '<', 20), target='two')
        >>> str(_)
        'm<20:two'

      - Otherwise, if the part's `a` is more than `30`, the part is immediately **rejected** (`R`):

        >>> example_wf.rules[2]
        Rule(condition=Condition('a', '>', 30), target='R')
        >>> str(_)
        'a>30:R'

      - Otherwise, because no other rules matched, the part is immediately **accepted** (`A`):

        >>> example_wf.rules[3]
        Rule(condition=Condition.always(), target='A')
        >>> str(_)
        'A'

    If a part is sent to another workflow, it immediately switches to the start of that workflow
    instead and never returns. If a part is **accepted** (sent to `A`) or **rejected** (sent to `R`)
    the part immediately stops any further processing.

    The system works, but it's not keeping up with the torrent of weird metal shapes. The Elves ask
    if you can help sort a few parts and give you the list of workflows and some part ratings
    (your puzzle input). For example:

        >>> example_factory, example_parts = input_from_text('''
        ...     px{a<2006:qkq,m>2090:A,rfg}
        ...     pv{a>1716:R,A}
        ...     lnx{m>1548:A,A}
        ...     rfg{s<537:gd,x>2440:R,A}
        ...     qs{s>3448:A,lnx}
        ...     qkq{x<1416:A,crn}
        ...     crn{x>2662:A,R}
        ...     in{s<1351:px,qqz}
        ...     qqz{s>2770:qs,m<1801:hdj,R}
        ...     gd{a>3333:R,R}
        ...     hdj{m>838:A,pv}
        ...
        ...     {x=787,m=2655,a=1222,s=2876}
        ...     {x=1679,m=44,a=2067,s=496}
        ...     {x=2036,m=264,a=79,s=2244}
        ...     {x=2461,m=1339,a=466,s=291}
        ...     {x=2127,m=1623,a=2188,s=1013}
        ... ''')
        >>> len(example_factory.workflows)
        11
        >>> len(example_parts)
        5

    The workflows are listed first, followed by a blank line, then the ratings of the parts the
    Elves would like you to sort. All parts begin in the workflow named `in`. In this example,
    the five listed parts go through the following workflows:

        >>> accepted_parts = list(example_factory.run_demo(example_parts))
        {x=787,m=2655,a=1222,s=2876}: in -> qqz -> qs -> lnx -> A
        {x=1679,m=44,a=2067,s=496}: in -> px -> rfg -> gd -> R
        {x=2036,m=264,a=79,s=2244}: in -> qqz -> hdj -> pv -> A
        {x=2461,m=1339,a=466,s=291}: in -> px -> qkq -> crn -> R
        {x=2127,m=1623,a=2188,s=1013}: in -> px -> rfg -> A

    Ultimately, three parts are **accepted**:

        >>> accepted_parts  # doctest: +NORMALIZE_WHITESPACE
        [Part({'x': 787, 'm': 2655, 'a': 1222, 's': 2876}),
         Part({'x': 2036, 'm': 264, 'a': 79, 's': 2244}),
         Part({'x': 2127, 'm': 1623, 'a': 2188, 's': 1013})]

    Adding up the `x`, `m`, `a`, and `s` rating for each of the accepted parts gives:

        >>> [sum(part) for part in accepted_parts]
        [7540, 4623, 6951]

    Adding all of the ratings for **all** of the accepted parts gives the sum total of:

        >>> sum(_)
        19114

    Sort through all of the parts you've been given; **what do you get if you add together all of
    the rating numbers for all of the parts that ultimately get accepted?**

        >>> part_1(example_factory, example_parts)
        part 1: accepted parts sum up to 19114
        19114
    """

    result = sum(sum(part) for part in parts if factory.accepts_part(part))

    print(f"part 1: accepted parts sum up to {result}")
    return result


def part_2(factory: 'Factory') -> int:
    """
    Even with your help, the sorting process **still** isn't fast enough.

    One of the Elves comes up with a new plan: rather than sort parts individually through all of
    these workflows, maybe you can figure out in advance which combinations of ratings will be
    accepted or rejected.

    Each of the four ratings (`x`, `m`, `a`, `s`) can have an integer value ranging from a minimum
    of `1` to a maximum of `4000`. Of **all possible distinct combinations** of ratings, your job is
    to figure out which ones will be **accepted**.

    In the above example, there are **`167409079868000`** distinct combinations of ratings that will
    be accepted:

        >>> factory, _ = input_from_file('data/19-example.txt')
        >>> factory.accepted_combinations_count(min_rating=1, max_rating=4000)
        167409079868000

    Consider only your list of workflows; the list of part ratings that the Elves wanted you to sort
    is no longer relevant. **How many distinct combinations of ratings will be accepted by the
    Elves' workflows?**

        >>> part_2(factory)
        part 2: total 167409079868000 combinations will be accepted
        167409079868000
    """

    result = factory.accepted_combinations_count()

    print(f"part 2: total {result} combinations will be accepted")
    return result


@dataclass(frozen=True)
class Part:
    ratings: dict[str, int]

    def get(self, variable: str) -> int:
        return self.ratings[variable]

    @classmethod
    def from_line(cls, line: str) -> Self:
        # '{x=787,m=2655,a=1222,s=2876}'
        values = parse_line(line, '{x=$,m=$,a=$,s=$}')
        return cls({k: int(v) for k, v in zip('xmas', values, strict=True)})

    def __str__(self) -> str:
        return '{' + ','.join(f'{k}={v}' for k, v in self.ratings.items()) + '}'

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.ratings!r})'

    def __iter__(self) -> Iterator[int]:
        return iter(self.ratings.values())


class PartRange:
    def __init__(self, ranges: dict[str, range]):
        self.ranges = ranges if all(ranges) else {}

    def get(self, variable: str) -> range:
        return self.ranges[variable]

    def split(self, variable: str, value: int) -> tuple[Self, Self]:
        range_og = self.get(variable)
        if value not in range_og:
            raise ValueError(f"{variable}={value} not in {range_og.start}..{range_og.stop}")

        return (
            type(self)(self.ranges | {variable: range(range_og.start, value)}),
            type(self)(self.ranges | {variable: range(value, range_og.stop)}),
        )

    @classmethod
    def full(cls, variables: Iterable[str], rating_range: range) -> Self:
        return cls({var: rating_range for var in variables})

    @classmethod
    def empty(cls) -> Self:
        return cls({})

    def __str__(self) -> str:
        if not self:
            return '{}'
        return '{' + ','.join(f'{k}={r.start}..{r.stop}' for k, r in self.ranges.items()) + '}'

    def __repr__(self) -> str:
        if not self:
            return f'{type(self).__name__}.empty()'
        return f'{type(self).__name__}({self.ranges!r})'

    def __iter__(self) -> Iterator[range]:
        return iter(self.ranges.values())

    def __len__(self) -> int:
        if not self:
            return 0
        return prod(len(r) for r in self)

    def __bool__(self) -> bool:
        return bool(self.ranges)


@dataclass(frozen=True)
class Condition:
    variable: str
    op: str
    value: int

    def matches(self, part: Part) -> bool:
        if self.is_always_true():
            return True

        part_value = part.get(self.variable)
        match self.op:
            case '<':
                return part_value < self.value
            case '>':
                return part_value > self.value
            case unsupported:
                raise ValueError(unsupported)

    def split(self, part_range: PartRange) -> tuple[PartRange, PartRange]:
        if self.is_always_true():
            return part_range, PartRange.empty()

        match self.op:
            case '<':
                # 1..40 & x<20 -> 1..20, 20..40
                return part_range.split(self.variable, self.value)
            case '>':
                # 1..40 & x>20 -> 21..40, 1..21
                low, high = part_range.split(self.variable, self.value + 1)
                return high, low
            case unsupported:
                raise ValueError(unsupported)

    @classmethod
    def always(cls) -> Self:
        return cls('', '', 0)

    def is_always_true(self) -> bool:
        return not self.op

    def __str__(self) -> str:
        if self.is_always_true():
            return ''
        return f'{self.variable}{self.op}{self.value}'

    def __repr__(self) -> str:
        if self.is_always_true():
            return f'{type(self).__name__}.always()'
        return f'{type(self).__name__}({self.variable!r}, {self.op!r}, {self.value!r})'

    @classmethod
    def from_str(cls, string: str) -> Self:
        if '>' in string:
            variable, value = string.split('>')
            return cls(variable, '>', int(value))
        elif '<' in string:
            variable, value = string.split('<')
            return cls(variable, '<', int(value))
        else:
            raise ValueError(string)


@dataclass(frozen=True)
class Rule:
    condition: Condition
    target: str

    def __str__(self) -> str:
        if self.condition.is_always_true():
            return self.target
        return f'{self.condition}:{self.target}'

    @classmethod
    def from_str(cls, string: str) -> Self:
        if ':' not in string:
            return cls(condition=Condition.always(), target=string)

        # 'a>1716:R'
        condition_str, target = string.split(':')
        return cls(condition=Condition.from_str(condition_str), target=target)


@dataclass(frozen=True)
class Workflow:
    name: str
    rules: list[Rule]

    def __str__(self) -> str:
        rules_str = ','.join(str(rule) for rule in self.rules)
        return f'{self.name}{{{rules_str}}}'

    @classmethod
    def from_line(cls, line: str) -> Self:
        # 'pv{a>1716:R,A}'
        name, rules_part = parse_line(line.strip(), '${$}')
        return cls(name, [Rule.from_str(rule_str) for rule_str in rules_part.split(',')])

    def evaluate(self, part: Part) -> str:
        try:
            return next(
                rule.target
                for rule in self.rules
                if rule.condition.matches(part)
            )
        except StopIteration:
            raise ValueError('no rule matches') from None

    def evaluate_range(self, part_range: PartRange) -> Iterable[tuple[PartRange, str]]:
        for rule in self.rules:
            when_true, when_false = rule.condition.split(part_range)
            if when_true:
                yield when_true, rule.target
            part_range = when_false


class Factory:
    def __init__(self, workflows: Iterable[Workflow]):
        self.workflows: dict[str, Workflow] = {wf.name: wf for wf in workflows}

    def run_demo(self, parts: Iterable[Part]) -> Iterable[Part]:
        for part in parts:
            print(f'{part}:', ' -> '.join(self.workflows_chain(part)))
            if self.accepts_part(part):
                yield part

    def workflows_chain(self, part: Part, workflow_name: str = 'in') -> Iterable[str]:
        yield workflow_name
        if workflow_name in ('A', 'R'):
            return
        yield from self.workflows_chain(part, self.workflows[workflow_name].evaluate(part))

    def accepts_part(self, part: Part, workflow_name: str = 'in') -> bool:
        if workflow_name == 'A':
            return True
        elif workflow_name == 'R':
            return False

        return self.accepts_part(part, self.workflows[workflow_name].evaluate(part))

    def accepted_ranges(
        self, part_range: PartRange, workflow_name: str = 'in'
    ) -> Iterable[PartRange]:
        if workflow_name == 'A':
            return [part_range]
        if workflow_name == 'R':
            return []

        return (
            result_range
            for subrange, name in self.workflows[workflow_name].evaluate_range(part_range)
            for result_range in self.accepted_ranges(subrange, name)
        )

    def accepted_combinations_count(self, min_rating: int = 1, max_rating: int = 4000) -> int:
        return sum(
            len(subrange)
            for subrange in self.accepted_ranges(
                PartRange.full('xmas', range(min_rating, max_rating + 1))
            )
        )


def input_from_file(fn: str) -> tuple[Factory, list[Part]]:
    return input_from_lines(open(relative_path(__file__, fn)))


def input_from_text(text: str) -> tuple[Factory, list[Part]]:
    return input_from_lines(text.strip().splitlines())


def input_from_lines(lines: Iterable[str]) -> tuple[Factory, list[Part]]:
    workflows_group, parts_group = line_groups(lines)
    factory = Factory(Workflow.from_line(line.strip()) for line in workflows_group)
    parts = [Part.from_line(line) for line in parts_group]
    return factory, parts


def main(input_fn: str = 'data/19-input.txt') -> tuple[int, int]:
    factory, parts = input_from_file(input_fn)
    result_1 = part_1(factory, parts)
    result_2 = part_2(factory)
    return result_1, result_2


if __name__ == '__main__':
    main()
