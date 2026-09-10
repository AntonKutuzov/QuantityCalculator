import pint
import pytest
from pint import Quantity, UnitRegistry
from sympy import Symbol

from QCalculator import Datum
from QCalculator.Exceptions.DatumExceptions import (
    IncompatibleUnits,
    InitializationError,
    InvalidString,
    InvalidSymbol,
    UndefinedUnit
)

from tests import exception_handling


ur = Datum.ureg
fur = UnitRegistry(system='SI')


@pytest.fixture
def d1():
    return Datum('l', 2, 'meter')

@pytest.fixture
def d2():
    return Datum('t', 5.2, 'second')

@pytest.fixture
def d3():
    return Datum('d', 25.5, 'cm')


def _test_datum(datum, expected):
    assert datum._symbol_str == expected['symbol']
    assert datum._value_str == pytest.approx(expected['value'], rel=1e-6, abs=1e-9)
    assert datum.units == expected['units']


def test_init_datum():
    # testing initialisation from separate variables
    dat1 = Datum('n', 150, '')
    expect1 = {
        'symbol': 'n',
        'value': 150,
        'units': ur.Unit(''),
        'units str': 'dimensionless',
        'base units': ur.Unit(''),
        'base units str': 'dimensionless'
    }
    _test_datum(dat1, expect1)

    dat2 = Datum('p', 101.325, 'kPa')
    expect2 = {
        'symbol': 'p',
        'value': 101.325,
        'units': ur('kPa'),
        'units str': 'kilopascal',
        'base units': ur('Pa'),
        'base units str': 'kilogram / meter / second ** 2'
    }
    _test_datum(dat2, expect2)

    with pytest.raises(TypeError):
        Datum(1, 2, 3)

    with pytest.raises(pint.UndefinedUnitError):
        Datum('a', 101, 'huh')

    with pytest.raises(InvalidSymbol):
        Datum('N', 6.02*10**23, 'dimensionless')

    with pytest.raises(InvalidSymbol):
        Datum('', 10, 'km')
        Datum(' ', 10, 'km')


@pytest.mark.parametrize(
    "symbol, quantity, exception, expected",
    [
        pytest.param('l', 50 * ur('cm'), None, {'symbol': 'l', 'value': 50, 'units': ur('cm'), 'units str': 'centimeter', 'base units': ur('m'), 'base units str': 'meter'}, id='normal'),
        pytest.param('l1', 50 * ur('cm'), None, {'symbol': 'l1', 'value': 50, 'units': ur('cm'), 'units str': 'centimeter', 'base units': ur('m'), 'base units str': 'meter'}, id='letter-and-number'),
        pytest.param('l_min', 50 * ur('cm'), None, {'symbol': 'l_min', 'value': 50, 'units': ur('cm'), 'units str': 'centimeter', 'base units': ur('m'), 'base units str': 'meter'}, id='underscore'),
        pytest.param('l1_min', 50 * ur('cm'), None, {'symbol': 'l1_min', 'value': 50, 'units': ur('cm'), 'units str': 'centimeter', 'base units': ur('m'), 'base units str': 'meter'}, id='letter-number-underscore'),
        pytest.param('la12', 50 * ur('cm'), None, {'symbol': 'la12', 'value': 50, 'units': ur('cm'), 'units str': 'centimeter', 'base units': ur('m'), 'base units str': 'meter'}, id='letters-numbers'),

        pytest.param('_l', 50 * ur('cm'), InvalidSymbol, None, id='underscore-first'),
        pytest.param('0l', 50 * ur('cm'), InvalidSymbol, None, id='number-first'),
        pytest.param('#$L', 50 * ur('cm'), InvalidSymbol, None, id='special-symbols'),
    ]
)
def test_from_quantity(symbol, quantity, exception, expected):
    with exception_handling(exception):
        d = Datum.from_quantity(symbol, quantity)
        _test_datum(d, expected)


