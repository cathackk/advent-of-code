from typing import Optional


class BSRange:
    def __init__(self, lower: Optional[int], upper: Optional[int]):
        self._lower = lower
        self._upper = upper

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.lower}, {self.upper})"

    def __str__(self) -> str:
        if self.is_bounded():
            return f"[{self.lower} .. {self.upper}]"
        elif self.has_lower():
            return f"[{self.lower} ...]"
        elif self.has_upper():
            return f"[... {self.upper}]"
        else:
            return "[...]"

    def has_lower(self) -> bool:
        return self._lower is not None

    @property
    def lower(self) -> int:
        if self._lower is None:
            raise ValueError(f"{self} has no lower bound")

        return self._lower

    @lower.setter
    def lower(self, lower: int):
        if self._upper is not None:
            assert lower < self._upper
        self._lower = lower

    def has_upper(self) -> bool:
        return self._upper is not None

    @property
    def upper(self) -> int:
        if self._upper is None:
            raise ValueError(f"{self} has no upper bound")

        return self._upper

    @upper.setter
    def upper(self, upper: int):
        if self._lower is not None:
            assert self._lower < upper
        self._upper = upper

    def has_single_value(self) -> bool:
        return (
            self._lower is not None and
            self._upper is not None and
            self._lower == self._upper - 1
        )

    @property
    def single_value(self) -> int:
        if not self.has_single_value():
            raise ValueError(f"{self} doesn't have a single value")

        return self.lower

    def is_bounded(self) -> bool:
        return self.has_lower() and self.has_upper()

    @property
    def mid(self) -> int:
        return (self.lower + self.upper) // 2
