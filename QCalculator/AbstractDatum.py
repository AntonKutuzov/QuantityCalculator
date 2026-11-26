from __future__ import annotations

from abc import ABC, abstractmethod
from pint import Quantity, Unit, UndefinedUnitError, DimensionalityError
from typing import Self
from math import isinf, isnan

from QCalculator.DefStrings import AbstractDDS, DSpec
from QCalculator.util import validate_type, check_unit_validity
from QCalculator.Exceptions.QDefStringExceptions import UndefinedUnits, IncompatibleUnits



class AbstractDatum(ABC):
    ddef: AbstractDDS
    spec: DSpec


    def __init__(self, dds: str) -> None:
        self._dds = self.ddef(dds)

        if self.spec.ref_units is not None:
            ru = self.spec.ureg.parse_units(self.spec.ref_units)

            if not ru.is_compatible_with(self.units):
                iue = IncompatibleUnits(from_unit=self.units, to_unit=ru)
                iue.add_note(f'The allowed units for this Datum-like class are "{ru}" or any other '
                             f'compatible units.')
                raise iue

    def __str__(self) -> str:
        return self.dds.string

    def __eq__(self, other) -> bool:
        if not isinstance(other, AbstractDatum):
            raise TypeError(f'Expected "Datum", got: "{type(other)}".')

        from math import isclose

        conditions = [
            self.units == self.spec.ureg.Unit(other.units),  # bcs other.unit is not str, but Unit
            isclose(self.value, other.value),
            self.variable == other.variable
        ]

        return all(conditions)

    @abstractmethod
    def _from_quantity(self, var: str, q: Quantity, *args, **kwargs) -> Self:
        """
        Calls the public "from_quantity" method if the respective class by using type(self).
        """
        ...

    @classmethod
    @abstractmethod
    def from_quantity(cls, var: str, q: Quantity, *args, **kwargs) -> Self:
        ...

    # ================================================================================================== PRIVATE HELPERS
    @classmethod
    def _normalize_units(cls, u: str | Unit) -> Unit:
        validate_type(u, (str, Unit))
        check_unit_validity(cls, u)

        try:
            return cls.spec.ureg.parse_units(str(u))

        except UndefinedUnitError:
            raise UndefinedUnits(cls, u)

    # =================================================================================================== PUBLIC METHODS
    def to(self, units: str | Unit) -> Self:
        validate_type(units, (str, Unit))
        check_unit_validity(self.__class__, units)

        try:
            new_q = self.quantity.to(units)

        except DimensionalityError as e:
            raise IncompatibleUnits(from_unit=str(self.units), to_unit=str(units)) from e

        return self._from_quantity(self.variable, new_q)

    def scale(self, factor: float | int) -> Self:
        validate_type(factor, (float, int))

        if isnan(factor) or isinf(factor):
            raise ValueError('"factor" must be a real number.')

        return self._from_quantity(self.variable, factor * self.quantity)

    def compatible_units(self, other: AbstractDatum | Quantity | str | Unit) -> bool:
        """Checks whether the self Datum instance has compatible units with "other" object which encodes units."""

        if isinstance(other, (AbstractDatum, Quantity)):
            u = self._normalize_units(other.units)

        elif isinstance(other, (str, Unit)):
            u = self._normalize_units(other)

        else:
            raise TypeError(f'Expected "Datum", "pint.Quantity", "str", or "pint.Unit", got "{type(other)}"')

        return self.units.is_compatible_with(u)

    @property
    def quantity(self) -> Quantity:
        return self.value * self.units

    @property
    def variable(self) -> str:
        return self.dds.variable

    @property
    def value(self) -> float | int:
        return self.dds.value

    @property
    def units(self) -> Unit:
        return self.spec.ureg.parse_units(self.dds.units)

    @property
    def base(self) -> Self:
        q = self.quantity.to_base_units()
        d = self._from_quantity(self.variable, q)
        return d

    @property
    def dds(self) -> AbstractDDS:
        return self._dds
