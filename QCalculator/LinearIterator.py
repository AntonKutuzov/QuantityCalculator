from QCalculator import Formula, Datum
from QCalculator.Exceptions.DatumExceptions import InvalidDatumDefString
from QCalculator.Exceptions.LinearIteratorExceptions import (
    NoValueError,
    UnusedSymbolError,
    IncompatibleUnitsError,
    RewritingError,
    FormulasNotIndicated,
    UnreachableTarget
)

from typing import List, Dict, Optional, Set, overload, Tuple
from collections.abc import Iterable, Sequence
from pint import Unit
from copy import deepcopy


class LinearIterator:
    def __init__(self, formulas: List[str], ref_units: Optional[Dict[str|Tuple, str|Unit]] = None) -> None:
        self._formulas = self._normalize_formulas(formulas, ref_units)
        self._ref_units = self._select_units() if ref_units is not None else None
        self._data: Dict[str, Datum] = dict()
        self._target = None

    # ================================================================================================== PRIVATE HELPERS
    def _select_units(self) -> Dict[str, Optional[str]]:
        present_units = dict()

        for s in self.symbols:
            for f in self.formulas:
                if s not in present_units and s in f.symbols:
                    u = f._ref_units[s]
                    present_units[s] = u

        return present_units

    @staticmethod
    def _normalize_formulas(f: List[str], u: Dict[str, str]) -> Set[Formula]:
        fs = set()

        if not f:
            raise FormulasNotIndicated()

        for old_f in f:
            if isinstance(old_f, str):
                new_f = Formula(old_f, ref_units=u)

                fs.add(new_f)
            else:
                raise TypeError(f'Expected type "str", got "{type(f)}".')

        return fs

    def _confirm_symbol(self, var: str, raise_exception: bool = True) -> bool:
        if not Datum._confirm_symbol(var, raise_exception=False):
            raise InvalidDatumDefString(string=var, details=f'The symbol "{var}" cannot be used.')

        for f in self.formulas:
            if var in f.symbols:
                return True
        else:
            if raise_exception:
                raise UnusedSymbolError(symbol=var)
            else:
                return False

    def _confirm_units(self, var: str, u: str|Unit, raise_exception: bool = True) -> bool:
        units = Datum.normalize_units(u)

        if self._ref_units is not None:
            res = units.is_compatible_with(self._ref_units[var])

            if raise_exception and not res:
                raise IncompatibleUnitsError(var=var, units=units, ref=self._ref_units[var])
            else:
                return res
        else:
            return True


    # =================================================================================================== READ AND WRITE
    def write(self,
              *data: Datum|str,
              rewrite: bool = False
              ) -> None:

        for d in data:
            if not isinstance(d, (Datum, str)):
                raise TypeError(f'Expected "Datum" or "str", got: "{type(d)}".')

            d = Datum.as_datum(d)
            self._confirm_symbol(d.symbol)
            self._confirm_units(d.symbol, d.units)

            if self.has_value(d.symbol):
                if rewrite:
                    self.erase(d.symbol)
                else:
                    old_datum = self.read(d.symbol)
                    raise RewritingError(var=d.symbol, old=old_datum)

            self._data.update({d.symbol : d})

            for f in self._formulas:
                if d.symbol in f.symbols:
                    f.write(d, rewrite=rewrite)

    @overload
    def read(self, var: str, units: Optional[str] = None) -> Datum:
        ...

    @overload
    def read(self, var: List[str], units: Optional[List[str]] = None) -> Dict[str, Datum]:
        ...

    def read(self,
             var: str|List[str],
             units: Optional[str | Unit | List[str|Unit]] = None
             ) -> Datum | Dict[str, Datum]:

        if isinstance(var, str):
            self._confirm_symbol(var)

            if self.has_value(var):
                d = self._data[var]

                if units is not None:
                    self._confirm_units(var, units)
                    d.ito(units)

                return d
            else:
                raise NoValueError(symbol=var)

        elif isinstance(var, list):
            if units is None:
                units = len(var)*[None]  # because in the next if- units must be a list

            if len(var) == len(units):
                res = dict()
                for v, u in zip(var, units):
                    r = self.read(v, u)
                    res[v] = r

                return res
            else:
                raise ValueError('The lengths of the "var" and "units" lists must be the same.')
        else:
            raise TypeError('The read() method accepts its parameters either as string or as lists of strings.')

    @overload
    def erase(self) -> None:
        ...

    @overload
    def erase(self, var: str) -> None:
        ...

    @overload
    def erase(self, var: List[str]) -> None:
        ...

    def erase(self, var: Optional[Iterable[str] | str] = None) -> None:
        if isinstance(var, str):
            if self.has_value(var):
                d = self.read(var)  # variable is confirmed here
                self._data.pop(d.symbol)

                for f in self._formulas:
                    if var in f.symbols and f.has_value(var):
                        f.erase(var)

        elif isinstance(var, Iterable):
            for s in var:
                self.erase(s)

        elif var is None:
            self.erase(self.symbols)

        else:
            raise TypeError(f'Expected "str" or "Iterable[str]", got "{type(var)}".')


    # ========================================================================================================= ANALYSIS
    @overload
    def has_value(self, var: str) -> bool:
        ...

    @overload
    def has_value(self, var: Sequence[str]) -> List[bool]:
        ...

    def has_value(self, var: str|Sequence[str]) -> bool|List[bool]:
        if isinstance(var, str):
            self._confirm_symbol(var)
            return self._data.get(var) is not None

        elif isinstance(var, Sequence):
            hvl = list()
            for v in var:
                hv = self.has_value(v)
                hvl.append(hv)
            return hvl

        else:
            raise TypeError(f'Expected "str" or "Sequence[str]", got "{type(var)}".')

    # ===================================================================================================== CALCULATIONS
    def iter(self) -> Dict[str, Datum]:
        """
        Takes all solvable equations in the LI and solves them **once**. Returns all the obtained
        Datum instances.

        :return: dict of newly obtained Datum instances, Dict[str, Datum]
        """

        res = dict()
        for f in self.solvables:
            r = f.solve(rounding=False)
            res.update(r)
        return res

    def solve(self) -> Optional[Datum]:
        tempvars = list()

        while self.solvables:
            res = self.iter()

            self.write(*res.values())

            if self.target is None:  # if .target is None, it has to attribute .symbol => another if-statement
                continue
            elif self.has_value(self.target.symbol):
                solution = self.read(self.target.symbol, self.target.units)
                return solution
            else:  # if no value
                continue

        if self.target is None:
            return None
        else:
            raise UnreachableTarget(target=self.target.symbol)


    # ======================================================================================================= PROPERTIES
    @property
    def solvables(self) -> Set[Formula]:
        solvable_eqs = set()

        for f in self.formulas:
            if f.solvable and not f.all_values:
                solvable_eqs.add(f)

        return solvable_eqs

    @property
    def data(self) -> Dict[str, Datum]:
        return deepcopy(self._data)

    @property
    def symbols(self) -> Set[str]:
        symbols = set()

        for f in self.formulas:
            for s in f.symbols:
                symbols.add(s)

        return symbols

    @property
    def formulas(self) -> Set[Formula]:
        return deepcopy(self._formulas)

    @property
    def target(self) -> Datum:
        return self._target

    @target.setter
    def target(self, datum: Datum|str) -> None:
        # runs type check, relevant string or symbol check
        datum = Datum.as_datum(datum)
        self._confirm_symbol(datum.symbol)
        self._confirm_units(datum.symbol, datum.units)
        self._target = datum
