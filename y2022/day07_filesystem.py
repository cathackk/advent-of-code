"""
Advent of Code 2022
Day 7: No Space Left On Device
https://adventofcode.com/2022/day/7
"""

from functools import lru_cache
from typing import Iterable, Self, Union

from meta.aoc_tools import data_path


def part_1(filesystem: 'Directory', size_limit: int = 100_000) -> int:
    """
    You can hear birds chirping and raindrops hitting leaves as the expedition proceeds.
    Occasionally, you can even hear much louder sounds in the distance; how big do the animals get
    out here, anyway?

    The device the Elves gave you has problems with more than just its communication system. You try
    to run a system update:

    ```
    $ system-update --please --pretty-please-with-sugar-on-top
    Error: No space left on device
    ```

    Perhaps you can delete some files to make space for the update?

    You browse around the filesystem to assess the situation and save the resulting terminal output
    (your puzzle input). For example:

        >>> fs = Directory.from_text('''
        ...     $ cd /
        ...     $ ls
        ...     dir a
        ...     14848514 b.txt
        ...     8504156 c.dat
        ...     dir d
        ...     $ cd a
        ...     $ ls
        ...     dir e
        ...     29116 f
        ...     2557 g
        ...     62596 h.lst
        ...     $ cd e
        ...     $ ls
        ...     584 i
        ...     $ cd ..
        ...     $ cd ..
        ...     $ cd d
        ...     $ ls
        ...     4060174 j
        ...     8033020 d.log
        ...     5626152 d.ext
        ...     7214296 k
        ... ''')

    The filesystem consists of a tree of files (plain data) and directories (which can contain other
    directories or files). The outermost directory is called `/`. You can navigate around the
    filesystem, moving into or out of directories and listing the contents of the directory you're
    currently in.

    Within the terminal output, lines that begin with $ are **commands you executed**, very much
    like some modern computers:

      - `cd` means **change directory**. This changes which directory is the current directory, but
        the specific result depends on the argument:
        - `cd x` moves **in** one level: it looks in the current directory for the directory named
        `x` and makes it the current directory.
        - `cd ..` moves **out** one level: it finds the directory that contains the current
          directory, then makes that directory the current directory.
        - `cd /` switches the current directory to the outermost directory, `/`.
      - `ls` means **list**. It prints out all of the files and directories immediately contained
        by the current directory:
        - `123 abc` means that the current directory contains a file named `abc` with size 123.
        - `dir xyz` means that the current directory contains a directory named `xyz`.

    Given the commands and output in the example above, you can determine that the filesystem looks
    like this:

        >>> fs.draw()
        - / (dir)
          - a (dir)
            - e (dir)
              - i (file, size=584)
            - f (file, size=29116)
            - g (file, size=2557)
            - h.lst (file, size=62596)
          - b.txt (file, size=14848514)
          - c.dat (file, size=8504156)
          - d (dir)
            - j (file, size=4060174)
            - d.log (file, size=8033020)
            - d.ext (file, size=5626152)
            - k (file, size=7214296)

    Here, there are four directories: `/` (the outermost directory), `a` and `d` (which are in `/`),
    and `e` (which is in `a`). These directories also contain files of various sizes.

    Since the disk is full, your first step should probably be to find directories that are good
    candidates for deletion. To do this, you need to determine the **total size** of each directory.
    The total size of a directory is the sum of the sizes of the files it contains, directly or
    indirectly. (Directories themselves do not count as having any intrinsic size.)

    The total sizes of the directories above can be found as follows:

      - The total size of directory `e` is **584** because it contains a single file `i` of size 584
        and no other directories:

        >>> fs.at_path('/a/e').total_size()
        584

      - The directory `a` has total size **94_853** because it contains files `f` (size 29_116),
        `g` (size 2_557), and `h.lst` (size 62_596), plus file `i` indirectly (`a` contains `e`
        which contains `i`):

        >>> fs.at_path('/a').total_size()
        94853

      - Directory `d` has total size 24_933_642:

        >>> fs.at_path('/d').total_size()
        24933642

      - As the outermost directory, `/` contains every file. Its total size is 48_381_165,
        the sum of the size of every file:

        >>> fs.total_size()
        48381165

    To begin, find all of the directories with a **total size of at most 100_000**, then calculate
    the sum of their total sizes. In the example above, these directories are `a` and `e`; the sum
    of their total sizes is **95_437** (94_853 + 584). (As in this example, this process can count
    files more than once!)

        >>> {path: size for path, dir_ in fs.walkdirs() if (size := dir_.total_size()) <= 100_000}
        {'/a': 94853, '/a/e': 584}
        >>> sum(_.values())
        95437

    Find all of the directories with a total size of at most 100_000.
    **What is the sum of the total sizes of those directories?**

        >>> part_1(fs)
        part 1: total size of dirs with size less than 100000 is 95437
        95437
    """

    result = sum(
        size
        for _, dir_ in filesystem.walkdirs()
        if (size := dir_.total_size()) <= size_limit
    )

    print(f"part 1: total size of dirs with size less than {size_limit} is {result}")
    return result


