from typing import Optional, List, Dict

from QCalculator.Exceptions import QCException
from QCalculator.Datum import Datum


class FormulaException(QCException):
    def __init__(self, message: str, details: str):
        super().__init__(message, details)


class ReadWriteError(QCException):
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, details)

class SolutionError(QCException):
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, details)

class NotFoundError(QCException):
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, details)


# ReadWriteErrors
class RewritingError(ReadWriteError):
    def __init__(self, var: str, old: Datum, details: Optional[str] = None):
        message = f'Cannot rewrite variable "{var}". Current magnitude: {old.magnitude} {old.units_str}.'
        super().__init__(message, details)

class InvalidUnitError(ReadWriteError):
    def __init__(self, var: str, units: str, ref: str, details: Optional[str] = None):
        message = f'The units "{units}" for variable "{var}" are not compatible with the reference units "{ref}".'
        super().__init__(message, details)

class WrongUnitEquation(ReadWriteError):
    def __init__(self, f: str, units: Dict[str, str], details: Optional[str] = None):
        message = f'Current units ({units}) do not form an equality when substituted into an equation "{f}"'
        super().__init__(message, details)

class OverlappingVariables(ReadWriteError):
    def __init__(self, formula: str, vars: List[str], details: Optional[str] = None):
        message = f'The formula "{formula}" has several variables with the same symbol: [{",".join(vars)}]'
        super().__init__(message, details)

class InvalidSymbol(ReadWriteError):
    def __init__(self, expr: str, details: Optional[str] = None):
        message = f'The expression "{expr}" contains a symbol that cannot be used in sympy expressions.'
        super().__init__(message, details)


# SolutionErrors
class ConsistencyError(SolutionError):
    def __init__(self, formula: str, details: Optional[str] = None):
        message = f'The formula {formula} is inconsistent. It has contradicting values.'
        super().__init__(message, details)

class EquationNotSolvable(SolutionError):
    def __init__(self, formula: str, details: Optional[str] = None):
        message = f'The equation derived from the formula "{formula}" cannot be solved.'
        super().__init__(message, details)

class FailedConsistencyCheck(SolutionError):
    def __init__(self, formula: str, details: Optional[str] = None):
        message = f'Could not run the consistency check for the formula "{formula}".'
        super().__init__(message, details)


# NotFoundErrors
class SymbolNotFound(NotFoundError):
    def __init__(self, formula: str, symbol: str, details: Optional[str] = None):
        message = f'The variable "{symbol}" is not present in the formula "{formula}".'
        super().__init__(message, details)

class NoValueError(NotFoundError):
    def __init__(self, formula: str, symbol: str, details: Optional[str] = None):
        message = f'The variable "{symbol}" in the formula "{formula}" does not have a value.'
        super().__init__(message, details)

class TargetNotFound(NotFoundError):
    def __init__(self, formula: str, details: Optional[str] = None):
        message = f'The target variable is not specified for the formula "{formula}".'
        super().__init__(message, details)

class UnknownNotFound(NotFoundError):
    def __init__(self, formula: str, details: Optional[str] = None):
        message = f'Could not determine the unknown variable for the formula "{formula}".'
        super().__init__(message, details)

class NoneReferenceUnits(NotFoundError):
    def __init__(self, formula: str, var: str, details: Optional[str] = None):
        message = f'The reference units for variable "{var}" in formula "{formula}" are not found.'
        super().__init__(message, details)
