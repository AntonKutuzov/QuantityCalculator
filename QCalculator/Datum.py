# imports


# class description
"""
Purpose: join sympy Symbol and pint Unit in one class to represent a variable that is both capable of handling units
(as pint.Quantity) and is possible to use in smypy computations (done later in Formula class).

Invariants
    - symbol (str; must be possible to use in sympy expressions)
    - base units (str, Unit; is set up at the beginning, cannot be changed. Always a base SI unit)
    = All units inside the class are instances of local UnitRegistry so that pint allows operations on them

Public methods
    # initializers
        __init__(symbol: str, magnitude: float|int, units: str|Unit) -> None
        .from_string(datum: str) -> Datum
        .from_quantity(quantity: pint.Quantity, symbol: str) -> Datum
        .as_datum(d: Datum|Quantity|str, symbol: str = '') -> Datum

    # normalization
        .normalize_units(u: str|Unit) -> Datum.ureg.Unit

    # Datum–Quantity and Datum–Datum arithmetics
        .div(other: Datum|Quantity) -> Quantity
        .rdiv(other: Datum|Quantity) -> Quantity
        .mul(other: Datum|Quantity) -> Quantity
        .add(other: Datum|Quantity) -> Quantity
        .sub(other: Datum|Quantity) -> Quantity
        .rsub(other: Datum|Quantity) -> Quantity

    # Datum analysis
        .get_decimals(value: float|int|str) -> int
        .is_compatible(other: Datum|Quantity|str|Unit) -> bool

    # mutators
        .to(units: str|Unit, in_place: bool = False) -> Optional[Datum]
        .ito(units: str|Unit) -> None
        .to_base_units(in_place: bool = False) -> Optional[Datum]
        .ito_base_units() -> None
        .scale(factor: float|int, in_place: bool = False) -> Optional[Datum]
        .iscale(factor: float|int) -> None

    # properties
        .quantity -> Quantity
        .symbol -> str
        .sp_symbol -> sympy.Symbol
        .magnitude -> float|int
        .units -> Unit
        .units_str -> str
        .base_quantity -> Quantity
        .base_units -> Unit
        .base_units_str -> str
        .num_decimals -> int
"""


from __future__ import annotations

from pint import UnitRegistry, Quantity, Unit, DimensionalityError
from sympy.parsing.sympy_parser import parse_expr
from sympy import Symbol
from copy import copy
from typing import Optional, Tuple

from QCalculator.Exceptions.DatumExceptions import InvalidSymbol, InitializationError, IncompatibleUnits


