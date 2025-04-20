from pint import Quantity, Unit, UnitRegistry


class Datum:
    def __init__(self, symbol: str, value: float|int, unit: str):
        self._ureg = UnitRegistry(system='SI')

        self._symbol = symbol
        self._value = value
        self._unit = self._ureg.Unit(unit)
        self._base_unit = (1*self._unit).to_base_units().units
        self._ZERO_TOLERANCE_EXPONENT = 3

    def __str__(self) -> str:
        return f'{self.symbol} = {self.value} {self.unit}'

    def __eq__(self, other: 'Datum'):
        from math import isclose

        if not self._ZTE_test():
            raise Exception()

        conditions = (
            self.symbol == other._symbol,
            isclose(self.value, other.value, rel_tol=eval(f'10E{self._ZERO_TOLERANCE_EXPONENT}')),
            self.quantity.to_base_units() == other.quantity.to_base_units()
        )

        return all(conditions)

    # ========================================================================================== arithmetical operations
    def __truediv__(self, other) -> Quantity:
        if isinstance(other, Datum):
            return self.quantity / other.quantity
        elif isinstance(other, Quantity|int|float):
            return self.quantity / other
        else:
            raise Exception(f'Unsupported operation: division of Datum by {type(other)}.')

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __mul__(self, other) -> Quantity:
        if isinstance(other, Datum):
            return self.quantity * other.quantity
        elif isinstance(other, Quantity|int|float):
            return self.quantity * other
        else:
            raise Exception(f'Unsupported operation: multiplication of Datum by {type(other)}.')

    def __rmul__(self, other):
        return self.__mul__(other)

    def __sub__(self, other) -> Quantity:
        if isinstance(other, Datum):
            return self.quantity - other.quantity
        elif isinstance(other, Quantity):
            return self.quantity - other
        else:
            raise Exception(f'Unsupported operation: subtraction of Datum by {type(other)}.')

    def __rsub__(self, other):
        return self.__sub__(other)

    def __add__(self, other) -> Quantity:
        if isinstance(other, Datum):
            return self.quantity + other.quantity
        elif isinstance(other, Quantity):
            return self.quantity + other
        else:
            raise Exception(f'Unsupported operation: multiplication of Datum by {type(other)}.')

    def __radd__(self, other):
        return self.__add__(other)

    def _ZTE_test(self) -> bool:
        zte = self._ZERO_TOLERANCE_EXPONENT

        if isinstance(zte, int) and 0 < zte < 100:
            return True
        else:
            return False

    # ================================================================================================= analysis methods
    @staticmethod
    def get_decimals(value: float) -> int:
        if value == 0.0:
            raise Exception('Cannot determine decimal digits from a value of 0.')
        str_value = str(float(value))

        if 'e' in str_value:
            decimals = str_value.split('e')[1][1:] # to account for both e+ and e-
            return int(decimals)
        else:
            decimals = str_value.split('.')[1]
            return len(decimals)

    # =================================================================================================== changing value
    def to(self, unit: str, in_place: bool = False) -> 'Datum':
        u = self._ureg.Unit(unit)
        q = self.quantity

        if q.is_compatible_with(u):
            new_q = q.to(u)
        else:
            raise Exception(f'Incompatible units: "{self.unit}" and "{unit}"')

        if in_place:
            self._value = new_q.magnitude
            self._unit = new_q.units
        else:
            return Datum(self.symbol, new_q.magnitude, new_q.units)

    def to_base_units(self, in_place: bool = False) -> 'Datum':
        return self.to(self.base_unit, in_place=in_place)

    # ======================================================================================================= properties
    @property
    def quantity(self) -> Quantity:
        return self._value * Unit(self._unit)

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def value(self) -> float|int:
        return self._value

    @property
    def unit(self) -> str:
        return str(self._unit)

    @property
    def base_unit(self) -> str:
        return str(self._base_unit)

    @property
    def num_decimals(self) -> int:
        return self.get_decimals(self.value)
