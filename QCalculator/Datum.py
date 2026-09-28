from __future__ import annotations

from pint import UnitRegistry, Quantity, Unit, DimensionalityError, UndefinedUnitError
from sympy.parsing.sympy_parser import parse_expr
from math import isnan, isinf

from QCalculator.Exceptions.DatumExceptions import (
    IncompatibleUnits,
    InvalidVarName, UndefinedUnit
)
from QCalculator.DatumDefString import DatumDefString
from QCalculator._util import validate_type


class Datum:
    ureg = UnitRegistry(system='SI')

    def __init__(self, dds: str, *, sympy_safe: bool = True) -> None:
        self._dds = DatumDefString(dds)

        if not isinstance(sympy_safe, bool):
            raise TypeError(f'Expected "bool", got: "{type(sympy_safe)}".')

        self._sympy_safe = sympy_safe

        self._check_sympy_safety(self.dds.variable)


    # ========================================================================================= ALTERNATIVE CONSTRUCTORS
    @classmethod
    def from_quantity(cls, var: str, q: Quantity, *, sympy_safe: bool = True) -> Datum:
        validate_type(var, str)
        validate_type(q, Quantity)
        validate_type(sympy_safe, bool)

        return Datum(f'{var} = {q.magnitude} {q.units}', sympy_safe=sympy_safe)


    # ================================================================================================== PRIVATE HELPERS
    def _check_sympy_safety(self, symbol: str) -> None:
        if self._sympy_safe:
            try:
                parse_expr(f'{symbol} - 1')
            except TypeError as e:
                raise InvalidVarName(
                    var=symbol,
                    details=f'The symbol "{symbol}" cannot be used in sympy expressions.\nTo ignore, set "sympy_safe" to True in constructor.'
                ) from e
        else:
            return None


    # ==================================================================================================== MAGIC METHODS
    def __str__(self) -> str:
        return f'{self.variable} = {self.value} {self.units}'

    def __eq__(self, other: Datum):
        """
        Two Datums are considered equal if they have equal quantities, and have the same variables.

        :param other:
        :return:
        """

        if not isinstance(other, Datum):
            raise TypeError(f'Expected "Datum", got: "{type(other)}".')

        from math import isclose

        conditions = [
            self.units == self.ureg.Unit(other.units),
            isclose(self.value, other.value),
            self.variable == other.variable
        ]

        return all(conditions)

    # ========================================================================================================= MUTATORS
    def to(self, units: str | Unit) -> Datum:
        validate_type(units, (str, Unit))
        DatumDefString.check_unit_validity(units)

        try:
            new_q = self.quantity.to(units)

        except DimensionalityError as e:
            raise IncompatibleUnits(from_unit=str(self.units), to_unit=str(units)) from e

        return Datum.from_quantity(self.variable, new_q)

    def scale(self, factor: float|int) -> Datum:
        validate_type(factor, (float, int))

        if isnan(factor) or isinf(factor):
            raise ValueError('"factor" must be a real number.')

        return Datum.from_quantity(self.variable, factor * self.quantity, sympy_safe=self._sympy_safe)


    # ====================================================================================================== NORMALIZERS
    @classmethod
    def _normalize_units(cls, u: str | Unit) -> Unit:
        validate_type(u, (str, Unit))
        DatumDefString.check_unit_validity(u)

        try:
            return cls.ureg.Unit(u)

        except UndefinedUnitError:
            raise UndefinedUnit(f'The units given for that Datum definition string do not exist: "{u}".')

    # =================================================================================================== DATUM ANALYSIS
    def compatible_units(self, other: Datum|Quantity|str|Unit) -> bool:
        """Checks whether the self Datum instance has compatible units with "other" object which encodes units."""

        if isinstance(other, (Datum, Quantity)):
            u = Datum._normalize_units(other.units)

        elif isinstance(other, (str, Unit)):
            u = Datum._normalize_units(other)

        else:
            raise TypeError(f'Expected "Datum", "pint.Quantity", "str", or "pint.Unit", got "{type(other)}"')

        return self.units.is_compatible_with(u)


    # ======================================================================================================= PROPERTIES
    @property
    def quantity(self) -> Quantity:
        return Quantity(self.value, self.units)

    @property
    def variable(self) -> str:
        return self.dds.variable

    @property
    def value(self) -> float|int:
        return self.dds.value

    @property
    def units(self) -> Unit:
        return self.ureg.Unit(self.dds.units)

    @property
    def base(self) -> Datum:
        q = self.quantity.to_base_units()
        d = Datum.from_quantity(self.variable, q, sympy_safe=self._sympy_safe)
        return d

    @property
    def dds(self) -> DatumDefString:
        return self._dds
