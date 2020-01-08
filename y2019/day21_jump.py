from typing import Optional

from y2019.intcode import load_tape
from y2019.intcode import Machine


def robot_run(*lines: str) -> Optional[int]:
    io = Machine(load_tape("data/21-program.txt")).run_io()
    print(io.read_str(), end='')

    script = "".join(line+"\n" for line in lines)
    print(script, end="")
    io.write(script)

    answer = list(io.read())
    if answer[-1] > 255:
        print(''.join(chr(v) for v in answer[:-1]), end="")
        return answer[-1]
    else:
        print(''.join(chr(v) for v in answer), end="")
        return None


def part_1():
    result = robot_run(
        "OR A J",
        "AND B J",
        "AND C J",
        "NOT J J",
        "AND D J",
        "WALK"
    )
    print(f"part 1: result={result}")


def part_2():
    result = robot_run(
        "OR D J",
        "OR A T",
        "AND B T",
        "AND C T",
        "NOT T T",
        "AND T J",
        "AND E T",
        "OR H T",
        "AND T J",
        "RUN",
    )
    print(f"part 2: result={result}")


if __name__ == '__main__':
    # part_1()
    part_2()
