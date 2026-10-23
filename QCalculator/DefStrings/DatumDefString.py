from QCalculator.DefStrings.CustomVarDDS import CustomVarDDS
from QCalculator.Exceptions.DatumExceptions import InvalidDatumDefString
from QCalculator.util import unpack_keys
from QCalculator.Exceptions.QDefStringExceptions import InvalidQDefString


# PH0<variable>PH1=PH2<value>PH3<units>PH4
class DatumDefString(
    CustomVarDDS,
    pattern = CustomVarDDS.create_pattern(unpack_keys({
        (0, 4): '',
        (1, 2): ' +',
        3: '(?: +',
        4: ')?'
    }))
):
    def __new__(cls, string: str, *args, sympy_safe: bool = True, **kwargs) -> object:
        try:
            return super().__new__(cls, string, sympy_safe=sympy_safe)
        except InvalidQDefString as iqds:
            raise InvalidDatumDefString(string) from iqds


    def __init__(self, string: str, *, sympy_safe: bool = True):
        super().__init__(string, sympy_safe=sympy_safe)


    @property
    def string(self) -> str:
        u = self.ureg.parse_units(self.units)
        return rf'{self.variable} = {float(self.value)} {u}'



if __name__ == '__main__':
    dds = DatumDefString('N_A = 6.02e23 1/mole')

    print(dds.symbol)
    print(dds.subscript)
    print(dds.whole)
    print(dds.exponent)
    print(dds.units)
