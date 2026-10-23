from QCalculator.Exceptions import QCException


class QDefStringException(QCException):
    pass


class CannotInstantiateQDS(QDefStringException):
    def __init__(self):
        super().__init__('the QDefString class is intended only for creating subclasses, not instantiation.')



class UnitException(QDefStringException):
    ...

class VariableException(QDefStringException):
    ...

class DDSValueError(QDefStringException):
    ...

class InvalidQDefString(QDefStringException):
    def __init__(self, qds: str) -> None:
        super().__init__(f'The QDefString "{qds}" does not match the base pattern.')



class InvalidUnitExpression(UnitException):
    def __init__(self, units: str) -> None:
        super().__init__(f'The units expression "{units}" is invalid.')

class UndefinedUnit(UnitException):
    def __init__(self, cls: type, units: str):
        super().__init__(f'The units "{units}" are not defined in the used UnitRegistry of {cls}.')

class UnitNotAllowed(UnitException):
    def __init__(self, cls, units: str) -> None:
        super().__init__(f'The provided units "{units}" is not allowed in class {cls}.')



class VariableNotAllowed(VariableException):
    def __init__(self, cls, sym: str) -> None:
        super().__init__(f'The provided symbol "{sym}" is not allowed in class {cls}.')
