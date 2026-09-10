from __future__ import annotations

from pint import UnitRegistry, Quantity, Unit, DimensionalityError, UndefinedUnitError
from typing import Any, Literal
from sympy.parsing.sympy_parser import parse_expr

from QCalculator.Exceptions.DatumExceptions import (
    IncompatibleUnits,
    InvalidVarName, UndefinedUnit
)
from QCalculator.DatumDefString import DatumDefString


class Datum:
    ureg = UnitRegistry(system='SI')

    def __init__(self, dds: str, *, sympy_safe: bool = True) -> None:
        self._dds = DatumDefString(dds)
        self._sympy_safe = sympy_safe

        self._confirm_symbol(self.dds.variable)

    # ================================================================================================== PRIVATE HELPERS
    def _confirm_symbol(self, symbol: str) -> None:
        if self._sympy_safe:
            try:
                parse_expr(f'{symbol} - 1')
            except TypeError as e:
                raise InvalidVarName(
                    var=symbol,
                    details=f'The symbol "{symbol}" cannot be used in sympy expressions.'
                ) from e
        else:
            return None

    @staticmethod
    def _validate_type(check_for: Literal['variable', 'magnitude', 'units'], var: Any) -> None:
        symbol_types = (str,)
        magnitude_types = (float, int)
        magnitude_forbidden = (bool,)
        units_types = (str, Unit)

        check_types = tuple()
        avoid = tuple()

        match check_for:
            case 'variable':
                check_types = symbol_types
                avoid = tuple()
            case 'magnitude':
                check_types = magnitude_types
                avoid = magnitude_forbidden
            case 'units':
                check_types = units_types
                avoid = tuple()
            case _:
                raise ValueError(f'The "check_for" parameter must be a string "symbol", "magnitude", or "units", got: "{check_for}" or type "{type(check_for)}".')

        if isinstance(var, check_types) and not isinstance(var, avoid):
            return
        else:
            raise TypeError(f'The attribute "{check_for}" must be of types "{check_types}", got: {type(var)}.')

    # ========================================================================================= ALTERNATIVE CONSTRUCTORS
    @classmethod
    def from_quantity(cls, var: str, q: Quantity, *, sympy_safe: bool = True) -> Datum:
        cls._validate_type('variable', var)

        if not isinstance(q, Quantity):
            raise TypeError(f'Expected "pint.Quantity", got: "{type(q)}".')

        return Datum(f'{var} = {q.magnitude} {q.units}', sympy_safe=sympy_safe)


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
            self.units == other.units,
            isclose(self.value, self.value),
            self.variable == other.variable
        ]

        return all(conditions)

    # ========================================================================================================= MUTATORS
    def to(self, units: str | Unit) -> Datum:
        Datum._validate_type('units', units)

        try:
            new_q = self.quantity.to(units)

        except DimensionalityError as e:
            raise IncompatibleUnits(from_unit=str(self.units), to_unit=str(units)) from e

        return Datum.from_quantity(self.variable, new_q)

    def scale(self, factor: float|int) -> Datum:
        if not isinstance(factor, (float, int)):
            raise TypeError(f'Expected float or int, got "{type(factor)}".')

        return Datum.from_quantity(self.variable, factor * self.quantity, sympy_safe=self._sympy_safe)


    # ====================================================================================================== NORMALIZERS
    @classmethod
    def _normalize_units(cls, u: str | Unit) -> Unit:
        cls._validate_type('units', u)
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
