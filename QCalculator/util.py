from pint import UndefinedUnitError, Unit
from typing import Any, Tuple, Match, Literal, Optional, Pattern, Dict, List, overload
from QCalculator import patterns
from QCalculator.Exceptions.QDefStringExceptions import (
    UndefinedUnit,
    InvalidUnitExpression
)



def validate_type(
        check_vars: Any,
        check_types: type | Tuple[type, ...]
) -> None:
    if not isinstance(check_vars, check_types):
        raise TypeError(f'Expected "{check_types}", got: "{type(check_vars)}".')


@overload
def validate_types(
        check_vars: List[Any],
        check_types: type
) -> None:
    ...

@overload
def validate_types(
        check_vars: List[Any],
        check_types: Tuple[type]
) -> None:
    ...

def validate_types(
        check_vars: List[Any],
        check_types: List[type | Tuple[type]]
) -> None:
    if isinstance(check_types, (type, tuple)):
        for v in check_vars:
            validate_type(v, check_types)

    elif isinstance(check_vars, list):
        for v, t in zip(check_vars, check_types):
            validate_type(v, t)

    else:
        raise TypeError(f'Expected "type" of "List[type | Tuple[type]], got: "{type(check_types)}".')


def validate_match(m: Match, match_str: str, pattern: str) -> None:
    if m is None:
        raise ValueError(f'The string "{match_str}" does not match the {pattern} regex.')
    else:
        return


def must_match(
        pattern: Literal['symbol', 'variable', 'value', 'units', 'dds', 'other'],
        string: str | int | float,
        custom_pattern: Optional[Pattern] = None
) -> Match:
    m = None
    p: Pattern

    match pattern:
        case 'symbol':
            p = patterns.symbol
        case 'variable':
            p = patterns.variable
        case 'value':
            p = patterns.value
        case 'units':
            p = patterns.unit
        case 'other':
            if custom_pattern is not None:
                p = custom_pattern
                # m = custom_pattern.fullmatch(string)
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
    unpacked = dict()

    for t, u in d.items():
        if isinstance(t, tuple):
            for v in t:
                unpacked[v] = u
        else:
            unpacked[t] = u

    return unpacked



def check_unit_validity(cls, unit: str | Unit) -> None:
    if not isinstance(unit, (str, Unit)):
        raise TypeError(f'Expected "str" or "pint.Unit", got: "{unit}".')

    unit = str(unit)

    try:
        cls.ureg.parse_units(unit)

    except (AssertionError, ValueError, TypeError):
        raise InvalidUnitExpression(unit)

    except UndefinedUnitError:
        raise UndefinedUnit(cls, unit)