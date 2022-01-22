"""
Advent of Code 2015
Day 7: Some Assembly Required
https://adventofcode.com/2015/day/7
"""

from enum import Enum
from typing import Iterable

from common.file import relative_path


def part_1(circuit: 'Circuit') -> int:
    """
    This year, Santa brought little Bobby Tables a set of wires and bitwise logic gates!
    Unfortunately, little Bobby is a little under the recommended age range, and he needs help
    assembling the circuit.

    Each wire has an identifier (some lowercase letters) and can carry a 16-bit signal (a number
    from `0` to `65535`). A signal is provided to each wire by a gate, another wire, or some
    specific value. Each wire can only get a signal from one source, but can provide its signal to
    multiple destinations. A gate provides no signal until all of its inputs have a signal.

    The included instructions booklet describes how to connect the parts together: `x AND y -> z`
    means to connect wires `x` and `y` to an AND gate, and then connect its output to wire `z`.

    For example:

      - `123 -> x` means that the signal `123` is provided to wire `x`:

        >>> (c1 := Connection.from_str('123 -> x'))
        Connection(Command.VALUE, '123', target='x')
        >>> c1.evaluate()
        ('x', 123)

      - `x AND y -> z` means that the bitwise AND of wire `x` and wire `y` is provided to wire `z`:

        >>> (c2 := Connection.from_str('x AND y -> z'))
        Connection(Command.AND, 'x', 'y', target='z')
        >>> c2.evaluate({'x': 12, 'y': 10})
        ('z', 8)

      - `p LSHIFT 2 -> q` means that the value from `p` is left-shifted by 2 and provided to `q`:

        >>> (c3 := Connection.from_str('p LSHIFT 2 -> q'))
        Connection(Command.LSHIFT, 'p', '2', target='q')
        >>> c3.evaluate({'p': 3})
        ('q', 12)

      - `NOT e -> f` means that the bitwise complement of the value from wire e is provided to `f`:

        >>> (c4 := Connection.from_str('NOT e -> f'))
        Connection(Command.NOT, 'e', target='f')
        >>> c4.evaluate({'e': 1})
        ('f', 65534)

    Other possible gates include `OR` (bitwise OR) and `RSHIFT` (right-shift).

    For example, here is a simple circuit:

        >>> example = circuit_from_text('''
        ...     123 -> x
        ...     456 -> y
        ...     x AND y -> d
        ...     x OR y -> e
        ...     x LSHIFT 2 -> f
        ...     y RSHIFT 2 -> g
        ...     NOT x -> h
        ...     NOT y -> i
        ... ''')

    After it is run, these are the signals on the wires:

        >>> from common.utils import sorted_keys
        >>> sorted_keys(evaluate_circuit(example))
        {'d': 72, 'e': 507, 'f': 492, 'g': 114, 'h': 65412, 'i': 65079, 'x': 123, 'y': 456}

    In little Bobby's kit's instructions booklet (provided as your puzzle input), what signal is
    ultimately provided to **wire `a`**?

        >>> part_1([Connection.from_str('123 -> t'), Connection.from_str('t LSHIFT 1 -> a')])
        part 1: circuit outputs value a=246
        246
    """

    result = evaluate_circuit(circuit)['a']
    print(f"part 1: circuit outputs value a={result}")
    return result


def part_2(circuit: 'Circuit', b_override: int) -> int:
    """
    Now, take the signal you got on wire `a`, override wire `b` to that signal, and reset the other
    wires (including wire `a`). What new signal is ultimately provided to wire `a`?

        >>> example = [Connection.from_str('8 -> b'), Connection.from_str('b RSHIFT 1 -> a')]
        >>> evaluate_circuit(example)['a']
        4
        >>> example_overriden = override_value(example, 'b', 200)
        >>> evaluate_circuit(example_overriden)['a']
        100

        >>> part_2(example, b_override=300)
        part 2: after override b=300 circuit outputs value a=150
        150
    """

    result = evaluate_circuit(override_value(circuit, 'b', b_override))['a']
    print(f"part 2: after override b={b_override} circuit outputs value a={result}")
    return result


