"""Disjoint Set Union (Union-Find) with path compression and union by rank."""
from __future__ import annotations

from typing import Generic, Hashable, TypeVar

T = TypeVar("T", bound=Hashable)


class DisjointSet(Generic[T]):
    """
    Disjoint Set Union (DSU) data structure.
    Operations run in near O(1) amortized time (inverse Ackermann function alpha(N)).
    """

    def __init__(self, elements: list[T] | None = None) -> None:
        self.parent: dict[T, T] = {}
        self.rank: dict[T, int] = {}
        self.size: dict[T, int] = {}
        self._count = 0
        if elements:
            for elem in elements:
                self.make_set(elem)

    def make_set(self, x: T) -> None:
        """Initialize a new disjoint set for element x."""
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            self.size[x] = 1
            self._count += 1

    def find(self, x: T) -> T:
        """Find the canonical representative of element x with path compression."""
        if x not in self.parent:
            self.make_set(x)
            return x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: T, y: T) -> bool:
        """
        Merge the sets containing x and y using union by rank.
        Returns True if sets were disjoint and merged, False if already in the same set.
        """
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False

        if self.rank[root_x] < self.rank[root_y]:
            root_x, root_y = root_y, root_x

        self.parent[root_y] = root_x
        self.size[root_x] += self.size[root_y]
        if self.rank[root_x] == self.rank[root_y]:
            self.rank[root_x] += 1

        self._count -= 1
        return True

    def connected(self, x: T, y: T) -> bool:
        """Check if x and y belong to the same connected component."""
        return self.find(x) == self.find(y)

    def component_size(self, x: T) -> int:
        """Get the number of elements in the component containing x."""
        return self.size[self.find(x)]

    @property
    def count(self) -> int:
        """Total number of disjoint components."""
        return self._count
