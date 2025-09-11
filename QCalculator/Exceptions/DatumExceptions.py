from QCalculator.Exceptions import QCException


class DatumException(QCException):
    def __init__(self, message: str, comment: str):
        super().__init__(message, comment)


class InvalidZeroToleranceExponent(DatumException):
    def __init__(self, comment: str, value: int):
        self._message = ('The zero tolerance exponent must be between 0 and 100. Got: {value}.')
        super().__init__(self._message, comment)


class UnsupportedOperation(DatumException):
    def __init__(self, comment: str, other_type: str):
        self._message = f'You cannot divide Datum by {other_type}.'
        super().__init__(self._message, comment)


class CannotDetermineSignificantDigits(DatumException):
    def __init__(self, comment: str, number: int|float):
        self._message = (f'Could not determine the number of significant digits from the number {number}.\n'
                         f'Check that the number is not zero.')
        super().__init__(self._message, comment)


class IncompatibleUnits(DatumException):
    def __init__(self, comment: str, from_unit: str, to_uint: str):
        self._message = f'Could not convert units {from_unit} to {to_uint}.'
        super().__init__(self._message, comment)
