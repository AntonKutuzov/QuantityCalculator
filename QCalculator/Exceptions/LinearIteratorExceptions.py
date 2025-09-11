from QCalculator.Exceptions import QCException


class LinIterExceptions(QCException):
    def __init__(self, message: str, comment: str):
        super().__init__(message, comment)


class InvalidZeroToleranceExponent(LinIterExceptions):
    def __init__(self, comment: str, value: int):
        self._message = f'The zero tolerance exponent must be between 0 and 100. Got: {value}.'
        super().__init__(self._message, comment)

class InconsistentVariable(LinIterExceptions):
    def __init__(self, comment: str, var: str, v1: int|float, v2: int|float):
        self._message = f'The variable "{var}" has contradicting values: "{v1}" and "{v2}".'
        super().__init__(self._message, comment)


class TargetNotFound(LinIterExceptions):
    def __init__(self, comment: str):
        self._message = f'Specify target variable for the linear iterator.'
        super().__init__(self._message, comment)


class SolutionNotFound(LinIterExceptions):
    def __init__(self, comment: str):
        self._message = f'Could not find the solution.'
        super().__init__(self._message, comment)


class CannotRewriteVariable(LinIterExceptions):
    def __init__(self, comment: str, var: str, old_value: int|float, new_value: int|float):
        self._message = f'Could not rewrite the variable "{var}" from {old_value} to {new_value}.'
        super().__init__(self._message, comment)


class VariableNotFound(LinIterExceptions):
    def __init__(self, comment: str, var: str):
        self._message = f'Could not find a variable with symbol: "{var}".'
        super().__init__(self._message, comment)
