from hypothesis import given, strategies as st
from QCalculator.DefStrings.DatumDefString import DatumDefString
from math import isclose

from tests import skip_sympy_unsafe_symbols
from QCalculator.util import check_unit_validity





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
def test_string_INV1(symbol, value, units):
    if skip_sympy_unsafe_symbols(symbol):
        return None

    dds = f'{symbol} = {value} {units}'

    ddef1 = DatumDefString(dds)
    ddef2 = DatumDefString(ddef1.string)

    assert ddef1.variable == ddef2.variable
    assert isclose(ddef1.value, ddef2.value)


@given(
    value = st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False)
    )
)
def test_composed_value_INV2(value):
    dds = f'x = {value}'

    ddef = DatumDefString(dds)

    value = ddef.value
    composed_value = ddef.sign * (ddef.whole + ddef.decimal) * 10 ** ddef.exponent

    assert isclose(value, composed_value, rel_tol=1e-15)


def test_units_INV3():
    for u in units:
        dds = DatumDefString(f'x = 5 {u}')
        assert check_unit_validity(dds.__class__, dds.units) is None


@given(
    symbol = st.from_regex('([a-z]|[A-Z]+)(_[a-zA-Z0-9]+)?', fullmatch=True),
)
def test_variable_INV4(symbol):
    if skip_sympy_unsafe_symbols(symbol):
        return None

    dds = f'{symbol} = 1'
    ddef = DatumDefString(dds)

    if ddef.subscript:
        assert ddef.variable == ddef.symbol + '_' + ddef.subscript
    else:
        assert ddef.variable == ddef.symbol


@given(
    value = st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False)
    )
)
def test_positive_product_INV5(value):
    dds = f'x = {value}'

    ddef = DatumDefString(dds)

    assert ddef.value * ddef.sign >= 0.0


@given(
    symbol = st.from_regex('([a-z]|[A-Z]+)(_[a-zA-Z0-9]+)?', fullmatch=True),
    value = st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False)
    ),
    units = st.sampled_from(units)
)
def test_string_INV6(symbol, value, units):
    if skip_sympy_unsafe_symbols(symbol):
        return None

    dds = f'{symbol} = {float(value)} {units}'

    assert DatumDefString(dds).string == dds


@given(
    value = st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False)
    )
)
def test_INV7_to_INV9(value):
    dds = f'x = {value}'

    ddef = DatumDefString(dds)

    assert ddef.whole >= 0
    assert 0.0 <= ddef.decimal < 1
    assert ddef.num_decimals >= 0
