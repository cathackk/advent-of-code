from collections import defaultdict


def load_directs(fn):
    for line in open(fn, 'r'):
        yield line.strip().split(')')


def build_orbit_map(directs):
    omap = defaultdict(list)
    for body, link in directs:
        omap[body].append(link)
    return dict(omap)


def total_body_orbits(body, omap):
    links = omap.get(body, [])
    return len(links) + sum(total_body_orbits(link, omap) for link in links)


def total_orbits(omap):
    return sum(total_body_orbits(body, omap) for body in omap.keys())


def path_length(omap, start, target):
    print(f"calculating path from {start!r} to {target!r} ...")
    root = find_root(omap)
    print(f"root={root!r}")

    ps = find_path_down(omap, root, start)
    print(f"path from {root!r} to {start!r}: {ps}")
    pt = find_path_down(omap, root, target)
    print(f"path from {root!r} to {target!r}: {pt}")

    length = len(set(ps) ^ set(pt)) + 1
    print(f"path from {start!r} to {target!r} is {length} long")

    return length


def find_root(omap):
    roots = omap.keys() - {link for links in omap.values() for link in links}
    assert len(roots) == 1
    return next(iter(roots))


def find_path_down(omap, start, target):
    links = omap.get(start, [])
    if target in links:
        return [start, target]
    else:
        for link in links:
            path = find_path_down(omap, link, target)
            if path:
                return [start] + path
        else:
            return None


if __name__ == '__main__':
    directs = load_directs('data/06-orbits.txt')
    # print(directs)
    omap = build_orbit_map(directs)
    # print(omap)

    print(f"total orbits: {total_orbits(omap)}")

    length = path_length(omap, 'YOU', 'SAN')
    transfers = length - 3
    print(f"transfers: {transfers}")
