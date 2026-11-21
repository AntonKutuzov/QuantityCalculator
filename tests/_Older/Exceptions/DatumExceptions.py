from QCalculator.Exceptions import QCException
from typing import Optional, Callable

'''
DatumException
├── SymbolException
│   ├── SymbolSympyUnsafe
│   └── InvalidVarName
├── UnitsException
│   ├── IncompatibleUnits
│   ├── UndefinedUnit
│   └── InvalidUnitExpression
├── ValueException
│   └── FilteringException
└── InvalidDatumDefString
'''


class DatumException(QCException):
    pass

class SymbolException(DatumException):
    pass

class ValueException(DatumException):
    pass

class UnitsException(DatumException):
    pass


class InvalidDatumDefString(DatumException):
    def __init__(self, dds: str):
        super().__init__(f'The Datum definition string "{dds}" is invalid.')


class SymbolSympyUnsafe(SymbolException):
    def __init__(self, symbol: str):
        super().__init__(f'The symbol "{symbol}" cannot be used in expressions with sympy.')

class InvalidVarName(SymbolException):
    def __init__(self, var: str) -> None:
        super().__init__(f'The variable with name "{var}" cannot be used.')

class FilteringException(ValueException):
    def __init__(self, val: float|int) -> None:
        super().__init__(f'The value {val} did not pass one of the filtering conditions.')

class InvalidUnitExpression(UnitsException):
    def __init__(self, units: str) -> None:
        super().__init__(f'The units expression "{units}" is invalid.')

class IncompatibleUnits(UnitsException):
    def __init__(self, from_unit: str, to_unit: str):
        super().__init__(f'Could not convert units {from_unit} to {to_unit}.')

class UndefinedUnit(UnitsException):
    def __init__(self, units: str):
        super().__init__(f'The units "{units}" are not defined in the used UnitRegistry.')
