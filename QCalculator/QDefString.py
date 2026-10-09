from typing import Pattern
from abc import ABC, abstractmethod
from pint import Unit
from re import compile

from QCalculator import DEF_UR
from QCalculator._util import must_match


class QDefString(str, ABC):
    _ureg = DEF_UR

    def __new__(cls, string, *args, **kwargs) -> object:
        must_match('other', string, cls._pattern)
        return super().__new__(cls, string)

    def __init_subclass__(cls, pattern: Pattern, **kwargs):
        cls._pattern = pattern
        super().__init_subclass__(**kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__()

    @property
    @abstractmethod
    def variable(self) -> str:
        ...

    @property
    @abstractmethod
    def value(self) -> float:
        ...

    @property
    @abstractmethod
    def unit(self) -> Unit:
        ...



class DummyDefString(QDefString, pattern=compile(r'ABC')):
    def __init__(self, dds: str) -> None:
        super().__init__(dds)

    @property
    def variable(self) -> str:
        return 'just a variable'

    @property
    def value(self) -> float:
        return 0.0

    @property
    def unit(self) -> Unit:
        return Unit('dimensionless')


class Dummy2(QDefString, pattern=compile(r'HUH')):
    def __init__(self, dds: str) -> None:
        super().__init__(dds)

    @property
    def variable(self) -> str:
        return 'just a huh'

    @property
    def value(self) -> float:
        return -0.0

    @property
    def unit(self) -> Unit:
        return Unit('H')



qds = DummyDefString('ABC')
h = Dummy2('huh')

print(qds, type(qds))
print(h, type(h))

print(qds.variable)
print(h.variable)
