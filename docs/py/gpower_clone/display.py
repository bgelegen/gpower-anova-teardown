"""G*Power on-screen formatting (SPEC.md R-15)."""
from __future__ import annotations

import math

from .contract import INTEGER_FIELDS, OUTPUT_FIELDS
from .engine import Result


def format_fraction(x: float) -> str:
    """lambda, critical F, power: %.7f inside (0.01, 100), else %.7g."""
    if 0.01 < abs(x) < 100:
        return f"{x:.7f}"
    return f"{x:.7g}"


def format_integer(x: float) -> str:
    """df and N: floor(x + 0.5); 5 significant digits from 1e12 up."""
    if abs(x) >= 1e12:
        return f"{x:.5g}"
    return str(math.floor(x + 0.5))


def format_result(result: Result) -> dict:
    """Result attribute name -> text exactly as G*Power shows it."""
    out = {}
    for attr in OUTPUT_FIELDS:
        value = getattr(result, attr)
        out[attr] = (format_integer(value) if attr in INTEGER_FIELDS
                     else format_fraction(value))
    return out
