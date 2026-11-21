from QCalculator.DefStrings.DatumDefString import DatumDefString
from QCalculator.Exceptions.QDefStringExceptions import InvalidUnitsExpression, InvalidQDefString
import pytest



"""
Tests in this file refer to DDS, SYM, WHL, DEC, EXP, and UNT of the documentation requirements. They test whether
the constructor correctly raises InvalidQDefString exception when given a wrong dds, or sucessfully create an
instance of DatumDefString when given correct one. So, in general the test must satisfy the following if-statement

if (dds matches all the rules):
    create an instance of DatumDefString
else:
    raise InvalidQDefString exception

The tests do not evaluate properties.
"""



#           TEST GENERAL DDS STRUCTURE          #
@pytest.mark.parametrize(
    "dds",
    ['g_Moon1= 9.81 m/s**2', 'g_Moon1 =9.81 m/s**2', 'g_Moon1 = 9.81m/s**2',
     '  g_Moon1 = 9.81 m/s**2', 'g_Moon1 = 9.81 m/s**2  ', '  g_Moon1 = 9.81 m/s**2   '
     ]
)
def test_spaces_between_major_groups_DDS1_invalid(dds):
    with pytest.raises(InvalidQDefString):
        _ = DatumDefString(dds)


def test_multiple_equal_sign():
    with pytest.raises(InvalidQDefString):
        _ = DatumDefString('m == 5 kg')


def test_spaces_between_major_groups_DDS1_valid():
    _ = DatumDefString('g_Moon1 = 9.81 m/s**2')


@pytest.mark.parametrize(
    "dds",
    [
        'g_Moon1 = 9.81 m/s**2',
        'g_Moon1 = 9E1 m/s**2',
        'g_Moon1 = 9.81E1',
        'g = 9.81E1 m/s**2',
    ]
)
def test_optional_groups_DDS2_valid(dds):
    _ = DatumDefString(dds)


@pytest.mark.parametrize(
    "dds",
    [
        '_Moon1 = 9.81 m/s**2',
        'g_Moon1 = .81E1 m/s**2',
        'g_Moon1 = E1 m/s**2',
        'g_Moon1 = m/s**2',
    ]
)
def test_optional_groups_DDS2_invalid(dds):
    with pytest.raises(InvalidQDefString):
        _ = DatumDefString(dds)


def test_valid_underscore_use_DDS3():
    _ = DatumDefString('g_Moon1 = 9.81 m/s**2')

    with pytest.raises(InvalidQDefString):
        _ = DatumDefString('g_ = 9.81 m/s**2')


def test_valid_decimal_dot_use_DDS4():
    _ = DatumDefString('g_Moon1 = 9.81 m/s**2')

    with pytest.raises(InvalidQDefString):
        _ = DatumDefString('g_Moon1 = 9. m/s**2')


def test_valid_exponent_sign_use_DDS5():
    _ = DatumDefString('N_A = 6.02E23 mole ** -1')
    _ = DatumDefString('N_A = 6.02e23 mole ** -1')

    with pytest.raises(InvalidQDefString):
        _ = DatumDefString('N_A = 6.02E mole ** -1')

    with pytest.raises(InvalidQDefString):
        _ = DatumDefString('N_A = 6.02e mole ** -1')


def test_valid_space_after_value_use_DDS6():
    _ = DatumDefString('g_Moon1 = 9.81 m/s**2')

    with pytest.raises(InvalidQDefString):
        _ = DatumDefString('g_Moon1 = 9.81 ')


def test_leading_spaces():
    with pytest.raises(InvalidQDefString):
        _ = DatumDefString('     N_A = 6.02e mole ** -1')


def test_trailing_spaces():
    with pytest.raises(InvalidQDefString):
        _ = DatumDefString('N_A = 6.02e mole ** -1    ')



#           TEST VARIABLE GROUP          #
# testing symbol
@pytest.mark.parametrize(
    "dds",
    [
        'g1_Moon1 = 9.81 m/s**2',
        'g$%_Moon1 = 9.81 m/s**2',
        'AC0_Moon1 = 9.81 m/s**2',
        ' _Moon1 = 9.81 m/s**2',
        '\r_Moon1 = 9.81 m/s**2',
    ]
)
def test_latin_letters_only_SYM1(dds):
    with pytest.raises(InvalidQDefString):
        _ = DatumDefString(dds)

# SYM-2 is checked in "test_optional_groups_DDS2_invalid"

def test_single_lower_case_SYM3_valid():
    _ = DatumDefString('x = -9')


def test_single_lower_case_SYM3_invalid():
    with pytest.raises(InvalidQDefString):
        _ = DatumDefString('aha = 1.234')


def test_upper_case_SYM4_valid():
    _ = DatumDefString('BMI_Pete = 23.2')
    _ = DatumDefString('A = 6')



