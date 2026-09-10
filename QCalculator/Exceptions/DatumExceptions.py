from QCalculator.Exceptions import QCException
from typing import Optional

'''
DatumException
├── SymbolException
│   ├── SymbolSympyUnsafe
│   └── InvalidVarName
├── UnitsException
│   ├── IncompatibleUnits
│   ├── UndefinedUnit
│   └── InvalidUnitExpression
└── InvalidDatumDefString
'''


class DatumException(QCException):
    pass

class SymbolException(DatumException):
    pass

class UnitsException(DatumException):
    pass


class InvalidDatumDefString(DatumException):
    def __init__(self, dds: str, *, details: Optional[str] = None):
        super().__init__(
            f'The Datum definition string "{dds}" is invalid.',
            details
        )


class SymbolSumpyUnsafe(SymbolException):
    def __init__(self, symbol: str, *, details: Optional[str] = None):
        super().__init__(
            f'The symbol "{symbol}" cannot be used in expressions with sympy.',
            details
        )

class InvalidVarName(SymbolException):
    def __init__(self, var: str, *, details: Optional[str] = None) -> None:
        super().__init__(
            f'The variable with name "{var}" cannot be used.',
            details
        )

class InvalidUnitExpression(UnitsException):
    def __init__(self, units: str, *, details: Optional[str] = None) -> None:
        super().__init__(
            f'The units expression "{units}" is invalid.',
            details
        )

class IncompatibleUnits(UnitsException):
    def __init__(self, from_unit: str, to_unit: str, *, details: Optional[str] = None):
        super().__init__(
            f'Could not convert units {from_unit} to {to_unit}.',
            details
        )

class UndefinedUnit(UnitsException):
    def __init__(self, units: str, *, details: Optional[str] = None):
        super().__init__(
            f'The units "{units}" are not defined in the used UnitRegistry.',
            details
        )
