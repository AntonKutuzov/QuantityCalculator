from QCalculator.Computations.Formula import Formula
from QCalculator.Storage import UNIT_REGISTRY
from typing import List, Dict, Tuple
from QCalculator.Storage.Files import read
from QCalculator.Storage.CONSTANTS import FORMULAS_FILE, UNITS_FILE, DEFAULTS_FILE, ZERO_TOLERANCE_EXPONENT
from QCalculator.Computations.Datum import Datum
from QCalculator.Commenting import comment


class LinearIterator:
    def __init__(self):
        self._formulas = self._load_formulas()
        self._templates = [Formula(f) for f in self.formulas]
        self._temporary_equations = self._templates.copy()
        self._read_constants()

        self._target = None

    def _load_formulas(self) -> List[str]:
        formulas = list()

        for line in read(FORMULAS_FILE):
            formulas.append(line)

        return formulas

    def _all_symbols(self) -> List[str]:
        names = list()

        for f in self._templates:
            for v in f.values.keys():
                names.append(v)

        return names

    def _read_constants(self) -> None:
        for line in read(DEFAULTS_FILE):
            var, value = line.strip('\n').split(':')
            unit = UNIT_REGISTRY[var]
            self.write(Datum(var, float(value), unit))

    def _zte_test(self, zte: int) -> bool:
        if isinstance(zte, int) and 0 < zte < 20:
            return True
        else:
            return False

    def _is_close(self, num1: float|int, num2: float|int) -> bool:
        from math import isclose

        if self._zte_test(ZERO_TOLERANCE_EXPONENT):
            zte = eval(f'10e-{ZERO_TOLERANCE_EXPONENT}')
        else:
            raise Exception(f'Invalid ZERO_TOLERANCE_EXPONENT value: {ZERO_TOLERANCE_EXPONENT}')

        return isclose(num1, num2, abs_tol=zte)

    def _test_var_presence(self, var: str) -> bool:
        return var in self._all_symbols()

    def _consistency_check(self, var: str, value: float|int, raise_exception: bool = True) -> bool:
        if self.has_value(var):
            d = self.read(var, rounding=False)

            if not self._is_close(d.value, value):
                raise Exception(f'Inconsistent variable: "{var}" has unequal values of {d.value} and {value}')
        else:
            return True

    def _compute_all(self) -> List[Datum]:
        interres = list()
        units_list = dict([ u.split(':') for u in read(UNITS_FILE) ])

        for f in self._temporary_equations:
            if f.solvable:
                s = f.unknown
                comment(f'\t\tSolving {f.expr} for {s}:', end=' ')
                u = units_list[s]
                f.target = Datum(s, 0.001, u)
                res = f.eval(ignore_failures=True, rounding=False)

                if len(res) > 1:
                    comment(res)
                    raise Exception('Something strange happens...')
                elif len(res) == 1:
                    comment(f'got {res[0]}')
                    interres.append(res[0])
                else:
                    comment('no numerical result')
                    continue

        return interres

    def _iterate(self) -> List[Datum]:
        if self.target is None:
            raise Exception('Target is not set.')

        while True:
            comment('\tComputing, considering new data...')
            res = self._compute_all()

            comment('\tINTERMEDIATE: ', *res)

            comment('\tWriting in new data...')
            for d in res:
                self._consistency_check(d.symbol, d.value)
                self.write(d)

            if res:
                yield res
            else:
                return res

    def solve(self,
              stop_at_target: bool = True,
              alter_target: bool = True,
              ) -> Datum:

        for data in self._iterate():
            comment('\tOVERALL:', *data)
            comment('New iteration...')
            if self.target.symbol in [d.symbol for d in data] and stop_at_target:
                break

        for f in self._temporary_equations:
            f.consistency_check(raise_exception=True, silent_failure=True)

        if self.has_value(self.target.symbol):
            answer = self.read(self.target.symbol, rounding=False)
            comment(answer)

            if alter_target:
                self.target = answer

            return answer
        else:
            raise Exception('Could not find the solution.')

    def write(self, datum: Datum) -> None:
        if self.has_value(datum.symbol):
            old = self.values[datum.symbol]
            new = datum.value
            if not self._is_close(old, new):
                comment(self.values)
                raise Exception(f'Cannot rewrite the variable: "{datum.symbol}"')

        WROTE = False

        self.values.update( {datum.symbol : datum.value} )
        for f in self._temporary_equations:
            if datum.symbol in f.symbols:
                WROTE = True
                f.write(datum)

        if not WROTE:
            raise Exception(f'Variable "{datum.symbol}" is not among the variables of the given formulas set.')

    def read(self,
             var: str,
             units: str = 'default',
             rounding: bool = True,
             round_to: int = 2) -> Datum:
        u = UNIT_REGISTRY[var]
        v = self.values[var]
        if rounding:
            v = round(v, round_to)
        d = Datum(var, v, u)

        if not units == 'default':
            d.to(units, in_place=True)

        return d

    def erase(self, var: str) -> None:
        for f in self._temporary_equations:
            f.erase(var)

    def clear(self) -> None:
        self._temporary_equations = self._templates.copy()

    def has_value(self, name: str) -> bool:
        names = list()

        for f in self._templates:
            for v, n in f.values.items():
                if n is not None:
                    names.append(v)

        return name in set(names)

    @property
    def formulas(self) -> List[str]:
        return self._formulas

    @property
    def target(self) -> Datum:
        return self._target

    @target.setter
    def target(self, value: Datum) -> None:
        if self._test_var_presence(value.symbol):
            self._target = value
        else:
            raise Exception(f'Variable not found in Formulas file: {value.symbol}')

    @property
    def values(self) -> Dict[str, float|int]:
        values = dict()

        for f in self._temporary_equations:
            for s, v in f.values.items():
                if v is None:
                    continue
                elif values.get(s) is None:
                    values.update( {s : v} )
                else:
                    old = values[s]
                    new = v

                    if self._is_close(old, new):
                        continue
                    else:
                        comment(f.values)
                        raise Exception(f'Found two different values for the same variable: {old} and {new} for variable '
                                        f'"{s}"')
        return values

    @property
    def quantities(self) -> Dict[str, Tuple[float, str]]:
        # Don't use UnitRegistry, because you cannot operate on units of different ones
        qs = dict()

        for var, value in self.values.items():
            u = UNIT_REGISTRY[var]
            qs.update( {var : (float(value), u)} )

        return qs
