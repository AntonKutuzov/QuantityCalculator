import pytest
from QCalculator.Datum import Datum
from QCalculator.DefStrings.DatumDefString import DatumDefString


#           __eq__          #
@pytest.mark.parametrize(
    'd1, d2',
    [
        (Datum('m = 5 kg'), True),
        (Datum('m = 5 kg'), DatumDefString('m = 5 kg')),
        (Datum('m = 5 kg'), 'm = 5 kg'),
        (Datum('m = 5 kg'), ['m', '=', '5', 'kg']),
    ]
)
def test__eq__invalid_type(d1, d2):
    with pytest.raises(TypeError):
        _ = d1 == d2


@pytest.mark.parametrize(
    'd1, d2',
    [
        (Datum('m = 5 kg'), Datum('m = 5 kg')),
        (Datum('m = 5 kg'), Datum('m = 5.0 kg')),
        (Datum('m = 5.0 kg'), Datum('m = 5 kg')),
    ]
)
def test__eq__True_cases(d1, d2):
    assert d1 == d2


@pytest.mark.parametrize(
    'd1, d2',
    [
        (Datum('m = 5 kg'), Datum('m = 5 km')),
        (Datum('m_a = 5 kg'), Datum('m = 5 kg')),
        (Datum('m = 5.1 kg'), Datum('m = 5 kg')),
        (Datum('m = 5e1 kg'), Datum('m = 5 kg')),
        (Datum('m = -5 kg'), Datum('m = 5 kg')),
    ]
)
def test__eq__False_cases(d1, d2):
    assert d1 != d2
