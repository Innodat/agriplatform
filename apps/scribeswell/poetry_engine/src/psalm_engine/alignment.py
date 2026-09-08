"""Conservative monotonic alignment; normalization never changes stored text."""

import logging
import unicodedata

from .models import Alignment, Token


def consonants(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if "\u05d0" <= c <= "\u05ea")


def without_cantillation(text: str) -> str:
    return "".join(c for c in text if not "\u0591" <= c <= "\u05af")


def align_tokens(left: list[Token], right: list[Token], max_group: int = 4) -> list[Alignment]:
    """Minimize unmatched tokens, then prefer smaller exact consonantal groups.

    At most max_group contiguous tokens per source. Potential alternatives, vowel
    distinctions and repeated strings need human inspection; scores are heuristic.
    """
    result = []
    for verse in sorted({t.verse for t in left + right}):
        a = sorted([t for t in left if t.verse == verse], key=lambda t: t.position)
        b = sorted([t for t in right if t.verse == verse], key=lambda t: t.position)
        n, m = len(a), len(b)
        costs = {(n, m): 0}
        steps = {}
        for i in range(n, -1, -1):
            for j in range(m, -1, -1):
                if (i, j) == (n, m):
                    continue
                options = []
                if i < n:
                    options.append((100 + costs[i + 1, j], 1, 0))
                if j < m:
                    options.append((100 + costs[i, j + 1], 0, 1))
                for x in range(1, min(max_group, n - i) + 1):
                    la = "".join(consonants(t.surface) for t in a[i : i + x])
                    for y in range(1, min(max_group, m - j) + 1):
                        rb = "".join(consonants(t.surface) for t in b[j : j + y])
                        if la and la == rb:
                            options.append((x + y - 2 + costs[i + x, j + y], x, y))
                cost, x, y = min(options)
                costs[i, j], steps[i, j] = cost, (x, y)
        i = j = 0
        while i < n or j < m:
            x, y = steps[i, j]
            matched = bool(x and y)
            result.append(
                Alignment(
                    verse=verse,
                    left_ids=[t.id for t in a[i : i + x]],
                    right_ids=[t.id for t in b[j : j + y]],
                    status="consonantal_match" if matched else "unmatched",
                    confidence=(0.95 if x == y == 1 else 0.8) if matched else 0,
                    note="Consonantal agreement only; vocalization/alternative alignments not adjudicated."
                    if matched
                    else "No exact contiguous match; retained for review.",
                )
            )
            i, j = i + x, j + y
    unmatched = sum(r.status == "unmatched" for r in result)
    if unmatched:
        logging.getLogger(__name__).warning("%d unmatched token groups retained", unmatched)
    return result
