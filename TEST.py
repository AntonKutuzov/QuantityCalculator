import pytest
from pint import Quantity
from sympy import Symbol

from QCalculator.Datum import Datum
from QCalculator.Exceptions.DatumExceptions import (
    DifferentSymbols,
    IncompatibleUnits,
    InitialisationError,
    InvalidSymbol,
)


@pytest.fixture
def d_m():
    return Datum("m", 2.0, "meter")


@pytest.fixture
def d_s():
    return Datum("t", 4.0, "second")


def test_init_variants_and_invalid_init():
    d1 = Datum("x", 10, "kg")
    assert d1.symbol == "x"
    assert d1.value == 10

    q = 3 * Datum.ureg.meter
    d2 = Datum("l", q)
    assert d2.value == 3
    assert d2.units_str == "meter"

    d3 = Datum("a = 9.81 meter / second ** 2")
    assert d3.symbol == "a"
    assert pytest.approx(d3.value) == 9.81

    with pytest.raises(InitialisationError):
        Datum(1, 2, 3)


def test_from_quantity_valid_and_invalid_symbol():
    d = Datum.from_quantity("v", 12 * Datum.ureg("m/s"))
    assert d.symbol == "v"
    assert d.units_str == "meter / second"

    with pytest.raises(InvalidSymbol):
        Datum.from_quantity("", 1 * Datum.ureg.meter)


def test_from_string_valid_and_invalid_formats():
    d = Datum.from_string("p = 12.5 pascal")
    assert d.symbol == "p"
    assert d.value == 12.5

    with pytest.raises(InitialisationError):
        Datum.from_string("p=12.5pascal")

    with pytest.raises(InvalidSymbol):
        Datum.from_string("x = 1*10e+2 meter")


def test_domesticate_units_and_to_datum_paths(d_m):
    u = Datum.domesticate_units("kg")
    assert str(u) == "kilogram"

    d_copy = Datum.to_datum(d_m)
    assert d_copy == d_m
    assert d_copy is not d_m

    d_from_q = Datum.to_datum(5 * Datum.ureg.second, symbol="t")
    assert d_from_q.symbol == "t"

    d_from_str = Datum.to_datum("z = 7 meter")
    assert d_from_str.symbol == "z"

    with pytest.raises(TypeError):
        Datum.to_datum(42)


def test_str_eq_iter_and_zte(d_m):
    assert str(d_m) == "m = 2.0 meter"

    same = Datum("m", 2.0, "meter")
    assert d_m == same

    different_units_value = Datum("m", 200, "centimeter")
    assert not (d_m == different_units_value)

    different_symbol = Datum("x", 2.0, "meter")
    assert not (d_m == different_symbol)

    assert list(iter(d_m)) == ["m", 2.0, Datum.ureg.meter]

    assert Datum._ZTE_test(7) is True
    assert Datum._ZTE_test(0) is False
    d_m._ZERO_TOLERANCE_EXPONENT = 25
    with pytest.raises(InvalidSymbol):
        _ = d_m == same


def test_div_mul_magic_and_type_errors(d_m, d_s):
    q_div = d_m / d_s
    assert isinstance(q_div, Quantity)
    assert str(q_div.units) == "meter / second"

    d_div = d_m.div(d_s, new_datum_symbol="v")
    assert isinstance(d_div, Datum)
    assert d_div.symbol == "v"

    d_scaled = d_m.div(2)
    assert isinstance(d_scaled, Datum)
    assert d_scaled.value == 1.0

    assert (8 / d_m).magnitude == 4

    q_mul = d_m * d_s
    assert isinstance(q_mul, Quantity)
    assert str(q_mul.units) == "meter * second"

    d_mul = d_m.mul(d_s, new_datum_symbol="A")
    assert isinstance(d_mul, Datum)
    assert d_mul.symbol == "A"

    assert (d_m * 3).value == 6.0
    assert (3 * d_m).value == 6.0

    with pytest.raises(TypeError):
        d_m.div("bad")
    with pytest.raises(TypeError):
        d_m.mul(None)
    with pytest.raises(TypeError):
        d_m.rdiv("bad")


