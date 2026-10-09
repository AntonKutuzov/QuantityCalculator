from typing import Any, Tuple, Match, Literal, Optional, Pattern
from QCalculator import DatumDefString


def validate_type(
        check_vars: Any,
        check_types: type | Tuple[type, ...]
) -> None:
    if not isinstance(check_vars, check_types):
        raise TypeError(f'Expected "{check_types}", got: "{type(check_vars)}".')


def validate_match(m: Match, match_str: str, pattern: str) -> None:
    if m is None:
        raise ValueError(f'The string "{match_str}" does not match the {pattern} pattern.')
    else:
        return


def must_match(
        pattern: Literal['symbol', 'variable', 'dds', 'other'],
        string: str,
        custom_pattern: Optional[Pattern] = None
) -> Match:
    m = None
    p: Pattern

    match pattern:
        case 'symbol':
            p = DatumDefString.patterns.symbol
            # m = DatumDefString.patterns.symbol.fullmatch(string)
        case 'variable':
            p = DatumDefString.patterns.variable
            # m = DatumDefString.patterns.variable.fullmatch(string)
        case 'dds':
            p = DatumDefString.patterns.dds
            # m = DatumDefString.patterns.dds.fullmatch(string)
        case 'other':
            if custom_pattern is not None:
                p = custom_pattern
                # m = custom_pattern.fullmatch(string)
            else:
                raise ValueError(f'The pattern "{pattern}" is not supported.')
        case _:
            raise ValueError(f'The pattern "{pattern}" is not supported.')

    m = p.fullmatch(string)  # I don't see how it might be referenced before assignment

    if m is None:
        raise ValueError(f'The string "{string}" does not match the "{pattern}" pattern.\nThe pattern: "{p.pattern}"')
    else:
        return m