@pytest.mark.parametrize(
    "string, exception, expected",
    [
        pytest.param('t=15ms',          None,   {'symbol': 't', 'value': 15, 'units': ur('ms'), 'units str': 'millisecond', 'base units': ur('s'), 'base units str': 'second'},                                         id='no-spaces'),
        pytest.param('t_1 = 15 ms',     None,   {'symbol': 't_1', 'value': 15, 'units': ur('ms'), 'units str': 'millisecond', 'base units': ur('s'), 'base units str': 'second'},                                         id='underscore'),
        pytest.param('t = 15 ms',       None,   {'symbol': 't', 'value': 15, 'units': ur('ms'), 'units str': 'millisecond', 'base units': ur('s'), 'base units str': 'second'},                                         id='whole-part'),
        pytest.param('t = -15 ms',      None,   {'symbol': 't', 'value': -15, 'units': ur('ms'), 'units str': 'millisecond', 'base units': ur('s'), 'base units str': 'second'},                                        id='negative-whole'),
        pytest.param('t = 15.2 ms',     None,   {'symbol': 't', 'value': 15.2, 'units': ur('ms'), 'units str': 'millisecond', 'base units': ur('s'), 'base units str': 'second'},                                       id='decimal-part'),
        pytest.param('t = 15.2',        None,   {'symbol': 't', 'value': 15.2, 'units': ur('dimensionless'), 'units str': 'dimensionless', 'base units': ur('dimensionless'), 'base units str': 'dimensionless'},       id='unitless-string'),
        pytest.param('t12 = 15 ms',     None,   {'symbol': 't12', 'value': 15, 'units': ur('ms'), 'units str': 'millisecond', 'base units': ur('s'), 'base units str': 'second'},                                       id='numbers-in-variable'),
        pytest.param('ta = 15 ms',      None,   {'symbol': 'ta', 'value': 15, 'units': ur('ms'), 'units str': 'millisecond', 'base units': ur('s'), 'base units str': 'second'},                                        id='multiple-letter-variable'),
        pytest.param('ta12 = 15 ms',    None,   {'symbol': 'ta12', 'value': 15, 'units': ur('ms'), 'units str': 'millisecond', 'base units': ur('s'), 'base units str': 'second'},                                      id='multiple-letters-and-numbers-variable'),
        pytest.param('t = 15 ms**2',    None,   {'symbol': 't', 'value': 15, 'units': ur('ms**2'), 'units str': 'millisecond ** 2', 'base units': ur('s**2'), 'base units str': 'second ** 2'},                         id='units-with-power'),
        pytest.param('t = 15 ms**-2',   None,   {'symbol': 't', 'value': 15, 'units': ur('ms**-2'), 'units str': '1 / millisecond ** 2', 'base units': ur('s**-2'), 'base units str': '1 / second ** 2'},               id='units-with-negative-power'),
        pytest.param('t = 6.02e10',     None,   {'symbol': 't', 'value': 6.02e10, 'units': ur('dimensionless'), 'units str': 'dimensionless', 'base units': ur('dimensionless'), 'base units str': 'dimensionless'},    id='value-with-e-power'),
        pytest.param('t = 6.02e-10',    None,   {'symbol': 't', 'value': 6.02e-10, 'units': ur('dimensionless'), 'units str': 'dimensionless', 'base units': ur('dimensionless'), 'base units str': 'dimensionless'},   id='value-with-negative-e-power'),
        pytest.param('t = 2.2**10',     None,   {'symbol': 't', 'value': 2.2**10, 'units': ur('dimensionless'), 'units str': 'dimensionless', 'base units': ur('dimensionless'), 'base units str': 'dimensionless'},    id='value-with-**-power'),
        pytest.param('t = 2.2**-10',    None,   {'symbol': 't', 'value': 2.2**-10, 'units': ur('dimensionless'), 'units str': 'dimensionless', 'base units': ur('dimensionless'), 'base units str': 'dimensionless'},   id='value-with-negative-**-power'),
        pytest.param('t = 3.3^10',      None,   {'symbol': 't', 'value': 3.3**10, 'units': ur('dimensionless'), 'units str': 'dimensionless', 'base units': ur('dimensionless'), 'base units str': 'dimensionless'},    id='value-with-^-power'),
        pytest.param('t = 3.3^-10',     None,   {'symbol': 't', 'value': 3.3**-10, 'units': ur('dimensionless'), 'units str': 'dimensionless', 'base units': ur('dimensionless'), 'base units str': 'dimensionless'},   id='value-with-negative-^-power'),

        pytest.param('lorem ipsum', InvalidString, None, id='not-a-ddf'),
        pytest.param('N = 6.02e23', InvalidSymbol, None, id='symbol-forbidden-sympy'),
        pytest.param( '= 10 km', InvalidString, None, id='variable-missing'),
        pytest.param('0a = 22.4 L/mole', InvalidString, None, id='invalid-variable-1'),
        pytest.param('#$ = 22.4 L/mole', InvalidString, None, id='invalid-variable-2'),
        pytest.param('V = 22.4 yuh', UndefinedUnit, None, id='unknown-units'),
        pytest.param('V = .4', InvalidString, None, id='invalid-value-1'),
        pytest.param('V_0 = 4.', InvalidString, None, id='invalid-value-2'),
    ]
)
def test_from_string(string, exception, expected):
    with exception_handling(exception):
        d = Datum.from_string(string)
        _test_datum(d, expected)


