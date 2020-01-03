from typing import Dict
from typing import Iterable
from typing import Tuple

Data = Dict[str, int]
Aunt = Tuple[int, Data]
Knowns = Dict[str, Tuple[str, int]]

def load_aunts(fn: str) -> Iterable[Aunt]:
    for line in open(fn):
        """
        Sue 8: cars: 10, pomeranians: 7, goldfish: 8
        """
        name_part, data_part = line.strip().split(': ', 1)
        sue, number = name_part.split(' ')
        assert sue == "Sue"
        number = int(number)
        yield (
            int(number),
            {key: int(value) for key, value in (d.split(': ') for d in data_part.split(', '))}
        )


def matches(aunt_data: Data, knowns: Knowns) -> bool:
    for key, value in aunt_data.items():
        op, known_value = knowns[key]
        if op == '=':
            if value != known_value:
                return False
        elif op == '<':
            if value >= known_value:
                return False
        elif op == '>':
            if value <= known_value:
                return False
        else:
            raise ValueError(op)
    else:
        return True


if __name__ == '__main__':
    knowns = {
        'children': ('=', 3),
        'cats': ('>', 7),
        'samoyeds': ('=', 2),
        'pomeranians': ('<', 3),
        'akitas': ('=', 0),
        'vizslas': ('=', 0),
        'goldfish': ('<', 5),
        'trees': ('>', 3),
        'cars': ('=', 2),
        'perfumes': ('=', 1)
    }
    for num, data in load_aunts("data/16-input.txt"):
        if matches(data, knowns):
            print(num, data)