def part_2(
    filesystem: 'Directory',
    disk_size: int = 70_000_000,
    update_size: int = 30_000_000
) -> int:
    """
    Now, you're ready to choose a directory to delete.

    The total disk space available to the filesystem is **70_000_000**. To run the update, you need
    unused space of at least **30_000_000**. You need to find a directory you can delete that will
    **free up enough space** to run the update.

    In the example above, the total size of the outermost directory (and thus the total amount of
    used space) is 48381165; this means that the size of the unused space must currently be
    21618835, which isn't quite the 30000000 required by the update.

        >>> fs = Directory.from_file(data_path(__file__, 'example.txt'))
        >>> fs.total_size()
        48381165
        >>> 70_000_000 - fs.total_size()
        21618835

    Therefore, the update still requires a directory with total size of at least 8381165 to be
    deleted before it can run.

        >>> need_to_free = fs.total_size() + 30_000_000 - 70_000_000
        >>> need_to_free
        8381165

    To achieve this, you have the following options:

      - Delete directory `e`, which would increase unused space by 584.
      - Delete directory `a`, which would increase unused space by 94_853.
      - Delete directory `d`, which would increase unused space by 24_933_642.
      - Delete directory `/`, which would increase unused space by 48_381_165.

    Directories `e` and `a` are both too small; deleting them would not free up enough space.
    However, directories `d` and `/` are both big enough!

        >>> {path: size for path, d in fs.walkdirs() if (size := d.total_size()) >= need_to_free}
        {'/': 48381165, '/d': 24933642}

    Between these, choose the smallest: `d`, increasing unused space by **24_933_642**.

        >>> min(_.values())
        24933642

    Find the smallest directory that, if deleted, would free up enough space on the filesystem to
    run the update. **What is the total size of that directory?**

        >>> part_2(fs)
        part 2: delete dir /d with size 24933642
        24933642
    """

    size_to_free = filesystem.total_size() + update_size - disk_size
    assert size_to_free > 0

    deleted_size, deleted_path = min(
        (size, dirname)
        for dirname, dir_ in filesystem.walkdirs()
        if (size := dir_.total_size()) >= size_to_free
    )

    print(f"part 2: delete dir {deleted_path} with size {deleted_size}")
    return deleted_size


# subfilesystem or int of given size
FileSystemItem = Union['Directory', int]
PathLike = Union[str, list[str]]


class Directory:

    def __init__(self, subitems: Iterable[tuple[str, FileSystemItem]] = ()):
        self.subitems = dict(subitems)

    def __getitem__(self, key: str) -> FileSystemItem:
        return self.subitems[key]

    def __setitem__(self, key: str, value: FileSystemItem) -> None:
        self.subitems[key] = value

    def at_path(self, path: PathLike) -> FileSystemItem:
        if isinstance(path, str):
            assert path.startswith('/')
            path = path[1:].split('/')

        if len(path) == 0:
            return self
        elif len(path) == 1:
            return self.subitems[path[0]]
        else:
            subitem = self.subitems[path[0]]
            assert isinstance(subitem, Directory)
            return subitem.at_path(path[1:])

    def walkdirs(self, current_path: str = '/') -> Iterable[tuple[str, 'Directory']]:
        yield current_path, self
        yield from (
            (path, subdir)
            for dirname, dir_ in self.subitems.items()
            if isinstance(dir_, Directory)
            for path, subdir in dir_.walkdirs(current_path.rstrip('/') + '/' + dirname)
        )

    @lru_cache()
    def total_size(self) -> int:
        def sizeof(item: FileSystemItem) -> int:
            if isinstance(item, int):
                return item
            elif isinstance(item, Directory):
                return item.total_size()
            else:
                raise TypeError(type(item))

        return sum(sizeof(item) for item in self.subitems.values())

    def draw(self, level: int = 0) -> None:
        if level == 0:
            print('- / (dir)')
            self.draw(level=1)
            return

        indent = '  ' * level

        for key, value in self.subitems.items():
            if isinstance(value, Directory):
                print(f'{indent}- {key} (dir)')
                value.draw(level + 1)
            elif isinstance(value, int):
                print(f'{indent}- {key} (file, size={value})')
            else:
                raise TypeError(type(value))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(fn))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        root = cls()
        current_path: list[str] = []

        for command, output in group_command_lines(lines):
            if command.startswith('cd '):
                assert not output

                target = command.removeprefix('cd ')
                if target == '/':
                    current_path = []
                elif target == '..':
                    current_path.pop()
                else:
                    assert '/' not in target
                    current_path.append(target)

            elif command == 'ls':
                sub_fs = root.at_path(current_path)
                assert isinstance(sub_fs, cls)
                for item in output:
                    size, name = item.split(' ')
                    sub_fs[name] = cls() if size == 'dir' else int(size)

            else:
                raise KeyError(command)

        return root


def group_command_lines(lines: Iterable[str]) -> Iterable[tuple[str, list[str]]]:
    """ Returns input lines grouped into tuples (command: str, output: list[str]) """
    command, output = None, []
    for line in lines:
        line = line.strip()
        if line.startswith('$ '):
            if command:
                # flush
                yield command, output
                output = []
            command = line.removeprefix('$ ')
        else:
            output.append(line)

    # flush leftovers
    if command:
        yield command, output


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    filesystem = Directory.from_file(input_path)
    result_1 = part_1(filesystem)
    result_2 = part_2(filesystem)
    return result_1, result_2


if __name__ == '__main__':
    main()
