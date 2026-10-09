from typing import Any, Tuple, Match, Literal
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
        pattern: Literal['symbol', 'variable', 'dds'],
        string: str
) -> Match:
    m = None

    match pattern:
        case 'symbol':
            m = DatumDefString.patterns.symbol.fullmatch(string)
        case 'variable':
            m = DatumDefString.patterns.variable.fullmatch(string)
        case 'dds':
            m = DatumDefString.patterns.dds.fullmatch(string)
        case _:
            raise ValueError(f'The pattern "{pattern}" is not supported.')

    if m is None:
        raise ValueError(f'The string "{string}" does not match the "{pattern}" pattern.')
    else:
        return m