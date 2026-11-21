from pint import Quantity
import pytest

from QCalculator.Datum import Datum
from tests._Older.Exceptions.DatumExceptions import InvalidVarName


ureg = Datum.spec.ureg


#           __init__            #
@pytest.mark.parametrize(
    "dds",
    [
        'm = 5 kg',
        'm = 5 kg'
    ]
)
def test_init_valid_types(dds):
    _ = Datum(dds)


@pytest.mark.parametrize(
    "dds",
    [
        2, ['m', '=', '5', 'kg'], True, Datum,
    ]
)
def test_init_invalid_types(dds):
    with pytest.raises(TypeError):
        _ = Datum(dds)


def test_units_belonging_to_ureg():
    d = Datum('g = 9.81 m/s**2')
    assert d.units._REGISTRY is Datum.spec.ureg



#           from_quantity           #
@pytest.mark.parametrize(
    "v, q",
    [
        ('m', Quantity('5 kg')),
        ('l', Quantity('10 m')),
    ]
)
def test_from_quantity_valid_types(v, q):
    _ = Datum.from_quantity(v, q)


@pytest.mark.parametrize(
    "v, q",
    [
        (1, Quantity('5 kg')),
        ([1, 2, 3], Quantity('10 m')),
        (True, Quantity('10 m')),

        ('m', '10 m'),
        ('m', ['10', 'm']),
    ]
)
def test_from_quantity_invalid_types(v, q):
    with pytest.raises(TypeError):
        _ = Datum.from_quantity(v, q)


@pytest.mark.parametrize(
    'v, q, variable, value, units',
    [
        ('m', Quantity('5 kg'), 'm', 5.0, ureg.parse_units('kg')),
        ('g_Moon', Quantity('9.81 m/s**2'), 'g_Moon', 9.81, ureg.parse_units('m/s**2')),
        ('N_A', Quantity('6.02e23 mole ** -1'), 'N_A', 6.02e23, ureg.parse_units('mole ** -1')),
        ('x', Quantity('0.3'), 'x', 0.3, ureg.parse_units('dimensionless')),
    ]
)
def test_from_quantity_correct_quantity_use(v, q, variable, value, units):
    d = Datum.from_quantity(v, q)

    assert d.variable == variable
    assert d.value == value
    assert d.units == units
