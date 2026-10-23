from __future__ import annotations
from abc import abstractmethod, ABC

from pint import Quantity, Unit, UndefinedUnitError, DimensionalityError
from math import isnan, isinf

from QCalculator.DefStrings.QDefString import QDefString
from QCalculator.util import (validate_type, check_unit_validity)
from QCalculator.Exceptions.DatumExceptions import (
    UndefinedUnit, IncompatibleUnits)



class AbstractDatum(ABC):
    def __new__(
            cls,
            dds: str,
            *args,
            sympy_safe: bool = True,
            **kwargs
    ) -> object:
        cls.qds(dds, sympy_safe=sympy_safe)  # yes, QDS is not callable, but subclasses are
        return super().__new__(cls)


    def __init_subclass__(
            cls,
            qds: type[QDefString],
            **kwargs
    ) -> None:
        cls.ureg = qds.ureg
        cls.qds = qds  # we are working with the class itself here, not instance
        super().__init_subclass__()


    def __init__(
            self,
            dds: str,
            *args,
            sympy_safe: bool = True,
            **kwargs
    ) -> None:
        validate_type(sympy_safe, bool)
        self._sympy_safe = sympy_safe
        self._dds = self.qds(dds, sympy_safe=sympy_safe)

        # if sympy_safe:
        #     self._check_sympy_safety()

        super().__init__()


    @abstractmethod
    def __str__(self) -> bool:
        ...

    @abstractmethod
    def __eq__(self, other: AbstractDatum) -> bool:
        ...

    @classmethod
    @abstractmethod
    def from_quantity(cls, var: str, q: Quantity, *, sympy_safe: bool, **kwargs) -> AbstractDatum:
        ...

    # ================================================================================================== PRIVATE HELPERS
    @classmethod
    def _normalize_units(cls, u: str | Unit) -> Unit:
        validate_type(u, (str, Unit))
        check_unit_validity(cls, u)

        try:
            return cls.ureg.parse_units(str(u))

        except UndefinedUnitError:
            raise UndefinedUnit(f'The units given for that Datum definition string do not exist: "{u}".')


    # =================================================================================================== PUBLIC METHODS
    def to(self, units: str | Unit) -> AbstractDatum:
        validate_type(units, (str, Unit))
        check_unit_validity(self.__class__, units)

        try:
            new_q = self.quantity.to(units)

        except DimensionalityError as e:
            raise IncompatibleUnits(from_unit=str(self.units), to_unit=str(units)) from e

        return self.from_quantity(self.variable, new_q, sympy_safe=self._sympy_safe)

    def scale(self, factor: float|int) -> AbstractDatum:
        validate_type(factor, (float, int))

        if isnan(factor) or isinf(factor):
            raise ValueError('"factor" must be a real number.')

        return self.from_quantity(self.variable, factor * self.quantity, sympy_safe=self._sympy_safe)


    def compatible_units(self, other: AbstractDatum|Quantity|str|Unit) -> bool:
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
        return self.ureg.parse_units(self.dds.units)

    @property
    @abstractmethod
    def base(self) -> AbstractDatum:
        q = self.quantity.to_base_units()
        d = self.from_quantity(self.variable, q, sympy_safe=self._sympy_safe)
        return d

    @property
    @abstractmethod
    def dds(self) -> QDefString:
        return self._dds