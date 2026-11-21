import pytest
from hypothesis import given, strategies as st

from QCalculator.DefStrings import AbstractDDS, DSpec, PatternGenerator
from QCalculator.Exceptions.QDefStringExceptions import (
    InvalidQDefString, SymbolSympyUnsafe, UndefinedUnits,
    InvalidVarName, FilteringException
)


# AbstractDDS is an abstract class, and it cannot be instantiated.
# Hence, a subclass is created for testing.
class DDS(AbstractDDS):
    _PG = PatternGenerator(placeholders=('', ' +', ' +', ' +', ''))
    spec = DSpec(
        pattern=_PG.pattern,
        sympy_safe=False,
        allowed_symbols=frozenset({'m', 'V', 'g', 'x'}),  # symbols, not variables
        value_filters=frozenset({
            lambda x: x>=0,
        })
    )

    @property
    def string(self) -> str:
        return f'{self.variable} = {self.value} {self.units}'


# ==========================================================================

def test_string_slices():
    dds = DDS('g_Moon = 1.635 m/s**2')

    print(dds)

    assert dds[2:6] == 'Moon'
    assert dds[::-1] == '2**s/m 536.1 = nooM_g'


# test __init__
@pytest.mark.parametrize(
    'dds, var, val, units',
    [
        ('m = 5 kg', 'm', 5.0, 'kg'),
        ('g_Moon = 3.27 m/s**2', 'g_Moon', 3.27, 'm/s**2'),
        ('V = 5e-2 km/h', 'V', 5e-2, 'km/h'),
    ]
)
def test_init_valid(dds, var, val, units):
    DDS(dds, check_units=False)


def test_init_invalid():
    with pytest.raises(InvalidQDefString):
        DDS(' m = 5  kg')  # in DDS only a single space is allowed, see above


@pytest.mark.parametrize(
    'dds',
    [42, DDS, False, 0.0, filter, [1, 2, 3]]
)
def test_init_TypeError(dds):
    with pytest.raises(TypeError):
        DDS(dds)

def test_subscript_returns_None():
    dds = DDS('m = 5 kg')
    assert dds.subscript is None


def test_forbidden_symbol():
    with pytest.raises(InvalidVarName):
        DDS('y = 4.5')


@pytest.mark.parametrize(
    'dds',
    [
        'm_A = 45 kg',
        'm_123 = 4.5 g',
        'V_water = 18 mL',
        'V_EG = 20 mL',
        'g_Moon = 3.27 m/s**2',
        'g_Earth = 9.81 m/s**2'
    ]
)
def test_variables_with_allowed_symbol(dds):
    DDS(dds)


@pytest.mark.parametrize(
    'dds',
    [
        'V_1 = -15.0 m/s',
        'V_2 = -15 m/s'
    ]
)
def test_value_filters(dds):
    with pytest.raises(FilteringException):
        DDS(dds)


@pytest.mark.parametrize(
    'dds',
    [
        'V_1 = 15.0 m/s',
    ]
)
def test_filter_provocation(dds):
    DDS(dds)


# checking __eq__
def test_check__eq__():
    dds1 = DDS('m = 5 gram')
    dds2 = DDS('m = 5.0 kilogram')

    assert dds1 == dds2


# checking sympy safety
class DDS2(AbstractDDS):
    _PG = PatternGenerator(placeholders=('', ' ', ' ', ' ', ''))
    spec = DSpec(pattern=_PG.pattern, sympy_safe=True)

    @property
    def string(self) -> str:
        return f'{self.variable} = {self.value} {self.units}'


@pytest.mark.parametrize(
    'dds, exception',
    [
        ('m = 5 kg', False),
        ('N = 6.02e23', True)
    ]
)
def test_sympy_safety(dds, exception):
    if exception:
        with pytest.raises(SymbolSympyUnsafe):
            DDS2(dds)
    else:
        DDS2(dds)


