from __future__ import annotations

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from sympy import I, Expr
from typing import Dict, Tuple, List, Optional

from QCalculator.Datum import Datum
from QCalculator.Exceptions.FormulaExceptions import *
from QCalculator.Exceptions.LinearIteratorExceptions import VariableNotFound


class Formula:
    """
    Formulas class allows to join together several Datum instances with a simple mathematical relation. For example,
    S=v*t joins three Datum instances. The Formula then allows to write down two of the three variables and solve for
    the missing one by using .write and .eval. The class uses sympy and Datum .symbol attributes to operate on the
    formula.
    """

    def __init__(self, expr: str) -> None:
        self._target: Optional[str] = None
        self._rounding: Optional[int] = None
        self._return_units: Optional[Datum.ureg.Unit] = None

        if '=' in expr:
            raise Exception('The equation must not contain the "=" sign. Rewrite the equation as "everything = 0". use the minus signs.')

        self._expression = parse_expr(expr)
        self._tempex = parse_expr(expr)
        self._symbols = self.expr.free_symbols
        self._values: Dict[str, Optional[int|float]] = dict([(s, None) for s in self.symbols])
        self._units: Dict[str, Datum.ureg.Unit] = dict()
        self._ZERO_TOLERANCE_EXPONENT: int = 7

    def __str__(self):
        return str(self._tempex)

    def __iter__(self):
        return self.symbols.__iter__()

    @staticmethod
    def _is_close(num1: float|int, num2: float|int, zte: int = 3) -> bool:
        from math import isclose

        if not Datum._ZTE_test(zte):
            raise InvalidZeroToleranceExponent(value=zte, comment='')

        # print(num1, num2, zte, eval(f"10e-{zte}"))
        return isclose(num1, num2, abs_tol=eval(f"10e-{zte}"))

    def decimals(self) -> Dict[str, int]:
        return dict([(s, Datum.get_decimals(v)) for s, v in self.values.items() if v is not None])

    def min_decimals(self, only_number: bool = False) -> int | Tuple[str, int]:
        decs = self.decimals()
        min_pair = min(decs.items(), key=lambda i: i[1])

        if only_number:
            return min_pair[1]
        else:
            return min_pair

    def consistency_check(self,
                              raise_exception: bool = True,
                              silent_failure: bool = False,
                              zte: Optional[int] = None,
                          ) -> bool:
        """
        .consistency_check() checks if the values written into a formula still obey that formula. Let's say, if the
        Formula instance describes a Pythagorean theorem, c**2 = a**2 + b**2, then writing in a=3, b=4, c=5 will pass
        the consistency check since 5**2 - 3**2 - 4**2 = 0. If, however, c=6, then the consistency check would raise
        an exception (unless manually disabled via raise_exception=True) because 6**2 - 3**2 - 4**2 < 0.

        Of course, if not all numbers are written to the Formula instance, consistency check cannot be ran. If no
        exception is needed when the test cannot be ran, set silent_failure to True.

        :param raise_exception: bool = True. Raise exception if the test is failed. Otherwise, return False.
        :param silent_failure: bool = False. Raise exception if the test cannot be ran.
        :param zte: the zero tolerance exponent. If None, the default value is used.
        :return: bool. True is the formula is consistent False if not.
        """


        expr = self.expr  # the .expr property itself creates a copy of the sympy expression

        # writing in the saved values for each symbol (or complaining if no value is found).
        for s, v in self.values.items():
            if v is None:
                if not silent_failure:
                    raise CannotRunConsistencyCheck(formula=self.expr_str, comment='')
                else:
                    return True
            else:
                expr = expr.subs(s, v)

        # we are here only if all values were present, so our expression is not a number
        expr = float(expr)

        # check with ._is_close() whether the number is close to zero
        if zte is None:
            zte = self._ZERO_TOLERANCE_EXPONENT

        if self._is_close(expr, 0, zte=zte):
            return True
        elif not raise_exception:
            return False
        else:
            raise InconsistentFormula(formula=self.expr_str, comment=f'{self.values}')

    def _push(self) -> None:
        for s, v in self.values.items():
            if v is not None:
                self._tempex = self._tempex.subs(s, v)

    def _symbol_check(self, symbol: str) -> bool:
        """Checks if the symbol is present in the formula's expression"""
        return symbol in self.symbols

    def write(self,
                  d: Datum | str,
                  rewrite: bool = False
              ) -> None:
        """
        Saves the given Datum value to the Formula's "memory".

        :param d: Datum or string suitable for Datum.to_datum
        :param rewrite: if True Datums with the same symbol will not raise an exception
        :return: None
        """

        datum = Datum.to_datum(d)
        symbol = datum.symbol
        datum.ito_base_units()

        if symbol in self.values:
            if self.has_value(symbol) and not rewrite:
                raise RewritingError(
                    comment='Set rewrite=True to overrule this restriction. NOTE: the formula may become inconsistent.',
                    variable=symbol,
                    old_value=str(self._values[symbol]),
                    old_units=str(self._units[symbol])
                )
            self._values[symbol] = datum.value
            self._units[symbol] = datum.units
        else:
            raise VariableNotFound(comment=f'The variable is not present in the expression: {self.expr}.', var=symbol)

    def read(self, var: str, units: str | Datum.ureg.Unit = 'auto') -> Datum:
        value = self._values[var]
        base_units = self._units[var]

        if units == 'auto':
            units = base_units

        return Datum(var, value, base_units).to(units)

    def erase(self, symbol: str) -> None:
        if self.has_value(symbol):
            self._values[symbol] = None
            self._units[symbol] = None
        else:
            raise VariableNotFound(comment='', var=symbol)

    def has_value(self, var: str) -> bool:
        return self._values.get(var) is not None

    def eval(self,
             *,
             drop_negatives: bool = False,
             drop_complex: bool = False,
             ignore_failures: bool = False,
             num_only: bool = False,
             rounding: bool = True,
             write_target: bool = False,
             reset_target: bool = False
             ) -> List[Datum | Expr]:
        """
        .eval() returns a list of solutions (solves using sympy) for a given variable. Those may include numerical
        solutions if self.solvable is True, or sympy expressions if there were not enough variables provided to
        solve for the required variable.

        By combining "write_target" and "reset_target" each Formula instance can be used to preserve the obtained
        values of the target variable (single-time solution) or to solve for the same target many times.

        :param drop_negatives: If True, no negative numerical solutions will be returned
        :param drop_complex: If True, no complex or imaginary solutions will be returned
        :param ignore_failures: if True, even an empty list of solutions will be returned
        :param num_only: If True, only numerical solutions (float and int) will be returned
        :param rounding: If True, the numerical solutions will be rounded to the number of digits indicated in self.target Datum instance
        :param write_target: If True, the obtained value of the target variable is recorded by .write(). Useful for linear equations with one solution
        :param reset_target: If True, the .target variable is set back to None
        :return: A list of Datum objects for numerical solutions and sympy Expr objects for other solutions.
        """

        # if there's no target specified, it makes no sense to continue
        if self.target is None:
            raise TargetNotFound(comment='specify target variable.', formula=self.expr_str)

        # copy the present values to the temporary expression
        self._push()
        self.consistency_check(silent_failure=True)

        # solve the temporary expression for the set target
        solutions = sp.solve(self._tempex, self.target)

        # filer the solutions according to specified criteria (specified in parameters)
        # sorting is done by dropping every irrelevant solution, not keeping the relevant ones
        retained_solutions = list()

        for solution in solutions:
            if drop_negatives and solution < 0:
                continue
            elif drop_complex and solution.has(I):
                continue
            elif num_only and not isinstance(solution, (sp.Float, sp.Integer)):
                continue
            else:
                if isinstance(solution, (sp.Float, sp.Integer)):
                    magn = float(solution)
                    if rounding:
                        magn = round(magn, self._rounding)

                    d = Datum(self.target, magn, self._units[self.target])

                    if write_target:
                        self.write(d)

                    d.ito(self.units[self.target])
                    retained_solutions.append(d)
                else:
                    retained_solutions.append(solution)

        # if no solutions were left/found, and we do not ignore failures, set FAIL flag to True, otherwise False
        if not retained_solutions and not ignore_failures:
            FAIL = True
        else:
            FAIL = False

        # reset of the system (independently of whether we succeeded in solving the equation)
        self._tempex = self.expr

        if reset_target:
            self._rounding = None
            self._target = None

        # if  we failed, reset also target units and raise an exception
        if FAIL:
            if reset_target:
                self._units[self.target] = None
            raise SolutionNotFound(comment='Could not find any solutions.', formula=self.expr_str)
        else:
            if not retained_solutions:
                self._units[self.target] = None
            return retained_solutions

    @property
    def has_values(self) -> bool:
        return None not in self._values.values()

    @property
    def solvable(self) -> bool:
        # number of unknowns is number of None's in the value dict
        return len([k for k in self.symbols if not self.has_value(k)]) == 1

    @property
    def unknown(self) -> str:
        if self.solvable:
            for s in self.symbols:
                if not self.has_value(s):
                    return str(s)
            else:
                # if everything does well, this code should never be reached due to self.solvable condition
                raise EquationNotSolvable(comment='Equation must be solvable to use this method ("Formula.unknown()").', formula=self.expr_str)
        else:
            raise EquationNotSolvable(comment='Equation must be solvable to use this method ("Formula.unknown()").', formula=self.expr_str)


    @property
    def symbols(self) -> Tuple[str, ...]:
        symbols = tuple(self._symbols)
        return tuple([str(s) for s in symbols])

    @property
    def values(self) -> Dict[str, Optional[float|int]]:
        return dict([(str(s), v) for s, v in self._values.items()])

    @property
    def units_str(self) -> Dict[str, str]:
        return dict([(s, str(v)) for s, v in self._units.items()])

    @property
    def units(self) -> Dict[str, Datum.ureg.Unit]:
        return self._units

    @property
    def expr_str(self) -> str:
        return str(self._expression)

    @property
    def expr(self) -> Expr:
        return self._expression.copy()

    @property
    def target(self) -> str:
        return self._target

    @target.setter
    def target(self, datum: Datum|str) -> None:
        if isinstance(datum, str):
            datum = Datum.from_string(datum)

        self._target = datum.symbol
        self._rounding = datum.num_decimals
        self._return_units = datum.units
        self._units[self._target] = datum.to_base_units().units


if __name__ == '__main__':
    values = [10, 20, 30, 40, 50, 60, 70, 80, 90]

    f = Formula(expr='n - mps/M')
    f.target = 'n = 0.001 mole'
    f.write('M = 18 g/mole')
    print(f.values)
