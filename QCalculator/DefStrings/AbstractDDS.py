from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Match, Optional

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
                e.add_note(f'The symbols allowed by the class are: "{self.spec.allowed_symbols}".')
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
        return str(self._match.group('variable'))

    @property
    def subscript(self) -> Optional[str]:
        s = self._match.group('subscript')

        if s is None:
            return None
        else:
            return str(s)

    @property
    def symbol(self) -> str:
        return str(self._match.group('symbol'))

    @property
    def value(self) -> float:
        return float(self._match.group('value'))

    @property
    def units(self) -> str:
        units = self._match.group('units')

        if units is not None:
            units = str(units)
        else:
            units = 'dimensionless'

        return units

    @property
    @abstractmethod
    def string(self) -> str:
        ...