def test_from_string_details():
    details = {
        'symbol': 'h',
        'whole': '5',
        'decimal': '.2',
        'value_power': '2',
        'power_type': 'e',
        'units': 'm**2',
    }

    d, det = Datum.from_string('h = 5.2e2 m**2', return_details=True)
    assert det == details


def test_as_datum():
    # initialization from string
    s = 'p = 101.325 kPa'
    fd = Datum.as_datum(s)
    expect = {
        'symbol': 'p',
        'value': 101.325,
        'units': ur('kPa'),
        'units str': 'kilopascal',
        'base units': ur('Pa'),
        'base units str': 'kilogram / meter / second ** 2'
    }
    _test_datum(fd, expect)

    # initialization from quantity and symbol
    q = 10 * ur('meter')
    fd = Datum.as_datum(q, symbol='l')
    expect = {
        'symbol': 'l',
        'value': 10,
        'units': ur('m'),
        'units str': 'meter',
        'base units': ur('m'),
        'base units str': 'meter'
    }
    _test_datum(fd, expect)

    # initialization from datum and check that they are different objects
    d = Datum('m', 15.1, 'g')
    fd = Datum.as_datum(d)

    expect_old = {
        'symbol': 'm',
        'value': 15.1,
        'units': ur('g'),
        'units str': 'gram',
        'base units': ur('kilogram'),
        'base units str': 'kilogram'
    }
    expect_new1 = {
        'symbol': 'm',
        'value': 15.1,
        'units': ur('g'),
        'units str': 'gram',
        'base units': ur('kilogram'),
        'base units str': 'kilogram'
    }
    expect_new2 = {
        'symbol': 'm',
        'value': 0.0151,
        'units': ur('kg'),
        'units str': 'kilogram',
        'base units': ur('kilogram'),
        'base units str': 'kilogram'
    }

    _test_datum(fd, expect_new1)

    # changing new Datum to see if it affects the old one
    fd.ito_base_units()

    _test_datum(fd, expect_new2)
    _test_datum(d, expect_old)

    # testing invalid initializations
    with pytest.raises(InitializationError):
        Datum.as_datum('definitely not a Datum definition string')

    with pytest.raises(InitializationError):
        Datum.as_datum(q)

def test_str_(d1, d2):
    assert d1.__str__() == 'l = 2.0 meter'
    assert d2.__str__() == 't = 5.2 second'


def test_eq_(d1, d2):
    assert (d1 == d2) is False
    assert (d1 == Datum('l', 2.0, 'm')) is True
    assert (d1 == Datum('l', 200, 'cm')) is True
    assert (d1 == Datum('L', 2.0, 'm')) is False
    assert (d1 == Datum('a', 2.0, 'm')) is False
    assert (d1 == Datum('l', 2.0, 'second')) is False
    assert (d1 == Datum('l', 4.0,'m')) is False


