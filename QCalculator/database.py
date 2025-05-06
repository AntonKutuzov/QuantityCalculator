from typing import Dict, List, Optional
from QCalculator.Formula import Formula


FORMULA_LIST: List[Formula] = list()
UNIT_REGISTRY: Dict[str, str] = dict()
VARIABLES: List[str] = list()
DEFAULTS: Dict[str, float | int] = dict()


def add_formula(
        formula: str,
        *,
        add_vars: bool = False,
        var_units: Optional[Dict[str, str]] = None,
        defaults: Optional[Dict[str, int | float]] = None
) -> bool:
    if formula not in FORMULA_LIST:
        f = Formula(formula)
        FORMULA_LIST.append(f)

        if add_vars and var_units is not None:
            for var in f.symbols:
                u = var_units[var]
                d = defaults.get(var) if defaults is not None else None
                add_variable(var, u, default=d)
        return True

    else:
        return False


def add_variable(
        symbol: str,
        unit: str,
        *,
        default: Optional[int | float] = None,
) -> bool:
    if symbol not in VARIABLES:
        VARIABLES.append(symbol)
        add_unit(symbol, unit)
        if default is not None:
            add_default_value(symbol, default)
        return True

    else:
        return False


def add_unit(
        var: str,
        unit: str,
        *,
        alter: bool = False
) -> bool:
    if UNIT_REGISTRY.get(var) is None or alter:
        UNIT_REGISTRY.update({var: unit})
        return True
    else:
        return False


def add_default_value(
        var: str,
        default: int | float,
        *,
        alter: bool = False
) -> bool:
    if DEFAULTS.get(var) is None or alter:
        DEFAULTS.update({var: default})
        return True
    else:
        return False
