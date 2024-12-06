from typing import Any, Callable, Iterable, overload

from common.rect import Rect


Pos = tuple[int, int]
PosChar = tuple[Pos, Any]
PosChars = Iterable[PosChar] | dict[Pos, Any]
Blending = Callable[[str, str], str | None]


class Canvas:
    """
    Utility class for drawing ascii pictures:

        >>> c = Canvas()
        >>> _ = c.draw((1, 1), "o")
        >>> _ = c.draw((3, 1), "O")
        >>> c.draw_many(((x, 2), "-") for x in range(1, 4))
        >>> print(c)
        o O
        ---
        >>> c.print(margin=1, empty_char='·')
        ·····
        ·o·O·
        ·---·
        ·····
    """
    def __init__(
        self,
        chars: PosChars = (),
        bounds: Rect | None = None,
        blending: Callable[[str, str], str | None] | None = None,
    ):
        self.chars: dict[Pos, str] = {}
        self.bounds = bounds
        self.blending = blending

        self.draw_many(chars)

    def draw_many(self, chars: PosChars, blending: Blending | None = None) -> None:
        items: Iterable[PosChar] = chars.items() if isinstance(chars, dict) else chars
        for pos, obj in items:
            self._draw_single_char(pos, str(obj), blending)

    def draw(self, pos: Pos, obj: Any, blending: Blending | None = None) -> str:
        text = str(obj)
        if len(text) == 0:
            return ''
        if len(text) == 1:
            return self._draw_single_char(pos, text, blending)

        x_0, y = pos
        return ''.join(
            self._draw_single_char((x, y), char, blending)
            for x, char in enumerate(text, start=x_0)
        )

    def _draw_single_char(self, pos: Pos, drawn_char: str, blending: Blending | None) -> str:
        self._check_bounds(pos)
        assert len(drawn_char) == 1

        if (current_char := self.chars.get(pos)):
            drawn_char = self._blended_char(current_char, drawn_char, blending)

        self.chars[pos] = drawn_char
        return drawn_char

    def _blended_char(
        self,
        current_char: str,
        drawn_char: str,
        custom_blending: Blending | None,
    ) -> str:
        for blend_func in (custom_blending, self.blending):
            if blend_func and (blended := blend_func(current_char, drawn_char)):
                return blended
        return drawn_char

    def _check_bounds(self, pos: Pos) -> None:
        if self.bounds and pos not in self.bounds:
            raise IndexError(f"`pos` must be in bounds {self.bounds} (got {pos!r})")

    def _effective_bounds(self, custom_bounds: Rect | None = None) -> Rect:
        if custom_bounds:
            return custom_bounds
        if self.bounds:
            return self.bounds
        if self.chars:
            return Rect.with_all(self.chars)

        raise ValueError("canvas is empty and bounds are given")

    @overload
    def get(self, pos: Pos, default: str) -> str:
        ...

    @overload
    def get(self, pos: Pos, default: None) -> str | None:
        ...

    def get(self, pos: Pos, default: str | None = None) -> str | None:
        self._check_bounds(pos)
        return self.chars.get(pos, default)

    def __getitem__(self, pos: Pos) -> str:
        self._check_bounds(pos)
        return self.chars[pos]

    def __contains__(self, pos: Pos) -> bool:
        return pos in self.chars

    def __setitem__(self, pos: Pos, obj: Any) -> None:
        self._check_bounds(pos)
        if len(char := str(obj)) != 1:
            raise ValueError(f"`str(obj)` must be 1 character long (was {char!r})")
        self.chars[pos] = obj

    def lines(
        self,
        empty_char: str = ' ',
        bounds: Rect | None = None,
        margin: int = 0,
    ) -> Iterable[str]:
        used_bounds = self._effective_bounds(bounds)
        if margin:
            used_bounds = used_bounds.grow_by(dx=margin, dy=margin)

        return (
            ''.join(self.get((x, y), empty_char) for x in used_bounds.range_x()).rstrip()
            for y in used_bounds.range_y()
        )

    def print(
        self,
        empty_char: str = ' ',
        bounds: Rect | None = None,
        margin: int = 0,
    ) -> None:
        for line in self.lines(empty_char, bounds, margin):
            print(line)

    def render(
        self,
        empty_char: str = ' ',
        bounds: Rect | None = None,
        margin: int = 0,
    ) -> str:
        return "\n".join(self.lines(empty_char, bounds, margin))

    def __str__(self) -> str:
        return self.render()
