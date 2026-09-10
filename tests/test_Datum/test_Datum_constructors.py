from tests.test_Datum import (
    ex1, ex2, ex3, ex4,
    _test_datum, ur, fur
)
import pytest
from QCalculator.Datum import Datum
from QCalculator.Exceptions.DatumExceptions import InvalidSymbol, UndefinedUnit, InvalidString

"""
Indicate only initial and final states, not what it calls in between, and what it does. The function description here
must represent *state*, not *paths* of the class' instance.

def __init__(self,
                 symbol: str,
                 magnitude: float|int|str,
                 units: str|Unit
            ) -> None:
    - checks the symbol -> InvalidSymbol, TypeError
    - domesticates units -> UndefinedUnit, TypeError
    - converts magnitude to a float -> TypeError
    - assigns symbol
    - assigns magnitude
    - assigns units

def from_string(dds: str) -> Datum:
    - checks dds' type -> TypeError
    - parses the string -> InvalidString
    - assigns symbol
    - assigns magnitude
    - assigns units -> UndefinedUnit

def from_quantity(symbol: str, quantity: pint.Quantity|int) -> Datum:
    - checks the symbol -> InvalidSymbol
    - check the type of 'quantity' -> TypeError
    - assigns symbol
    - assigns magnitude
    - assigns units

def as_datum(d: Datum|pint.Quantity|str, symbol: str) -> Datum:
    - checks d's type -> TypeError
    - parse string (if d is a string) -> InvalidString
    - assigns symbol -> InvalidSymbol
    - assigns magnitude
    - assigns units -> UndefinedUnit
    
    1) Ignores 'symbol' unless d is pint.Quantity
"""


@pytest.mark.parametrize(
    'symbol, magnitude, units, expected',
    [
        pytest.param('l', 2, 'meter', ex1, id='int-to-float'),
        pytest.param('d', 25.5, 'cm', ex3, id='float-to-float'),
        pytest.param('d', '25.5', 'cm', ex3, id='str-to-float'),
        pytest.param('t', 5.2, ur('second'), ex2, id='ureg-units'),
        pytest.param('t', 5.2, fur('second'), ex2, id='foreign-ureg-units'),
        pytest.param('n', 1, '', ex4, id='dimensionless-units'),
        pytest.param('n', 1, 'dimensionless', ex4, id='dimensionless-units')
    ]
)
def test_datum_init_nominal(symbol, magnitude, units, expected):
    d = Datum(symbol, magnitude, units)
    _test_datum(d, expected)


@pytest.mark.parametrize(
    'symbol, magnitude, units, exception',
    [
        pytest.param('N', 1, '', InvalidSymbol, id='InvalidSymbol'),
        pytest.param(5, 1, '', TypeError, id='TypeError-symbol'),
        pytest.param('m', 1, 'huh', UndefinedUnit, id='UndefinedUnit'),
        pytest.param('m', 1, 3, TypeError, id='TypeError-units'),
        pytest.param('p', TypeError, 'kPa', TypeError, id='TypeError-magnitude')
    ]
)
def test_datum_init_errors(symbol, magnitude, units, exception):
    with pytest.raises(exception):
        Datum(symbol, magnitude, units)


@pytest.mark.parametrize(
    'dds, expected',
    [
        pytest.param('l = 2 m', ex1, id='int-to-float'),
        pytest.param('t = 5.2 s', ex2, id='float-to-float'),
        pytest.param('d = 25.5 cm', ex3, id='non-base-units'),
        pytest.param('l=2m', ex1, id='no-spaces'),

        pytest.param('V0 = 22.4 L/mole', {'symbol': 'V0', 'magnitude': 22.4, 'units': ur('L/mole')}, id='V0'),
        pytest.param('V_0 = 22.4 L/mole', {'symbol': 'V_0', 'magnitude': 22.4, 'units': ur('L/mole')}, id='V_0'),
        pytest.param('V0_1 = 22.4 L/mole', {'symbol': 'V0_1', 'magnitude': 22.4, 'units': ur('L/mole')}, id='V0_1'),
        pytest.param('V0_a = 22.4 L/mole', {'symbol': 'V0_a', 'magnitude': 22.4, 'units': ur('L/mole')}, id='V0_a'),
        pytest.param('Vab = 22.4 L/mole', {'symbol': 'Vab', 'magnitude': 22.4, 'units': ur('L/mole')}, id='Vab'),

        pytest.param('n = 1', ex4, id='units-is-dimensionless'),
        pytest.param('n = 1 dimensionless', ex4, id='units-is-dimensionless-mentioned')
    ]
)
def test_from_string_nominal(dds, expected):
    d = Datum.from_string(dds)
    _test_datum(d, expected)


