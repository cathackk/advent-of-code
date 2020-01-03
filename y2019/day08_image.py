from typing import Callable
from typing import Iterable
from typing import List


Layer = List[List[int]]


BLACK = 0
WHITE = 1
TRANSPARENT = 2


def load_data(fn="data/08-image.txt") -> List[int]:
    with open(fn) as f:
        return [int(v) for line in f for v in line.strip()]


def create_image_layers(data, width=25, height=6) -> Iterable[Layer]:
    g = iter(data)
    while True:
        yield [[next(g) for _ in range(width)] for _ in range(height)]


def pixel_counter(counted: int) -> Callable[[Layer], int]:
    return lambda layer: sum(1 for row in layer for pixel in row if pixel == counted)


def combine_layers(layers: Iterable[Layer]) -> Layer:

    def combine_pixels(now, prev):
        return now if prev == TRANSPARENT else prev

    result = None

    for layer in layers:
        if result is None:
            result = layer
        else:
            result = [
                [
                    combine_pixels(p, r)
                    for p, r in zip(row, result_row)
                ]
                for row, result_row in zip(layer, result)
            ]

    return result


def draw_layer(layer: Layer):
    d = {WHITE: '#', BLACK: ' ', TRANSPARENT: '?'}
    print('\n'.join(''.join(d[p] for p in row) for row in layer))
    # print('\n'.join(''.join(str(p) for p in row) for row in layer))


def part1():
    layers = list(create_image_layers(load_data()))

    # layer with the fewest zeroes
    layer = min(layers, key=pixel_counter(0))
    ones = pixel_counter(1)(layer)
    twos = pixel_counter(2)(layer)
    print(f"{ones} * {twos} = {ones * twos}")


def part2():
    layers = list(create_image_layers(load_data()))
    image = combine_layers(layers)
    draw_layer(image)


def test():
    data = [int(v) for v in '0222112222120000']
    layers = create_image_layers(data, 2, 2)
    image = combine_layers(layers)
    draw_layer(image)


if __name__ == '__main__':
    # part1()
    part2()
    # test()
