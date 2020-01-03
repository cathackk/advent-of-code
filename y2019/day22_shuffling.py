from typing import Iterable
from typing import Tuple

Instr = Tuple[str, int]


def inverse(x, m):
    t, newt = 0, 1
    r, newr = m, x % m
    while newr != 0:
        quotient = r // newr
        t, newt = newt, t - quotient * newt
        r, newr = newr, r - quotient * newr
    if r > 1:
        return None
    return t % m


def gsm(a, n, m):
    assert n >= 0
    assert m > 1

    a = a % m

    if n == 0:
        return 1

    elif n % 2 == 1:
        q = (1 + a) % m
        g1 = gsm(a*a, (n-1)//2, m)
        return (q * g1) % m

    else:
        q = (1 + a + a*a) % m
        g1 = gsm(a*a, (n-2)//2, m)
        return (q * g1) % m


class SPN:
    def __init__(self, a: int, b: int, m: int):
        assert m > 1
        self.a = a % m
        self.b = b % m
        self.m = m

    def __repr__(self):
        return f'{type(self).__name__}({self.a}, {self.b}, {self.m})'

    def __str__(self):
        return f"{self.a}x + {self.b} mod {self.m}"

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            and self.a == other.a
            and self.b == other.b
            and self.m == other.m
        )

    def __mul__(self, k: int) -> 'SPN':
        return type(self)(self.a * k, self.b * k, self.m)

    def __add__(self, k: int) -> 'SPN':
        return type(self)(self.a, self.b + k, self.m)

    def __mod__(self, m: int) -> 'SPN':
        assert m == self.m
        return self

    def __call__(self, x):
        """
        >>> SPN(3, 6, 11)(1)
        9
        >>> SPN(3, 6, 11)(4)
        7
        >>> SPN(1, 0, 11)(SPN(3, 0, 11))
        SPN(3, 0, 11)
        >>> SPN(3, 0, 11)(SPN(1, 2, 11))
        SPN(3, 6, 11)
        >>> SPN(3, 6, 11)(SPN(-1, -1, 11))
        SPN(8, 3, 11)
        """
        return (x * self.a + self.b) % self.m

    def __pow__(self, power: int):
        """
        >>> SPN(3, 6, 11) ** 0
        SPN(1, 0, 11)
        >>> SPN(3, 6, 11) ** 1
        SPN(3, 6, 11)
        >>> SPN(3, 6, 11) ** 2
        SPN(9, 2, 11)
        >>> SPN(3, 6, 11) ** 3
        SPN(5, 1, 11)
        >>> SPN(3, 0, 11) ** 10
        SPN(1, 0, 11)
        >>> SPN(3, 6, 11) ** -1
        SPN(4, 9, 11)
        """
        if power == 0:
            return type(self)(1, 0, self.m)
        if power == 1:
            return self
        elif power > 1:
            ap = pow(self.a, power, self.m)
            bp = self.b * (1 - ap) * inverse(1 - self.a, self.m)
            return type(self)(ap, bp, self.m)
        elif power == -1:
            a_inv = inverse(self.a, self.m)
            return type(self)(a_inv, -a_inv * self.b, self.m)
        elif power < -1:
            return (self ** abs(power)) ** -1

    @classmethod
    def combine(cls, spns: Iterable['SPN']) -> 'SPN':
        """
        >>> SPN.combine([SPN(3, 0, 11), SPN(1, 2, 11), SPN(-1, -1, 11)])
        SPN(8, 3, 11)
        """
        result = None
        for spn in spns:
            if result is None:
                result = spn
            else:
                result = result(spn)
        return result


def load_instrs(fn: str) -> Iterable[Instr]:
    for line in open(fn):
        line = line.strip()
        if line.startswith("deal with increment "):
            _, n = line.rsplit(" ", 1)
            yield 'dwi', int(n)
        elif line.startswith("cut "):
            _, n = line.rsplit(" ", 1)
            yield 'cut', int(n)
        elif line == "deal into new stack":
            yield 'reverse', 0
        else:
            raise ValueError(line)


def spn_from_instr(instr: Instr, modulo: int) -> SPN:
    c, n = instr
    if c == 'dwi':
        return SPN(inverse(n, modulo), 0, modulo)
    elif c == 'cut':
        return SPN(1, n, modulo)
    elif c == 'reverse':
        return SPN(-1, -1, modulo)
    else:
        raise ValueError(c)


def test():
    instrs = list(load_instrs("data/22-test.txt"))
    cards = 7

    for r in range(6):
        print(f"==== SPN ** {r} ====")
        spn = SPN.combine(spn_from_instr(instr, cards) for instr in instrs) ** r
        print(f"> spn = {spn}")
        spn_inv = spn ** (-1)
        print([spn(n) for n in range(cards)])
        for c in range(cards):
            print(f"card {c} is at position {spn_inv(c)}")
        print()

    print("==== SPN ** R ====")

    repeats = 101741582076661
    spn3 = spn ** repeats
    spn3_inv = spn ** (-repeats)
    print([spn3(n) for n in range(cards)])
    for c in range(cards):
        print(f"card {c} is at position {spn3_inv(c)}")


def part_1(searched_card=2019):
    cards = 10007
    spn = SPN.combine(
        spn_from_instr(instr, cards)
        for instr in load_instrs("data/22-input.txt")
    ) ** -1
    position = spn(searched_card)
    print(f"part 1: card [{searched_card}] is at position {position}")
    print(f"        (at position {position} is card [{(spn**-1)(position)}])")
    return position


def part_2(deck_position=2020):
    cards = 119315717514047
    repeats = 101741582076661
    spn = SPN.combine(
        spn_from_instr(instr, cards)
        for instr in load_instrs("data/22-input.txt")
    ) ** repeats
    card = spn(deck_position)
    print(f"part 2: at position {deck_position} is card [{card}]")
    print(f"        card [{card}] is at position {(spn**-1)(card)}")
    return card


if __name__ == '__main__':
    # test()
    part_1()
    part_2()
