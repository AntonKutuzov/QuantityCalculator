from __future__ import annotations

from pint import Quantity

from QCalculator.AbstractDatum import AbstractDatum
from QCalculator.DefStrings.DatumDefString import DatumDefString
from QCalculator import DEF_UR
from QCalculator.util import validate_type



class Datum(AbstractDatum, qds=DatumDefString, ureg=DEF_UR):
    def __init__(self, dds: str, *, sympy_safe: bool = True):
        super().__init__(dds, sympy_safe=sympy_safe)

    def __str__(self):
        return f'{self.variable} = {self.value} {self.units}'

    def __eq__(self, other: Datum):
        if not isinstance(other, Datum):
            raise TypeError(f'Expected "Datum", got: "{type(other)}".')

        from math import isclose

        conditions = [
            self.units == self.ureg.Unit(other.units),  # bcs other.unit is not str, but Unit
            isclose(self.value, other.value),
            self.variable == other.variable
        ]

        return all(conditions)


    @classmethod
    def from_quantity(cls, var: str, q: Quantity, *, sympy_safe: bool = True, **kwargs) -> Datum:
        validate_type(var, str)
        validate_type(q, Quantity)
        validate_type(sympy_safe, bool)

        return cls(f'{var} = {q.magnitude} {q.units}', sympy_safe=sympy_safe)

    @property
    def base(self) -> Datum:
        q = self.quantity.to_base_units()
        d = self.from_quantity(self.variable, q, sympy_safe=self._sympy_safe)
        return d

    @property
    def dds(self) -> DatumDefString:
        return self._dds



if __name__ == '__main__':
    d = Datum('m = 50 g')
    print(d.variable, d.value, d.units)
    print(d.base)
    print(d.dds)