# testing properties
def test_match():
    ddef = 'g = 9.81 m / s ** 2'
    dds = DDS(ddef)
    assert dds.match == dds.spec.pattern.fullmatch(ddef)


@pytest.mark.parametrize(
    'dds, check_units, exc',
    [
        ('m = 5 kg', True, None),
        ('m = 5 huh', True, UndefinedUnits),
        ('m = 5 huh', False, None),
        ('m = 5 kg', False, None)
    ]
)
def test_units(dds, check_units, exc):
    if exc is not None:
        with pytest.raises(exc):
            DDS(dds, check_units=check_units)
    else:
        DDS(dds, check_units=check_units)


@pytest.mark.parametrize(
    'dds, sym, sub, val, units',
    [
        ('m = 5 kg', 'm', None, 5.0, 'kg'),
        ('g_Moon = 1.635 m/s**2', 'g', 'Moon', 1.635, 'm/s**2'),
    ]
)
def test_rest_properties(dds, sym, sub, val, units):
    ddef = DDS(dds, check_units=False)

    assert ddef.symbol == sym
    assert ddef.subscript == sub
    assert ddef.value == val
    assert ddef.units == units


# invariants
class DDS3(AbstractDDS):
    _PG = PatternGenerator(placeholders=('', ' +', ' +', ' +', ''))
    spec = DSpec(
        pattern=_PG.pattern,
        sympy_safe=False,
    )

    @property
    def string(self) -> str:
        return f'{self.variable} = {self.value} {self.units}'


units = [
    'm/s', 'J/mole/K', 'kg/m', 'g/kg',
    'm * s', 'm * kg', 'N * m', 'N * s',
    'mole ** -1', 'second ** -2', 'meter / second ** 2', 'meter ** 3',
    'kg', 'm', 's',
    'dimensionless', 'percent',
    'coulomb', 'second', 'pascal', 'newton', 'kelvin',
]


@given(
    symbol = st.from_regex('([a-z]|[A-Z]+)(_[a-zA-Z0-9]+)?', fullmatch=True),
    value = st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False)
    ),
    units = st.sampled_from(units)
)
def test_string_and_dds_to_dds(symbol, value, units):
    from math import isclose

    dds = f'{symbol} = {value} {units}'
    ddef1 = DDS3(dds)
    ddef2 = DDS3(ddef1.string)
    ddef3 = DDS3(ddef1)

    assert ddef1.variable == ddef2.variable
    assert ddef1.variable == ddef3.variable
    assert isclose(ddef1.value, ddef2.value)
    assert isclose(ddef1.value, ddef3.value)


@given(
    symbol=st.from_regex('([a-z]|[A-Z]+)(_[a-zA-Z0-9]+)?', fullmatch=True),
    value=st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False)
    ),
    units=st.sampled_from(units)
)
def test_string(symbol, value, units):
    dds = f'{symbol} = {value} {units}'
    ddef = DDS3(dds)

    assert DDS3(ddef).string == str(ddef)



@given(
    symbol=st.from_regex('([a-z]|[A-Z]+)(_[a-zA-Z0-9]+)?', fullmatch=True),
    value=st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False)
    ),
    units=st.sampled_from(units)
)
def test_match(symbol, value, units):
    dds = f'{symbol} = {value} {units}'
    ddef = DDS3(dds)

    assert DDS3(ddef).match == DDS3.spec.pattern.fullmatch(ddef)



@given(
    symbol=st.from_regex('([a-z]|[A-Z]+)(_[a-zA-Z0-9]+)?', fullmatch=True),
    value=st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False)
    ),
    units=st.sampled_from(units)
)
def test_symbol_and_sub_forming_a_var(symbol, value, units):
    dds = f'{symbol} = {value} {units}'
    ddef = DDS3(dds)

    if ddef.subscript is not None:
        assert ddef.variable == ddef.symbol + '_' + ddef.subscript
    else:
        assert ddef.variable == ddef.symbol

