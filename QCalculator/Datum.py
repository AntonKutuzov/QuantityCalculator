from __future__ import annotations

from pint import Quantity

from QCalculator import AbstractDatum
from QCalculator.DefStrings import DatumDefString
from QCalculator.util import validate_type


class Datum(AbstractDatum):
    ddef = DatumDefString
    spec = ddef.spec

    def _from_quantity(self, var: str, q: Quantity, *args, **kwargs) -> Datum:
        return type(self).from_quantity(
            var=var,
            q=q
        )

    @classmethod
    def from_quantity(cls, var: str, q: Quantity, *args, **kwargs) -> Datum:
        validate_type(var, str)
        validate_type(q, Quantity)

        return cls(f'{var} = {q.magnitude} {q.units}')
