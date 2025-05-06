from QCalculator.LinearIterator import LinearIterator
from typing import List
from QCalculator.Datum import Datum


class Assumption:
    def __init__(self, symbol: str, name: str = ''):
        self._symbol = symbol
        self._name = name
        self._variables = list()
        self._to_compute = list()
        self._assume = list()

    def __str__(self):
        return (f"{self._symbol} (full name: '{self._name}'). Assumes {', '.join([str(datum) for datum in self.variables])}."
                f" Computes {', '.join([str(var.symbol) + ' in ' + str(var.unit) for var in self.compute])}."
                f" Temporarily assumes for calculations that {', '.join(str(var) for var in self.assume)}.")

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
