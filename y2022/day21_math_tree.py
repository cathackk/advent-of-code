"""
Advent of Code 2022
Day 21: Monkey Math
https://adventofcode.com/2022/day/21
"""

from typing import Iterable

from common.file import relative_path


def part_1(tree: 'Tree', root_monkey: str = 'root') -> int:
    """
    The monkeys are back! You're worried they're going to try to steal your stuff again, but it
    seems like they're just holding their ground and making various monkey noises at you.

    Eventually, one of the elephants realizes you don't speak monkey and comes over to interpret.
    As it turns out, they overheard you talking about trying to find the grove; they can show you
    a shortcut if you answer their **riddle**.

    Each monkey is given a **job**: either to **yell a specific number** or to **yell the result of
    a math operation**. All of the number-yelling monkeys know their number from the start; however,
    the math operation monkeys need to wait for two other monkeys to yell a number, and those two
    other monkeys might **also** be waiting on other monkeys.

    Your job is to **work out the number the monkey named `root` will yell** before the monkeys
    figure it out themselves.

    For example:

        >>> t = tree_from_text('''
        ...     root: pppw + sjmn
        ...     dbpl: 5
        ...     cczh: sllz + lgvd
        ...     zczc: 2
        ...     ptdq: humn - dvpt
        ...     dvpt: 3
        ...     lfqf: 4
        ...     humn: 5
        ...     ljgn: 2
        ...     sjmn: drzm * dbpl
        ...     sllz: 4
        ...     pppw: cczh / lfqf
        ...     lgvd: ljgn * ptdq
        ...     drzm: hmdt - zczc
        ...     hmdt: 32
        ... ''')

    Each line contains the name of a monkey, a colon, and then the job of that monkey:

      - A lone number means the monkey's job is simply to yell that number.
      - A job like `aaaa + bbbb` means the monkey waits for monkeys `aaaa` and `bbbb` to yell each
        of their numbers; the monkey then yells the sum of those two numbers.
      - `aaaa - bbbb` means the monkey yells `aaaa`'s number minus `bbbb`'s number.
      - Job `aaaa * bbbb` will yell `aaaa`'s number multiplied by `bbbb`'s number.
      - Job `aaaa / bbbb` will yell `aaaa`'s number divided by `bbbb`'s number.

    So, in the above example, monkey `drzm` has to wait for monkeys `hmdt` and `zczc` to yell their
    numbers:

        >>> t['drzm']
        ('hmdt', '-', 'zczc')

    Fortunately, both `hmdt` and `zczc` have jobs that involve simply yelling a single number, so
    they do this immediately: `32` and `2`:

        >>> t['hmdt'], t['zczc']
        (32, 2)

    Monkey `drzm` can then yell its number by finding `32` minus `2`: **`30`**.

        >>> tree_eval(t, 'hmdt'), tree_eval(t, 'zczc')
        (32, 2)
        >>> op_eval(32, '-', 2)
        30
        >>> tree_eval(t, 'drzm')
        30

    Then, monkey `sjmn` has one of its numbers (`30`, from monkey `drzm`), and already has its other
    number, `5`, from `dbpl`. This allows it to yell its own number by finding `30` multiplied by
    `5`: **`150`**.

        >>> t['sjmn']
        ('drzm', '*', 'dbpl')
        >>> tree_eval(t, 'sjmn')
        150

    This process continues until root yells a number: **`152`**.

        >>> tree_eval(t, 'root')
        152

    However, your actual situation involves considerably more monkeys.
    **What number will the monkey named `root` yell?**

        >>> part_1(t)
        part 1: monkey 'root' yells 152
        152
    """

    result = tree_eval(tree, root_monkey)

    print(f"part 1: monkey {root_monkey!r} yells {result}")
    return result


