import sys
from typing import Any
from typing import Callable
from typing import Iterable
from typing import TypeVar


T = TypeVar('T')


def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


def ilog(
        items: Iterable[T],
        formatter: Callable[[int, T], str] = None,
        every: int = 1
) -> Iterable[T]:
    for index, item in enumerate(items):
        if index % every == 0:
            if formatter:
                eprint(formatter(index, item))
            else:
                eprint('>', index, item)
        yield item


def create_logger(debug: bool = False) -> Callable[[Any], None]:
    if debug:
        def log(*args, **kwargs):
            eprint(*args, **kwargs)
        return log
    else:
        def nolog(_):
            pass
        return nolog
