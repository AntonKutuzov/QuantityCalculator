from QCalculator.Exceptions import QCException
from QCalculator import Datum

from typing import Optional


class LinIterException(QCException):
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, details)



class ReadWriteError(LinIterException):
    pass

class NotFoundError(LinIterException):
    pass



class NoValueError(NotFoundError):
    def __init__(self, symbol: str, details: Optional[str] = None):
        message = f'The variable "{symbol}" does not have a value.'
        super().__init__(message, details)

class FormulasNotIndicated(NotFoundError):
    def __init__(self, details: Optional[str] = None):
        message = 'Linear Iterator must have at least one formula.'
        super().__init__(message, details)

class UnreachableTarget(NotFoundError):
    def __init__(self, target: str, details: Optional[str] = None):
        message = f'The indicated target "{target}" was not possible to find.'
        super().__init__(message, details)

class UnusedSymbolError(ReadWriteError):
    def __init__(self, symbol: str, details: Optional[str] = None):
        message = f'The variable "{symbol}" is not used in any of the formulas.'
        super().__init__(message, details)

class IncompatibleUnitsError(ReadWriteError):
    def __init__(self, var: str, units: str, ref: str, details: Optional[str] = None):
        message = f'The units "{units}" for variable "{var}" are not compatible with the reference units "{ref}".'
        super().__init__(message, details)

class RewritingError(ReadWriteError):
    def __init__(self, var: str, old: Datum, details: Optional[str] = None):
        message = f'Cannot rewrite variable "{var}". Current magnitude: {old.magnitude} {old.units_str}.'
        super().__init__(message, details)
