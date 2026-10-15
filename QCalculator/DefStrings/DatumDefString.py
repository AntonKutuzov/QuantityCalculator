from typing import Literal

from QCalculator.DefStrings.CustomVarDDS import CustomVarDDS
from QCalculator.Exceptions.DatumExceptions import InvalidDatumDefString
from QCalculator._util import unpack_keys
from QCalculator.Exceptions.QDefStringExceptions import InvalidQDefString
from QCalculator import DEF_UR


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
    def __new__(cls, string: str, *args, **kwargs) -> object:
        try:
            return super().__new__(cls, string)
        except InvalidQDefString as iqds:
            raise InvalidDatumDefString(string) from iqds

    def __init__(self, string: str):
        super().__init__(string)



if __name__ == '__main__':
    dds = DatumDefString('N_A = 6.02e23 1/mole')

    print(dds.symbol)
    print(dds.subscript)
    print(dds.whole)
    print(dds.exponent)
    print(dds.unit)
