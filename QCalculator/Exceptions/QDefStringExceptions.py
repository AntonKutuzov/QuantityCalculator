from QCalculator.Exceptions import QCException


class QDefStringException(QCException):
    pass



class UnitsException(QDefStringException):
    ...

class VariableException(QDefStringException):
    ...

class DDSValueError(QDefStringException):
    ...

class InvalidQDefString(QDefStringException):
    def __init__(self, qds: str) -> None:
        super().__init__(f'The QDefString "{qds}" does not match the base pattern.')



class SymbolSympyUnsafe(VariableException):
    def __init__(self, symbol: str):
        super().__init__(f'The symbol "{symbol}" cannot be used in expressions with sympy.')

class InvalidVarName(VariableException):
    def __init__(self, var: str) -> None:
        super().__init__(f'The variable with name "{var}" cannot be used.')



class FilteringException(DDSValueError):
    def __init__(self, val: float|int) -> None:
        super().__init__(f'The value {val} did not pass one of the filtering conditions.')



class InvalidUnitsExpression(UnitsException):
    def __init__(self, units: str) -> None:
        super().__init__(f'The units expression "{units}" is invalid.')

class UndefinedUnits(UnitsException):
    def __init__(self, cls: type, units: str):
        super().__init__(f'The units "{units}" are not defined in the used UnitRegistry of {cls}.')

class IncompatibleUnits(UnitsException):
    def __init__(self, from_unit: str, to_unit: str):
        super().__init__(f'Could not convert units {from_unit} to {to_unit}.')

class UnitsNotAllowed(UnitsException):
    def __init__(self, cls, units: str) -> None:
        super().__init__(f'The provided units "{units}" is not allowed in class {cls}.')