def test_add_sub_rsub_and_unit_and_symbol_rules():
    d1 = Datum("x", 2, "meter")
    d2 = Datum("x", 50, "centimeter")
    d3 = Datum("y", 1, "meter")

    out = d1.add(d2)
    assert out.symbol == "x"
    assert pytest.approx(out.value) == 2.5
    assert out.units_str == "meter"

    out_other_units = d1.add(d2, use_units_of="other")
    assert out_other_units.units_str == "centimeter"
    assert pytest.approx(out_other_units.value) == 250

    with pytest.raises(DifferentSymbols):
        d1.add(d3)

    keep_other_symbol = d1.add(d3, symbol_ex=False, use_symbol_of="other")
    assert keep_other_symbol.symbol == "y"

    with pytest.raises(IncompatibleUnits):
        d1.add(Datum("x", 1, "second"))

    # sub works with Datum
    sub_out = d1.sub(d2)
    assert pytest.approx(sub_out.value) == 1.5

    # sub currently tries `other.scale(-1)`, so Quantity input raises AttributeError
    with pytest.raises(AttributeError):
        d1.sub(1 * Datum.ureg.meter)

    rsub_datum = d2.rsub(d1)
    assert pytest.approx(rsub_datum.to("meter").value) == 1.5

    rsub_q = d2.rsub(3 * Datum.ureg.meter)
    assert pytest.approx(rsub_q.value) == 250

    with pytest.raises(IncompatibleUnits):
        d1.rsub(1 * Datum.ureg.second)

    # non-quantity else branch in rsub raises AttributeError while building exception payload
    with pytest.raises(AttributeError):
        d1.rsub(1)


def test_static_helpers_symbol_analysis_and_get_quantity(d_m):
    assert Datum._swap_self_other("self") == "other"
    assert Datum._swap_self_other("other") == "self"
    with pytest.raises(ValueError):
        Datum._swap_self_other("bad")

    assert d_m._symbol_analysis(1 * Datum.ureg.meter) == "m"

    d_x = Datum("x", 1, "meter")
    with pytest.raises(DifferentSymbols):
        d_m._symbol_analysis(d_x)
    assert d_m._symbol_analysis(d_x, symbol_ex=False, use_symbol_of="other") == "x"
    with pytest.raises(InvalidSymbol):
        d_m._symbol_analysis(d_x, symbol_ex=False, use_symbol_of="bad")
    with pytest.raises(TypeError):
        d_m._symbol_analysis(123)

    q = Datum._get_quantity(d_m)
    assert isinstance(q, Quantity)
    q2 = Datum._get_quantity(4 * Datum.ureg.second)
    assert isinstance(q2, Quantity)
    with pytest.raises(TypeError):
        Datum._get_quantity("no")


def test_create_datum_ip_get_decimals_and_compatibility(d_m, d_s):
    q = 2 * Datum.ureg.meter
    out_q = Datum._create_datum_ip(q, None)
    assert isinstance(out_q, Quantity)
    out_d = Datum._create_datum_ip(q, "z")
    assert isinstance(out_d, Datum)
    assert out_d.symbol == "z"

    assert Datum.get_decimals(1.234) == 3
    assert Datum.get_decimals(1e-6) == 6
    with pytest.raises(InvalidSymbol):
        Datum.get_decimals(0.0)

    assert d_m.is_compatible(d_m)
    assert d_m.is_compatible(2 * Datum.ureg.meter)
    assert d_m.is_compatible("centimeter")
    assert d_m.is_compatible(Datum.ureg.centimeter)
    assert not d_m.is_compatible(d_s)
    with pytest.raises(TypeError):
        d_m.is_compatible(123)


def test_conversion_scaling_and_properties(d_m):
    d_cm = d_m.to("centimeter")
    assert isinstance(d_cm, Datum)
    assert pytest.approx(d_cm.value) == 200

    d_m.to("centimeter", in_place=True)
    assert d_m.units_str == "centimeter"
    assert d_m.value == 200

    with pytest.raises(IncompatibleUnits):
        d_m.to("second")

    d_back_base = d_m.to_base_units()
    assert d_back_base.units_str == "meter"

    d_m.ito("meter")
    assert d_m.units_str == "meter"

    d_m.ito_base_units()
    assert d_m.units_str == d_m.base_units_str

    d2 = d_m.scale(10)
    assert d2.value == d_m.value * 10

    d_m.scale(0.5, in_place=True)
    assert d_m.value == 1.0

    d_m.iscale(2)
    assert d_m.value == 2.0

    assert d_m.quantity == 2.0 * Datum.ureg.meter
    assert d_m.symbol == "m"
    assert d_m.sp_symbol == Symbol("m")
    assert d_m.value == 2.0
    assert d_m.magnitude == 2.0
    assert d_m.units_str == "meter"
    assert str(d_m.units) == "meter"
    assert str(d_m.base_units) == "meter"
    assert d_m.base_units_str == "meter"
    assert d_m.num_decimals == 1
