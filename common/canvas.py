from typing import Any, Callable, Iterable

from common.rect import Rect


Pos = tuple[int, int]
PosChar = tuple[Pos, Any]
PosChars = Iterable[PosChar] | dict[Pos, Any]
Blending = Callable[[str, str], str | None]

# TODO: utilize in more puzzles


class Canvas:
    """
    Utility class for drawing ascii pictures:

        >>> c = Canvas(bounds=Rect.at_origin(5, 4))
        >>> _ = c.draw((1, 1), "o")
        >>> _ = c.draw((3, 1), "O")
        >>> c.draw_many(((x, 2), "-") for x in range(1, 4))
        >>> print(c)
        ·····
        ·o·O·
        ·---·
        ·····
    """
    def __init__(
        self,
        chars: PosChars = (),
        default_char: str = '·',
        bounds: Rect | None = None,
        blending: Callable[[str, str], str | None] | None = None,
    ):
        self.chars: dict[Pos, str] = {}
        self.default_char = default_char
        self.bounds = bounds
        self.blending = blending

        self.draw_many(chars)

    def draw_many(self, chars: PosChars, blending: Blending | None = None) -> None:
        items: Iterable[PosChar] = chars.items() if isinstance(chars, dict) else chars
        for pos, char in items:
            self._draw_single_char(pos, char, blending)

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
        assert len(drawn_char) == 1

        if self.bounds and pos not in self.bounds:
            raise ValueError(f"`pos` must be in bounds {self.bounds} (got {pos!r})")

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

    def __str__(self) -> str:
        if not self.bounds and not self.chars:
            raise ValueError("canvas is empty")

        bounds = self.bounds or Rect.with_all(self.chars)
        return '\n'.join(
            ''.join(self.chars.get((x, y), self.default_char) for x in bounds.range_x())
            for y in bounds.range_y()
        )
