from Calculator.Storage import UNIT_REGISTRY, DEFAULT_VALUES, VARIABLE_NAMES
from Calculator.Storage.CONSTANTS import FORMULAS_FILE, UNITS_FILE, DEFAULTS_FILE, NAMES_FILE
from Calculator.Utils import write, remove, find
from Calculator.Computations import Formula
from typing import Dict, Any


def add_formula(
        formula: Formula,
        add_vars: bool = True,
        units: Dict[str, str] = None,
        defaults: Dict[str, Any] = None
        ) -> None:

    if not find(FORMULAS_FILE, formula.expr, search="BY LINE"):
        write(FORMULAS_FILE, formula.expr)
    else:
        return

    if add_vars:
        vars = formula.symbols

        for v in vars:
            u = units[v]
            add_variable(v, u, defaults.get(v))


def remove_formula(formula: Formula, remove_vars: bool = True) -> None:
    if find(FORMULAS_FILE, formula.expr):
        remove(FORMULAS_FILE, formula.expr+'\n')
    else:
        return

    vars = formula.symbols

    if not remove_vars:
        return None

    for var in vars:
        if not find(FORMULAS_FILE, var, search='BY SYMBOL'):
            u = UNIT_REGISTRY[var]
            remove(UNITS_FILE, f'{var}:{u}\n')

            if find(DEFAULTS_FILE, var, search='BY SYMBOL'):
                remove(DEFAULTS_FILE, f'{var}:{DEFAULT_VALUES[var]}\n')


def add_variable(
        var: str,
        unit: str,
        default: str = None,
        name: str = ''
        ) -> None:

    default_string = f'{var}:{default}'
    units_string = f'{var}:{unit}'
    name_string = f'{var}:{name}'

    if default is not None and not find(DEFAULTS_FILE, default_string, search='BY LINE'):
        write(DEFAULTS_FILE, default_string)

    if not find(UNITS_FILE, units_string, search='BY LINE'):
        write(UNITS_FILE, units_string)

    if not find(NAMES_FILE, name_string, search='BY LINE'):
        write(NAMES_FILE, name_string)


def remove_variable(var: str) -> None:
    unit = UNIT_REGISTRY[var]  # because a variable must have units (or must be labeled 'dimensionless')
    default = DEFAULT_VALUES.get(var)
    name = VARIABLE_NAMES.get(var)

    remove(UNITS_FILE, f'{var}:{unit}')

    if default is not None:
        remove(DEFAULTS_FILE, f'{var}:{default}')

    if name is not None:
        remove(NAMES_FILE, f'{var}:{name}')
