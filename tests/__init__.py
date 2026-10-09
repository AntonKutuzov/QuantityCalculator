from contextlib import nullcontext
from pytest import raises


def exception_handling(exception):
    return (
        nullcontext()
        if exception is None
        else
        raises(exception)
    )
