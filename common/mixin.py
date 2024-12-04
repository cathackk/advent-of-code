from abc import ABC, abstractmethod
from typing import Iterator


class Orderable(ABC):
    @abstractmethod
    def __iter__(self) -> Iterator:
        ...

    def __hash__(self) -> int:
        return hash(repr(self))

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and tuple(self) == tuple(other)

    def __gt__(self, other) -> bool:
        return isinstance(other, type(self)) and tuple(self) > tuple(other)
