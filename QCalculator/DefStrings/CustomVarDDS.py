from typing import Literal

from QCalculator.DefStrings.QDefString import QDefString
from QCalculator._util import unpack_keys


# PH0<variable>PH1=PH2<value>PH3<units>PH4
class CustomVarDDS(
    QDefString,
    pattern = QDefString.create_pattern(unpack_keys({
        (0, 4): '',
        1: '.* ',
        2: ' +',
        3: '(?: +',
        4: ')?'
    }))
):
    def __init__(self, dds: str) -> None:
        super().__init__(dds)

    @property
    def symbol(self) -> str:
        return str(self.match.group('symbol'))

    @property
    def subscript(self) -> str:
        s = self.match.group('sub')

        if s is None:
            return ''
        else:
            return str(s)

    @property
    def whole(self) -> int:
        return int(self.match.group('whole'))

    @property
    def decimal(self) -> float:
        dec = self.match.group('decimal')

        if dec is None:
            return 0.0
        else:
            return float(f'0.{dec}')

    @property
    def sign(self) -> Literal[1, -1]:
        v = self.match.group('value')
        if v[0] == '-':
            return -1
        else:
            return 1

    @property
    def exponent(self) -> int:
        e = self.match.group('exponent')

        if e is None:
            return 0
        else:
            return int(e)

    @property
    def num_decimals(self) -> int:
        dec = self.decimal

        if dec == 0.0:
            return 0
        else:
            return len(str(dec)) - 2

    @property
    def norm_string(self) -> str:
        u = self.ureg.parse_units(self.unit)
        u = str(u)

        return f'{self.variable} = {self.value} {u}'



if __name__ == '__main__':
    dds = CustomVarDDS('N_A = 6.02e23 1/mole')

    print(dds.symbol)
    print(dds.subscript)
    print(dds.whole)
    print(dds.exponent)
    print(dds.unit)
