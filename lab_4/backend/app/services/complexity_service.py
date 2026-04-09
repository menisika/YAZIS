"""Syntactic complexity scoring — isolated so it can be swapped easily."""
from __future__ import annotations

from app.services.nlp_service import TokenData

_SUBORDINATE_DEPS = {"relcl", "advcl", "ccomp", "xcomp", "acl"}


def _tree_depth(tokens: list[TokenData]) -> int:
    """Longest path from root to any leaf, using head_index graph."""
    if not tokens:
        return 0
    # Build children map
    children: dict[int, list[int]] = {t.index: [] for t in tokens}
    root_idx: int | None = None
    for t in tokens:
        if t.dep == "ROOT":
            root_idx = t.index
        else:
            children[t.head_index].append(t.index)

    if root_idx is None:
        root_idx = tokens[0].index

    # BFS/DFS for max depth
    def dfs(node: int) -> int:
        kids = children.get(node, [])
        if not kids:
            return 0
        return 1 + max(dfs(k) for k in kids)

    return dfs(root_idx)


def compute_raw_complexity(tokens: list[TokenData]) -> float:
    """
    Raw (un-normalised) complexity score.
    Combine four signals:
      - tree depth
      - subordinate clause count
      - average dependency distance
      - log of token count
    """
    import math

    n = len(tokens)
    if n == 0:
        return 0.0

    depth = _tree_depth(tokens)
    sub_clauses = sum(1 for t in tokens if t.dep in _SUBORDINATE_DEPS)
    avg_dep_dist = sum(abs(t.head_index - t.index) for t in tokens) / n

    # Weighted combination (weights chosen to give roughly equal contribution)
    score = (
        depth * 2.0
        + sub_clauses * 3.0
        + avg_dep_dist * 2.5
        + math.log1p(n) * 1.5
    )
    return score


def normalise_scores(raw_scores: list[float]) -> list[float]:
    """Normalise a list of raw scores to [0, 100]."""
    if not raw_scores:
        return []
    mn, mx = min(raw_scores), max(raw_scores)
    if mx == mn:
        return [50.0] * len(raw_scores)
    return [(s - mn) / (mx - mn) * 100 for s in raw_scores]
