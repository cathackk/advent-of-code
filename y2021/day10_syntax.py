"""
Advent of Code 2021
Day 10: Syntax Scoring
https://adventofcode.com/2021/day/10
"""

from dataclasses import dataclass
from typing import ClassVar
from typing import Iterable

from common.utils import relative_path


def part_1(lines: Iterable[str]) -> int:
    r"""
    The navigation subsystem syntax is made of several lines containing **chunks**. There are one or
    more chunks on each line, and chunks contain zero or more other chunks. Adjacent chunks are not
    separated by any delimiter; if one chunk stops, the next chunk (if any) can immediately start.
    Every chunk must **open** and **close** with one of four legal pairs of matching characters:

        >>> CHUNK_PAIRS
        ['()', '[]', '{}', '<>']

    So, `()` is a legal chunk that contains no other chunks, as is `[]`:

        >>> validate('()')
        >>> validate('[]')

    More complex but valid chunks include:

        >>> validate('([])')
        >>> validate('{()()()}')
        >>> validate('<([{}])>')
        >>> validate('[<>({}){}[([])<>]]')
        >>> validate('(((((((((())))))))))')

    Some lines are **incomplete**, but others are **corrupted**. Find and discard the corrupted
    lines first.

    A corrupted line is one where a chunk **closes with the wrong character** - that is, where
    the characters it opens and closes with do not form one of the four legal pairs listed above.

    Examples of corrupted chunks include:

        >>> print(validate('(]'))
        '(]' - Expected ')', but found ']' instead.
        >>> print(validate('{()()()>'))
        '{()()()>' - Expected '}', but found '>' instead.
        >>> print(validate('(((()))}'))
        '(((()))}' - Expected ')', but found '}' instead.
        >>> print(validate('<([]){()}[{}])'))
        '<([]){()}[{}])' - Expected '>', but found ')' instead.

    For example, consider the following navigation subsystem:

        >>> example_lines = lines_from_text('''
        ...     [({(<(())[]>[[{[]{<()<>>
        ...     [(()[<>])]({[<{<<[]>>(
        ...     {([(<{}[<>[]}>{[]{[(<()>
        ...     (((({<>}<{<{<>}{[]{[]{}
        ...     [[<[([]))<([[{}[[()]]]
        ...     [{[{({}]{}}([{[{{{}}([]
        ...     {<[[]]>}<{[{[{[]{()[[[]
        ...     [<(<(<(<{}))><([]([]()
        ...     <{([([[(<>()){}]>(<<{{
        ...     <{([{{}}[<[[[<>{}]]]>[]]
        ... ''')

    Some of the lines aren't corrupted, just incomplete; you can ignore these lines for now.

        >>> complete_lines = [line for line in example_lines if is_complete(line)]
        >>> len(complete_lines)
        5

    The remaining five lines are corrupted:

        >>> print('\n'.join(str(validate(line)) for line in complete_lines))
        '{([(<{}[<>[]}>{[]{[(<()>' - Expected ']', but found '}' instead.
        '[[<[([]))<([[{}[[()]]]' - Expected ']', but found ')' instead.
        '[{[{({}]{}}([{[{{{}}([]' - Expected ')', but found ']' instead.
        '[<(<(<(<{}))><([]([]()' - Expected '>', but found ')' instead.
        '<{([([[(<>()){}]>(<<{{' - Expected ']', but found '>' instead.

    Stop at the first incorrect closing character on each corrupted line.

    Did you know that syntax checkers actually have contests to see who can get the high score for
    syntax errors in a file? It's true! To calculate the syntax error score for a line, take the
    **first illegal character** on the line and look it up in the following table:

        >>> SyntaxValidationError.SCORING
        {')': 3, ']': 57, '}': 1197, '>': 25137}

    In the above example, an illegal `)` was found twice (`2*3 = 6` points), an illegal `]` was
    found once (`57` points), an illegal `}` was found once (`1197` points), and an illegal `>` was
    found once (`25137` points). So, the total syntax error score for this file is
    `6+57+1197+25137 = 26397` points!

        >>> syntax_score(complete_lines)
        26397

    Find the first illegal character in each corrupted line of the navigation subsystem.
    **What is the total syntax error score for those errors?**

        >>> part_1(example_lines)
        part 1: total score of syntactically invalid lines is 26397
        26397
    """

    result = syntax_score(lines)

    print(f"part 1: total score of syntactically invalid lines is {result}")
    return result


