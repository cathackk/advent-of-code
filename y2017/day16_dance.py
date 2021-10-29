from typing import Any
from typing import Iterable
from typing import List


Dancers = str
Move = tuple[str, Any, Any]
Dance = Iterable[Move]
Permutation = List[int]


def spin(ds: Dancers, distance: int) -> Dancers:
    """
    >>> spin('abcde', 3)
    'cdeab'
    >>> spin('abcde', 1)
    'eabcd'
    """
    assert 0 < distance < len(ds)
    return ds[-distance:] + ds[:-distance]


def exchange(ds: Dancers, a: int, b: int) -> Dancers:
    """
    >>> exchange('eabcd', 3, 4)
    'eabdc'
    """
    assert 0 <= a < len(ds)
    assert 0 <= b < len(ds)
    if a == b:
        return ds
    if a > b:
        a, b = b, a
    return ds[:a] + ds[b:b+1] + ds[a+1:b] + ds[a:a+1] + ds[b+1:]


def partner(ds: Dancers, a: str, b: str) -> Dancers:
    """
    >>> partner('eabdc', 'e', 'b')
    'baedc'
    """
    assert len(a) == 1
    assert len(b) == 1
    ia = ds.index(a)
    ib = ds.index(b)
    return exchange(ds, ia, ib)


def load_dance(fn: str) -> Dance:
    for line in open(fn):
        for move in line.strip().split(','):
            if move.startswith('s'):
                # s10 -> spin
                yield ('s', int(move[1:]), None)
            elif move.startswith('x'):
                # x6/13 -> exchange
                a, b = move[1:].split('/')
                yield ('x', int(a), int(b))
            elif move.startswith('p'):
                # pk/n -> partner
                a, b = move[1:].split('/')
                yield ('p', a, b)


def do_dance(dancers: Dancers, dance: Dance) -> Dancers:
    """
    >>> do_dance('abcde', [('s', 1, None), ('x', 3, 4), ('p', 'e', 'b')])
    'baedc'
    """
    for instr, a, b in dance:
        if instr == 's':
            assert b is None
            dancers = spin(dancers, int(a))
        elif instr == 'x':
            dancers = exchange(dancers, int(a), int(b))
        elif instr == 'p':
            dancers = partner(dancers, a, b)
        else:
            raise KeyError(instr)
    return dancers


def do_dance_repeated(dancers: Dancers, dance: Dance, repeats: int) -> Dancers:
    history: List[Dancers] = [dancers]
    while len(history) < repeats:
        dancers = do_dance(dancers, dance)
        if dancers == history[0]:
            # cycle detected
            return history[repeats % len(history)]
        history.append(dancers)
    return dancers


def create_dancers(count: int) -> Dancers:
    return ''.join(chr(ord('a') + k) for k in range(count))


def part_1(dance: Dance) -> Dancers:
    dancers = do_dance(create_dancers(16), dance)
    print(f"part 1: after the dance -> {dancers}")
    return dancers


def part_2(dance: Dance) -> Dancers:
    dancers = do_dance_repeated(create_dancers(16), dance, repeats=1_000_000_000)
    print(f"part 2: after the dance repeated 1e9x -> {dancers}")
    return dancers


if __name__ == '__main__':
    dance_ = list(load_dance("data/16-input.txt"))
    part_1(dance_)
    part_2(dance_)
