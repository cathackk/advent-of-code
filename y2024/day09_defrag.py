"""
Advent of Code 2024
Day 9: Disk Fragmenter
https://adventofcode.com/2024/day/9
"""

from dataclasses import dataclass, replace
from typing import Iterable, Iterator, Self

from tqdm import tqdm

from common.chain import Link
from common.file import relative_path
from common.iteration import chunks, maybe_next


def part_1(disk_map: list['File']) -> int:
    """
    Another push of the button leaves you in the familiar hallways of some friendly amphipods
    (y2021/day23_organize.py)! Good thing you each somehow got your own personal mini submarine.
    The Historians jet away in search of the Chief, mostly by driving directly into walls.

    While The Historians quickly figure out how to pilot these things, you notice an amphipod in
    the corner struggling with his computer. He's trying to make more contiguous free space by
    compacting all of the files, but his program isn't working; you offer to help.

    He shows you the **disk map** (your puzzle input) he's already generated. For example:

        >>> example_0 = disk_map_from_text('2333133121414131402')

    The disk map uses a dense format to represent the layout of **files** and **free space** on the
    disk. The digits alternate between indicating the length of a file and the length of free space.

    So, a disk map like `12345` would represent a one-block file, two blocks of free space,
    a three-block file, four blocks of free space, and then a five-block file.

        >>> example_1 = disk_map_from_text('12345')
        >>> example_1  # doctest: +ELLIPSIS
        [File(id_num=0, size=1, gap=2), File(id_num=1, size=3, gap=4), File(id_num=2, size=5)]

    A disk map like `90909` would represent three nine-block files in a row (with no free space
    between them):

        >>> disk_map_from_text('90909')
        [File(id_num=0, size=9), File(id_num=1, size=9), File(id_num=2, size=9)]

    Each file on disk also has an **ID number** based on the order of the files as they appear
    **before** they are rearranged, starting with ID `0`. So, the disk map `12345` has three files:
    a one-block file with ID `0`, a three-block file with ID `1`, and a five-block file with ID `2`.
    Using one character for each block where digits are the file ID and `.` is free space, the disk
    map `12345` represents these individual blocks:

        >>> print_blocks(example_1)
        0..111....22222

    The first example above represents these individual blocks:

        >>> example_0  # doctest: +ELLIPSIS
        [File(id_num=0, size=2, gap=3), File(id_num=1, size=3, gap=3), ...]
        >>> print_blocks(example_0)
        00...111...2...333.44.5555.6666.777.888899

    The amphipod would like to **move file blocks one at a time** from the end of the disk to the
    leftmost free space block (until there are no gaps remaining between file blocks). For the disk
    map `12345`, the process looks like this:

        >>> result_1 = organize_blocks_naive(example_1, visualize=True)
        0..111....22222
        02.111....2222.
        022111....222..
        0221112...22...
        02211122..2....
        022111222......
        >>> result_1
        [0, 2, 2, 1, 1, 1, 2, 2, 2]
        >>> list(organize_blocks(example_1))
        [0, 2, 2, 1, 1, 1, 2, 2, 2]
        >>> list(organize_blocks(example_1)) == result_1
        True

    The first example requires a few more steps:

        >>> result_0 = organize_blocks_naive(example_0, visualize=True)
        00...111...2...333.44.5555.6666.777.888899
        009..111...2...333.44.5555.6666.777.88889.
        0099.111...2...333.44.5555.6666.777.8888..
        00998111...2...333.44.5555.6666.777.888...
        009981118..2...333.44.5555.6666.777.88....
        0099811188.2...333.44.5555.6666.777.8.....
        009981118882...333.44.5555.6666.777.......
        0099811188827..333.44.5555.6666.77........
        00998111888277.333.44.5555.6666.7.........
        009981118882777333.44.5555.6666...........
        009981118882777333644.5555.666............
        00998111888277733364465555.66.............
        0099811188827773336446555566..............
        >>> result_0
        [0, 0, 9, 9, 8, 1, 1, 1, 8, 8, 8, 2, 7, 7, 7, 3, 3, 3, 6, 4, 4, 6, 5, 5, 5, 5, 6, 6]
        >>> list(organize_blocks(example_0)) == result_0
        True

    The final step of this file-compacting process is to update the **filesystem checksum**.
    To calculate the checksum, add up the result of multiplying each of these blocks' position with
    the file ID number it contains. The leftmost block is in position `0`. If a block contains free
    space, skip it instead.

    Continuing the first example, the first few blocks' position multiplied by its file ID number
    are `0 * 0 = 0`, `1 * 0 = 0`, `2 * 9 = 18`, `3 * 9 = 27`, `4 * 8 = 32`, and so on.

        >>> [pos * f_id for pos, f_id in enumerate(result_0)]  # doctest: +ELLIPSIS
        [0, 0, 18, 27, 32, 5, 6, 7, 64, ...]

    In this example, the checksum is the sum of these, **`1928`**:

        >>> blocks_checksum(result_0)
        1928

    Compact the amphipod's hard drive using the process he requested.
    **What is the resulting filesystem checksum?**

        >>> part_1(example_0)
        part 1: resulting filesystem checksum is 1928
        1928
    """

    result = blocks_checksum(organize_blocks(disk_map))

    print(f"part 1: resulting filesystem checksum is {result}")
    return result


