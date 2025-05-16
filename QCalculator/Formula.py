from QCalculator.Datum import Datum
import sympy as sp
from typing import Dict, Tuple, List
from QCalculator._settings import SETTINGS
from QCalculator.Commenting import comment


class Formula:
    def __init__(self, expr: str):
        self._target = None
        self._rounding = None
        self._return_units = None

        self._expression = sp.parse_expr(expr)
        self._tempex = sp.parse_expr(expr)
        self._symbols = self._expression.free_symbols
        self._values = self._generate_value_dict()
        self._units = dict()

    def __str__(self):
        return str(self._tempex)

    def _generate_value_dict(self) -> Dict[sp.Symbol, float|int|None]:
        value_dict = dict()

        for symbol in self._symbols:
            value_dict.update({symbol : None})

        return value_dict

    @staticmethod
    def _zte_test(zte: int) -> bool:
        if isinstance(zte, int) and 0 < zte < 20:
            return True
        else:
            return False

    @staticmethod
    def _is_close(num1: float|int, num2: float|int) -> bool:
        from math import isclose
        ZERO_TOLERANCE_EXPONENT = SETTINGS['ZERO TOLERANCE EXPONENT']

        if Formula._zte_test(ZERO_TOLERANCE_EXPONENT):
            zte = eval(f'10e-{ZERO_TOLERANCE_EXPONENT}')
        else:
            raise Exception(f'Invalid ZERO_TOLERANCE_EXPONENT value: {ZERO_TOLERANCE_EXPONENT}')

        return isclose(num1, num2, abs_tol=zte)

    def decimals(self) -> Dict[str, int]:
        decs = dict()

        for s, v in self.values.items():
            if v is not None:
                comment(v)
                dec = Datum.get_decimals(v)
                decs.update( {s : dec} )

        return decs

    def min_decimals(self, only_number: bool = False) -> int | Dict[str, int]:
        decs = self.decimals()
        min_value = min(decs.values())

        for s, v in decs.items():
            if v == min_value:
                if only_number:
                    return v
                else:
                    return {s : v}

    def consistency_check(self, raise_exception: bool = True, silent_failure: bool = False) -> bool:
        expr = self._expression.copy()

        for s, v in self.values.items():
            if v is None and not silent_failure:
                comment(self.values)
                raise Exception(f'Cannot run consistency check for {self.expr}. Not all values are written down.')
            elif v is None and silent_failure:
                return True
            expr = expr.subs(s, v)

        expr = float(expr)

        if Formula._is_close(expr, 0):
            return True
        elif not raise_exception:
            return False
        else:
            comment(self.values)
            raise Exception(f'Inconsistent formula: "{self.expr}" has contradicting values')

    def _push(self) -> None:
        for s, v in self.values.items():
            if v is not None:
                self._tempex = self._tempex.subs(s, v)

    def write(self, datum: Datum) -> None:
        datum = datum.to_base_units()
        symbol = datum.symbol
        value = datum.value
        s = sp.Symbol(symbol)

        if s in self._values:
            self._values[s] = value
            self._units[s] = datum.unit
        else:
            return None

    def erase(self, symbol: str) -> None:
        s = sp.Symbol(symbol)

        self._values[s] = None
        self._units[s] = None

    def has_value(self, var: str) -> bool:
        s = sp.Symbol(var)

        if self._values.get(s) is not None:
            return True
        else:
            return False

    def eval(self,
             *,
             drop_negatives: bool = False,
             drop_complex: bool = False,
             ignore_failures: bool = False,
             return_all: bool = False,
             rounding: bool = True,
             ) -> List[Datum]:

        if self._target is None:
            raise Exception('specify target variable.')

        self._push()
        symbol = sp.Symbol(self.target)
        solutions = sp.solve(self._tempex, self.target)
        data = list()

        for solution in solutions:
            if drop_negatives and solution < 0:
                continue
            elif drop_complex and solution.has(sp.I):
                continue
            elif not return_all and not isinstance(solution, (sp.Float, sp.Integer)):
                continue
            else:
                if isinstance(solution, (sp.Float, sp.Integer)):
                    magn = float(solution)

                    if rounding:
                        magn = round(magn, self._rounding)

                    d = Datum(self.target, magn, self._units[symbol])
                    d.to(self._units[symbol], in_place=True)
                    data.append(d)
                    self.write(d)
                else:
                    data.append(solution)

        if not data and not ignore_failures:
            raise Exception('Could not find any solutions.')

        self._tempex = self._expression
        self._target = None
        self._rounding = None
        self._units[symbol] = None

        return data

    @property
    def has_values(self) -> bool:
        for n in self._values.values():
            if n is not None:
                return True
        else:
            return False

    @property
    def solvable(self) -> bool:
        num_unknowns = 0

        for n in self._values.values():
            if n is None:
                num_unknowns += 1

        return num_unknowns == 1

    @property
    def unknown(self) -> str:
        if self.solvable:
            for v, n in self._values.items():
                if n is None:
                    return str(v)
        else:
            raise Exception('Equation must be solvable to use this method')


    @property
    def symbols(self) -> Tuple[str, ...]:
        symbols = tuple(self._symbols)
        new_symbols = list()

        for s in symbols:
            new_symbols.append( str(s) )

        return tuple(new_symbols)

    @property
    def values(self) -> Dict[str, float|int]:
        new_dict = dict()

        for s, v in self._values.items():
            new_dict.update({ str(s) : v })

        return new_dict

    @property
    def units(self) -> Dict[str, str]:
        new_dict = dict()

        for s, v in self._units.items():
            new_dict.update({str(s): v})

        return new_dict

    @property
    def expr(self) -> str:
        return str(self._expression)

    @property
    def target(self) -> str:
        return self._target

    @target.setter
    def target(self, value: 'Datum') -> None:
        self._target = value.symbol
        self._rounding = value.num_decimals
        self._return_units = value.unit
        self._units[sp.Symbol(self._target)] = value.to_base_units().unit


"""
f = Formula(expr='n - mps/M')
f.write(Datum('mps', 5, 'g'))
f.write(Datum('M', 18, 'g/mole'))
f.target = Datum('n', 0.001, 'mole')

comment(*f.eval())

comment(f.values)
comment(f.decimals())
comment(f.min_decimals())

comment(f.consistency_check())
"""