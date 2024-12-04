from typing import Any, Iterable, Iterator, Self

from common.utils import some


class Link:
    __slots__ = ['value', 'prev_link', 'next_link']

    def __init__(self, value, prev_link: Self = None, next_link: Self = None):
        self.value = value
        self.prev_link = prev_link
        self.next_link = next_link

    @classmethod
    def build_chain(cls, items: Iterable[Any]) -> tuple[Self, Self, int]:
        items = iter(items)

        try:
            first_link = last_link = cls(next(items))
            count = 1
        except StopIteration as stop:
            raise ValueError("build_chain() arg is an empty sequence") from stop

        for item in items:
            last_link = cls(item).connect_to(prev_link=last_link)
            count += 1

        return first_link, last_link, count

    def connect_to(self, prev_link: Self = None, next_link: Self = None) -> Self:
        if prev_link is not None:
            self.prev_link = prev_link
            self.prev_link.next_link = self
        if next_link is not None:
            self.next_link = next_link
            self.next_link.prev_link = self
        return self

    def insert_after(self, value) -> Self:
        return type(self)(value).connect_to(prev_link=self, next_link=self.next_link)

    def insert_before(self, value) -> Self:
        return type(self)(value).connect_to(prev_link=self.prev_link, next_link=self)

    def disconnect(self) -> Self:
        if self.prev_link is not None:
            self.prev_link.next_link = self.next_link
        if self.next_link is not None:
            self.next_link.prev_link = self.prev_link
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

    def follow(self, steps: int) -> Self | None:
        link: Self | None = self

        for _ in range(abs(steps)):
            if link is None:
                raise ValueError("reached end of chain")

            link = link.next_link if steps > 0 else link.prev_link

        return link

    def _sub_repr(self, sublink: Self | None) -> str:
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

    def __hash__(self):
        return hash(self.value)

    def __iter__(self):
        head = self
        while True:
            yield head.value
            head = head.next_link
            if head is self or head is None:
                return


class Circle:
    def __init__(self, items: Iterable[Any]):
        self.current_link, last_link, self.length = Link.build_chain(items)
        self.current_link.connect_to(prev_link=last_link)

    def current(self) -> Any:
        return self.current_link.value

    def _follow(self, steps: int) -> Link | None:
        steps = steps % self.length
        if steps > self.length // 2:
            steps -= self.length

        return self.current_link.follow(steps)

    def __getitem__(self, steps: int) -> Any:
        return some(self._follow(steps)).value

    def shift(self, steps: int):
        self.current_link = some(self._follow(steps))

    def shift_to_value(self, value: Any):
        try:
            self.current_link = next(link for link in self.links() if link.value == value)
        except StopIteration as not_found:
            raise ValueError(f"{value} is not in the circle") from not_found

    def insert(self, steps: int, value: Any):
        self.shift(steps)
        self.current_link = self.current_link.insert_after(value)
        self.length += 1

    def pop(self, steps: int) -> Any:
        self.shift(steps + 1)
        removed_link = some(self.current_link.prev_link)
        removed_link.disconnect()
        self.length -= 1
        return removed_link.value

    def links(self) -> Iterator[Link]:
        link = self.current_link
        while True:
            yield link
            if link.next_link is None:
                raise ValueError(f"broken link: {link}, next=None, prev={link.prev_link}")
            link = some(link.next_link)
            if link is self.current_link:
                break

    def __iter__(self) -> Iterator:
        return (link.value for link in self.links())

    def __str__(self):
        return ' -> '.join(str(value) for value in self) + ' -> ...'

    def __len__(self):
        return self.length
