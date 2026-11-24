from dataclasses import dataclass
from typing import Pattern, Callable, Optional
from pint import UnitRegistry
from QCalculator import DEF_UR


@dataclass(frozen=True)
class DSpec:
    pattern: Pattern[str]
    KW_ONLY = None
    allowed_symbols: frozenset[str] = frozenset({})
    sympy_safe: bool = True
    ureg: UnitRegistry = DEF_UR
    value_filters: frozenset[Callable[[int|float], bool]] = frozenset({})
    ref_units: Optional[str] = None  # only for Datum, not DDS
