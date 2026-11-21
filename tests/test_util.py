import pytest

from re import Match

from QCalculator.DefStrings import AbstractDDS, PatternGenerator, DSpec
from QCalculator.Exceptions.QDefStringExceptions import SymbolSympyUnsafe, UndefinedUnits, InvalidUnitsExpression
from QCalculator.util import (
validate_type, validate_types, must_match, unpack_keys,
check_sympy_safety, check_unit_validity
)



# TESTING validate_type
@pytest.mark.parametrize(
    'var, types',
    [
        (5, int),
        (5.0, float),
        ('5', (str, float, int)),
        (5.0, (int, float)),
        (False, (bool,)),
        (True, (int, bool)),
    ]
)
def test_validate_type_valid(var, types):
    assert validate_type(var, types) is None


@pytest.mark.parametrize(
    'var, types',
    [
        (5.0, int),
        (5.0, (str, bool)),
        ('5', (float, int)),
        (1, (bool,)),
    ]
)
def test_validate_type_invalid(var, types):
    with pytest.raises(TypeError):
        validate_type(var, types)



# TESTING validate_types
@pytest.mark.parametrize(
    'var, types',
    [
        ([5], [int]),
        ([5.0], [float]),
        (['5'], [(str, float, int)]),
        ([5, 5.0], [int, float]),
        (['5', 5, 5], [(str, int, float), (int, float), (int,)])
    ]
)
def test_validate_types_valid(var, types):
    assert validate_types(var, types) is None


@pytest.mark.parametrize(
    'var, types',
    [
        ([5], [float]),
        ([5.0], [(str, int)]),
        (['5'], [(float, int, bool)]),
        ([5, 5.0], [int, str]),
        (['5', 5, 5], ([str, int, float], [int, float], float))
    ]
)
def test_validate_type_invalid(var, types):
    with pytest.raises(TypeError):
        validate_types(var, types)


@pytest.mark.parametrize(
    'var, types',
    [
        ([5], [float, int]),
        (['5', 5, True], [(float, int, bool)]),
        ([5, 5.0], [int, str, int]),
        (['5', 5, 5], ([],))
    ]
)
def test_validate_type_different_list_size(var, types):
    with pytest.raises(ValueError):
        validate_types(var, types)


# TESTING must_match
@pytest.mark.parametrize(
    'pattern, string',
    [
        ('symbol', 'BMI'),
        ('variable', 'BMI_Pete'),
        ('value', '5.12e2'),
        ('units', 'm / s ** 2')
    ]
)
def test_must_match_valid(pattern, string):
    assert isinstance(must_match(pattern, string), Match)


@pytest.mark.parametrize(
    'pattern, string',
    [
        ('symbol', 'BmI'),
        ('variable', '_Pete'),
        ('value', '5.12ee2'),
        ('units', '')
    ]
)
def test_must_match_invalid(pattern, string):
    with pytest.raises(ValueError):
        must_match(pattern, string)


def test_must_match_wrong_pattern():
    with pytest.raises(ValueError):
        must_match('huh', 'hello world')


def test_must_match_other_pattern():
    from re import compile

    regex = '[A-Z][a-z]?[0-9]?'
    string = 'Cl2'
    pattern = compile(regex)
    ref_match = pattern.fullmatch(string)
    test_match = must_match('other', string, pattern)

    assert ref_match.string == test_match.string
    assert ref_match.re == test_match.re
    assert ref_match.span() == test_match.span()


# TESTING unpack_keys
def test_unpack_keys():
    d0 = {
        (1, 2, 3): 'a',
        4: 'b',
        (5,): 'c'
    }

    d1 = {
        1: 'a',
        2: 'a',
        3: 'a',
        4: 'b',
        5: 'c'
    }

    test_d = unpack_keys(d0)

    assert test_d == d1


@pytest.mark.parametrize(
    'd',
    [
        1234, [1, 2, 3, 4], False, object
    ]
)
def test_unpack_keys_wrong_types(d):
    with pytest.raises(TypeError):
        unpack_keys(d)


# TESTING check_unit_validity
class DDS(AbstractDDS):
    _pg = PatternGenerator(placeholders=('', ' +', ' +', ' +', ''))
    spec = DSpec(pattern = _pg.pattern)

    @property
    def string(self) -> str:
        return f'{self.variable} = {self.value} {self.units}'


def test_check_unit_validity_correct():
    pass


@pytest.mark.parametrize(
    'cls, unit',
    [
        (str, 'm'),
        (TypeError, 'm'),

        (DDS, 42),
        (DDS, False),
        (DDS, DDS)
    ]
)
def test_check_unit_validity_TypeError(cls, unit):
    with pytest.raises(TypeError):
        check_unit_validity(cls, unit)


@pytest.mark.parametrize(
    'unit',
    [
        'huh', 'aaa', 'mmm',
    ]
)
def test_check_unit_validity_UndefinedUnits(unit):
    with pytest.raises(UndefinedUnits):
        check_unit_validity(DDS, unit)


@pytest.mark.parametrize(
    'unit',
    [
        '-+=', '1234', '12_', '$#'
    ]
)
def test_check_unit_validity_InvalidUnitsExpression(unit):
    with pytest.raises(InvalidUnitsExpression):
        check_unit_validity(DDS, unit)


# TESTING check_sympy_safety
def test_check_sympy_safety_correct():
    assert check_sympy_safety('m') is None

def test_check_sympy_safety_wrong():
    with pytest.raises(SymbolSympyUnsafe):
        check_sympy_safety('N')
