from typing import Any, Iterable, Iterator, MutableSet, TypeVar

T = TypeVar('T')


class IdentitySet(MutableSet[T]):
    def __init__(self, iterable: Iterable = ()):
        self.map: dict[int, T] = {}  # id -> object
        self.update(iterable)

    def __len__(self) -> int:  # Sized
        return len(self.map)

    def __iter__(self) -> Iterator[T]:  # Iterable
        return iter(self.map.values())

    def __contains__(self, item: Any) -> bool:  # Container
        return id(item) in self.map

    def add(self, value: T) -> None:  # MutableSet
        self.map[id(value)] = value

    def update(self, iterable: Iterable[T]):
        self.map.update((id(value), value) for value in iterable)

    def discard(self, value: T) -> None:  # MutableSet
        # do not raise en exception if absent
        self.map.pop(id(value), None)

    def __repr__(self) -> str:
        tn = type(self).__name__
        return f'{tn}({list(self)!r})' if self else f'{tn}()'
