"""
Example of a refactored module (illustrative target shape).

This file shows one possible clean structure after applying SOLID-oriented
refactoring to ``examples/before/sample.py``. The live CLI may produce
slightly different but equivalent code.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass


@dataclass
class Accumulator:
    """Holds a running total with explicit increment operations."""

    value: int = 0

    def add(self, amount: int) -> None:
        """Add ``amount`` to the running total."""
        self.value += amount

    def total(self) -> int:
        """Return the current total."""
        return self.value


def weighted_nested_sum(
    a: Sequence[int],
    b: Sequence[int],
    c: Sequence[int],
    d: Mapping[str, int] | None,
    e: Sequence[int],
    f: Sequence[int],
) -> int:
    """
    Compute a weighted sum using parallel sequences.

    The original implementation mixed indexing styles and implicit length
    assumptions; this version uses explicit bounds and clearer structure.

    Args:
        a: Primary left multiplicand sequence.
        b: Sequence paired with ``a`` for products.
        c: Modulo-weight sequence aligned with ``a`` indices.
        d: Optional map keyed by stringified ``b`` indices.
        e: Sequence scaled into ``tmp`` contributions.
        f: Parallel sequence to ``e`` for pairwise combination.

    Returns:
        Combined scalar result.
    """
    total = 0
    len_a, len_b = len(a), len(b)
    len_c = len(c)

    for i in range(len_a):
        for j in range(len_b):
            c_part = c[i % len_c] if len_c else 0
            total += a[i] * b[j] + c_part
            if d is not None:
                total += d.get(str(j), 0)

    tmp: list[int] = []
    len_e, len_f = len(e), len(f)
    for k in range(len_e):
        if k < len_f:
            tmp.append(e[k] * 2 + f[k])
        else:
            tmp.append(e[k])

    return total + sum(tmp)


def summarize_data(data: Iterable[int]) -> tuple[int, list[int]]:
    """
    Aggregate ``data`` into a weighted sum and a transformed list.

    Args:
        data: Integer stream to process.

    Returns:
        A pair ``(accumulated_weighted_sum, transformed_values)``.
    """
    items = list(data)
    acc = 0
    for item in items:
        acc += item * 3 if item > 10 else item

    transformed: list[int] = []
    for item in items:
        transformed.append(item * item if item % 2 == 0 else item + 1)

    return acc, transformed
