from QCalculator.Exceptions import QCException
from typing import Optional


class DatumException(QCException):
    pass


class SymbolException(DatumException):
    pass


class DifferentSymbols(SymbolException):
    def __init__(self, self_symbol: str, other_symbol: str, *, details: Optional[str] = None):
        super().__init__(
            f'The two compatible Datums have different symbols: "{self_symbol}", "{other_symbol}". Overrule by setting "symbol_ex" to False.',
            details
        )

class InvalidSymbol(SymbolException):
    def __init__(self, var: str, *, details: Optional[str] = None) -> None:
        super().__init__(f'The symbol "{var}" cannot be used.', details)


class IncompatibleUnits(DatumException):
    def __init__(self, from_unit: str, to_unit: str, *, details: Optional[str] = None):
        super().__init__(f'Could not convert units {from_unit} to {to_unit}.', details)


class InitializationError(DatumException):
    def __init__(self, args, *, details: Optional[str] = None) -> None:
        super().__init__(
            f'Cannot initialise Datum instance from the provided set of positional arguments: {args}.',
            details
        )

