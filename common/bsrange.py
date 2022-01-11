from typing import Optional


class BSRange:
    def __init__(self, lower: Optional[int], upper: Optional[int]):
        self._lower = lower
        self._upper = upper

    def __repr__(self):
        return f"{type(self).__name__}({self.lower}, {self.upper})"

    def __str__(self):
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
    def lower(self) -> Optional[int]:
        return self._lower

    @lower.setter
    def lower(self, lower: int):
        if self.has_upper():
            assert lower < self.upper
        self._lower = lower

    def has_upper(self) -> bool:
        return self._upper is not None

    @property
    def upper(self) -> Optional[int]:
        return self._upper

    @upper.setter
    def upper(self, upper: int):
        if self.has_lower():
            assert self.lower < upper
        self._upper = upper

    def has_single_value(self) -> bool:
        return self.has_lower() and self.has_upper() and self.lower == self.upper - 1

    @property
    def single_value(self) -> Optional[int]:
        return self.lower if self.has_single_value() else None

    def is_bounded(self) -> bool:
        return self.has_lower() and self.has_upper()

    @property
    def mid(self) -> Optional[int]:
        return (self.lower + self.upper) // 2 if self.is_bounded() else None
