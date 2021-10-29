from typing import Iterable


Link = tuple[int, list[int]]
Group = set[int]


def load_links(fn: str) -> Iterable[Link]:
    for line in open(fn):
        # 1977 <-> 197, 879, 1237
        source, targets = line.strip().split(' <-> ')
        yield int(source), [int(v) for v in targets.split(', ')]


def create_groups(links: Iterable[Link]) -> dict[int, Group]:
    groups: dict[int, Group] = dict()

    for source, targets in links:
        for target in targets:
            gs, gt = groups.get(source), groups.get(target)
            if gs and gt:
                if gs is not gt:
                    gs.update(gt)
                    groups.update((t, gs) for t in gt)
            elif gs and not gt:
                gs.add(target)
                groups[target] = gs
            elif not gs and gt:
                gt.add(source)
                groups[source] = gt
            else:
                g = {source, target}
                groups[source] = g
                groups[target] = g

    return groups


if __name__ == '__main__':
    groups_ = create_groups(load_links("data/12-input.txt"))
    print(f"part 1: group with 0 has {len(groups_[0])} elements")
    groups_count = len(set(id(g) for g in groups_.values()))
    print(f"part 2: there are {groups_count} groups total")
