from pint import UndefinedUnitError, Unit
from typing import Any, Tuple, Match, Literal, Optional, Pattern, Dict, List, overload
from QCalculator import patterns
from QCalculator.Exceptions.QDefStringExceptions import (
    UndefinedUnits,
    InvalidUnitsExpression,
    SymbolSympyUnsafe
)
from tokenize import TokenError



def validate_type(
        check_vars: Any,
        check_types: type | Tuple[type, ...]
) -> None:
    """Checks that the provided variable is an instance of one of the provided types."""
    if not isinstance(check_vars, check_types):
        raise TypeError(f'Expected "{check_types}", got: "{type(check_vars)}".')


def validate_types(
        check_vars: List[Any],
        check_types: List[type | Tuple[type]]
) -> None:
    """
    Checks that one or more provided variables belong to one or more types. The function wraps validate_type for a more
    general case.

    For every variable in the "check_vars" list the function
    """

    if not len(check_vars) == len(check_types):
        raise ValueError('The lengths of "check_vars" and "check_types" lists must be the same.')

    if isinstance(check_types, (type, tuple)):
        for v in check_vars:
            validate_type(v, check_types)

    elif isinstance(check_vars, list):
        for v, t in zip(check_vars, check_types):
            validate_type(v, t)

    else:
        raise TypeError(f'Expected "type" of "List[type | Tuple[type]], got: "{type(check_types)}".')



def must_match(
        pattern: Literal['symbol', 'variable', 'value', 'units', 'other'],
        string: str | int | float,
        custom_pattern: Optional[Pattern] = None
) -> Match:
    p: Pattern

    match pattern:
        case 'symbol':
            p = patterns.symbol
        case 'variable':
            p = patterns.variable
        case 'value':
            p = patterns.value
        case 'units':
            p = patterns.units
        case 'other':
            if custom_pattern is not None:
                p = custom_pattern
            else:
                raise ValueError(f'The regex "{pattern}" is not supported.')
        case _:
            raise ValueError(f'The regex "{pattern}" is not supported.')

    m = p.fullmatch(string)  # I don't see how it might be referenced before assignment

    if m is None:
        raise ValueError(f'The string "{string}" does not match the "{pattern}" regex.\nThe regex: "{p.pattern}"')
    else:
        return m


def unpack_keys(d: Dict[Tuple[Any, ...] | Any, Any]) -> Dict[Any, Any]:
    validate_type(d, dict)

    unpacked = dict()

    for t, u in d.items():
        if isinstance(t, tuple):
            for v in t:
                unpacked[v] = u
        else:
            unpacked[t] = u

    return unpacked



def check_unit_validity(cls, unit: str | Unit) -> None:
    validate_type(unit, (str, Unit))

    try:
        getattr(cls, 'spec')
    except AttributeError:
        raise TypeError(f'The class "{cls}" does not have a "spec" attribute.')

    unit = str(unit)

    try:
        cls.spec.ureg.parse_units(unit)

    except (AssertionError, ValueError, TypeError, TokenError):
        raise InvalidUnitsExpression(unit)

    except UndefinedUnitError:
        raise UndefinedUnits(cls, unit)


def check_sympy_safety(symbol: str) -> None:
    from sympy import parse_expr

    try:
        parse_expr(f'{symbol} - 1')
    except TypeError as e:
        raise SymbolSympyUnsafe(
            f'The symbol "{symbol}" cannot be used in sympy expressions.\nTo ignore, set "sympy_safe" to True in constructor.'
        ) from e
