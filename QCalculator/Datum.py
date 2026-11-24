from __future__ import annotations

from pint import Quantity, Unit, DimensionalityError
from typing import Optional

from QCalculator import AbstractDatum
from QCalculator.DefStrings import DatumDefString
from QCalculator.Exceptions.QDefStringExceptions import IncompatibleUnits
from QCalculator.util import validate_type


class Datum(AbstractDatum):
    ddef = DatumDefString
    spec = ddef.spec

    def _from_quantity(self, var: str, q: Quantity, units: Optional[str | Unit] = None, *args, **kwargs) -> Datum:
        return type(self).from_quantity(
            var=var,
            q=q,
            units=units
        )

    @classmethod
    def from_quantity(cls, var: str, q: Quantity, units: Optional[str | Unit] = None, *args, **kwargs) -> Datum:
        validate_type(var, str)
        validate_type(q, Quantity)

        if units is not None:
            try:
                q.ito(units)
            except DimensionalityError:
                raise IncompatibleUnits(from_unit=q.units, to_unit=units)

        return cls(f'{var} = {q.magnitude} {q.units}')
