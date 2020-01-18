from typing import Iterable
from typing import Iterator
from typing import List


def load_data(fn: str) -> Iterable[int]:
    return (
        int(v)
        for line in open(fn)
        for v in line.strip().split(' ')
    )


def read_metadata(data: Iterator[int]) -> Iterable[int]:
    nodes_count = next(data)
    metadata_count = next(data)
    for _ in range(nodes_count):
        yield from read_metadata(data)
    for _ in range(metadata_count):
        yield next(data)


def read_value(data: Iterator[int]) -> int:
    nodes_count = next(data)
    metadata_count = next(data)
    child_values = [read_value(data) for _ in range(nodes_count)]
    metadata = [next(data) for _ in range(metadata_count)]
    if nodes_count == 0:
        return sum(metadata)
    else:
        return sum(
            child_values[m-1]
            for m in metadata
            if 0 <= m-1 < len(child_values)
        )


def part_1(data: List[int]) -> int:
    result = sum(read_metadata(iter(data)))
    print(f"part 1: sum of metadatas is {result}")
    return result


def part_2(data: List[int]) -> int:
    result = read_value(iter(data))
    print(f"part 2: value of the root node is {result}")
    return result


if __name__ == '__main__':
    data_ = list(load_data("data/08-input.txt"))
    part_1(data_)
    part_2(data_)