@pytest.mark.parametrize(
    "other, expected, exception",
    [
        (Quantity(1, 'meter'),          2*ur('dimensionless'),   None),
        (Quantity(2, 'second'),         1*ur('meter / second'),  None),
        (Quantity(4, 'dimensionless'),  0.5*ur('meter'),         None),

        (Datum('l', 2, 'meter'),    1*ur('dimensionless'),       None),
        (Datum('a', 4, 'second'),   0.5*ur('meter / second'),    None),

        ('string', None, TypeError),
        (2, None, TypeError)
    ]
)
def test_div(d1, other: Quantity|Datum, expected: Quantity, exception):
    if exception is None:
        res = d1.div(other)
        assert res.magnitude == pytest.approx(expected.magnitude)
        assert res.units == expected.units
    else:
        with pytest.raises(exception):
            d1.div(other)


@pytest.mark.parametrize(
    "other, expected, exception",
    [
        (Quantity(1, 'meter'),          0.5*ur('dimensionless'), None),
        (Quantity(2, 'second'),         1*ur('second / meter'),  None),
        (Quantity(4, 'dimensionless'),  2*ur('meter ** -1'),     None),

        (Datum('l', 2, 'meter'),    1*ur('dimensionless'),   None),
        (Datum('a', 4, 'second'),   2*ur('second / meter'),  None),

        ('string', None, TypeError),
        (2, None, TypeError)
    ]
)
def test_rdiv(d1, other: Quantity|Datum, expected: Quantity, exception):
    if exception is None:
        res = d1.rdiv(other)
        assert res.magnitude == pytest.approx(expected.magnitude)
        assert res.units == expected.units

    else:
        with pytest.raises(exception):
            d1.rdiv(other)


@pytest.mark.parametrize(
    "other, expected, exception",
    [
        (Quantity(1, 'meter'),          2*ur('meter ** 2'),      None),
        (Quantity(2, 'second'),         4*ur('second * meter'),  None),
        (Quantity(4, 'dimensionless'),  8*ur('meter'),           None),

        (Datum('l', 2, 'meter'),    4*ur('meter ** 2'),      None),
        (Datum('a', 4, 'second'),   8*ur('second * meter'),  None),

        ('string', None, TypeError),
        (2, None, TypeError)
    ]
)
def test_mul(d1, other: Quantity|Datum, expected: Quantity, exception):
    if exception is None:
        res = d1.mul(other)
        assert res.magnitude == pytest.approx(expected.magnitude)
        assert res.units == expected.units

    else:
        with pytest.raises(exception):
            d1.mul(other)


@pytest.mark.parametrize(
    "other, expected, exception",
    [
        (Quantity(1, 'meter'),          3*ur('meter'),   None),
        (Quantity(2, 'second'),         None,                   IncompatibleUnits),
        (Quantity(4, 'dimensionless'),  None,                   IncompatibleUnits),

        (Datum('l', 2, 'meter'),    4*ur('meter'),   None),
        (Datum('a', 4, 'meter'),    6*ur('meter'),   None),
        (Datum('t', 2, 'second'),   None,                   IncompatibleUnits),

        ('string', None, TypeError),
        (2, None, TypeError)
    ]
)
def test_add(d1, other: Quantity|Datum, expected: Quantity, exception):
    if exception is None:
        res = d1.add(other)
        assert res.magnitude == pytest.approx(expected.magnitude)
        assert res.units == expected.units

    else:
        with pytest.raises(exception):
            d1.add(other)


@pytest.mark.parametrize(
    "other, expected, exception",
    [
        (Quantity(1, 'meter'),         1*ur('meter'),    None),
        (Quantity(2, 'second'),        None,                    IncompatibleUnits),
        (Quantity(4, 'dimensionless'), None,                    IncompatibleUnits),

        (Datum('l', 6, 'meter'),    -4*ur('meter'),  None),
        (Datum('a', 2, 'meter'),    0*ur('meter'),   None),
        (Datum('t', 2, 'second'),   None,                   IncompatibleUnits),

        ('string', None, TypeError),
        (2, None, TypeError)
    ]
)
def test_sub(d1, other: Quantity|Datum, expected: Quantity, exception):
    if exception is None:
        res = d1.sub(other)
        assert res.magnitude == pytest.approx(expected.magnitude)
        assert res.units == expected.units

    else:
        with pytest.raises(exception):
            d1.sub(other)