class Command(Enum):
    VALUE = (0, 1)
    NOT = (1, 1)
    AND = (2, 2)
    OR = (3, 2)
    LSHIFT = (4, 2)
    RSHIFT = (5, 2)

    def __init__(self, code: int, argcount: int):
        self.code = code
        self.argcount = argcount

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class Connection:
    def __init__(self, command: Command, arg1: str, arg2: str | None = None, *, target: str):
        assert arg1 is not None
        if command.argcount >= 2:
            assert arg2 is not None

        self.command = command
        self.arg1 = arg1
        self.arg2 = arg2
        self.target = target

    def __repr__(self):
        tn = type(self).__name__
        arg2_repr = f', {self.arg2!r}' if self.arg2 is not None else ''
        return f'{tn}({self.command!r}, {self.arg1!r}{arg2_repr}, target={self.target!r})'

    def __str__(self):
        if self.command == Command.VALUE:
            return f"{self.arg1} -> {self.target}"
        elif self.command == Command.NOT:
            return f"NOT {self.arg1} -> {self.target}"
        else:
            return f"{self.arg1} {self.command.name} {self.arg2} -> {self.target}"

    @classmethod
    def from_str(cls, line: str):
        """
        456 -> y
        x AND y -> d
        x OR y -> e
        x LSHIFT 2 -> f
        y RSHIFT 2 -> g
        NOT x -> h
        """
        parts = line.strip().split(' ')
        assert parts[-2] == "->"
        target = parts[-1]
        del parts[-2:]

        if len(parts) == 1:
            return cls(Command.VALUE, parts[0], target=target)
        elif len(parts) == 2:
            assert parts[0] == "NOT"
            return cls(Command.NOT, parts[1], target=target)
        elif len(parts) == 3:
            return cls(Command[parts[1]], parts[0], parts[2], target=target)
        else:
            raise ValueError(parts)

    def required_variables(self) -> Iterable[str]:
        if not self.arg1.isnumeric():
            yield self.arg1
        if self.arg2 is not None and not self.arg2.isnumeric():
            yield self.arg2

    def evaluate(self, values: dict[str, int] = None) -> tuple[str, int]:
        return self.target, self._eval_value(values or {})

    def _eval_value(self, values: dict[str, int]) -> int:
        val1 = int(self.arg1) if self.arg1.isnumeric() else values[self.arg1]

        if self.command == Command.VALUE:
            return val1
        elif self.command == Command.NOT:
            return val1 ^ 0xffff

        assert self.arg2 is not None
        val2 = int(self.arg2) if self.arg2.isnumeric() else values[self.arg2]
        if self.command == Command.AND:
            return val1 & val2
        elif self.command == Command.OR:
            return val1 | val2
        elif self.command == Command.LSHIFT:
            return val1 << val2
        elif self.command == Command.RSHIFT:
            return val1 >> val2
        else:
            raise ValueError(f"unsupported command {self.command.name}")


Circuit = list[Connection]


def evaluate_circuit(circuit: Circuit) -> dict[str, int]:
    unprocessed_connections = list(circuit)

    values: dict[str, int] = {}

    while unprocessed_connections:
        known_variables = set(values.keys())
        conn = next(
            i for i in unprocessed_connections
            if all(
                rv in known_variables
                for rv in i.required_variables()
            )
        )
        unprocessed_connections.remove(conn)
        key, value = conn.evaluate(values)
        values[key] = value

    return values


def override_value(circuit: Circuit, wire: str, value: int) -> Circuit:
    con_to_override = next(c for c in circuit if c.command == Command.VALUE and c.target == wire)
    con_overriden = Connection(Command.VALUE, str(value), target=wire)
    return [con_overriden if con is con_to_override else con for con in circuit]


def circuit_from_text(text: str) -> Circuit:
    return list(connections_from_lines(text.strip().splitlines()))


def circuit_from_file(fn: str) -> Circuit:
    return list(connections_from_lines(open(relative_path(__file__, fn))))


def connections_from_lines(lines: Iterable[str]) -> Iterable[Connection]:
    return (Connection.from_str(line.strip()) for line in lines)


if __name__ == '__main__':
    circuit_ = circuit_from_file('data/07-input.txt')
    a = part_1(circuit_)
    part_2(circuit_, b_override=a)