def part_2(disk_map: Iterable['File']) -> int:
    """
    Upon completion, two things immediately become clear. First, the disk definitely has a lot more
    contiguous free space, just like the amphipod hoped. Second, the computer is running much more
    slowly! Maybe introducing all of that file system fragmentation was a bad idea?

    The eager amphipod already has a new plan: rather than move individual blocks, he'd like to try
    compacting the files on his disk by moving **whole files** instead.

    This time, attempt to move whole files to the leftmost span of free space blocks that could fit
    the file. Attempt to move each file exactly once in order of **decreasing file ID** number
    starting with the file with the highest file ID number. If there is no span of free space to
    the left of a file that is large enough to fit the file, the file does not move.

    The first example from above now proceeds differently:

        >>> example_0 = disk_map_from_file('data/09-example.txt')
        >>> result_0 = list(organize_files(example_0, visualize=True))
        00...111...2...333.44.5555.6666.777.888899
        0099.111...2...333.44.5555.6666.777.8888..
        0099.1117772...333.44.5555.6666.....8888..
        0099.111777244.333....5555.6666.....8888..
        00992111777.44.333....5555.6666.....8888..
        >>> result_0  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        [File(id_num=0, size=2),
         File(id_num=9, size=2),
         File(id_num=2, size=1),
         File(id_num=1, size=3),
         File(id_num=7, size=3, gap=1),
         File(id_num=4, size=2, gap=1),
         File(id_num=3, size=3, gap=4), ...]

    The process of updating the filesystem checksum is the same; now, this example's checksum would
    be **`2858`**:

        >>> files_checksum(result_0)
        2858

    Start over, now compacting the amphipod's hard drive using this new method instead.
    **What is the resulting filesystem checksum?**

        >>> part_2(example_0)
        part 2: resulting filesystem checksum is 2858
        2858
    """

    result = files_checksum(organize_files(disk_map))

    print(f"part 2: resulting filesystem checksum is {result}")
    return result


@dataclass(frozen=True)
class File:
    id_num: int
    size: int
    gap: int

    def __post_init__(self) -> None:
        assert self.id_num >= 0
        assert self.size >= 1
        assert self.gap >= 0

    def blocks(self) -> Iterable[int | None]:
        for _ in range(self.size):
            yield self.id_num
        for _ in range(self.gap):
            yield None

    def __repr__(self) -> str:
        gap_repr = f', gap={self.gap!r}' if self.gap else ''
        return f'{type(self).__name__}(id_num={self.id_num!r}, size={self.size!r}{gap_repr})'

    def __str__(self) -> str:
        id_char = str(self.id_num)[-1]
        return (id_char * self.size) + ('.' * self.gap)

    def __iter__(self) -> Iterator[int]:
        return iter((self.id_num, self.size, self.gap))

    @classmethod
    def many_from_lines(cls, lines: Iterable[str]) -> Iterable[Self]:
        nums = [int(char) for line in lines for char in line.strip()]
        if len(nums) % 2 == 1:
            nums.append(0)

        return (
            cls(id_num=id_num, size=size, gap=gap)
            for id_num, (size, gap) in enumerate(chunks(nums, 2))
        )