@pytest.mark.parametrize(
    "other, expected, exception",
    [
        (Quantity(1, 'meter'),         -1*ur('meter'),   None),
        (Quantity(2, 'second'),        None,                    IncompatibleUnits),
        (Quantity(4, 'dimensionless'), None,                    IncompatibleUnits),

        (Datum('l', 6, 'meter'),    4*ur('meter'),   None),
        (Datum('a', 2, 'meter'),    0*ur('meter'),   None),
        (Datum('t', 2, 'second'),   None,            IncompatibleUnits),

        ('string', None, TypeError),
        (2, None, TypeError)
    ]
)
def test_rsub(d1, other: Quantity | Datum, expected: Quantity, exception):
    if exception is None:
        res = d1.rsub(other)
        assert res.magnitude == pytest.approx(expected.magnitude)
        assert res.units == expected.units

    else:
        with pytest.raises(exception):
            d1.rsub(other)


@pytest.mark.parametrize(
    "other, expected",
    [
        (Datum('t', 5, 'second'), 5*ur('second')),
        (Quantity(10, 'meter'), Quantity(10, 'meter'))
    ]
)
def test_get_quantity(other, expected):
    assert Datum._get_quantity(other) == expected


@pytest.mark.parametrize(
    "value, expected, exception",
    [
        pytest.param(0.0,           1,  None,           id='zero'),
        pytest.param(0.1,           1,  None,           id='float-1'),
        pytest.param(0.001,         3,  None,           id='float-2'),
        pytest.param(12,            0,  None,           id='int'),
        pytest.param('0.1',         1,  None,           id='str-float'),
        pytest.param('huh',         0,  InvalidString,  id='non-num-str'),
        pytest.param('1',           0,  None,           id='str-int'),
        pytest.param(False,         0,  TypeError,      id='bool-False'),
        pytest.param(True,          0,  TypeError,      id='bool-True'),
    ]
)
def test_get_decimals(value, expected, exception):
    if exception is not None:
        with pytest.raises(exception):
            assert Datum.get_decimals(value) == expected
    else:
        assert Datum.get_decimals(value) == expected


@pytest.mark.parametrize(
    "other, expected, exception",
    [
        (Datum('l', 10, 'cm'), True, None),
        (Datum('k', 5, 'nm'), True, None),
        (1*ur('mm'), True, None),
        ('cm', True, None),
        (ur('centimeter'), True, None),

        (Datum('l', 5, 'second'), False, None),
        (1*ur('newton'), False, None),
        ('K', False, None),
        (ur('pascal'), False, None),

        (False, False, TypeError),
        (True, False, TypeError),
        (1, False, TypeError)
    ]
)
def test_is_compatible(d1, other, expected, exception):
    if exception is not None:
        with pytest.raises(exception):
            assert d1.is_compatible(other) is expected
    else:
        assert d1.is_compatible(other) is expected


@pytest.mark.parametrize(
    "unit, in_place, exception, expected_new, expected_original",
    [
        ('ms',  True,    None,              None,                                                                                                                                               {'symbol': 't', 'value': 5_200, 'units': ur('millisecond'), 'units str': 'millisecond', 'base units': ur('second'), 'base units str': 'second'}),
        ('ms',  False,   None,              {'symbol': 't', 'value': 5_200, 'units': ur('millisecond'), 'units str': 'millisecond', 'base units': ur('second'), 'base units str': 'second'},    {'symbol': 't', 'value': 5.2, 'units': ur('second'), 'units str': 'second', 'base units': ur('second'), 'base units str': 'second'}),
        ('km',  True,    IncompatibleUnits, None,                                                                                                                                               {'symbol': 't', 'value': 5.2, 'units': ur('second'), 'units str': 'second', 'base units': ur('second'), 'base units str': 'second'}),
        ('km',  False,   IncompatibleUnits, None,                                                                                                                                               {'symbol': 't', 'value': 5.2, 'units': ur('second'), 'units str': 'second', 'base units': ur('second'), 'base units str': 'second'})

    ]
)
def test_to(d2, unit, in_place, exception, expected_new, expected_original):
    if exception is not None:
        with pytest.raises(exception):
            d2.to(unit, in_place=in_place)
            _test_datum(d2, expected_original)
    else:
        d = d2.to(unit, in_place=in_place)
        if in_place:
            assert d is None
        else:
            _test_datum(d, expected_new)
        _test_datum(d2, expected_original)