# testing subscript
@pytest.mark.parametrize(
    "dds",
    [
        'g_1@ = 9.81 m/s**2',
        'g_abc\t = 9.81 m/s**2',
        'g_1/2 = 9.81 m/s**2',
        'g_-1 = 9.81 m/s**2',
        'g_0.5 = 9.81 m/s**2',
        'g_a bc = 9.81 m/s**2',
        'g_   = 9.81 m/s**2',
    ]
)
def test_latin_letters_and_numbers_SUB1(dds):
    with pytest.raises(InvalidQDefString):
        _ = DatumDefString(dds)


def test_at_least_one_symbol_SUB2():
    with pytest.raises(InvalidQDefString):
        _ = DatumDefString('g_ = 9.81 m/s**2')


@pytest.mark.parametrize(
    "dds",
    [
        "x_first = 5",
        "x_i = 5",
        "x_SEC = 5",
        "x_F = 5",
        "x_1 = 5",
        "x_12345 = 5",

        "x_F1A = 5",
        "x_AHA123 = 5",
        "x_HuH14 = 5",
    ]
)
def test_case_SUB3_to_SUB5(dds):
    _ = DatumDefString(dds)




#           TESTING VALUE GROUP             #
# testing whole group
@pytest.mark.parametrize(
    "dds",
    [
        'X_A = *7.9 dimensionless',
        'X_A = abc.123 dimensionless',
        'X_A =   .12 dimensionless',
        'X_A = \t\r.0 dimensionless'
    ]
)
def test_numbers_only_WHL1(dds):
    with pytest.raises(InvalidQDefString):
        _ = DatumDefString(dds)


@pytest.mark.parametrize(
    "dds",
    [
        'V_Car = 10.05 m/s',
        'V_Car = -10.05 m/s',
        'V_Car = -10 m/s',
    ]
)
def test_minus_sign_WHL2_valid(dds):
    _ = DatumDefString(dds)


@pytest.mark.parametrize(
    "dds",
    [
        'V_Car = --10.05 m/s',
        'V_Car = --10 m/s',
    ]
)
def test_minus_sign_WHL2_invalid(dds):
    with pytest.raises(InvalidQDefString):
        _ = DatumDefString(dds)


def test_leading_zeroes_WHL4():
    _ = DatumDefString('V = 0012 L')


# testing decimal group
@pytest.mark.parametrize(
    "dds",
    [
        'X_A = 1.$% dimensionless',
        'X_A = 123.huh dimensionless',
        'X_A = 15.    dimensionless',
        'X_A = 0.\t\r dimensionless'
    ]
)
def test_numbers_only_DEC1(dds):
    with pytest.raises(InvalidQDefString):
        _ = DatumDefString(dds)


def test_trailing_zeroes_DEC2():
    _ = DatumDefString('V = 12.12300000 L')


# testing exponent group
@pytest.mark.parametrize(
    "dds",
    [
        'X_A = 1.1E# dimensionless',
        'X_A = 1.2Eab dimensionless',
        'X_A = 15.E    dimensionless',
        'X_A = 0.0E\t\r dimensionless'
    ]
)
def test_numbers_only_EXP1(dds):
    with pytest.raises(InvalidQDefString):
        _ = DatumDefString(dds)


@pytest.mark.parametrize(
    "dds",
    [
        'N_p = 6.02e23',
        'N_p = 6.02e-23',
        'N_p = 6.02e+23',
        'N_p = 6.02E23',
        'N_p = 6.02E-23',
        'N_p = 6.02E+23',

    ]
)
def test_sign_EXP2_to_EXP3_valid(dds):
    _ = DatumDefString(dds)


@pytest.mark.parametrize(
    "dds",
    [
        'N_p = 6.02e--23',
        'N_p = 6.02e++23',
        'N_p = 6.02E--23',
        'N_p = 6.02E++23',
    ]
)
def test_sign_EXP2_to_EXP3_invalid(dds):
    with pytest.raises(InvalidQDefString):
        _ = DatumDefString(dds)




#           TESTING UNITS GROUP             #
@pytest.mark.parametrize(
    "dds, exception",
    [
        ('m = 5.6 ', InvalidQDefString),
        ('m = 5.6 \r', InvalidQDefString),
        ('m = 5.6 \t', InvalidQDefString),
        ('m = 5.6 \n', InvalidQDefString),

        ('m = 5.6 m *8 2', InvalidUnitsExpression),
    ]
)
def test_no_empty_string_UNT1(dds, exception):
    with pytest.raises(exception):
        _ = DatumDefString(dds)




#           COMPLEX EXPRESSIONS         #
@pytest.mark.parametrize(
    "dds",
    [
        'g_Moon1 = 1.635 m/s ** 2',
        'N_Av = 6.022E+23 mole ** -1',
        'CONV_A1 = 0.96434',
        'x_f = 0.56 dimensionless',
        'm_electron = 9.1093837e-31 kg',
        'CHARGE_electron = -1.60217663E-19 coulombs',
        'a = 5',
    ]
)
def test_complex_expressions(dds):
    _ = DatumDefString(dds)


@pytest.mark.parametrize(
    "dds",
    [
        'a = 0',
        'a = 0.0',
        'a = -0',
        'a = -0.0'
    ]
)
def test_special_cases(dds):
    _ = DatumDefString(dds)
