from __future__ import annotations

from QCalculator import Datum, DatumDefString, UnitDict
from QCalculator._util import validate_type, must_match

from typing import List, Optional, Dict, Tuple, Callable
from copy import deepcopy
from sympy import parse_expr, Eq, solve, Symbol, Number, simplify, im
from pint import Quantity
from collections import namedtuple
from math import isclose



class Formula:
    _FILTERS = namedtuple('_FILTERS', 'REAL_ONLY, POSITIVES, NEGATIVES, NON_NEG, NON_POS, ZERO, NO_FILTER')

    filters = _FILTERS(
        lambda l: simplify(im(l)) == 0,
        lambda l: l > 0.0,
        lambda l: l < 0.0,
        lambda l: l >= 0.0,
        lambda l: l <= 0.0,
        lambda l: isclose(l, 0.0),
        lambda l: True
    )

    DEF_UNITS: Optional[UnitDict.UNITS_DICT] = None

    def __init__(
            self,
            formula: str,
            *,
            def_units: Optional[UnitDict.UNITS_DICT] = None,
            unit_by_symbol: bool = False
    ) -> None:

        self._eq: Eq
        self._make_sympy_eq(formula)
        self._ubs = unit_by_symbol
        self._data = list()
        self._target = None

        # Instance defu has priority over class-level defu. If both are None – then it's None
        self._defu: Optional[UnitDict] = None

        if def_units is not None:
            self._defu = UnitDict(def_units)
        elif self.DEF_UNITS is not None:
            self._defu = UnitDict(self.DEF_UNITS)
        else:
            pass


    def __contains__(self, item: str | Datum | DatumDefString):
        if isinstance(item, Datum | DatumDefString):
            item = Formula._to_Datum(item)

            for d in self.data:
                if d == item.base:
                    return True
            else:
                return False

        elif isinstance(item, str):
            for v in self.variables:
                if v == item:
                    return True
            else:
                return False

        else:
            raise TypeError(f'Expected "str", "Datum" or "DatumDefString", got "{type(item)}".')


    def __str__(self):
        return f'{self._eq.lhs} = {self._eq.rhs}'


    def __eq__(self, other: Formula) -> bool:
        validate_type(other, Formula)

        eq_var = self.variables[0]

        if eq_var in other:
            self_solved = solve(self.eq, eq_var)
            other_solved = solve(other.eq, eq_var)
            return self_solved == other_solved
        else:
            return False



    # ================================================================================================== PRIVATE METHODS
    @staticmethod
    def _to_Datum(dds: DatumDefString | str | Datum) -> Datum:
        if isinstance(dds, (str, DatumDefString)):
            return Datum(dds)

        elif isinstance(dds, Datum):
            return dds

        else:
            raise TypeError(f'Expected "str", "DatumDefString" or "Datum", got "{type(dds)}".')


    def _make_sympy_eq(self, expr: str, _evaluate: bool = False) -> None:
        if '=' in expr:
            lhs, rhs = expr.split('=')

            try:
                lhs = parse_expr(lhs)
                rhs = parse_expr(rhs)
            except (ValueError, SyntaxError):
                raise ValueError('InvalidFormula Exception')

            self._eq = Eq(lhs, rhs, evaluate=_evaluate)  # assigning here so that self.variables does not generate an error
        else:
            raise ValueError(f'An equation must have an equal sign: "{expr}".')

        # check that all variables fit the DDS requirements
        for v in self.variables:
            must_match('variable', v)


    # ================================================================================================= DATA I/O METHODS
    def write(
            self,
            *data: DatumDefString | str | Datum,
            rewrite: bool = False
    ) -> None:
        """
        Stores the indicated values in the Formula instance. The units of each variable are written to the default unit
        dict. If the dict is not present, it is created. If rewrite is True, and the same variables are written in the
        same function call, the last instance is saved.

        :param data:
        :param rewrite:
        :return:
        """

        """
        The methods goes through two major if-statements:
        (1) First it decides whether the units provided are compatible with default, if this check is possible.
        (2) Writes data or raises exception based on whether the units are compatible and whether the variable already
            has a value.
        """

        validate_type(rewrite, bool)

        for d in data:
            # define variables
            d = Formula._to_Datum(d)  # type of d validated here
            v = d.variable
            u = str(d.base.units)

            # try checking unit compatibility
            unit_compatible = True  # True by default, because False aborts writing.

            if self._defu is None:
                self._defu = UnitDict({v: u}, unit_by_symbol=self._ubs)
            # if defu is present, and there is a value
            elif self._defu.get(v):
                unit_compatible = self._defu.compatible_with_default(v, u)
            # if defu is present, but there's no value
            else:
                self._defu[v] = u

            # ! By now self._defu for sure exists with at least one value.

            # Anyway, check if the value is already written. If it is,...
            if self.has_value(v):
                # ...see if rewrite is False; if it is, raise exception.
                if not rewrite:
                    raise Exception(f'Cannot overwrite a variable that already has value: "{v}" in "{d}". "{self}".')
                # Otherwise, if units are compatible, erase old and write new.
                # (Which is also the case when we failed to check compatibility)
                elif unit_compatible:
                    self.erase(v)
                    self._data.append(d.base)
                # if not compatible, raise exception.
                else:
                    defu = self._defu.get(v)
                    raise ValueError(f'The units of variable "{v}" are not compatible with the default units "{defu}"')

            # If no value is written, but units are compatible, write the data.
            elif unit_compatible:
                # (Cannot move the writing operation out of the conditionals, because in case of abortion,
                # there must be no variable erased or written).
                self._data.append(d.base)

            # If not value is written, but units are NOT compatible, raise exception.
            else:
                defu = self._defu.get(v)
                raise Exception(f'The units for variable "{v}" "{d.units}" are not compatible with default units "{defu}".')


    def read(self, *variables: str, force_list: bool = False) -> Datum | List[Datum]:
        ret_list = list()

        for var in variables:
            validate_type(var, str)
            if var not in self:  # be careful with __contains__, it's tricky
                raise Exception(f'Variable "{var}" is not present in the formula: "{self}".')
            # no must_match, because "in self" goes through the self.variables list, and there all variables are checked

            v = list(filter(lambda dds: dds.variable == var, self.data))

            if len(v) == 0:
                raise ValueError(f'Variable "{var}" does not have a value.')
            if len(v) > 1:
                raise Exception(f'Duplicate found for variable "{v}".')
            else:
                ret_list.extend(v)

        if force_list:
            return ret_list
        elif len(ret_list) == 1:
            return ret_list[0]
        else:  # elif len > 1, not force_list
            return ret_list


    def erase(self, *var: str) -> None:
        for v in var:
            """
            The code here is almost copied from .read, because it must be possible to erase duplicates, but no
            possible to read them. Hence, .read cannot be used here.
            """

            validate_type(v, str)

            if v not in self:  # be careful with __contains__, it's tricky
                raise Exception(f'Variable "{v}" is not present in the formula: "{self}".')
            # no must_match needed, because self.variables only contains matched variables

            to_remove = list(filter(lambda dds: dds.variable == v, self.data))

            for tr in to_remove:  # a list is used in case we have duplicates
                self._data.remove(tr)




    # =================================================================================================== VALUE CHECKERS
    def is_consistent(self, silent_missing_value_error: bool = True) -> bool:
        """If all values are written, the two sides of the equation may not be equal to each other. This function
        checks that they are. **In case not all variables are present, returns True**"""

        from math import isclose

        if self.all_values:
            lhs = self.eq.lhs.subs(self.base_values)
            rhs = self.eq.rhs.subs(self.base_values)

            return isclose(rhs, lhs, rel_tol=1e-12, abs_tol=1e-15)
            # 15 digits are the last digit not affected by operations with float in Python (abs_tol).

        elif silent_missing_value_error:
            return True

        else:
            raise ValueError(f'Not all variables in the formula "{self}" have a value.')


    def has_value(self, *var: str, force_list: bool = False) -> bool | List[bool]:
        ret_list = list()

        for v in var:
            try:
                self.read(v)  # type and presence checks are performed here
            except ValueError:  # must later become specific NoValueError or smth similar
                ret_list.append(False)
                continue

            ret_list.append(True)

        if force_list:
            return ret_list
        elif len(ret_list) == 1:
            return ret_list[0]
        else:
            return ret_list



    # ============================================================================================ COMPUTATIONAL METHODS
    def eval_symbolic(self) -> List[Eq]:
        if self.target is None:
            raise Exception(f'Target not found for "{self}".')

        self.is_consistent(silent_missing_value_error=True)

        res = list()

        sols = solve(self.eq, self.target.variable)
        t = Symbol(self.target.variable)

        for s in sols:
            eq = Eq(t, s, evaluate=False)
            res.append(eq)

        return res


    def eval_numeric(self, *filters: Callable[[float], bool]) -> List[float]:
        # run all necessary checks
        if self.target is None:
            raise Exception(f'Target not found for "{self}".')

        self.is_consistent(silent_missing_value_error=True)

        # if the value is already written, just return it
        if self.has_value(self.target.variable):
            v = self.read(self.target.variable)
            return [float(v.value)]

        # if it wasn't written, estimate it. It is not necessary for the equation to be solvable at that moment
        else:
            vd = self.base_values
            eq = self.eq.subs(vd)

            sols = solve(eq, self.target.variable)

            native_sols = [(float(s) if isinstance(s, Number) else s) for s in sols]
            # filterable_sols = [sol for sol in native_sols if isinstance(sol, float)]

            for fil in filters:
                try:
                    native_sols = list(filter(fil, native_sols))
                except TypeError as e:
                    if e.args[0] == 'Formula.<lambda>() takes 1 positional argument but 2 were given':
                        raise ValueError('The filters must be accessed exclusively via class name, not instance name.')
                    else:
                        raise e

            return native_sols


    def solve(
            self,
            *filters: Callable[[float], bool],
            auto_determine_unknown: bool = True,
            round_to: int = 15,
            units: Optional[str] = None
    ) -> List[Datum]:

        AUTO_TARGET: bool = False

        if not self.solvable:
            raise Exception(f'Equation "{self}" is currently not solvable.')

        if self.target is None:
            if auto_determine_unknown:
                AUTO_TARGET = True
                self.target = self.unknown(round_to=round_to, units=units)
            else:
                raise Exception(f'Target not found for formula "{self}".')


        # "sols" can only be a float number since we used eval_numeric, we checked for equation being solvable,
        # and we filter for real numbers.
        sols = self.eval_numeric(Formula.filters.REAL_ONLY, *filters)

        res = list()

        for sol in sols:
            sol = float(sol)  # from sympy Float to Python's native float

            q = Quantity(sol, self.target.base.units)
            q.ito(self.target.units if units is None else units)
            q = round(q, self.target.dds.num_decimals if round_to >= 15 else round_to)
            d = Datum.from_quantity(self.target.variable, q)

            res.append(d)

        if AUTO_TARGET:
            self.target = None

        return res




    # ========================================================================================= METHODS DEDUCING UNKNOWN
    def unknown_vars(self) -> List[str]:
        vs = set(self.variables)
        ds = set([d.variable for d in self.data])

        vs.difference_update(ds)
        vs = list(vs)

        return vs


    def unknown(
            self,
            round_to: int = 15,
            units: Optional[str] = None,
    ) -> str:

        if not self.solvable:
            raise Exception(f'Cannot determine the unknown, equation ({self}) is currently not solvable.')
        if units is not None:
            validate_type(units, str)

        # getting the unknown variable
        unk = self.unknown_vars()[0]  # it must be 1 var, because eq is solvable

        # In case units are not specified, use other sources to get them.
        units = self._defu.unit_for_solvable_eq(self.eq, unk, units)

        self._defu.is_unit_consistent(self.eq, {unk: units})

        # Create unknown's DDS
        validate_type(round_to, int)
        value = round(1/9, round_to)
        dds = f'{unk} = {value} {units}'
        must_match('dds', dds)

        return dds



    # ======================================================================================================= PROPERTIES
    @property
    def min_num_decimals(self) -> float:
        return min([d.dds.num_decimals for d in self.data])


    @property
    def solvable(self) -> bool:
        return len(self.unknown_vars()) == 1

    @property
    def all_values(self) -> bool:
        return self.unknown_vars() == set()

    @property
    def base_values(self) -> Dict[str, float | int]:
        vd = dict()

        for dds in self.data:
            vd.update({dds.variable: dds.base.value})

        return vd

    @property
    def data(self) -> List[Datum]:
        return deepcopy(self._data)

    @property
    def variables(self) -> List[str]:
        return [str(s) for s in self._eq.free_symbols]

    @property
    def eq(self) -> Eq:
        return self._eq.copy()

    @property
    def def_units(self) -> Optional[UnitDict]:
        return self._defu


    @property
    def target(self) -> Optional[Datum]:
        return self._target


    @target.setter
    def target(self, dds: DatumDefString | str | Datum | None) -> None:
        if dds is None:
            self._target = None

        else:
            """
            We don't know if all variables were written. It is possible that target is written before any variables, and
            hence before defu is even created. Hence, there are not so many things we can do.
            
            1) If we know that defu is present, AND that this variable is in the defu,
               we can check that the units are compatible.
            
            2) If we know that target was the last unknown variable, (we automatically know that defu exists),
               we can check that it makes the equation consistent. (no dependence on defu).
            """

            datum = self._to_Datum(dds)  # type of dds is checked here

            if self._ubs:
                key = datum.dds.symbol
            else:
                key = datum.variable

            if self._defu is None:
                # => no variables were written; too many unknowns, so just write the target's units
                self._target = datum
                self._defu = UnitDict({key : datum.units}, unit_by_symbol=self._ubs)

            elif self._defu and key in self._defu.keys():
                # if defu is present, and the target's variable is in there, we can check compatibility
                if self._defu.compatible_with_default(key, datum.units):
                    self._target = datum
                else:
                    defu = self._defu.get(key)
                    raise Exception(f'The units of target "{datum}" are not compatible with default units for this variable: "{defu}".')

            elif self._defu and self.solvable:
                # if defu is present, there's no target variable, but the equation is already solvable,
                # we can check consistency
                if self._defu.is_unit_consistent(self.eq, {key : datum.units}):
                    self._target = datum
                    self._defu[key] = datum.units
                else:
                    raise Exception(f'The units suggested by target "{datum}" are not consistent with the units of the rest of the variables: "{self.def_units}".')

            else:
                # if defu is present, there's no target variable, but the equation is NOT solvable,
                # there's nothing we can do, so
                self._target = datum
                self._defu[key] = datum.units





if __name__ == '__main__':
    f = Formula('y = -2*x**2 + 5*x + 2')
    f.write('y = 0')

    f.target = 'x = 0'

    print(*f.eval_numeric(Formula.filters.POSITIVES))