@pytest.mark.parametrize(
    "unit, in_place, expected",
    [
        ('km',  True,   {'symbol': 't', 'value': 5.2, 'units': ur('second'), 'units str': 'second', 'base units': ur('second'), 'base units str': 'second'}),
        ('km',  False,  {'symbol': 't', 'value': 5.2, 'units': ur('second'), 'units str': 'second', 'base units': ur('second'), 'base units str': 'second'})
    ]
)
def test_to_safety(d2, unit, in_place, expected):
    try:
        d2.to(unit, in_place=in_place)
    except IncompatibleUnits:
        pass
    finally:
        _test_datum(d2, expected)


@pytest.mark.parametrize(
    "unit, exception, expected",
    [
        ('cm', None, {'symbol': 'l', 'value': 200.0, 'units': ur('cm'), 'units str': 'centimeter', 'base units': ur('meter'), 'base units str': 'meter'}),
        ('Pa', IncompatibleUnits, None)
    ]
)
def test_ito(d1, unit, exception, expected):
    if exception is not None:
        with pytest.raises(exception):
            d1.ito(unit)
    else:
        d1.ito(unit)
        _test_datum(d1, expected)


@pytest.mark.parametrize(
    "in_place, expected_new, expected_original",
    [
        (True,  None,                                                                                                                                 {'symbol':'d', 'value': 0.255, 'units': ur('meter'), 'units str': 'meter', 'base units': ur('meter'), 'base units str': 'meter'}),
        (False, {'symbol': 'd', 'value': 0.255, 'units': ur('meter'), 'units str': 'meter', 'base units': ur('meter'), 'base units str': 'meter'},    {'symbol': 'd', 'value': 25.5, 'units': ur('centimeter'), 'units str': 'centimeter', 'base units': ur('meter'), 'base units str': 'meter'}),
    ]
)
def test_to_base_units(d3, in_place, expected_new, expected_original):
    d = d3.to_base_units(in_place=in_place)

    if in_place:
        assert d is None
    else:
        _test_datum(d, expected_new)

    _test_datum(d3, expected_original)


def test_ito_base_units(d3):
    expected = {
        'symbol': 'd',
        'value': 0.255,
        'units': ur('meter'),
        'units str': 'meter',
        'base units': ur('meter'),
        'base units str': 'meter'
    }

    d3.ito_base_units()
    _test_datum(d3, expected)


@pytest.mark.parametrize(
    "factor, in_place, exception, expected_new, expected_original",
    [
        (1,     False,  None,       {'symbol':'l', 'value':2.0, 'units':ur('meter'), 'units str':'meter', 'base units':'meter', 'base units str':'meter'},          {'symbol': 'l', 'value': 2.0, 'units': ur('meter'), 'units str': 'meter', 'base units': 'meter', 'base units str': 'meter'}),
        (2,     True,   None,       None,                                                                                                                           {'symbol': 'l', 'value': 4.0, 'units': ur('meter'), 'units str': 'meter', 'base units': 'meter', 'base units str': 'meter'}),
        (0.25,  False,  None,       {'symbol': 'l', 'value': 0.5, 'units': ur('meter'), 'units str': 'meter', 'base units': 'meter', 'base units str': 'meter'},    {'symbol': 'l', 'value': 2.0, 'units': ur('meter'), 'units str': 'meter', 'base units': 'meter', 'base units str': 'meter'}),
        (0.25,  True,   None,       None,                                                                                                                           {'symbol': 'l', 'value': 0.5, 'units': ur('meter'), 'units str': 'meter', 'base units': 'meter', 'base units str': 'meter'}),

        ('s',   True,   TypeError,  None,                                                                                                                           {'symbol': 'l', 'value': 2.0, 'units': ur('meter'), 'units str': 'meter', 'base units': 'meter', 'base units str': 'meter'}),
        (False, True,   None,       None,                                                                                                                           {'symbol': 'l', 'value': 0.0, 'units': ur('meter'), 'units str': 'meter', 'base units': 'meter', 'base units str': 'meter'}),
    ]
)
def test_scale(d1, factor, in_place, exception, expected_new, expected_original):
    if exception is None:
        newd = d1.scale(factor, in_place=in_place)

        if in_place:
            assert newd is None
        else:
            _test_datum(newd, expected_new)
        _test_datum(d1, expected_original)
    else:
        with pytest.raises(exception):
            d1.scale(factor, in_place=in_place)

