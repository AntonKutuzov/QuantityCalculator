from contextlib import nullcontext
from pytest import raises
from QCalculator.Exceptions.QDefStringExceptions import SymbolSympyUnsafe
from QCalculator.util import check_sympy_safety


def skip_sympy_unsafe_symbols(symbol):
    try:
        check_sympy_safety(symbol)
    except SymbolSympyUnsafe:
        return True

    return False


def exception_handling(exception):
    return (
        nullcontext()
        if exception is None
        else
        raises(exception)
    )
