from __future__ import annotations

from pint import UnitRegistry, Quantity, Unit, DimensionalityError, UndefinedUnitError
from typing import Any, Literal
from sympy.parsing.sympy_parser import parse_expr
from numbers import Real

from QCalculator.Exceptions.DatumExceptions import (
    IncompatibleUnits,
    InvalidVarName
)
from QCalculator.DatumDefString import DatumDefString


class Datum:
    #           SETTINGS            #

    SYMPY_SAFE: bool = True         # if True, restricts 'symbol' to strings that can be converted to sympy.Symbol

    #           SETTINGS            #

    ureg = UnitRegistry(system='SI')


    def __init__(self,
                 symbol: str,
                 magnitude: float|int,
                 units: str|Unit
                 ) -> None:

        Datum._validate_type('symbol', symbol)
        Datum._validate_type('magnitude', magnitude)
        Datum._validate_type('units', unit)
        Datum._confirm_symbol(symbol)

        self._symbol: str = symbol
        self._magnitude: float = float(magnitude)
        self._units: Unit = Datum.normalize_units(unit)
        self._dds: DatumDefString = DatumDefString(self.__str__())

    # ================================================================================================== PRIVATE HELPERS
    @classmethod
    def _confirm_symbol(cls, symbol: str, raise_exception: bool = True) -> bool:
        """
        Returns True if the symbol matches the regular expression specified for symbols, False otherwise.
        If "raise_exception" is set to True, raises InvalidVarName exception if the symbol does **not** match re.

        :param symbol: str, symbol to be checked
        :param raise_exception: if True, raises InvalidVarName for string that do not match the regular expression
        :return: bool
        """

        res = DatumDefString.patterns.variable.fullmatch(symbol)

        if res is None and raise_exception:
            raise InvalidVarName(
                var=symbol,
                details=f'The symbol "{symbol}" does not match the allowed pattern for variables.'
            )

        if cls.SYMPY_SAFE:
            try:
                parse_expr(f'{symbol} - 1')
            except TypeError:
                if raise_exception:
                    raise InvalidVarName(
                        var=symbol,
                        details=f'The symbol "{symbol}" cannot be used in sympy expressions.'
                    )
                else:
                    return False

        return res is not None  # if it matches, it is not None

    @staticmethod
    def _validate_type(check_for: Literal['symbol', 'magnitude', 'units'], var: Any) -> None:
        symbol_types = (str,)
        magnitude_types = (Real,)
        magnitude_forbidden = (bool,)
        units_types = (str, Unit)

        check_types = tuple()
        avoid = tuple()

        match check_for:
            case 'symbol':
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
    def from_quantity(cls, symbol: str, quantity: Quantity) -> Datum:
        cls._validate_type('symbol', symbol)

        if not isinstance(quantity, Quantity):
            raise TypeError(f'Expected "pint.Quantity", got: "{type(quantity)}".')

        cls._confirm_symbol(symbol)
        units = cls.normalize_units(quantity.units)

        return Datum(symbol, quantity.magnitude, units)


    @staticmethod
    def from_string(datum: str) -> Datum:
        dds = DatumDefString(datum)
        return Datum(dds.variable, dds.magnitude, dds.unit)


    @classmethod
    def as_datum(
            cls,
            d: Datum|Quantity|str,
            symbol: str = ''
    ) -> Datum:
        """Depending on the type of the parameter "d", uses either .from_string() or .from_quantity(), or just returns
        the copy of the parameter so that the object returned is always a Datum instance. Passing Quantity instance also
        requires passing in "symbol" parameter.

        Does that method make sense if you still have to give symbol for quantity, and not for Datum?"""

        if isinstance(d, Datum):
            newd = Datum(d.symbol, d.magnitude, d.units)
            return newd
            # so that changes of the returned object do not affect the original one and vice versa
            # copy() is not used, because magnitude must be rounded initially.
        elif isinstance(d, Quantity):
            return cls.from_quantity(symbol, d)
        elif isinstance(d, str):
            return cls.from_string(d)
        else:
            raise TypeError(f'The parameter "d" has a wrong type. Expected "Datum", "str" or "pint.Quantity", got "{type(d)}".')


    # ==================================================================================================== MAGIC METHODS
    def __str__(self) -> str:
        """Returns a string of the form <variable> = <magnitude> <units>. For example, 'm = 10 g' or 'v = 2 m/s'"""
        return f'{self.symbol} = {self.magnitude} {self.units_str}'

    def __eq__(self, other: Datum):
        """
        Two Datums are considered equal if they have equal base quantities (Quantity instances in base units), and
        have the same symbols.

        :param other:
        :return:
        """

        return self.eq(other, strict=True)

    def eq(self, other: Datum, strict: bool = False) -> bool:
        if not isinstance(other, Datum):
            raise TypeError(f'Expected "Datum", got: "{type(other)}".')

        from math import isclose

        mild_conditions = [
            self.base.units == other.base.units,
            isclose(self.base.magnitude, self.base.magnitude),
            self.symbol == other.symbol
        ]

        strict_conditions = [
            self.units == other.units,
            isclose(self.magnitude, self.magnitude),
            self.symbol == other.symbol
        ]

        conditions = strict_conditions if strict else mild_conditions
        return all(conditions)

    # ========================================================================================================= MUTATORS
    def to(self, units: str | Unit) -> Datum:
        Datum._validate_type('units', units)

        try:
            new_q = self.quantity.to(units)
            return Datum.from_quantity(self.symbol, new_q)

        except DimensionalityError as e:
            raise IncompatibleUnits(from_unit=self.units_str, to_unit=units) from e

    def to_base_units(self) -> Datum:
        return self.to(self.base.units)

    def scale(self, factor: float|int) -> Datum:
        if not isinstance(factor, (float, int)):
            raise TypeError(f'Expected float or int, got "{type(factor)}".')

        return Datum(self.symbol, self.magnitude * factor, self.units_str)


    # ====================================================================================================== NORMALIZERS
    @classmethod
    def normalize_units(cls, u: str|Unit) -> Unit:
        cls._validate_type('units', u)

        try:
            return cls.ureg.Unit(u)

        except AssertionError:
            raise ValueError(f'The units given for that Datum definition string is an invalid string: "{u}".')

        except (UndefinedUnitError, ValueError):
            raise ValueError(f'The units given for that Datum definition string cannot be parsed into pint.Unit: "{u}".')

    # =================================================================================================== DATUM ANALYSIS
    def get_decimals(self) -> int:
        return self.dds.num_decimals

    def is_compatible(self, other: Datum|Quantity|str|Unit) -> bool:
        """Checks whether the self Datum instance has compatible units with "other" object which encodes units."""

        if isinstance(other, (Datum, Quantity)):
            u = Datum.normalize_units(other.units)

        elif isinstance(other, (str, Unit)):
            u = Datum.normalize_units(other)

        else:
            raise TypeError(f'Expected "Datum", "pint.Quantity", "str", or "pint.Unit", got "{type(other)}"')

        return self.units.is_compatible_with(u)


    # ======================================================================================================= PROPERTIES
    @property
    def quantity(self) -> Quantity:
        return Quantity(self.magnitude, self.units)

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def magnitude(self) -> float|int:
        return self._magnitude

    @property
    def units(self) -> Unit:
        return self._units

    @property
    def units_str(self) -> str:
        return str(self.units)

    @property
    def base(self) -> Datum:
        q = self.quantity.to_base_units()
        d = Datum(self.symbol, q.magnitude, q.units)
        return d

    @property
    def dds(self) -> DatumDefString:
        return self._dds
