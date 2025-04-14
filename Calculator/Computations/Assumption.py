from Calculator.Computations.LinearIterator import LinearIterator
from typing import List
from Calculator.Computations.Datum import Datum
from Calculator.Storage.CONSTANTS import ASSUMPTIONS_FILE
from Calculator.Utils.Files import write, read


class Assumption:
    def __init__(self, symbol: str, name: str):
        self._symbol = symbol
        self._name = name
        self._variables = list()
        self._to_compute = list()
        self._assume = list()

    def __str__(self):
        return (f'{self._symbol} (full name: "{self._name}"). Assumes {', '.join([str(datum) for datum in self.variables])}.'
                f' Computes {', '.join([str(var.symbol) + ' in ' + str(var.unit) for var in self.compute])}.'
                f' Temporarily assumes for calculations that {', '.join(str(var) for var in self.assume)}.')

    def apply_to(self, iter: LinearIterator):
        tempiter = LinearIterator()  # temporary linear iterator
        keep_vars = list()

        for var in self.assume:
            tempiter.write(var)

        for var in self.variables:
            keep_vars.append(var)
            tempiter.write(var)

        for var in self.compute:
            tempiter.target = var
            tempiter.solve(stop_at_target=True, alter_target=True)
            keep_vars.append(tempiter.target)

        for var in keep_vars:
            iter.write(var)

    def to_set(self, *data: Datum) -> None:
        self._variables.extend(data)

    def to_compute(self, *data: Datum) -> None:
        self._to_compute.extend(data)

    def to_assume(self, *data: Datum) -> None:
        self._assume.extend(data)

    def save(self) -> None:
        assumption = f'!{self.symbol}: {self.name}'

        for var in self.variables:
            assumption += f'\nvariable {var.symbol}:{var.value}:{var.unit}'
        for var in self.assume:
            assumption += f'\nassume {var.symbol}:{var.value}:{var.unit}'
        for var in self.compute:
            assumption += f'\ncompute {var.symbol}::{var.unit}'

        assumption += '\n!\n'

        write(ASSUMPTIONS_FILE, assumption)

    @staticmethod
    def parse(assumption: str) -> 'Assumption':
        heading, *body, exmark, space = assumption.split('\n')
        symbol, name = [string.strip() for string in heading.strip('!').split(':')]

        a = Assumption(symbol, name)

        for line in body:
            data, value, unit = line.split(':')
            line_type, var = data.split()

            match line_type:
                case 'variable':
                    a.to_set(Datum(var, float(value), unit))
                case 'assume':
                    a.to_assume(Datum(var, float(value), unit))
                case 'compute':
                    a.to_compute(Datum(var, 0.1, unit)) # because here value = ''
                case _:
                    raise Exception('Invalid assumptions content. Check that the assumption follows all the rules.')
        return a

    @staticmethod
    def read(symbol: str) -> str:
        correct = False
        assumption = ''

        for line in read(ASSUMPTIONS_FILE):
            if f'!{symbol}: ' in line and correct is False:
                correct = True
                assumption += line + '\n'
            elif '!' in line:
                correct = False
            elif correct is True:
                assumption += line + '\n'
            else:
                pass

        if not assumption:
            raise Exception('Assumption with symbol "{symbol}" is not found in assumptions file.')

        assumption += '!\n'

        return assumption

    @staticmethod
    def load(assumption: str) -> 'Assumption':
        a = Assumption.read(assumption)
        return Assumption.parse(a)

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def name(self) -> str:
        return self._name

    @property
    def variables(self) -> List[Datum]:
        return self._variables

    @property
    def compute(self) -> List[Datum]:
        return self._to_compute

    @property
    def assume(self) -> List[Datum]:
        return self._assume
