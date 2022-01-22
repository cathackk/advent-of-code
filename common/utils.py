from typing import Any
from typing import TypeVar

T = TypeVar('T')


# pylint: disable=invalid-name
def ro(pos: tuple[int, int]) -> tuple[int, int]:
    # reading order -> y matters more than x
    x, y = pos
    return y, x


def assert_single_not_none(**kwargs: T) -> tuple[str, T]:
    """
        >>> assert_single_not_none(x=1, y=None, z=None)
        ('x', 1)
        >>> assert_single_not_none(x=1, y=2, z=None)
        Traceback (most recent call last):
        ...
        AssertionError: multiple keys were not None: x=1, y=2
        >>> assert_single_not_none(x=None, y=None, z=None)
        Traceback (most recent call last):
        ...
        AssertionError: all keys were None: x=None, y=None, z=None
    """
    not_none_count = sum(v is not None for v in kwargs.values())

    if not_none_count == 1:
        return [(k, v) for k, v in kwargs.items() if v is not None][0]

    elif not_none_count == 0:
        items_text = ", ".join(f"{k}=None" for k in kwargs)
        raise AssertionError(f"all keys were None: {items_text}")

    else:  # not_none_count > 1
        items_text = ", ".join(f"{k}={v!r}" for k, v in kwargs.items() if v is not None)
        raise AssertionError(f"multiple keys were not None: {items_text}")


def some(item: T | None) -> T:
    assert item is not None
    return item


def sorted_keys(d: dict[str, Any]) -> dict[str, Any]:
    """
    Useful in doctests:

        >>> sorted_keys({'x': 1, 'a': 2, 'y': 3, 'b': 4, 'w':5})
        {'a': 2, 'b': 4, 'w': 5, 'x': 1, 'y': 3}
    """

    return dict(sorted((k, v) for k, v in d.items()))
