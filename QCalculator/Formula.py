from __future__ import annotations

from sympy.logic.boolalg import BooleanTrue

from QCalculator.Exceptions.FormulaExceptions import (
    RewritingError, InvalidUnitError, OverlappingVariables, InvalidSymbol, WrongUnitEquation,
    ConsistencyError, EquationNotSolvable, FailedConsistencyCheck,
    SymbolNotFound, NoValueError, TargetNotFound, UnknownNotFound
)
from QCalculator import Datum

from typing import Dict, Optional, List, overload, Set, Iterable
from pint import Unit, Quantity
from sympy import parse_expr, Eq, solve, Float, simplify, im, re, Symbol
from copy import deepcopy, copy


class Formula:
    """
    Formula class wraps sympy equation to make it easy to work with relations of Datum instances. Formula relies on
    Datum class, but can be used without defining Datum instances since all relevant methods also accept Datum
    definition strings.

    The main functionality of Formula is implemented in the .eval() and .solve() methods. The purpose of Formula is to
    make it possible to join several Datum instances into an equation and solve the equation or rearrange it while
    preserving the values and the units of written variables.

    Example
    ---------
        >>> from QCalculator import Formula
        >>> f = Formula('s = v * t')
        >>> f.write('s = 4.8 m', 'v = 0.0965 m/s')
        >>> f.target = 't = 0.01 second'
        >>> t = f.solve()  # returns a list of Datum instances
        >>> print(*t)
        t = 49.74 second
    """

    REAL_ONLY = lambda l: simplify(im(l)) == 0
    POSITIVES = lambda l: l > 0.0
    NEGATIVES = lambda l: l < 0.0
    NON_NEG = lambda l: l >= 0.0
    NON_POS = lambda l: l <= 0.0
    ZERO = lambda l: l == 0.0
    NO_FILTER = lambda l: l


    def __init__(self, eq: str, ref_units: Optional[Dict[str, str|Unit]] = None):
        """
        Accepts a string that can be parsed as a sympy expression. Optionally accepts the reference units dict that is
        used to control the units of a Datum that is written with .write(). In the case the units are not compatible,
        an exception will be raised. If ref_units is None, then control is turned off.

        :param eq: an expression that will be parsed into sympy Eq
        :param ref_units: a dict of units used to control the units of written variables
        """

        self._eq = self._as_sympy_eq(eq)
        self._ref_units = self._complete_ref_units(ref_units) if ref_units is not None else None
        self._data: Set[Datum] = set()

        self._target: Optional[Datum] = None

    def __str__(self):
        return f'{self.eq.lhs} = {self.eq.rhs}'

    @staticmethod
    def _as_sympy_eq(expr: str, _evaluate: bool = False) -> Eq:
        """
        Prases an expression from the user to a sympy Equality

        :param expr:
        :return:
        """

        if '=' in expr:
            lhs, rhs = expr.split('=')

            try:
                lhs = parse_expr(lhs)
                rhs = parse_expr(rhs)
            except TypeError:
                raise InvalidSymbol(expr=expr)

            eq = Eq(lhs, rhs, evaluate=_evaluate)
        else:
            try:
                expr = parse_expr(expr)
            except TypeError:
                raise InvalidSymbol(expr=expr)

            eq = Eq(expr, 0, evaluate=_evaluate)
        return eq

    def _complete_ref_units(self, ru: Dict[str, str|Unit]) -> Dict[str, Optional[str]]:
        """
        Adds None to variables for which user did not specify values.

        :param ru:
        :return:
        """

        unit_dict: Dict[str, Optional[str]] = dict()

        for v, u in ru.copy().items():  # in case we pass a dict for many Formulas at once (see LinearIterator)
            if v in self.symbols:
                unit_dict.update({v : u})

        for s in self.symbols:
            if s not in unit_dict.keys():
                unit_dict.update({s : None})

        if None not in unit_dict:
            self._check_unit_equality(unit_dict)

        return unit_dict

    # ================================================================================================== GENERAL HELPERS
    def _confirm_symbol(self, symbol: str, raise_exception: bool = True) -> bool:
        """
        Checks that the symbol is present in the sympy expression.

        :param symbol:
        :param raise_exception:
        :return:
        """

        res = symbol in self.symbols

        if raise_exception and not res:
            raise SymbolNotFound(formula=self.eq_str, symbol=symbol)
        else:
            return res

    def _confirm_units(self, symbol: str, units: Optional[str|Unit] = None, raise_exception: bool = True) -> bool:
        """
        Compares the units of a variable to the reference units specified at the initialization step. Returns True
        if "units" is None (for default values in read() and write() methods).

        :param symbol: symbol of the variable
        :param units: units of the variable
        :param raise_exception: if True, an exception will be raised if units are not compatible
        :return: True if units are compatible, False if not and if "raise_exception" is False
        """

        if units is None:
            return True

        if self._ref_units is not None:
            units = Datum.normalize_units(units)
            res = units.is_compatible_with(self._ref_units[symbol])

            if raise_exception and not res:
                raise InvalidUnitError(var=symbol, units=units, ref=self._ref_units[symbol])
            else:
                return res

        else:
            return True

    def _check_unit_equality(self, units: Dict[str, str]) -> None:
        # because the Eq evaluates these numerically, and x/x is 1, not "dimensionless" as a Symbol
        units_updated = dict()

        for v, u in units.items():
            if u == '':
                u = 1
            else:
                q: Quantity = 1 * Datum.normalize_units(u)
                q.ito_base_units()
                u = str(q.units)

            units_updated.update({v : u})

        # units_updates = dict([(v, (1 if u == '' else u)) for v, u in units.items()])

        ueq = self.eq.subs(units_updated)

        if not isinstance(ueq, BooleanTrue):
            raise WrongUnitEquation(f=self.eq_str, units=units)

    def _value_dict(self) -> Dict[str, float|int]:
        """
        Returns a dict of values for all written variables. The dict is needed for substitution into the sympy expression
        in eval method.

        :return:
        """

        vd = dict()

        for d in self.data:
            d.ito_base_units()
            vd.update({d.symbol : d.magnitude})

        return vd

    # ============================================================================================== WRITING AND READING
    def write(
            self,
            *d: Datum|str,
            rewrite: bool = False,
            force_inconsistent: bool = False
    ) -> None:
        """
        Adds the values specified in "d" parameter to the _data attribute. Also checks for
        - consistency after the value is written
        - compatibility of units
        - presence of the variable in the formula

        :param d: Datum or str in the form of Datum definition string
        :param rewrite: set to True to overwrite an existing value
        :param force_inconsistent: set to True to write in an inconsistent value
        :return: None
        """

        for datum in d:
            if not isinstance(datum, (Datum, str)):
                raise TypeError(f'Expected Datum instance or str, got: "{type(d)}".')

            datum = Datum.as_datum(datum)
            self._confirm_symbol(datum.symbol)
            self._confirm_units(datum.symbol, datum.units)

            if self.has_value(datum.symbol):
                if rewrite:
                    self.erase(datum.symbol)
                else:
                    current_value = self.read(datum.symbol)
                    raise RewritingError(
                        var=datum.symbol,
                        old=current_value,
                        details='To enable rewriting set the "rewrite" parameter to True.'
                    )

            self._data.add(datum)
            if not self.consistency_check(silent_failure=True, raise_exception=False) and not force_inconsistent:
                raise ConsistencyError(formula=self.eq_str, details=f'The last value to write was "{str(datum)}".')

    @overload
    def read(self, var: str, units: Optional[str|Unit] = None) -> Datum:
        ...

    @overload
    def read(self, var: List[str], units: Optional[List[str | Unit]] = None) -> List[Datum]:
        ...

    def read(
            self,
            var: str | List[str],
            units: Optional[str | Unit | List[str|Unit]] = None
    ) -> Datum | List[Datum]:
        """
        Returns a (list of) Datum instance with the specified symbol. If no value is found, the NoValueError is raised.
        If lists are used, then the lengths of the lists for variables and units must be the same. To use default units,
        use None in the units list. "units" can always be set to None to use default value(s) of the variable(s).

        :param var: str | List[str] specifying the variables to be read
        :param units: units or list of units in which the variables must be read
        :return: Datum | List[Datum]
        """

        if isinstance(var, str):
            self._confirm_symbol(var)
            self._confirm_units(var, units)

            if self.has_value(var):
                ds = filter(lambda a: a.symbol == var, self._data)
                ds = copy(list(ds)[0])

                if units is not None:
                    ds.ito(units)

                return ds
            else:
                raise NoValueError(formula=self.eq_str, symbol=var)

        elif isinstance(var, list):
            if units is not None and not len(var) == len(units):
                raise ValueError('The lengths of "var" and "units" lists must be the same, or the "units" parameter must be None.')
            elif units is None:
                units = len(var)*[None]

            datum_list = list()

            for v, u in zip(var, units):
                datum = self.read(v, u)
                datum_list.append(datum)

            return datum_list

        else:
            raise TypeError("The read() method accepts either one variable or list of variables. Same for units.")

    def erase(self, var: Optional[str] = None) -> None:
        if var is not None:
            d = self.read(var)  # variable is confirmed here
            self._data.remove(d)
        else:
            for s in self.symbols:
                self.erase(s)

    # ================================================================================================= FORMULA ANALYSIS
    def consistency_check(
            self,
            silent_failure: bool = False,
            raise_exception: bool = True
    ) -> bool:
        """
        Checks that the formula is consistent with currently written values. The formula is consistent when substitution
        of the values give a true equality, i.e. LHS and RHS are equal.

        :param silent_failure: when True, the function returns True if not all values are written. Otherwise,
        FailedConsistencyCheck is raised
        :param raise_exception: when True, and the formula is inconsistent, the ConsistencyError is raised instead of
        returning False
        :return: True if the formula is consistent, False if not. True if there are not enough values to run the test
        and "silent_failure" is set to True
        """
        from math import isclose

        if all([self.has_value(v) for v in self.symbols]):
            vd = self._value_dict()

            lhs = self.eq.lhs.subs(vd)
            rhs = self.eq.rhs.subs(vd)

            if not isclose(rhs, lhs) and raise_exception:
                raise ConsistencyError(formula=self.eq_str)
            else:
                return isclose(rhs, lhs)

        elif silent_failure:
            return True

        else:
            raise FailedConsistencyCheck(formula=self.eq_str, details='Not all variables have values.')


    @overload
    def has_value(self, var: str) -> bool:
        ...

    @overload
    def has_value(self, var: List[str]) -> List[bool]:
        ...

    def has_value(self, var: str | Iterable[str]) -> bool | List[bool]:
        """
        Checks that the specified variable(s) has a value. Raises OverlappingVariables exception if there is more than
        one variable with the same symbol.

        :param var: variables to be checked
        :return:
        """

        if isinstance(var, str):
            self._confirm_symbol(var)
            ds = list(filter(lambda a: a.symbol == var, self._data))

            if len(ds) > 1:
                raise OverlappingVariables(
                    formula=self.eq_str,
                    vars=[d.symbol for d in ds],
                    details='This error could only occur if you directly changed the protected attribute ._data. '
                            'If this is not so, you have discovered a bug. Congratulations!'
                )
            else:
                return len(ds) > 0

        elif isinstance(var, (list, tuple, set)):
            res_list = list()
            for v in var:
                res_list.append(self.has_value(v))
            return res_list

        else:
            raise TypeError(f'The "has_value" method expects either a string or a list of strings, got: "{type(var)}".')

    # ===================================================================================================== COMPUTATIONS
    def eval(
            self,
            *filters,
            symbolic: bool = False
    ) -> List[Eq] | List[Float]:
        """
        Evaluates the expression by using sympy solve() function. If "symbolic" is set to True, the result is a list of
        Equality instances with the target variable expression in terms of all the other variables. If "symbolic" is
        False, the available values are substituted for variables and the resulting expression is returned.

        The "filters" parameters specify which solutions to keep and which to ignore. On a class level several pre-set
        filters are defined (such as REAL_ONLY, POSITIVES, ...). Each filter is passed to the standard Python's filter()
        function to filter the obtained solutions.

        Example
        ----------
            >>> from QCalculator import Formula
            >>> f = Formula('s = v * t')
            >>> f.write('s = 4.8 m', 'v = 0.0965 m/s')
            >>> f.target = 't = 0.01 second'
            >>> f.eval(symbolic=True)
            [Eq(t, s/v)]
            >>> f1 = Formula('x**2 + 5*x + 6')
            >>> f1.target = 'x = 0.001'
            >>> f1.eval(Formula.POSITIVES)
            []
            >>> f1.eval(Formula.NEGATIVES)
            [-3.00000000000000, -2.00000000000000]


        :param filters: function to be passed to the filter() Python function to sort solutions from sympy solve
        :param symbolic: if True, the function returns an Equality instance without substituting variable values
        :return: list of either sympy Equality or sympy Float (if the solution can be found)
        """

        if self.target is None:
            raise TargetNotFound(formula=self.eq_str)

        self.consistency_check(silent_failure=True)
        self._confirm_symbol(self.target.symbol)
        self._confirm_units(self.target.units)

        vd = self._value_dict()

        if not symbolic:
            if self.has_value(self.target.symbol):
                tbu = self.read(self.target.symbol, self.target.base_units)
                return [Float(tbu.magnitude)]
            else:
                eq = self.eq.subs(vd)
        else:
            eq = self.eq

        sols = solve(eq, self.target.symbol)

        if symbolic:
            res = list()
            for s in sols:
                t = Symbol(self.target.symbol)
                eq = Eq(t, s, evaluate=False)
                res.append(eq)
            sols = res
        else:
            for fil in filters:
                sols = list(filter(fil, sols))

        return sols


    def solve(
            self,
            *filters,
            rounding: bool = True,
            round_to: int = 2
    ) -> List[Datum]:
        """
        The solve() method wraps eval() method since often Formula is used to solve linear equations that yield real
        value which are compatible with the Datum class (imaginary or complex numbers are not). solve() also does
        rounding of the result if "rounding" parameter is set to True. The function rounds to the number of significant
        digits specified in the Datum definition string of the target variable (specified via .target setter).

        The solve() method can be used without specifying the target, because solve() is only solve the equations, not
        evaluate them symbolically. That is, the .unknown property is used to automatically determine the target. In
        this case the "round_to" parameter is used to specify to what number of significant digits the final value
        must be rounded. "round_to" is ignored if "rounding" is set to False.

        **NOTE**: if all the variables have a value, the UnknownNotFound error will be raised regardless of whether the
        target is specified.

        solve() uses eval() method with a Formula.REAL_ONLY filter (to keep the solutions compatible with Datum).

        :param filters: function to sort solutions passed directly to the eval() method used
        :param rounding: if True, the solution(s) will be rounded to the specified number of significant digits
        :param round_to: specifies number of significant digits for rounding if target is not specified
        :return: list of Datum instances
        """

        unk = self.unknown  # checks whether all variables have a value, and if they do, raises UnknownNotFound

        if self.target is None:
            if self._ref_units is None:
                raise Exception('Specify either target or reference units to solve equations without specifying target variable.')
            value = round(0.111111111111111, round_to)
            self.target = Datum(unk, value, self._ref_units[unk])

        # "sols" can only be a float number since we solve with "symbloic=False", we checked for equation being solvable
        # and we filter for real numbers.
        # NOTE: filters must be directly passed to the eval() method. The tests do not account for filters in solve().
        sols: List[Float] = self.eval(Formula.REAL_ONLY, *filters)

        res = list()

        for sol in sols:
            sol = float(sol)  # from smypy Float to Python's native float

            d = Datum(self.target.symbol, sol, self.target.base_units)
            d.ito(self.target.units)

            if rounding:
                mag = round(d.magnitude, Datum.get_decimals(self.target.magnitude))
                d = Datum(self.target.symbol, mag, self.target.units)

            res.append(d)

        return res

    # ======================================================================================================= PROPERTIES
    @property
    def decimals(self) -> Dict[str, int]:
        """
        Returns a dict with the number of decimal places for each variable written to the Formula instance

        :return:
        """

        decs = dict()

        for symbol in self.symbols:
            if self.has_value(symbol):
                d = self.read(symbol)
                dec = d.get_decimals(d.magnitude)
                decs[symbol] = dec

        return decs

    @property
    def solvable(self) -> bool:
        """
        Returns True if there's only one or no unknown variables

        :return:
        """

        values = self.has_value(list(self.symbols))
        nones = [v for v in values if v is False]  # count Falses. If there's one value missing, the equation can be solved
        return len(nones) <= 1

    @property
    def all_values(self) -> bool:
        """returns True if all values are already present in the Formula"""
        return len(self._data) == len(self.symbols)  # because we control for each var having no more than one value

    @property
    def unknown(self) -> str:
        """
        If the equation is solvable, returns the variable that has to be found (that yet has no value). Otherwise,
        raises EquationNotSolvable exception. If *all* variables already have a value, raises UnknownNotFound
        exception (since there's no unknowns).

        :return:
        """

        if self.solvable:
            for s in self.symbols:
                if not self.has_value(s):
                    return s
            else:
                raise UnknownNotFound(formula=self.eq_str)
        else:
            raise EquationNotSolvable(formula=self.eq_str)

    @property
    def data(self) -> Set[Datum]:
        """Returns a **deepcopy** of the data set where the written Datum instances are stored"""
        return deepcopy(self._data)

    @property
    def symbols(self) -> Set[str]:
        return set([str(s) for s in self._eq.free_symbols])

    @property
    def eq_str(self) -> str:
        return str(self)

    @property
    def eq(self) -> Eq:
        """Returns a **copy** of the sympy Equality used in this Formula instance"""
        return self._eq.copy()

    @property
    def target(self) -> Datum:
        """
        Returns a Datum instance defining the target variable, return units and the number of decimal places for
        founding of the target when it is found.
        """

        return self._target

    @target.setter
    def target(self, datum: Datum|str) -> None:
        d = Datum.as_datum(datum)

        self._confirm_symbol(d.symbol)
        self._confirm_units(d.symbol, d.units)

        self._target = d
