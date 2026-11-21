from typing import Literal

from QCalculator.DefStrings import AbstractDDS, PatternGenerator, DSpec



class DatumDefString(AbstractDDS):
    _DDS_pg = PatternGenerator(('', ' +', ' +', ' +', ''))
    spec = DSpec(_DDS_pg.pattern, sympy_safe=True)

    @property
    def symbol(self) -> str:
        return str(self.match.group('symbol'))

    @property
    def subscript(self) -> str:
        s = self.match.group('subscript')

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
    def string(self) -> str:
        return f'{self.variable} = {self.value} {self.units}'



if __name__ == '__main__':
    dds = DatumDefString(f'g_Moon = {9.81/6} m/s**2')
    print(DatumDefString(dds).subscript)
