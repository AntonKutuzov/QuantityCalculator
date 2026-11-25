from typing import Literal

from QCalculator.DefStrings import AbstractDDS, PatternGenerator, DSpec



class DatumDefString(AbstractDDS):
    _DDS_pg = PatternGenerator(('', ' +', ' +', ' +', ''))
    spec = DSpec(_DDS_pg.pattern, sympy_safe=True)


    @property
    def string(self) -> str:
        return f'{self.variable} = {self.value} {self.units}'



if __name__ == '__main__':
    dds = DatumDefString(f'g_Moon = {9.81/6} m/s**2')
    print(DatumDefString(dds).subscript)