def test_scale_safety(d1):
    expected = {
        'symbol': 'l',
        'value': 2,
        'units': ur('meter'),
        'base units': ur('meter'),
        'units str': 'meter',
        'base units str': 'meter'
    }

    try:
        d1.scale('lorem ipsum', in_place=True)
    except TypeError:
        pass
    finally:
        _test_datum(d1, expected)

def test_iscale(d3):
    expected = {
        'symbol': 'd',
        'value': -12.75,
        'units': ur('cm'),
        'units str': 'centimeter',
        'base units': ur('meter'),
        'base units str': 'meter'
    }

    d3.iscale(-0.5)
    _test_datum(d3, expected)


@pytest.mark.parametrize(
    "unit, expected, exception",
    [
        # ur() returns a Quantity, ur.Unit() returns a Unit instance
        (ur('centimeter'), ur('centimeter'), None),
        (fur('centimeter'), ur('centimeter'), None),
        ('cm', ur('centimeter'), None),
        ('centimeter', ur('centimeter'), None),
        ('pascal', ur('pascal'), None),  # test that is does not convert to base units
        ('', ur('dimensionless'), None),
        (fur('dimensionless'), ur('dimensionless'), None),
        (ur.Unit('millisecond'), ur.Unit('millisecond'), None),
        (fur.Unit('millisecond'), ur.Unit('millisecond'), None),

        ('definitely not a unit string', None, UndefinedUnit),
        (2, None, TypeError),
        (False, None, TypeError)
    ]
)
def test_normalize_units(unit, expected, exception):
    if not exception:
        newu = Datum.normalize_units(unit)
        assert newu._REGISTRY is ur
        assert newu == expected
    else:
        with pytest.raises(exception):
            Datum.normalize_units(unit)


def test_quantity_ppt(d1, d2, d3):
    assert d1.quantity == 2 * ur('m')
    assert d2.quantity == 5.2 * ur('s')
    assert d3.quantity == 25.5 * ur('cm')


def test_symbol_ppt(d1, d2, d3):
    assert d1.symbol == 'l'
    assert d2.symbol == 't'
    assert d3.symbol == 'd'


def test_sp_symbol_ppt(d1, d2, d3):
    assert d1.sp_symbol == Symbol('l')
    assert d2.sp_symbol == Symbol('t')
    assert d3.sp_symbol == Symbol('d')


def test_value_magnitude_ppt(d1, d2, d3):
    assert d1.magnitude == 2
    assert d2.magnitude == 5.2
    assert d3.magnitude == 25.5


def test_units_and_str_ppt(d1, d2, d3):
    assert type(d1.units) == ur.Unit
    assert type(d2.units) == ur.Unit
    assert type(d3.units) == ur.Unit

    assert d1.units == ur.Unit('meter')
    assert d2.units == ur.Unit('second')
    assert d3.units == ur.Unit('centimeter')

    assert d1.units_str == 'meter'
    assert d2.units_str == 'second'
    assert d3.units_str == 'centimeter'


def test_base_units_and_str_ppt(d1, d2, d3):
    assert d1.base_units == ur.Unit('meter')
    assert d2.base_units == ur.Unit('second')
    assert d3.base_units == ur.Unit('meter')

    assert d1.base_units_str == 'meter'
    assert d2.base_units_str == 'second'
    assert d3.base_units_str == 'meter'