@pytest.mark.parametrize(
    'dds, exception',
    [
        pytest.param(5, TypeError, id='wrong-dds-type'),
        pytest.param('hello world', InvalidString, id='InvalidString'),
        pytest.param('V_ = 5 L', InvalidString, id='InvalidString-1'),
        pytest.param('_V = 5 L', InvalidString, id='InvalidString-2'),
        pytest.param('4V = 5 L', InvalidString, id='InvalidString-3'),
        pytest.param('V$% = 5 L', InvalidString, id='InvalidString-4'),
        pytest.param('N = 5', InvalidSymbol, id='InvalidSymbol'),
        pytest.param('V0 = 5 Lol', UndefinedUnit, id='UndefinedUnit'),
    ]
)
def test_from_string_errors(dds, exception):
    with pytest.raises(exception):
        Datum.from_string(dds)


@pytest.mark.parametrize(
    'symbol, quantity, expected',
    [
        pytest.param('l', 2 * ur('m'), ex1, id='int-to-float'),
        pytest.param('t', 5.2 * ur('s'), ex2, id='float-to-float'),
        pytest.param('d', 25.5 * ur('cm'), ex3, id='non-base-units'),
        pytest.param('t', 5.2 * fur('s'), ex2, id='foreign-ureg'),
        pytest.param('n', 1 * ur(''), ex4, id='dimensionless-units'),
        pytest.param('n', 1 * fur(''), ex4, id='dimensionless-units-foreign-ureg'),
        pytest.param('n', 1, ex4, id='int-as-dimensionless-quantity'),
    ]
)
def test_from_quantity_nominal(symbol, quantity, expected):
    d = Datum.from_quantity(symbol, quantity)
    _test_datum(d, expected)


@pytest.mark.parametrize(
    'symbol, quantity, exception',
    [
        pytest.param('N', 2 * ur('m'), InvalidSymbol, id='InvalidSymbol'),
        pytest.param('p', 'huh', TypeError, id='TypeError')
    ]
)
def test_from_quantity_errors(symbol, quantity, exception):
    with pytest.raises(exception):
        Datum.from_quantity(symbol, quantity)


@pytest.mark.parametrize(
    'd, symbol, expected',
    [
        pytest.param(Datum('l', 2, 'meter'), '', ex1, id='Datum-no-symbol'),
        pytest.param(Datum('l', 2, 'meter'), 'p', ex1, id='Datum-ignore-symbol'),
        pytest.param(Datum('l', 2, 'meter'), 'N', ex1, id='Datum-invalid-symbol-provocation'),
        pytest.param(2 * ur('meter'), 'l', ex1, id='quantity'),
        pytest.param(2 * fur('meter'), 'l', ex1, id='quantity-foreign-ureg'),
        pytest.param('l = 2 m', '', ex1, id='str-no-symbol'),
        pytest.param('l = 2 m', 'p', ex1, id='str-other-symbol'),
        pytest.param('l = 2 m', 'N', ex1, id='str-invalid-symbol-provocation'),
        pytest.param('n = 1', '', ex4, id='str-dimensionless-units'),
        pytest.param('n = 1 dimensionless', '', ex4, id='str-dimensionless-units-mentioned'),
        pytest.param(1 * ur(''), 'n', ex4, id='quantity-dimensionless-units'),
        pytest.param(1, 'n', ex4, id='int-as-dimensionless-quantity'),
    ]
)
def test_as_datum_nominal(d, symbol, expected):
    d = Datum.as_datum(d, symbol)
    _test_datum(d, expected)


@pytest.mark.parametrize(
    'd, symbol, exception',
    [
        pytest.param(42, 'd', TypeError, id='d-type-error'),
        pytest.param('hello world', '', InvalidString, id='InvalidString'),
        pytest.param('hello world', 'N', InvalidString, id='InvalidString-with-InvalidSymbol-provocation'),
        pytest.param(5 * ur('m'), 'N', InvalidSymbol, id='Quantity-InvalidSymbol'),
        pytest.param('l = 2 huh', '', UndefinedUnit, id='str-UndefinedUnit'),
        pytest.param('N = 2 kg', '', InvalidSymbol, id='str-InvalidSymbol'),  # because it matched the pattern, but the symbol is not allowed
    ]
)
def test_as_datum_errors(d, symbol, exception):
    with pytest.raises(exception):
        Datum.as_datum(d, symbol)
