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
    def __init__(self, unit: str) -> None:
        super().__init__(f'The unit expression "{unit}" is invalid.')

class UndefinedUnit(UnitException):
    def __init__(self, cls: type, unit: str):
        super().__init__(f'The units "{unit}" are not defined in the used UnitRegistry of {cls}.')

class UnitNotAllowed(UnitException):
    def __init__(self, cls, unit: str) -> None:
        super().__init__(f'The provided unit "{unit}" is not allowed in class {cls}.')



class VariableNotAllowed(VariableException):
    def __init__(self, cls, var: str) -> None:
        super().__init__(f'The provided variable "{var}" is not allowed in class {cls}.')
