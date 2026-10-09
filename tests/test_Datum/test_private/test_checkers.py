import pytest
from QCalculator.Exceptions.DatumExceptions import InvalidSymbol
from tests.test_Datum import d1
from QCalculator.Datum import Regex


VALID_CASES = [
    'A', 'AB', 'AbC', 'ab',
    'A_1', 'a_2',
    'a3', 'ab123', 'ab_123',
]

INVALID_CASES = [
    '', ' ',
    '98a',
    'a_', '_B1', '1_B', 'a_1_2', 'a__1',
    'A-', '-A', 'a,', 'B%',
    'a ', 'b_1 ',
    'ж', 'ф'
]

@pytest.mark.parametrize("symbol", VALID_CASES)
def test_confirm_symbol_valid_cases(d1, symbol):
    assert d1._confirm_symbol(symbol, raise_exception=False) is True

@pytest.mark.parametrize("symbol", INVALID_CASES)
def test_confirm_symbol_invalid_cases_no_exception(d1, symbol):
    assert d1._confirm_symbol(symbol, raise_exception=False) is False

@pytest.mark.parametrize("symbol", INVALID_CASES)
def test_confirm_symbol_invalid_cases_with_exception(d1, symbol):
    with pytest.raises(InvalidSymbol):
        d1._confirm_symbol(symbol, raise_exception=True)

@pytest.mark.parametrize(
    "symbol, variable, subscript",
    [
        pytest.param('a', 'a', None),
        pytest.param('ab', 'ab', None),
        pytest.param('a1', 'a1', None),
        pytest.param('a_1', 'a', '1'),
        pytest.param('a_12', 'a', '12'),
        pytest.param('ab_12', 'ab', '12'),
        pytest.param('a_a', 'a', 'a'),
        pytest.param('a34_a12', 'a34', 'a12'),
    ]
)
def test_regex(symbol, variable, subscript):
    res = Regex.symbol.fullmatch(symbol)
    assert res.group('symbol') == variable
    assert res.group('sub') == subscript

