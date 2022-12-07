"""
Advent of Code 2022
Day 7: No Space Left On Device
https://adventofcode.com/2022/day/7
"""

from dataclasses import dataclass
from typing import Iterable
from typing import Union

from common.file import relative_path


def part_1(dir_sizes: dict[str, int], size_limit: int = 100_000) -> int:
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

        >>> cmds = commands_from_text('''
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
        >>> len(cmds)
        10
        >>> cmds[0]
        cd('/')
        >>> cmds[1]
        ls([Dir('a'), File('b.txt', 14848514), File('c.dat', 8504156), Dir('d')])
        >>> cmds[2]
        cd('a')
        >>> cmds[3]
        ls([Dir('e'), File('f', 29116), File('g', 2557), File('h.lst', 62596)])
        >>> cmds[4]
        cd('e')
        >>> cmds[5]
        ls([File('i', 584)])
        >>> cmds[6:9]
        [cd('..'), cd('..'), cd('d')]
        >>> cmds[9]
        ls([File('j', 4060174), File('d.log', 8033020), File('d.ext', 5626152), File('k', 7214296)])

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

        >>> fs = create_filesystem(cmds)
        >>> fs  # doctest: +NORMALIZE_WHITESPACE
        {'a': {'e': {'i': 584}, 'f': 29116, 'g': 2557, 'h.lst': 62596},
         'b.txt': 14848514, 'c.dat': 8504156,
         'd': {'j': 4060174, 'd.log': 8033020, 'd.ext': 5626152, 'k': 7214296}}
        >>> draw_filesystem(fs)
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

        >>> sizes = total_sizes(fs)

    The total sizes of the directories above can be found as follows:

      - The total size of directory `e` is **584** because it contains a single file `i` of size 584
        and no other directories:

        >>> sizes['/a/e']
        584

      - The directory `a` has total size **94_853** because it contains files `f` (size 29_116),
        `g` (size 2_557), and `h.lst` (size 62_596), plus file `i` indirectly (`a` contains `e`
        which contains `i`):

        >>> sizes['/a']
        94853

      - Directory `d` has total size 24_933_642:

        >>> sizes['/d']
        24933642

      - As the outermost directory, `/` contains every file. Its total size is 48_381_165,
        the sum of the size of every file:

        >>> sizes['/']
        48381165

    To begin, find all of the directories with a **total size of at most 100_000**, then calculate
    the sum of their total sizes. In the example above, these directories are `a` and `e`; the sum
    of their total sizes is **95_437** (94_853 + 584). (As in this example, this process can count
    files more than once!)

        >>> {d: size for d, size in sizes.items() if size <= 100_000}
        {'/a': 94853, '/a/e': 584}
        >>> sum(_.values())
        95437

    Find all of the directories with a total size of at most 100_000.
    **What is the sum of the total sizes of those directories?**

        >>> part_1(sizes)
        part 1: total size of dirs with size less than 100000 is 95437
        95437
    """

    result = sum(size for size in dir_sizes.values() if size <= size_limit)

    print(f"part 1: total size of dirs with size less than {size_limit} is {result}")
    return result


def part_2(
    dir_sizes: dict[str, int],
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

        >>> sizes = total_sizes(create_filesystem(commands_from_file('data/07-example.txt')))
        >>> sizes['/']
        48381165
        >>> 70_000_000 - sizes['/']
        21618835

    Therefore, the update still requires a directory with total size of at least 8381165 to be
    deleted before it can run.

        >>> need_to_free = sizes['/'] + 30_000_000 - 70_000_000
        >>> need_to_free
        8381165

    To achieve this, you have the following options:

      - Delete directory `e`, which would increase unused space by 584.
      - Delete directory `a`, which would increase unused space by 94_853.
      - Delete directory `d`, which would increase unused space by 24_933_642.
      - Delete directory `/`, which would increase unused space by 48_381_165.

    Directories `e` and `a` are both too small; deleting them would not free up enough space.
    However, directories `d` and `/` are both big enough!

        >>> {d: size for d, size in sizes.items() if size >= need_to_free}
        {'/': 48381165, '/d': 24933642}

    Between these, choose the smallest: `d`, increasing unused space by **24_933_642**.

        >>> min(_.values())
        24933642

    Find the smallest directory that, if deleted, would free up enough space on the filesystem to
    run the update. **What is the total size of that directory?**

        >>> part_2(sizes)
        part 2: delete dir /d with size 24933642
        24933642
    """

    need_to_free = dir_sizes['/'] + update_size - disk_size
    assert need_to_free > 0

    deleted_size, deleted_path = min(
        (size, name)
        for name, size in dir_sizes.items()
        if size >= need_to_free
    )

    print(f"part 2: delete dir {deleted_path} with size {deleted_size}")
    return deleted_size


FilesystemDict = dict[str, Union[int, 'FilesystemDict']]


def create_filesystem(commands: Iterable['Command']) -> FilesystemDict:
    filesystem: FilesystemDict = {}
    current_path: list[str] = []

    def cd_into(files: FilesystemDict, path: list[str]) -> FilesystemDict:
        if not path:
            return files

        subfs = files[path[0]]
        assert isinstance(subfs, dict)
        return cd_into(subfs, path[1:])


    for command in commands:
        if isinstance(command, CD):
            if command.dir_name == '/':
                current_path = []
            elif command.dir_name == '..':
                assert current_path
                current_path.pop()
            else:
                current_path.append(command.dir_name)

        elif isinstance(command, LS):
            current_dir = cd_into(filesystem, current_path)

            for item in command.listing:
                if isinstance(item, File):
                    current_dir[item.name] = item.size
                elif isinstance(item, Dir):
                    current_dir[item.name] = {}

        else:
            raise TypeError(type(command))

    return filesystem


def draw_filesystem(filesystem: FilesystemDict, level: int = 0) -> None:
    if level == 0:
        print('- / (dir)')
        draw_filesystem(filesystem, 1)
        return

    indent = '  ' * level

    for key, value in filesystem.items():
        if isinstance(value, dict):
            print(f'{indent}- {key} (dir)')
            draw_filesystem(value, level + 1)
        elif isinstance(value, int):
            print(f'{indent}- {key} (file, size={value})')
        else:
            raise TypeError(type(value))


def total_sizes(filesystem: FilesystemDict, path: str = '/') -> dict[str, int]:
    def joinpath(path_1: str, path_2: str) -> str:
        return path_1.rstrip('/') + '/' + path_2

    sizes = {path: 0}

    for key, value in filesystem.items():
        if isinstance(value, dict):
            subpath = joinpath(path, key)
            subdir_sizes = total_sizes(value, subpath)
            sizes.update(subdir_sizes)
            sizes[path] += subdir_sizes[subpath]
        elif isinstance(value, int):
            sizes[path] += value
        else:
            raise TypeError(type(value))

    return sizes


@dataclass(frozen=True)
class CD:
    dir_name: str

    def __repr__(self) -> str:
        return f'cd({self.dir_name!r})'


@dataclass(frozen=True)
class File:
    name: str
    size: int

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.name!r}, {self.size!r})'


@dataclass(frozen=True)
class Dir:
    name: str

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.name!r})'


@dataclass(frozen=True)
class LS:
    listing: list[File | Dir]

    def __repr__(self) -> str:
        return f'ls({self.listing!r})'

    @classmethod
    def from_output(cls, output: Iterable[str]) -> 'LS':
        def parse_fd(line: str) -> File | Dir:
            # dir a
            # 14848514 b.txt
            size, name = line.split()
            if size == 'dir':
                return Dir(name)
            else:
                return File(name, int(size))

        return cls([parse_fd(line) for line in output])


Command = CD | LS


def commands_from_file(fn: str) -> list[Command]:
    return list(commands_from_lines(open(relative_path(__file__, fn))))


def commands_from_text(text: str) -> list[Command]:
    return list(commands_from_lines(text.strip().splitlines()))


def commands_from_lines(lines: Iterable[str]) -> Iterable[Command]:
    for command, output in group_command_lines(lines):
        if command.startswith('cd '):
            assert not output
            yield CD(dir_name=command.removeprefix('cd '))
        elif command == 'ls':
            yield LS.from_output(output)
        else:
            raise ValueError(command)


def group_command_lines(lines: Iterable[str]) -> Iterable[tuple[str, list[str]]]:
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

    if command:
        yield command, output


def main(input_fn: str = 'data/07-input.txt') -> tuple[int, int]:
    # TODO: join the first two steps into one?
    commands = commands_from_file(input_fn)
    filesystem = create_filesystem(commands)
    dir_sizes = total_sizes(filesystem)

    result_1 = part_1(dir_sizes)
    result_2 = part_2(dir_sizes)
    return result_1, result_2


if __name__ == '__main__':
    main()
