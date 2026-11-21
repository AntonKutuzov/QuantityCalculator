from QCalculator.DefStrings.DatumDefString import DatumDefString
import pytest


ur = DatumDefString.spec.ureg


#           VARIABLE PROPERTIES GROUP           #
@pytest.mark.parametrize(
    "dds, variable, symbol, subscript",
    [
        pytest.param('X_A = 0.95', 'X_A', 'X', 'A', id='typical-example'),
        pytest.param('X_A      = 0.95', 'X_A', 'X', 'A', id='many-spaces-VRG3'),
        pytest.param('X = 0.95', 'X', 'X', '', id='subs-absent-VRG4'),
    ]
)
def test_variable_group(dds, variable, symbol, subscript):
    ddef = DatumDefString(dds)

    assert ddef.variable == variable
    assert ddef.symbol == symbol
    assert ddef.subscript == subscript



#           VALUE PROPERTIES GROUP           #
@pytest.mark.parametrize(
    "dds, whole, exponent",
    [
        pytest.param('N_A = 6.02e23 mole ** -1', 6, 23),
        pytest.param('N_A = 6.02e-23 mole ** -1', 6, -23),
        pytest.param('N_A = -6.02e23 mole ** -1', 6, 23),
        pytest.param('N_A = -6.02e-23 mole ** -1', 6, -23),
        pytest.param('N_A = -6.02e0 mole ** -1', 6, 0),
        pytest.param('N_A = 1234.56', 1234, 0),
    ]
)
def test_whole_and_exponent_VLG1(dds, whole, exponent):
    ddef = DatumDefString(dds)

    assert ddef.whole == whole
    assert ddef.exponent == exponent


@pytest.mark.parametrize(
    "dds, value",
    [
        pytest.param('x = 5 m', 5),
        pytest.param('x = 0005 m', 5),
        pytest.param('x = 0005.1000 m', 5.1),
    ]
)
def test_value_VLG2(dds, value):
    ddef = DatumDefString(dds)
    assert ddef.value == value


@pytest.mark.parametrize(
    "dds, decimal",
    [
        pytest.param('x = 5 m', 0.0),
        pytest.param('x = 5.1 m', 0.1),
        pytest.param('x = 5.1000 m', 0.1),
        pytest.param('x = 005.1000 m', 0.1),
        pytest.param('x = 5.10e-5 m', 0.1),
    ]
)
def test_decimal_VLG3(dds, decimal):
    ddef = DatumDefString(dds)
    assert ddef.decimal == decimal


def test_sign_DLG4():
    dds = DatumDefString('m = 15.1 kg')
    assert dds.sign == 1

    dds = DatumDefString('m = -15.1 kg')
    assert dds.sign == -1


@pytest.mark.parametrize(
    "dds, nd",
    [
        pytest.param('m = 15 kg', 0, id='decimal-is-absent'),
        pytest.param('m = 15.0 kg', 0, id='decimal-is-zero'),
        pytest.param('m = 15.1 kg', 1, id='decimal-is-non-zero'),
        pytest.param('m = 15.110000 kg', 2, id='trailing-zeroes'),
    ]
)
def test_num_decimals_VLG5(dds, nd):
    ddef = DatumDefString(dds)
    assert ddef.num_decimals == nd


#           UNITS PROPERTIES GROUP           #
@pytest.mark.parametrize(
    "dds, units",
    [
        pytest.param('m = 5 kg', 'kg'),
        pytest.param('m = 5 m / s', 'm/s'),
        pytest.param('m = 5', 'dimensionless'),
        pytest.param('m = 5 dimensionless', 'dimensionless'),
    ]
)
def test_units_UNG1(dds, units):
    ddef = DatumDefString(dds)
    assert ur.parse_units(ddef.units) == ur.parse_units(units)
