from hypothesis import given, strategies as st

from QCalculator.Datum import Datum
from QCalculator.DefStrings.DatumDefString import DatumDefString
from tests._Older.test_Datum import d1, d2
from tests import skip_sympy_unsafe_symbols



units = [
    'm/s', 'J/mole/K', 'kg/m', 'g/kg',
    'm * s', 'm * kg', 'N * m', 'N * s',
    'mole ** -1', 'second ** -2', 'meter / second ** 2', 'meter ** 3',
    'kg', 'm', 's',
    'dimensionless', 'percent',
    'coulomb', 'second', 'pascal', 'newton', 'kelvin',
]

ureg = Datum.spec.ureg



def test_datum_immutability(d1):
    old_d1 = d1

    d3 = d1.to('g')

    assert d1 == old_d1

    d3 = d1.scale(1/5)

    assert d1 == old_d1


def test_dds_is_up_to_date(d1):
    d3 = d1.to('g')

    assert d3.dds == DatumDefString('m = 5000 g')

    d3 = d1.scale(1 / 5)

    assert d3.dds == DatumDefString('m = 1 kg')


@given(
    symbol = st.from_regex('([a-z]|[A-Z]+)(_[a-zA-Z0-9]+)?', fullmatch=True),
    value = st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False)
    ),
    units = st.sampled_from(units)
)
def test_quantity_is_value_times_units(symbol, value, units):
    dds = f'{symbol} = {value} {units}'
    d = Datum(dds)

    assert d.quantity == d.value * d.units


@given(
    symbol = st.from_regex('([a-z]|[A-Z]+)(_[a-zA-Z0-9]+)?', fullmatch=True),
    value = st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False)
    ),
    units = st.sampled_from(units)
)
def test_compatible_units(symbol, value, units):
    dds = f'{symbol} = {value} {units}'
    d = Datum(dds)

    assert d.compatible_units(d.base.units) is True
    assert d.compatible_units(d.base) is True
    assert d.compatible_units(d.base.quantity) is True
    assert d.compatible_units(d.units) is True
    assert d.compatible_units(d.quantity) is True
    assert d.compatible_units(d) is True
    assert d.compatible_units(d.dds.units) is True
    assert d.compatible_units(d.base.dds.units) is True


@given(
    symbol = st.from_regex('([a-z]|[A-Z]+)(_[a-zA-Z0-9]+)?', fullmatch=True),
    value = st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False)
    ),
    units = st.sampled_from(units)
)
def test_compliance_with_dds(symbol, value, units):
    if skip_sympy_unsafe_symbols(symbol):
        return None

    dds = f'{symbol} = {value} {units}'
    d = Datum(dds)

    assert d.variable == d.dds.variable
    assert d.value == d.dds.value
    assert d.units == ureg.parse_units(d.dds.units)


@given(
    symbol = st.from_regex('([a-z]|[A-Z]+)(_[a-zA-Z0-9]+)?', fullmatch=True),
    value = st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False)
    ),
    units = st.sampled_from(units)
)
def test_redefinition_from_dds(symbol, value, units):
    if skip_sympy_unsafe_symbols(symbol):
        return None

    dds = f'{symbol} = {value} {units}'

    d1 = Datum(dds)
    d2 = Datum(d1.dds)

    assert d1.dds.string == d2.dds.string
    assert d1.dds.string == DatumDefString(dds).string
    assert d2.dds.string == DatumDefString(dds).string
    assert d1 == d2
    assert d1.base.dds.string == d2.base.dds.string


@given(
    value = st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False)
    ),
    units = st.sampled_from(units)
)
def test_redefinition_from_quantity(value, units):
    dds = f'x = {value} {units}'

    d1 = Datum(dds)
    d2 = Datum.from_quantity(d1.variable, d1.quantity)

    assert d1.dds == d2.dds
    assert d1.dds == DatumDefString(dds)
    assert d2.dds == DatumDefString(dds)
    assert d1 == d2
    assert d1.base.dds == d2.base.dds


@given(
    value = st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False, width=16)
    )
)
def test_scale_reversibility(value):
    d1 = Datum('m = 5 kg')

    if value == 0:
        return

    d3 = d1.scale(1/value)
    d4 = d3.scale(value)

    assert d4 == d1



def test_to_reversibility(d2):
    d3 = d2.to('km/h')
    d4 = d3.to('m/s')

    assert d4 == d2


@given(
    units = st.sampled_from(units)
)
def test_unit_normalization(units):
    dds = f'x = 0.15 {units}'

    d = Datum(dds)

    assert d.units == d.spec.ureg.parse_units(units)
    assert d.units._REGISTRY == d.spec.ureg
    assert d.quantity == d.spec.ureg.Quantity(f'0.15 {units}')