def disk_map_from_file(fn: str) -> list[File]:
    return list(File.many_from_lines(open(relative_path(__file__, fn)).readline()))


def disk_map_from_text(text: str) -> list[File]:
    return list(File.many_from_lines(text.strip().splitlines()))


def print_blocks(files: Iterable[File]) -> None:
    print(''.join(str(file) for file in files))


def organize_blocks_naive(disk_map: Iterable[File], visualize: bool = False) -> list[int | None]:
    blocks = [block for file in disk_map for block in file.blocks()]
    original_size = len(blocks)

    def print_ids():
        line = ''.join(str(block)[-1] if block is not None else '.' for block in blocks)
        print(line.ljust(original_size, '.'))

    if visualize:
        print_ids()

    start = 0
    while True:
        empty_pos = maybe_next(
            pos
            for pos, file_id in enumerate(blocks[start:], start=start)
            if file_id is None
        )
        if empty_pos is None:
            break

        start = empty_pos
        blocks[start] = blocks.pop()

        # trim blocks
        while blocks[-1] is None:
            blocks.pop()

        if visualize:
            print_ids()

    return blocks


def organize_blocks(disk_map: Iterable[File]) -> Iterable[int]:
    files = list(disk_map)
    head_pos, tail_pos = 0, len(files) - 1

    tail_id, tail_size = -1, 0

    while True:
        head_id, head_size, head_gap = files[head_pos]
        head_pos += 1

        # forward blocks
        yield from (head_id for _ in range(head_size))

        if head_pos > tail_pos:
            break

        # backward blocks
        for _ in range(head_gap):
            if not tail_size:
                # read tail
                tail_id, tail_size, _ = files[tail_pos]
                tail_pos -= 1
            yield tail_id
            tail_size -= 1

    yield from (tail_id for _ in range(tail_size))


def blocks_checksum(blocks: Iterable[int | None]) -> int:
    return sum(pos * block for pos, block in enumerate(blocks) if block is not None)


def _find_fitting_node(node: Link[File], first_node: Link[File]) -> Link[File] | None:
    # finds the first file node with a gap fitting given `node.file` (or `None` if there is none)
    moved_size = node.value.size
    for tested_node in first_node.iter_links():
        if tested_node == node:
            return None
        if tested_node.value.gap >= moved_size:
            return tested_node
    else:
        return None


def _adjust_node_gap(node: Link[File], *, new_gap: int = None, gap_delta: int = None) -> File:
    # adjusts file node in place by extending/reducing its gap
    file = node.value

    if new_gap is None:
        assert gap_delta is not None
        new_gap = file.gap + gap_delta

    node.value = replace(file, gap=new_gap)
    return node.value


def organize_files(disk_map: Iterable[File], visualize: bool = False) -> Iterable[File]:
    first_node, last_node, nodes_count = Link.build_chain(disk_map)

    if visualize:
        print_blocks(first_node)

    # immutable nodes list that won't be touched by reordering
    processed_nodes = list(last_node.iter_links(reverse=True))
    assert len(processed_nodes) == nodes_count

    for source_node in tqdm(
        processed_nodes,
        desc="organizing",
        unit=" files",
        unit_scale=True,
        delay=1.0,
    ):
        if not (target_node := _find_fitting_node(source_node, first_node)):
            # nowhere to move
            continue

        moved_file = source_node.value
        # 1. add total size of the moved file to its left neighbor's gap
        _adjust_node_gap(source_node.prev_link, gap_delta=moved_file.size + moved_file.gap)
        # 2. disconnect the source node
        source_node.disconnect()
        # 3. insert the file after the target node
        moved_node = target_node.insert_after(moved_file)
        _adjust_node_gap(moved_node, new_gap=target_node.value.gap - moved_file.size)
        # 4. reduce target node's gap
        _adjust_node_gap(target_node, new_gap=0)

        if visualize:
            print_blocks(first_node)

    return first_node


def files_checksum(files: Iterable[File]) -> int:
    return blocks_checksum(block for file in files for block in file.blocks())


def main(input_fn: str = 'data/09-input.txt') -> tuple[int, int]:
    disk_map = disk_map_from_file(input_fn)
    result_1 = part_1(disk_map)
    result_2 = part_2(disk_map)
    return result_1, result_2


if __name__ == '__main__':
    main()
