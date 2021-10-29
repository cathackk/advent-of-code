from collections import Counter
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import List
from typing import Optional


class Mobile:
    def __init__(self, name: str, weight: int, children: Iterable['Mobile']):
        self.name = name
        self.weight = weight
        self.children = list(children)
        self.total_weight = int(self.weight + sum(c.total_weight for c in self.children))

    def total_count(self) -> int:
        return 1 + sum(m.total_count() for m in self.children)

    def is_balanced(self) -> bool:
        if len(self.children) >= 2:
            first_child_weight = self.children[0].total_weight
            return all(child.total_weight == first_child_weight for child in self.children[1:])
        else:
            return True

    def find_disbalanced(self) -> Optional[tuple['Mobile', List['Mobile']]]:
        if len(self.children) < 2:
            # 0 or 1 children -> no disbalanced
            return None

        weights = [child.total_weight for child in self.children]
        weights_cnt = Counter(weights)

        if len(weights_cnt) == 1:
            # all weigh the same -> balanced
            return None

        elif len(weights_cnt) == 2:
            (w_ok, cnt_ok), (w_wrong, cnt_wrong) = weights_cnt.most_common(2)
            if cnt_ok > 1 and cnt_wrong == 1:
                wrong_child = self.children[weights.index(w_wrong)]
                ok_children = [self.children[i] for i, w in enumerate(weights) if w == w_ok]
                return wrong_child.find_disbalanced() or (wrong_child, ok_children)

        raise ValueError(f"cannot determine disbalanced with weights {weights}")

    def __repr__(self):
        return f'{type(self).__name__}({self.name!r}, {self.weight}, {self.children})'

    def __str__(self):
        bal_chr = '' if self.is_balanced() else '*'
        return f'{bal_chr}{self.name} ({self.total_weight})'

    def draw(self):
        for line in self._lines():
            print(line)

    def _lines(self) -> Generator[str, None, None]:
        s = ' ' + str(self) + ' '

        if not self.children:
            yield s
            return

        pad = ' ' * len(s)

        for c, child in enumerate(self.children):
            sublines = child._lines()
            if c == 0:
                yield s + Mobile._branch_chr(c, len(self.children)) + next(sublines)
            for s, subline in enumerate(sublines):
                yield pad + Mobile._branch_chr(c, len(self.children), s) + subline

    @staticmethod
    def _branch_chr(child_index: int, children_count: int, subline_index: int = None) -> str:
        assert children_count > 0
        if subline_index is None:
            if children_count == 1:
                return '─'
            elif child_index == 0:
                return '┬'
            elif child_index < children_count - 1:
                return '├'
            else:
                return '└'
        else:
            if subline_index == 0 and child_index > 0:
                if child_index < children_count - 1:
                    return '├'
                else:
                    return '└'
            else:
                if child_index < children_count - 1:
                    return '│'
                else:
                    return ' '


def load_mobile(fn: str) -> Mobile:
    protos: Dict[str, tuple[int, List[str]]] = dict()
    depends_on: Dict[str, str] = dict()

    for line in open(fn):
        line = line.strip()
        # enurd (528) -> gpaljor, ncuksjv, ozdrm, qkmsfo
        data_part, children_part = line.split(' -> ') if ' -> ' in line else (line, None)
        name, weight = data_part[:-1].split(' (')
        children = children_part.split(', ') if children_part else []
        protos[name] = (int(weight), children)
        for child in children:
            depends_on[child] = name

    return create_mobile(find_root(depends_on), protos)


def create_mobile(name: str, protos: Dict[str, tuple[int, List[str]]]) -> Mobile:
    weight, children_names = protos[name]
    return Mobile(
        name=name,
        weight=weight,
        children=(create_mobile(cname, protos) for cname in children_names)
    )


def find_root(depends_on: Dict[str, str]) -> str:
    key = next(iter(depends_on.keys()))
    while key in depends_on:
        key = depends_on[key]
    return key


def part_1(mobile: Mobile) -> str:
    print(f"part 1: bottom program is named {mobile.name}")
    return mobile.name


def part_2(mobile: Mobile) -> int:
    disbalanced = mobile.find_disbalanced()
    if disbalanced:
        wrong, oks = disbalanced
        ok1 = oks[0]
        weight_delta = ok1.total_weight - wrong.total_weight
        adjusted_weight = wrong.weight + weight_delta
        print(
            f"part 2: if {wrong.name} weight was {adjusted_weight} ({weight_delta:+}), "
            f"mobile would be balanced"
        )
        return adjusted_weight
    else:
        raise ValueError("no disbalance found!")


if __name__ == '__main__':
    mobile_ = load_mobile("data/07-input.txt")
    mobile_.draw()
    part_1(mobile_)
    part_2(mobile_)
