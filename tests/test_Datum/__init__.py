from QCalculator import Datum
from pint import UnitRegistry
import pytest



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

ex1 = {'symbol': 'l', 'magnitude': 2.0, 'units': ur('meter')}
ex2 = {'symbol': 't', 'magnitude': 5.2, 'units': ur('second')}
ex3 = {'symbol': 'd', 'magnitude': 25.5, 'units': ur('centimeter')}
ex4 = {'symbol': 'n', 'magnitude': 1, 'units': ur('dimensionless')}
ex3_base = {'symbol': 'd', 'magnitude': 0.255, 'units': ur('meter')}


def _test_datum(datum, expected):
    assert datum._symbol == expected['symbol']
    assert datum._magnitude == pytest.approx(expected['magnitude'], rel=1e-6, abs=1e-9)
    assert datum._units == expected['units']