# class implementation
class Datum:
    ureg = UnitRegistry(system='SI')
    _FORBIDDEN_SYMBOLS: Tuple[str] = ('', ' ')
    ROUNDING: int = 15
    # is needed to remove 1's after calculations in Formula. Removal is needed for hash function to work properly
    # Do not set ROUNDING to more than 15. If equal Datums a said to be different, try setting it to 14 or 13.

    def __init__(self,
                 symbol: str,
                 magnitude: float|int,
                 units: str|Unit
                 ) -> None:

        if not isinstance(symbol, str):
            raise TypeError('Symbol for Datum must be given as a string.')

        if Datum._sympy_symbol_check(symbol) and not Datum._symbol_forbidden(symbol):
            self._symbol: str = symbol
            self._magnitude: float = float(magnitude)

            try:
                self._units: Unit = Datum.normalize_units(units)
            except TypeError as te:
                raise InitializationError((symbol, magnitude, str(units)), details='Check that the units are of correct type.') from te
        else:
            raise InitializationError(
                symbol,
                details=f'The symbol "{symbol}" cannot be used in sympy expressions.'
            )

    @staticmethod
    def from_quantity(symbol: str, quantity: Quantity) -> Datum:
        sp_check = Datum._sympy_symbol_check(symbol)
        fs_check = not Datum._symbol_forbidden(symbol)

        if sp_check and fs_check:
            units = Datum.normalize_units(quantity.units)
            return Datum(symbol, quantity.magnitude, units)

        elif not sp_check:
            raise InitializationError(
                symbol,
                details='Cannot create Datum with this symbol, because it cannot be used in sympy expressions.'
            )

        elif not fs_check:
            raise InitializationError(
                symbol,
                details='Cannot create Datum with this symbol.'
            )

        else:
            raise Exception('This is not supposed to happen. There is a bug in the code.')


    @staticmethod
    def from_string(datum: str) -> Datum:
        """The general format is "<symbol> = <int or float number> <units>". Spaces are mandatory."""
        try:
            symbol, rest = datum.split('=')
            symbol = symbol.strip(' ')

            if Datum._symbol_forbidden(symbol):
                raise InitializationError(symbol, details='This symbol cannot be used for instantiating Datum.')

            rest = rest.strip(' ')
            rest += ' '  # to make it possible to convert ' ' to 'dimensionless'
            number, units = rest.split(' ', maxsplit=1)

            try:
                number = float(number)
            except ValueError as e:
                if '*' or '^' in number:
                    raise InitializationError(number, details=''
                                                            'To indicate powers use e-notation (ae+b or ae-b).'
                                                            ' Check that you have a space between the magnitude and the units of the Datum.'
                                                            '') from e
                else:
                    raise InitializationError(number, details='Check that you have a space between number and units. "10km" is wrong, "10 km" is correct.') from e

            units = Datum.normalize_units(units)

        except ValueError as e:
            raise InitializationError(
                datum,
                details=f'Invalid Datum definition string. Check the format: <symbol> = <magnitude> <units> (including spaces):'
                        f' "{datum}".'
            ) from e

        return Datum(symbol, number, units)

    @staticmethod
    def as_datum(
            d: Datum|Quantity|str,
            symbol: str = ''
    ) -> Datum:
        """Depending on the type of the parameter "d", uses either .from_string() or .from_quantity(), or just returns
        the copy of the parameter so that the object returned is always a Datum instance. Passing Quantity instance also
        requires passing in "symbol" parameter."""

        if isinstance(d, Datum):
            newd = Datum(d.symbol, d.magnitude, d.units)
            return newd
            # so that changes of the returned object do not affect the original one and vice versa
            # copy() is not used, because magnitude must be rounded initially.
        elif isinstance(d, Quantity):
            return Datum.from_quantity(symbol, d)
        elif isinstance(d, str):
            return Datum.from_string(d)
        else:
            raise InitializationError(
                type(d),
                details=f'The parameter "d" has a wrong type. Expected "Datum", "str" or "pint.Quantity".'
            )


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

        from math import isclose

        self_q = self.quantity
        other_q = other.quantity

        self_mag = self_q.to_base_units().magnitude
        other_mag = other_q.to_base_units().magnitude

        conditions = [
            self.base_units == other.base_units,
            isclose(self_mag, other_mag),
            self.symbol == other.symbol
        ]
        return all(conditions)

    def __hash__(self):
        return hash(self.symbol)
        # only symbol is used for hash() because
        # (1) float numbers obtained from calculations have tolerance and thus are not perfectly equal -> different hash
        # (2) same units expressed in different ways (used as strings of course) -> different strings -> different hash

    # arithmetics
    def div(self, other: Datum|Quantity) -> Quantity:
        q = Datum._get_quantity(other)
        res = self.quantity / q
        res.ito_reduced_units()
        return res

    def rdiv(self, other: Datum|Quantity) -> Quantity:
        q = Datum._get_quantity(other)
        res = q / self.quantity
        res.ito_reduced_units()
        return res

    def mul(self, other: Datum|Quantity) -> Quantity:
        q = Datum._get_quantity(other)
        res = q * self.quantity
        res.ito_reduced_units()
        return res

    def add(self, other: Datum|Quantity) -> Quantity:
        q = Datum._get_quantity(other)

        if self.is_compatible(other):
            return self.quantity + q
        else:
            raise IncompatibleUnits(
                from_unit=self.units_str,
                to_unit=str(other.units),
            )

    def sub(self, other: Datum|Quantity) -> Quantity:
        q = Datum._get_quantity(other)

        if self.is_compatible(other):
            return self.quantity - q
        else:
            raise IncompatibleUnits(
                from_unit=self.units_str,
                to_unit=str(other.units),
            )

    def rsub(self, other: Datum|Quantity) -> Quantity:
        q = Datum._get_quantity(other)

        if self.is_compatible(other):
            return q - self.quantity
        else:
            raise IncompatibleUnits(
                from_unit=self.units_str,
                to_unit=str(other.units),
            )

    # mutators
    def to(self, unit: str | Datum.ureg.Unit, in_place: bool = False) -> Optional[Datum]:
        try:
            new_q = self.quantity.to(unit)
            if in_place:
                self._magnitude = new_q.magnitude
                self._units = new_q.units
            else:
                return Datum.from_quantity(self.symbol, new_q)
        except DimensionalityError as e:
            raise IncompatibleUnits(from_unit=self.units_str, to_unit=unit) from e

    def ito(self, unit: str | Datum.ureg.Unit) -> None:
        self.to(unit, in_place=True)

    def to_base_units(self, in_place: bool = False) -> Optional[Datum]:
        return self.to(self.base_units_str, in_place=in_place)

    def ito_base_units(self) -> None:
        self.to(self.base_units, in_place=True)

    def scale(self, factor: float|int, in_place: bool = False) -> Optional[Datum]:
        if not isinstance(factor, (float, int)):
            raise TypeError(f'Expected float or int, got "{type(factor)}".')

        if in_place:
            self._magnitude = factor * self.magnitude
            return None
        else:
            return Datum(self.symbol, self.magnitude * factor, self.units_str)

    def iscale(self, factor: float|int) -> None:
        self.scale(factor, in_place=True)

    def pow(self, power: float|int) -> Quantity:
        q = self.quantity
        return q ** power


    # normalizers
    @staticmethod
    def normalize_units(u: str|Unit|Quantity) -> Unit|Quantity:
        if isinstance(u, (str, Unit)):
            return Datum.ureg.Unit(u)

        elif isinstance(u, Quantity):
            units = Datum.normalize_units(u.units)
            return u.magnitude * units

        else:
            raise TypeError(f'Cannot normalize units of {type(u)}')

    # Datum analysis
    @staticmethod
    def get_decimals(value: float|int|str) -> int:
        """
        Returns a number of decimal places in the provided float number. Works only if the number is not a zero.
        For example, returns 3 for 0.001 and 1 for 0.1. Also returns 0 for integers.
        """

        # the isinstance(value, bool) checks are needed because Python replaces
        # ints and floats with bools automatically
        if isinstance(value, int) and not isinstance(value, bool):
            return 0

        elif value == 0.0 and not isinstance(value, bool):
            raise ValueError('Cannot determine significant digits. Choose a non-zero magnitude.')

        if isinstance(value, float):
            str_value = str(float(value))  # to quickly check for e-notation instead of 10**2 or 10^2
            if int(value) == value:  # i.e. if it is an integer or a whole number, e.g. 2.0 or 10.0
                return 0

        elif isinstance(value, str):
            str_value = str(float(value))
            if '.' not in value:
                return 0  # because we then expect it to be an integer
                # placed after convertion to float to check that the string is truly a number, not a random 'huh'

        else:
            raise TypeError(f'Expected "float" or "str", got "{type(value)}".')

        if 'e' in str_value:
            decimals = str_value.split('e')[1][1:]  # to account for both e+ and e-
            return int(decimals)
        else:
            decimals = str_value.split('.')[1]
            return len(decimals)

    def is_compatible(self, other: Datum|Quantity|str|Unit) -> bool:
        """Checks whether the self Datum instance has compatible units with "other" object which encodes units."""

        if isinstance(other, (Datum, Quantity)):
            q = self._get_quantity(other)
            return self.units.is_compatible_with(q)
        elif isinstance(other, (str, Unit)):
            return self.units.is_compatible_with(other)
        else:
            raise TypeError(f'Expected "Datum", "pint.Quantity", "str", or "Datum.ureg.Unit", got "{type(other)}"')

    # private helpers
    @staticmethod
    def _sympy_symbol_check(symbol: str) -> bool:
        try:
            parse_expr(f'{symbol} - 1')
        except TypeError:
            return False
        return True

    @staticmethod
    def _symbol_forbidden(symbol: str) -> bool:
        """Returns True if the symbol is forbidden, False otherwise."""
        s = symbol.strip(' ')
        return s in Datum._FORBIDDEN_SYMBOLS

    @staticmethod
    def _get_quantity(d: Datum|Quantity) -> Quantity:
        if isinstance(d, Datum):
            return Datum.normalize_units(d.quantity)
        elif isinstance(d, Quantity):
            return Datum.normalize_units(d)
        else:
            raise TypeError(f'Expected Datum or pint.Quantity, got "{type(d)}".')

    # properties
    @property
    def quantity(self) -> Quantity:
        return self.magnitude * self.units

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def sp_symbol(self) -> Symbol:
        return Symbol(self.symbol)

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
    def base_quantity(self) -> Quantity:
        return self.quantity.to_base_units()

    @property
    def base_units(self) -> Unit:
        bq = self.base_quantity
        bu = bq.units
        return bu

    @property
    def base_units_str(self) -> str:
        return str(self.base_units)
