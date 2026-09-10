from pint import UnitRegistry, Unit
from pint.errors import UndefinedUnitError
from typing import Literal
from collections import  namedtuple

from QCalculator.Exceptions.DatumExceptions import (
    InvalidDatumDefString,
    InvalidUnitExpression,
    UndefinedUnit
)


class DatumDefString(str):
    from re import compile

    ureg = UnitRegistry(system='SI')

    _symbol_str = r'(?P<symbol>[a-z]|[A-Z]+)'
    _subscript_str = r'(?P<sub>[a-zA-Z0-9]+)'
    _variable_str = fr"(?P<variable>{_symbol_str}(_{_subscript_str})?)"
    _whole_str = r'-?(?P<whole>\d+)'
    _decimal_str = r'(?P<decimal>\d+)'
    _exponent_str = r'(?P<exponent>[-+]?\d+)'
    _value_str = fr"(?P<value>{_whole_str}(\.{_decimal_str})?((E|e){_exponent_str})?)"
    _units_str = r'(?P<units>[^\s](.*[^\s])?)'
    _dds_str = fr"{_variable_str} += +{_value_str}( +{_units_str})?"

    _symbol = compile(_symbol_str)
    _subscript = compile(_subscript_str)
    _variable = compile(_variable_str)
    _whole = compile(_whole_str)
    _decimal = compile(_decimal_str)
    _value = compile(_value_str)
    _units = compile(_units_str)
    _dds = compile(_dds_str)

    _PATTERNS = namedtuple('strings', 'symbol, subscript, variable, whole, decimal, value, units, dds')
    patterns = _PATTERNS(_symbol, _subscript, _variable, _whole, _decimal, _value, _units, _dds)


    def __init__(self, dds: str) -> None:
        if not isinstance(dds, str):
            raise InvalidDatumDefString(f'Datum definition string must be of type str, got: "{type(dds)}".')

        match = DatumDefString._dds.fullmatch(dds)
        if match is None:
            raise InvalidDatumDefString(dds)
        else:
            self._dds = match
            self._string = dds

        self.check_unit_validity(self.units)

    def __str__(self):
        return self.string

    @classmethod
    def check_unit_validity(cls, units: str | Unit) -> None:
        if not isinstance(units, (str, Unit)):
            raise TypeError(f'Expected "str" or "pint.Unit", got: "{units}".')

        units = str(units)

        try:
            cls.ureg.parse_units(units)

        except (AssertionError, ValueError, TypeError):
            raise InvalidUnitExpression(f'The units given for that Datum definition string is an invalid string: "{units}".')

        except UndefinedUnitError:
            raise UndefinedUnit(f'The units given for that Datum definition string do not exist: "{units}".')


    @property
    def symbol(self) -> str:
        return str(self._dds.group('symbol'))

    @property
    def subscript(self) -> str:
        s = self._dds.group('sub')

        if s is None:
            return ''
        else:
            return str(s)

    @property
    def variable(self) -> str:
        return str(self._dds.group('variable'))

    @property
    def value(self) -> float:
        return float(self._dds.group('value'))

    @property
    def whole(self) -> int:
        return int(self._dds.group('whole'))

    @property
    def decimal(self) -> float:
        dec = self._dds.group('decimal')

        if dec is None:
            return 0.0
        else:
            return float(f'0.{dec}')

    @property
    def sign(self) -> Literal[1, -1]:
        v = self._dds.group('value')
        if v[0] == '-':
            return -1
        else:
            return 1

    @property
    def exponent(self) -> int:
        e = self._dds.group('exponent')

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
            return len(str(dec)) - 2

    @property
    def units(self) -> str:
        u = self._dds.group('units')

        if u is None:
            u = 'dimensionless'
        else:
            u = str(u)

            while ' ' in u:
                u = u.replace(' ', '')

        return u


    @property
    def string(self) -> str:
        return f'{self.variable} = {self.value} {self.units}'


    @property
    def raw_string(self) -> str:
        return str(self._string)


if __name__ == '__main__':
    dds = DatumDefString(f'g_Moon1 = {9.81/6} m/s**2')
    print(dds)
