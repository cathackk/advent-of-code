from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import TypeVar


T = TypeVar('T')


class MultiBuffer:
    def __init__(self, scoring: Callable[[T], int], items: Iterable[T] = None):
        self._scoring = scoring
        self._buffers: Dict[int, List[T]] = dict()
        self._items_count = 0
        if items is not None:
            self.extend(items)

    def __len__(self):
        return self._items_count

    def __bool__(self):
        return self._items_count > 0

    def __iter__(self) -> Iterable[tuple[int, T]]:
        return (
            (score, item)
            for score, items in self._buffers.items()
            for item in items
        )

    def pop(self, index: int = -1) -> T:
        return self.pop_max(index)

    def pop_max(self, index: int = -1) -> T:
        score = max(self._buffers.keys())
        return self.pop_by_score(score, index)

    def pop_min(self, index: int = -1) -> T:
        score = min(self._buffers.keys())
        return self.pop_by_score(score, index)

    def pop_by_score(self, score: int, index: int = -1) -> T:
        buffer = self._buffers[score]
        item = buffer.pop(index)
        if not buffer:
            del self._buffers[score]
        self._items_count -= 1
        return item

    def append(self, item: T):
        score = self._scoring(item)
        if score not in self._buffers:
            self._buffers[score] = []
        self._buffers[score].append(item)
        self._items_count += 1

    def extend(self, items: Iterable[T]):
        for item in items:
            self.append(item)


def test():
    mb = MultiBuffer(lambda s: len(s))

    mb.append('dog')
    mb.extend(['cat', 'monkey', 'antelope', 'ox', 'spider'])
    assert len(mb) == 6

    assert mb.pop_min() == 'ox'
    assert len(mb) == 5

    assert mb.pop_min() == 'cat'
    assert len(mb) == 4

    assert mb.pop_max() == 'antelope'
    assert len(mb) == 3

    assert mb.pop_min() == 'dog'
    assert mb.pop_min() == 'spider'
    assert len(mb) == 1
    assert bool(mb) is True

    assert mb.pop_min() == 'monkey'
    assert len(mb) == 0
    assert bool(mb) is False
