from pytest import fixture
from QCalculator.Datum import Datum


@fixture
def d1():
    return Datum('m = 5 kg')

@fixture
def d2():
    return Datum('V_A = 15 m/s')
