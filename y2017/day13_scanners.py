from itertools import count
from typing import Iterable


Layer = tuple[int, int]


def load_layers(fn: str) -> Iterable[Layer]:
    for line in open(fn):
        ldepth, lrange = line.strip().split(': ')
        yield int(ldepth), int(lrange)


def caught_layers(layers: Iterable[Layer], delay: int = 0) -> Iterable[Layer]:
    for layer in layers:
        ldepth, lrange = layer
        scanner_round = 2 * (lrange - 1)
        if (ldepth + delay) % scanner_round == 0:
            yield layer


def severity_score(layers: Iterable[Layer], delay: int = 0) -> int:
    return sum(d * r for d, r in caught_layers(layers, delay))


def target_delay(layers: Iterable[Layer]) -> int:
    # naive solution - still works for small inputs
    layers = list(layers)
    for delay in count(0):
        if not any(caught_layers(layers, delay)):
            return delay


if __name__ == '__main__':
    layers_ = list(load_layers("data/13-input.txt"))
    print(f"part 1: severity score is {severity_score(layers_)}")
    print(f"part 2: smallest delay is {target_delay(layers_)}")
