import pytest
from pint import Unit, UnitRegistry, Quantity
from math import isclose

from QCalculator.Datum import Datum
from QCalculator.Exceptions.QDefStringExceptions import InvalidUnitsExpression, UndefinedUnits, IncompatibleUnits
from tests.test_Datum import d1, d2



#           to              #
@pytest.mark.parametrize(
    'u',
    [
        1, True, [1, 2, 3], ('a', 'b', 'c'), Unit, UnitRegistry
    ]
)
def test_to_invalid_types(d1, u):
    with pytest.raises(TypeError):
        d1.to(u)


@pytest.mark.parametrize(
    'u, exception',
    [
        ('huh', UndefinedUnits),
        ('m8*2', InvalidUnitsExpression),
    ]
)
def test_to_with_invalid_string(d1, u, exception):
    with pytest.raises(exception):
        d1.to(u)


@pytest.mark.parametrize(
    'u',
    [
        'm/kg',
        's/m',
        'm',
        'kelvin'
    ]
)
def test_IncompatibleUnit_raising(d2, u):
    with pytest.raises(IncompatibleUnits):
        d2.to(u)


@pytest.mark.parametrize(
    'u, value',
    [
        ('km/h', 54),
        ('mm/ms', 15),
        (Unit('mm/ms'), 15),
        (Unit('km/h'), 54)
    ]
)
def test_valid_conversion(d2, u, value):
    d3 = d2.to(u)

    assert d3.variable == d2.variable
    assert isclose(d3.value, value)
    assert d3.units == Datum.spec.ureg.Unit(u)




#               scale               #
@pytest.mark.parametrize(
    "factor",
    [
        [1, 2, 3], False, Datum, '42'
    ]
)
def test_scale_invalid_types(d1, factor):
    with pytest.raises(TypeError):
        d1.scale(factor)



@pytest.mark.parametrize(
    "factor",
    [
        float('nan'), float('inf'), float('-inf')
    ]
)
def test_scale_ValueError(d1, factor):
    with pytest.raises(ValueError):
        d1.scale(factor)


@pytest.mark.parametrize(
    "factor, value",
    [
        (1, 5),
        (2, 10),
        (0.2, 1),
        (-5, -25),
        (-1, -5),
        (0, 0)
    ]
)
def test_scale_valid_types(d1, factor, value):
    d3 = d1.scale(factor)

    assert d3.variable == d1.variable
    assert isclose(d3.value, value)
    assert d3.units == d1.units



#               from_quantity           #
"""
TEST:
    - type errors
    - custom units
"""

@pytest.mark.parametrize(
    'var, q, units',
    [
        (42, Quantity('5 m'), None),
        (True, Quantity('5 m'), None),
        ([4, 2], Quantity('5 m'), None),

        ('C_1', '5 m', None),
        ('C_1', 42 , None),
        ('C_1', True, None),
        ('C_1', [4, 2], None),
        ('C_1', d1, None),

        ('C_1', Quantity('5 m'), 42),
        ('C_1', Quantity('5 m'), True),
        ('C_1', Quantity('5 m'), ['k', 'm']),
        ('C_1', Quantity('5 m'), Datum),
    ]
)
def test_from_quantity_TypeError(var, q, units):
    with pytest.raises(TypeError):
        Datum.from_quantity(var, q, units=units)


@pytest.mark.parametrize(
    'var, q, units',
    [
        ('C_1', Quantity('5 m'), 'm'),
        ('C_1', Quantity('5 m'), Unit('m')),
        ('C_1', Quantity('5 m'), Datum.spec.ureg.parse_units('m')),
        ('C_1', Datum.spec.ureg('5 m'), 'm'),
    ]
)
def test_from_quantity_no_TypeError(var, q, units):
    _ = Datum.from_quantity(var, q, units=units)
