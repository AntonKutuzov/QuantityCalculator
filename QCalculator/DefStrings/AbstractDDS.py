from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Match, Optional, Literal

from QCalculator.DefStrings.DSpec import DSpec
from QCalculator.Exceptions.QDefStringExceptions import (
    InvalidQDefString,
    InvalidVarName,
    FilteringException
)
from QCalculator.util import check_unit_validity, check_sympy_safety, validate_type


class AbstractDDS(str, ABC):
    spec: DSpec

    def __new__(cls, dds, *args, check_units: bool = True, **kwargs) -> object:
        return super().__new__(cls, dds)

    def __init__(self, dds: str, *, check_units: bool = True):
        validate_type(dds, str)

        self._match = self.spec.pattern.fullmatch(dds)

        if self._match is None:
            raise InvalidQDefString(qds=dds)

        if self.spec.sympy_safe:
            check_sympy_safety(self.variable)

        if self.spec.allowed_symbols:  # if it's not empty
            if self.symbol not in self.spec.allowed_symbols:
                e = InvalidVarName(self.symbol)
                e.add_note(f'The symbols allowed by the class are: "{list(self.spec.allowed_symbols)}".')
                raise e

        for f in self.spec.value_filters:
            if not f(self.value):
                raise FilteringException(self.value)

        if check_units:
            check_unit_validity(type(self), self.units)

        super().__init__()


    def __str__(self):
        return self.string


    def __eq__(self, other: AbstractDDS):
        from math import isclose

        conditions = (
            self.variable == other.variable,
            isclose(self.value, other.value),
            self.spec.ureg.parse_units(self.units).is_compatible_with(other.spec.ureg.parse_units(other.units))
        )

        return all(conditions)


    @property
    def match(self) -> Match[str]:
        return self._match

    @property
    def variable(self) -> str:
        return str(self.match.group('variable'))

    @property
    def subscript(self) -> Optional[str]:
        s = self.match.group('subscript')

        if s is None:
            return ''
        else:
            return str(s)

    @property
    def symbol(self) -> str:
        return str(self.match.group('symbol'))

    @property
    def value(self) -> float:
        return float(self.match.group('value'))

    @property
    def whole(self) -> int:
        return int(self.match.group('whole'))

    @property
    def decimal(self) -> float:
        dec = self.match.group('decimal')

        if dec is None:
            return 0.0
        else:
            return float(f'0.{dec}')

    @property
    def sign(self) -> Literal[1, -1]:
        v = self.match.group('value')
        if v[0] == '-':
            return -1
        else:
            return 1

    @property
    def exponent(self) -> int:
        e = self.match.group('exponent')

        if e is None:
            return 0
        else:
            return int(e)

    @property
    def num_decimals(self) -> int:
        dec = self.decimal

        if dec == 0.0:
            return 0
        else:
            return len(str(dec)) - 2  # minus whole part, which is zero, and the decimal point

    @property
    def units(self) -> str:
        units = self.match.group('units')

        if units is not None:
            units = str(units)
        else:
            units = 'dimensionless'

        return units

    @property
    @abstractmethod
    def string(self) -> str:
        ...