def part_2(tree: 'Tree', root_monkey: str = 'root', human: str = 'humn') -> int:
    """
    Due to some kind of monkey-elephant-human mistranslation, you seem to have misunderstood a few
    key details about the riddle.

    First, you got the wrong job for the monkey named `root`; specifically, you got the wrong math
    operation. The correct operation for monkey `root` should be `=`, which means that it still
    listens for two numbers (from the same two monkeys as before), but now checks that the two
    numbers **match**.

    Second, you got the wrong monkey for the job starting with `humn:`. It isn't a monkey - it's
    **you**. Actually, you got the job wrong, too: you need to figure out what number you need to
    yell so that root's equality check passes. (The number that appears after `humn:` in your input
    is now irrelevant.)

    In the above example, the number you need to yell to pass root's equality test is **`301`**.
    (This causes `root` to get the same number, `150`, from both of its monkeys.)

        >>> t_original = tree_from_file('data/21-example.txt')
        >>> t2 = dict(t_original)
        >>> tree_op_replace(t2, 'root', op='-')
        >>> tree_backeval(t2, root='root', root_result=0, variable='humn')
        301

    **What number do you yell to pass root's equality test?**

        >>> part_2(t_original)
        part 2: you need to yell 301
        301
    """

    tree = dict(tree)
    tree_op_replace(tree, root_monkey, op='-')
    result = tree_backeval(tree, root=root_monkey, root_result=0, variable=human)

    print(f"part 2: you need to yell {result}")
    return result


Op = str
Instr = tuple[str, Op, str]
NodeValue = int | Instr
Tree = dict[str, NodeValue]


def op_eval(value_1: int, op: str, value_2: int) -> int:
    match op:
        case '+':
            return value_1 + value_2
        case '-':
            return value_1 - value_2
        case '*':
            return value_1 * value_2
        case '/':
            if value_1 % value_2 != 0:
                raise ValueError(value_1, '/', value_2)
            return value_1 // value_2
        case _:
            raise ValueError(op)


def tree_eval(tree: Tree, root: str) -> int:
    root_value = tree[root]
    if isinstance(root_value, int):
        return root_value

    assert isinstance(root_value, tuple)
    name_1, op, name_2 = root_value
    return op_eval(
        value_1=tree_eval(tree, root=name_1),
        op=op,
        value_2=tree_eval(tree, root=name_2),
        )


def tree_op_replace(tree: Tree, name: str, op: Op) -> None:
    value = tree[name]
    assert isinstance(value, tuple)
    name_1, _, name_2 = value
    tree[name] = (name_1, op, name_2)


OP_INV = {'+': '-', '-': '+', '*': '/', '/': '*'}


def tree_backeval(tree: Tree, root: str, root_result: int, variable: str) -> int:
    root_value = tree[root]
    if root == variable:
        assert isinstance(root_value, int)
        return root_result

    assert isinstance(root_value, tuple)
    name_1, op, name_2 = root_value

    if tree_contains(tree, name_1, variable):
        value_1 = tree_eval(tree, name_2)
        result_1 = op_eval(root_result, OP_INV[op], value_1)
        return tree_backeval(tree, root=name_1, root_result=result_1, variable=variable)

    elif tree_contains(tree, name_2, variable):
        value_1 = tree_eval(tree, name_1)

        if op in ('+', '*'):
            result_2 = op_eval(root_result, OP_INV[op], value_1)
        elif op in ('-', '/'):
            result_2 = op_eval(value_1, op, root_result)
        else:
            raise ValueError(op)

        return tree_backeval(tree, root=name_2, root_result=result_2, variable=variable)

    else:
        raise ValueError(f"{variable!r} not in tree {root!r}")


def tree_contains(tree: Tree, root: str, searched: str) -> bool:
    if root == searched:
        return True

    root_value = tree[root]
    if isinstance(root_value, int):
        return False

    assert isinstance(root_value, tuple)
    name_1, _, name_2 = root_value
    return tree_contains(tree, name_1, searched) or tree_contains(tree, name_2, searched)


def tree_from_file(fn: str) -> Tree:
    return dict(nodes_from_lines(open(relative_path(__file__, fn))))


def tree_from_text(text: str) -> Tree:
    return dict(nodes_from_lines(text.strip().splitlines()))


def nodes_from_lines(lines: Iterable[str]) -> Iterable[tuple[str, NodeValue]]:
    for line in lines:
        name, value = line.strip().split(': ')
        if value.isdigit():
            yield name, int(value)
        else:
            val1, op, val2 = value.split(' ')
            yield name, (val1, op, val2)


def main(input_fn: str = 'data/21-input.txt') -> tuple[int, int]:
    tree = tree_from_file(input_fn)
    result_1 = part_1(tree)
    result_2 = part_2(tree)
    return result_1, result_2


if __name__ == '__main__':
    main()
