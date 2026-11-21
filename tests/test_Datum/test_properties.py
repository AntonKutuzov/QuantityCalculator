from pint import Quantity
from tests._Older.test_Datum import d1, d2
from QCalculator.Datum import Datum
from QCalculator.DefStrings.DatumDefString import DatumDefString


ureg = Datum.spec.ureg


def test_quantity(d1):
    assert d1.quantity == Quantity('5 kg')

    d3 = d1.to('g')
    assert d3.quantity == Quantity('5000 g')

    d4 = d1.scale(1/5)
    assert d4.quantity == Quantity('1 kg')


def test_variable(d1):
    assert d1.variable == 'm'
    assert d1.variable == d1.dds.variable


def test_value(d1):
    assert d1.value == 5.0
    assert d1.value == d1.dds.value


def test_units(d1):
    assert d1.units == ureg.parse_units('kg')
    assert d1.units == ureg.parse_units(d1.dds.units)


def test_base(d1, d2):
    assert d1.base == d1
    assert d2.base == d2

    d3 = Datum('m = 150 g')
    assert d3.base == Datum('m = 0.15 kg')


def test_dds(d1):
    assert d1.dds == DatumDefString('m = 5 kg')
