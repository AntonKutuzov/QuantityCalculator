from QCalculator.Exceptions import QCException


class FormulaException(QCException):
    def __init__(self, message: str, comment: str):
        super().__init__(message, comment)


class InvalidZeroToleranceExponent(FormulaException):
    def __init__(self, comment: str, value: int):
        self._message = f'The zero tolerance exponent must be between 0 and 100. Got: {value}.'
        super().__init__(self._message, comment)


class CannotRunConsistencyCheck(FormulaException):
    def __init__(self, comment: str, formula: str):
        self._message = f'Could not run consistency check for the formula {formula}. Check that all variables are written in.'
        super().__init__(self._message, comment)


class InconsistentFormula(FormulaException):
    def __init__(self, comment: str, formula: str):
        self._message = f'The formula  {formula} is inconsistent. It has contradicting values.'
        super().__init__(self._message, comment)


class TargetNotFound(FormulaException):
    def __init__(self, comment: str, formula: str):
        self._message = f'Specify target variable for the formula: {formula}.'
        super().__init__(self._message, comment)


class SolutionNotFound(FormulaException):
    def __init__(self, comment: str, formula: str):
        self._message = f'Could not solve the equation from "{formula}".'
        super().__init__(self._message, comment)


class EquationNotSolvable(FormulaException):
    def __init__(self, comment: str, formula: str):
        self._message = f'The equation derived from the formula "{formula}" cannot be solved.'
        super().__init__(self._message, comment)
