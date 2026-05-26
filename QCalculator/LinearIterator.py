from QCalculator import Formula, Datum
from QCalculator.Exceptions.DatumExceptions import InvalidSymbol
from QCalculator.Exceptions.LinearIteratorExceptions import (
    NoValueError,
    UnusedSymbolError,
    IncompatibleUnitsError,
    RewritingError,
    FormulasNotIndicated,
    UnreachableTarget
)

from typing import List, Dict, Tuple, Optional, Set, overload
from pint import Unit
from copy import copy, deepcopy


class LinearIterator:
    def __init__(self, formulas: List[str], ref_units: Optional[Dict[str, str]] = None) -> None:
        self._formulas = self._normalize_formulas(formulas, ref_units)
        self._ref_units = self._select_units() if ref_units is not None else None
        self._data = set()
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
        if Datum._symbol_forbidden(var):
            raise InvalidSymbol(var=var, details='Cannot use spaces and empty strings to define Datum.')

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

            self._data.add(d)

            for f in self._formulas:
                if d.symbol in f.symbols:
                    f.write(d, rewrite=rewrite)

    @overload
    def read(self, var: str, units: Optional[str] = None) -> Datum:
        ...

    @overload
    def read(self, var: List[str], units: Optional[List[str]] = None) -> List[Datum]:
        ...

    def read(self,
             var: str|List[str],
             units: Optional[str | Unit | List[str|Unit]] = None
             ) -> Datum | List[Datum]:

        if isinstance(var, str):
            self._confirm_symbol(var)

            if self.has_value(var):
                d = filter(lambda d: d.symbol == var, self.data)
                d = copy(list(d)[0])  # normally, only one Datum with any symbol is allowed in self._data

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
                res = list()
                for v, u in zip(var, units):
                    r = self.read(v, u)
                    res.append(r)

                return res
            else:
                raise ValueError('The lengths of the "var" and "units" lists must be the same.')
        else:
            raise TypeError('The read() method accepts its parameters either as string or as lists of strings.')

    def erase(self, var: Optional[str] = None) -> None:
        if var is not None:
            if self.has_value(var):
                d = self.read(var)  # variable is confirmed here
                self._data.remove(d)

                for f in self.formulas:
                    if var in f.symbols and f.has_value(var):
                        f.erase(var)

            elif var in self.symbols:
                raise NoValueError(symbol=var)

            else:
                raise UnusedSymbolError(symbol=var)

        else:
            for s in self.symbols:
                if self.has_value(s):
                    self.erase(s)


    # ========================================================================================================= ANALYSIS
    def has_value(self, var: str) -> bool:
        self._confirm_symbol(var)
        return len(list(filter(lambda d: d.symbol == var, self.data))) > 0

    # ===================================================================================================== CALCULATIONS
    def iter(self) -> Set[Datum]:
        """
        Takes all solvable equations in the LI and solves them **once**. Returns all the obtained
        Datum instances.

        :return: set of newly obtained Datum instances
        """

        res = set()
        for f in self.solvables:
            r = f.solve(rounding=False)
            res = res.union(r)  # since each Datum in LI must have its own symbol, no overlaps are expected
        return res

    def solve(self) -> Optional[Datum]:
        while self.solvables:
            res = self.iter()

            self.write(*res)

            if self.target is None:  # if .target is None, it has to attribute .symbol => another if-statement
                continue
            elif self.has_value(self.target.symbol):
                return self.read(self.target.symbol, self.target.units)
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
    def data(self) -> Set[Datum]:
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
        if isinstance(datum, (str, Datum)):
            datum = Datum.as_datum(datum)
            self._confirm_symbol(datum.symbol)
            self._confirm_units(datum.symbol, datum.units)
            self._target = datum
        else:
            raise TypeError(f'Expected "str" or "Datum", got "{type(datum)}".')



if __name__ == "__main__":
    fs = ['n = mps/M', 'wmm = mps/msm', 'n = Np/NA']
    us = {
        'wmm':'',
        'mps':'g',
        'n':'mole',
        'msm':'g',
        'M':'g/mole',
        'Np':'',
        'NA':'mole**-1'
    }
    data = [
        'wmm = 0.1',
        'msm = 30 g',
        'M = 18 g/mole',
        'NA = 6.02e23 1/mole',
        'Np = 1'
    ]

    li = LinearIterator(fs, us)
    li.target = 'mps = 0.01 g'
    li.write(*data)
    print(li.solve())
