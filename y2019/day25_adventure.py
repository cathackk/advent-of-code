from typing import Generator
from typing import Iterable

from y2019.intcode import load_tape
from y2019.intcode import Machine


def subsequences(items: Iterable[str]) -> Iterable[list[str]]:
    """
        >>> list(subsequences(['A', 'B', 'C']))
        [['A', 'B', 'C'], ['B', 'C'], ['A', 'C'], ['C'], ['A', 'B'], ['B'], ['A'], []]
    """
    items = list(items)

    if items:
        cls = type(items)
        for subseq in subsequences(items[1:]):
            yield items[:1] + subseq
            yield subseq
    else:
        yield items


def generate_commands(items: list[str]) -> Generator[list[str], int, set[str]]:
    combs_left: list[set[str]] = sorted((set(ss) for ss in subsequences(items)), key=len)
    current_items = set(items)

    while combs_left:
        print(f"combs_left: {combs_left}")
        target_items = combs_left[len(combs_left)//2]
        print(f"target items: {target_items}, current_items: {current_items}")

        drop_commands = [f'drop {item}' for item in current_items - target_items]
        take_commands = [f'take {item}' for item in target_items - current_items]
        go_commands = ['inv', 'east']

        comp = yield drop_commands + take_commands + go_commands

        current_items = target_items

        if comp > 0:
            # items were larger than searched combination -> remove all supersets
            combs_left = [comb for comb in combs_left if not comb.issuperset(current_items)]
            print(f"{comp} > 0 -> trimming to {len(combs_left)}")
        elif comp < 0:
            # items were smaller than searched combination -> remove all subsets
            combs_left = [comb for comb in combs_left if not comb.issubset(current_items)]
            print(f"{comp} < 0 -> trimming to {len(combs_left)}")
        else:
            # found!
            return current_items


def solve(fn: str):
    io = Machine(load_tape(fn)).run_io()
    commands = [
        'west', 'take mug', 'north', 'take easter egg', 'south', 'east', 'south', 'east', 'north',
        'take candy cane', 'south', 'west', 'north', 'east', 'take coin', 'north', 'north',
        'take hypercube', 'south', 'east', 'take manifold', 'west', 'south', 'south', 'east',
        'take pointer', 'west', 'west', 'take astrolabe', 'north', 'east', 'north'
    ]
    items = [command[5:] for command in commands if command.startswith('take ')]

    while commands:
        print(io.read_str(), end='')
        command = commands[0]
        del commands[0]
        print(f">>> {command}")
        io.write(command+'\n')

    print(io.read_str(), end='')

    co = generate_commands(items)
    commands = next(co)
    try:
        while True:
            last_output = None
            for command in commands:
                print(f">>> {command}")
                io.write(command+'\n')
                last_output = io.read_str()
                print(last_output, end='')
            # ...
            commands = co.send(int(input()))
    finally:
        pass


def solution(fn: str):
    io = Machine(load_tape(fn)).run_io()

    commands = [
        'west', 'take mug',
        'east', 'east', 'take coin',
        'north', 'north', 'take hypercube',
        'south', 'south', 'south', 'west', 'take astrolabe',
        'north', 'east', 'north', 'east'
    ]

    for command in commands:
        print(io.read_str(), end='')
        print(f">>> {command}")
        io.write(command+"\n")
    print(io.read_str(), end='')


if __name__ == '__main__':
    solution("data/25-program.txt")
