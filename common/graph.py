import heapq
from dataclasses import dataclass
from dataclasses import field
from typing import Callable
from typing import Iterable
from typing import TypeVar

from tqdm import tqdm

from common.utils import some

Node = TypeVar('Node')
Edge = TypeVar('Edge')


def shortest_path(
    start: Node,
    target: Node,
    edges: Callable[[Node], Iterable[tuple[Node, Edge, int]]],
    description: str = "finding shortest path",
    nodes_count: int = None
) -> tuple[int, list[Edge]]:
    """
    General Dijkstra's algorithm
    """

    @dataclass(frozen=True, order=True)
    class PathInfo:
        prev_node: Node | None = field(compare=False, default=None)
        edge: Edge | None = field(compare=False, default=None)
        total_cost: int = field(compare=True, default=0)

    @dataclass(frozen=True, order=True)
    class NodeInfo:
        node: Node = field(compare=False)
        path: PathInfo = field(compare=True)

    # node -> previous edge forming cheapest path into this node
    visited_nodes: dict[Node, PathInfo] = {}
    # heap of unvisited nodes adjacent to visited nodes
    unvisited_nodes: list[NodeInfo] = []

    def visit_node(node: Node, path: PathInfo):
        visited_nodes[node] = path
        for next_node, edge, cost in edges(node):
            heapq.heappush(
                unvisited_nodes,
                NodeInfo(
                    node=next_node,
                    path=PathInfo(prev_node=node, edge=edge, total_cost=path.total_cost + cost)
                )
            )

    # start by visiting the `start` node
    visit_node(start, PathInfo())
    # then visit node by node, until target is reached
    with tqdm(
        total=nodes_count,
        desc=description,
        initial=1,
        unit=" nodes",
        unit_scale=True,
        delay=1.0
    ) as progress:
        while target not in visited_nodes:
            if not unvisited_nodes:
                raise ValueError("path not found")
            # visit cheapest unvisited node
            node_info = heapq.heappop(unvisited_nodes)
            if node_info.node in visited_nodes:
                continue
            visit_node(node_info.node, node_info.path)
            progress.update()

    # reconstruct the whole path by backtracking
    def backtrack(node: Node) -> Iterable[Edge]:
        while node != start:
            path = visited_nodes[node]
            yield some(path.edge)
            node = some(path.prev_node)

    final_cost = visited_nodes[target].total_cost
    final_edges = list(backtrack(target))[::-1]
    return final_cost, final_edges
