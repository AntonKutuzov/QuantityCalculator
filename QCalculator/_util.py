from typing import List, Any, Tuple


def validate_type(
        check_vars: Any,
        check_types: type | Tuple[type, ...]
) -> None:
    if not isinstance(check_vars, check_types):
        raise TypeError(f'Expected "{check_types}", got: "{type(check_vars)}".')
