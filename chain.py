from typing import Any
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple


class Link:
    __slots__ = ['value', 'prev_link', 'next_link']

    def __init__(self, value, prev_link: 'Link' = None, next_link: 'Link' = None):
        self.value = value
        self.prev_link = prev_link
        self.next_link = next_link

    @classmethod
    def build_chain(cls, items: Iterable[Any]) -> Tuple['Link', 'Link']:
        items = iter(items)
        first_link = last_link = cls(next(items))
        for item in items:
            last_link = cls(item).connect_to(prev_link=last_link)
        return first_link, last_link

    def connect_to(self, prev_link: 'Link' = None, next_link: 'Link' = None) -> 'Link':
        if prev_link is not None:
            self.prev_link = prev_link
            self.prev_link.next_link = self
        if next_link is not None:
            self.next_link = next_link
            self.next_link.prev_link = self
        return self

    def insert_after(self, value) -> 'Link':
        return type(self)(value).connect_to(prev_link=self, next_link=self.next_link)

    def insert_before(self, value) -> 'Link':
        return type(self)(value).connect_to(prev_link=self.prev_link, next_link=self)

    def disconnect(self) -> 'Link':
        if self.prev_link is not None:
            self.prev_link.connect_to(next_link=self.next_link)
        elif self.next_link is not None:
            self.next_link.connect_to(prev_link=None)
        self.prev_link = self.next_link = None
        return self

    def forward_count(self) -> int:
        link, count = self, 0
        while link.next_link is not None:
            link = link.next_link
            count += 1
        return count

    def backward_count(self) -> int:
        link, count = self, 0
        while link.prev_link is not None:
            link = link.prev_link
            count += 1
        return count

    def follow(self, steps: int) -> 'Link':
        link = self
        for _ in range(abs(steps)):
            link = link.next_link if steps > 0 else link.prev_link
        return link

    def _sub_repr(self, sublink: Optional['Link']) -> str:
        if sublink is None:
            return repr(None)
        elif sublink is self:
            return 'self'
        else:
            return f'{type(sublink).__name__}({sublink.value!r}, ...)'

    def __repr__(self):
        return (
            f'{type(self).__name__}({self.value!r}, '
            f'prev_link={self._sub_repr(self.prev_link)}, '
            f'next_link={self._sub_repr(self.next_link)})'
        )

    def __str__(self):
        return str(self.value)


class Circle:
    def __init__(self, items: List[Any]):
        assert len(items) > 0
        self._current_link, last_link = Link.build_chain(items)
        self._current_link.connect_to(prev_link=last_link)
        self._length = len(items)

    def current(self) -> Any:
        return self._current_link.value

    def shift(self, steps: int):
        self._current_link = self._current_link.follow(steps)

    def insert(self, steps: int, value: Any):
        self.shift(steps)
        self._current_link = self._current_link.insert_after(value)
        self._length += 1

    def pop(self, steps: int) -> Any:
        self.shift(steps + 1)
        removed_link = self._current_link.prev_link
        removed_link.disconnect()
        self._length -= 1
        return removed_link.value

    def __str__(self):
        def g():
            link = self._current_link
            yield str(link)
            link = link.next_link
            while link != self._current_link:
                yield str(link)
                link = link.next_link
        return ' -> '.join(g()) + ' -> ...'

    def __len__(self):
        return self._length
