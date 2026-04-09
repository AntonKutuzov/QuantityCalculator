from QCalculator.Exceptions import QCException


class DatumException(QCException):
    def __init__(self, message: str, comment: str):
        super().__init__(message, comment)


class DifferentSymbols(DatumException):
    def __init__(self, comment: str, self_symbol: str, other_symbol: str):
        self._message = f'The two compatible Datums have different symbols: "{self_symbol}", "{other_symbol}". Overrule by setting "symbol_ex" to False.'
        super().__init__(self._message, comment)


class IncompatibleUnits(DatumException):
    def __init__(self, comment: str, from_unit: str, to_unit: str):
        self._message = f'Could not convert units {from_unit} to {to_unit}.'
        super().__init__(self._message, comment)


class InitialisationError(DatumException):
    def __init__(self, comment: str, args) -> None:
        self._message = f'Cannot initialise Datum instance from the provided set of positional arguments: {args}.'
        super().__init__(self._message, comment)


class InvalidSymbol(DatumException):
    def __init__(self, comment: str, var: str) -> None:
        self._message = f'The symbol "{var}" cannot be used.'
        super().__init__(self._message, comment)