def part_2(lines: Iterable[str]) -> int:
    r"""
    Now, discard the corrupted lines. The remaining lines are **incomplete**.

    Incomplete lines don't have any incorrect characters - instead, they're missing some closing
    characters at the end of the line. To repair the navigation subsystem, you just need to figure
    out **the sequence of closing characters** that complete all open chunks in the line.

    You can only use closing characters (`)`, `]`, `}`, or `>`), and you must add them in
    the correct order so that only legal pairs are formed and all chunks end up closed.

    In the example above, there are five incomplete lines:

        >>> example_lines = lines_from_file('data/10-example.txt')
        >>> incomplete_errors = [
        ...     err for line in example_lines
        ...     if isinstance(err := validate(line), IncompleteValidationError)
        ... ]
        >>> len(incomplete_errors)
        5
        >>> print('\n'.join(str(err) for err in incomplete_errors))
        '[({(<(())[]>[[{[]{<()<>>' - Complete by adding '}}]])})]'.
        '[(()[<>])]({[<{<<[]>>(' - Complete by adding ')}>]})'.
        '(((({<>}<{<{<>}{[]{[]{}' - Complete by adding '}}>}>))))'.
        '{<[[]]>}<{[{[{[]{()[[[]' - Complete by adding ']]}}]}]}>'.
        '<{([{{}}[<[[[<>{}]]]>[]]' - Complete by adding '])}>'.

    Did you know that autocomplete tools **also** have contests? It's true! The score is determined
    by considering the completion string character-by-character. Start with a total score of `0`.
    Then, for each character, multiply the total score by `5` and then increase the total score by
    the point value given for the character in the following table:

        >>> IncompleteValidationError.SCORING
        {')': 1, ']': 2, '}': 3, '>': 4}

    The five lines' completion strings have total scores as follows:

        >>> scores = {err.closing: err.score for err in incomplete_errors}
        >>> scores
        {'}}]])})]': 288957, ')}>]})': 5566, '}}>}>))))': 1480781, ']]}}]}]}>': 995444, '])}>': 294}

    Autocomplete tools are an odd bunch: the winner is found by **sorting** all of the scores and
    then taking the middle score. (There will always be an odd number of scores to consider.)
    In this example, the middle score is `288957` because there are the same number of scores
    smaller and larger than it.

        >>> sorted(scores.values())[2]
        288957

    Find the completion string for each incomplete line, score the completion strings, and sort
    the scores. **What is the middle score?**

        >>> part_2(example_lines)
        part 2: median score of incomplete lines is 288957
        288957
    """

    result = incompletion_score(lines)

    print(f"part 2: median score of incomplete lines is {result}")
    return result


CHUNK_PAIRS = ['()', '[]', '{}', '<>']
OPENING, CLOSING = zip(*CHUNK_PAIRS)
O2C = dict(CHUNK_PAIRS)


@dataclass()
class SyntaxValidationError:
    line: str
    expected: str
    actual: str
    SCORING: ClassVar[dict[str, int]] = {')': 3, ']': 57, '}': 1197, '>': 25137}

    def __str__(self) -> str:
        return f'{self.line!r} - Expected {self.expected!r}, but found {self.actual!r} instead.'

    @property
    def score(self) -> int:
        return self.SCORING[self.actual]


@dataclass()
class IncompleteValidationError:
    line: str
    extra: str
    SCORING: ClassVar[dict[str, int]] = {')': 1, ']': 2, '}': 3, '>': 4}

    def __str__(self) -> str:
        return f'{self.line!r} - Complete by adding {self.closing!r}.'

    @property
    def closing(self) -> str:
        return ''.join(O2C[o] for o in reversed(self.extra))

    @property
    def score(self) -> int:
        total = 0
        for c in self.closing:
            total = total * 5 + self.SCORING[c]
        return total


def validate(line: str) -> SyntaxValidationError | IncompleteValidationError | None:
    stack = []
    for char in line:
        if char in OPENING:
            stack.append(char)
        elif char in CLOSING:
            opening = stack.pop()
            expected_closing = O2C[opening]
            if char != expected_closing:
                return SyntaxValidationError(line, expected=expected_closing, actual=char)
        else:
            raise ValueError(f'unexpected char {char!r}')

    if stack:
        return IncompleteValidationError(line, extra=''.join(stack))

    return None


def is_complete(line: str) -> bool:
    return not isinstance(validate(line), IncompleteValidationError)


def syntax_score(lines: Iterable[str]) -> int:
    return sum(
        err.score
        for line in lines
        if isinstance(err := validate(line), SyntaxValidationError)
    )


def incompletion_score(lines: Iterable[str]) -> int:
    scores = sorted(
        err.score
        for line in lines
        if isinstance(err := validate(line), IncompleteValidationError)
    )
    assert len(scores) % 2 == 1
    middle_index = len(scores) // 2
    return scores[middle_index]


def lines_from_text(text: str) -> list[str]:
    return [line.strip() for line in text.strip().split('\n')]


def lines_from_file(fn: str) -> list[str]:
    return [line.strip() for line in open(relative_path(__file__, fn))]


if __name__ == '__main__':
    lines_ = lines_from_file('data/10-input.txt')
    part_1(lines_)
    part_2(lines_)
