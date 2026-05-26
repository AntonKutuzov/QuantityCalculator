from QCalculator import LinearIterator, Formula, Datum
from QCalculator.Exceptions.DatumExceptions import InitializationError, InvalidSymbol
from QCalculator.Exceptions.FormulaExceptions import NoneReferenceUnits
from QCalculator.Exceptions.LinearIteratorExceptions import (
    NoValueError,
    FormulasNotIndicated,
    UnreachableTarget,
    UnusedSymbolError,
    IncompatibleUnitsError,
    RewritingError
)

import pytest
from contextlib import nullcontext
import pint
from copy import deepcopy

# ============================================================================================= PRESET DATA AND FIXTURES
def dict_is_subset(sub, sup):
    """
    Checks if "sub" is a "subdict" of "sup". A dict d1 is considered to be a subdict of d2 if d2 contains
    all the key-value pairs or d1 (same logic as with sets).

    :param sub: subdict (the one checked, with less items)
    :param sup: superdict (the one with more items)
    :return:
    """
    for k, v in sub.items():
        if not sup.get(k) == v:
            return False
    else:
        return True



formulas1 = [
        'n = mps/M',
        'n = Vpg/V0',
        'wmm = mps/msm',
        'n = Np/NA',
]

units1 = {
        'n': 'mole',
        'mps': 'g',
        'M': 'g/mole',
        'Vpg': 'L',
        'V0': 'L/mole',
        'wmm': 'dimensionless',
        'msm': 'g',
        'Np': 'dimensionless',
        'NA': 'mole**-1'
}

units1_nones = {
    'n': None,
    'mps': 'g',
    'M': 'g/mole',
    'Vpg': 'L',
    'V0': 'L/mole',
    'wmm': None,
    'msm': None,
    'Np': 'dimensionless',
    'NA': 'mole**-1'
}

@pytest.fixture
def li1():
    return LinearIterator(formulas=formulas1, ref_units=units1)

@pytest.fixture
def data():
    return deepcopy({
                Datum('n', 1.5, 'mole'),
                Datum('M', 18, 'g/mole'),
                Datum('NA', 6.02e23, 'mole**-1'),
                Datum('wmm', 0.25, '')
            })

def exception_handling(exception):
    return (
        nullcontext()
        if exception is None
        else
        pytest.raises(exception)
    )

# ========================================================================================================= INITIALIZING
@pytest.mark.parametrize(
    "li_formulas, li_units, expected_formulas, expected_units, exception",
    [
        pytest.param(
            [formulas1[0], formulas1[2]],
            units1,
            {Formula('n = mps/M'), Formula('wmm = mps/msm')},
            {'n':'mole', 'mps':'g', 'M':'g/mole', 'wmm':'dimensionless', 'msm':'g'},
            None,
            id='normal-init'
        ),
        pytest.param(
            [formulas1[0], formulas1[2], 'wmm = mps/msm'],
            units1,
            # set just throws away repeating items
            {Formula('n = mps/M'), Formula('wmm = mps/msm')},
            {'n':'mole', 'mps':'g', 'M':'g/mole', 'wmm':'dimensionless', 'msm':'g'},
            None,
            id='same-formula-init'
        ),
        pytest.param(
            list(),
            units1,
            set(),
            dict(),
            FormulasNotIndicated,
            id='no-formula-init'
        ),
    ]
)
def test_init_LI_formulas(li_formulas, li_units, expected_formulas, expected_units, exception):
    """
    Checks for:
    - definition with valid formulas (expected case)
    - definition with the same formulas (remember, it uses convertion to sets)
    - definition without formulas
    """

    with exception_handling(exception):
        li = LinearIterator(li_formulas, li_units)
        assert li._formulas == expected_formulas
        assert dict_is_subset(sup=li._ref_units, sub=expected_units) is True


@pytest.mark.parametrize(
    "li_formulas, li_units, expected_formulas, expected_units, exception",
    [
        pytest.param(
            formulas1,
            None,
            set([Formula(f) for f in formulas1]),
            None,
            None,
            id='init-without-units'
        ),
        pytest.param(
            formulas1,
            units1,
            set([Formula(f) for f in formulas1]),
            units1,
            None,
            id='init-with-units-all-formulas'
        ),
        pytest.param(
            formulas1[:2],
            units1,
            set([Formula(f) for f in formulas1[:2]]),
            {'n':'mole', 'mps':'g', 'M':'g/mole', 'Vpg':'L', 'V0':'L/mole'},
            None,
            id='init-with-units-some-formulas'
        ),
        pytest.param(
            formulas1[:2],
            dict([(k,v) if not k == 'n' else (v, 'qwerty') for k, v in units1.items()]),  # replace 'n':'mole' for 'n':'qwerty'
            set([Formula(f) for f in formulas1[:2]]),
            set(),
            pint.UndefinedUnitError,
            id='init-invalid-units'
        ),
        pytest.param(
            formulas1[:2],
            dict([(k, v) if not k == 'n' else ('p', v) for k, v in units1.items()]),  # replace 'n':'mole' for 'p':'mole'
            set([Formula(f) for f in formulas1[:2]]),
            set(),
            NoneReferenceUnits,  # we *replaced* 'n' for 'p', so now there are no key 'n' and hence no units for 'n' can be found
            id='init-no-unit-found'
        ),
    ]
)
def test_init_LI_units(li_formulas, li_units, expected_formulas, expected_units, exception):
    """
    Checks for:
    - definition without units
    - definition with units (x2)
    - definition with invalid units
    - definition with variable missing in reference_units dict
    """

    with exception_handling(exception):
        li = LinearIterator(li_formulas, li_units)
        assert li._formulas == expected_formulas
        assert li._ref_units == expected_units


# ================================================================================================== READING AND WRITING
# ============================================================================================================== writing
@pytest.mark.parametrize(
    "data, expected_data, exception",
    [
        pytest.param(
            [Datum('n', 1.5, 'mole'), Datum('Vpg', 15, 'L')],
            {Datum('n', 1.5, 'mole'), Datum('Vpg', 15, 'L')},
            None,
            id='writing-Datums'
        ),
        pytest.param(
            ['n = 1.5 mole', 'Vpg = 15 L'],
            {Datum('n', 1.5, 'mole'), Datum('Vpg', 15, 'L')},
            None,
            id='writing-strings'
        ),
        pytest.param(
            [1, 2, 3],
            list(),
            TypeError,
            id='writing-numbers-(TypeError)'
        ),
        pytest.param(
            [True, False],
            list(),
            TypeError,
            id='writing-boolean-(TypeError)'
        ),
        pytest.param(
            ['definitely not a datum definition string'],
            list(),
            InitializationError,
            id='writing-invalid-string'
        ),
        pytest.param(
            [' = 15 L', '= 1.5 mole'],
            list(),
            InitializationError,
            id='writing-forbidden-string'
        ),
    ]
)
def test_basic_write(li1, data, expected_data, exception):
    """
    Checks:
    - writing Datum
    - writing str
    - writing other types
    """

    with exception_handling(exception):
        li1.write(*data)
        assert li1._data == expected_data


@pytest.mark.parametrize(
    "data, exception",
    [
        pytest.param(
            ['n = 1.5 mole', 'p = 101.325 kPa'],
            UnusedSymbolError
        ),
        pytest.param(
            ['n = 1.5 mole', 'M = 18 g'],
            IncompatibleUnitsError
        )
    ]
)
def test_write_symbol_and_units_exceptions(li1, data, exception):
    """
    Checks:
    - writing with symbol unused in li
    - writing with wrong units
    """

    with pytest.raises(exception):
        li1.write(*data)


@pytest.mark.parametrize(
    "data, expected_data, rewrite, exception",
    [
        pytest.param(
            ['n = 1.5 mole', 'mps = 10 g', 'n = 2 mole'],
            {Datum('n', 2.0, 'mole'), Datum('mps', 10, 'g')},
            True,
            None,
            id='rewrite-True'
        ),
        pytest.param(
            ['n = 1.5 mole', 'mps = 10 g', 'n = 2 mole'],
            set(),
            False,
            RewritingError,
            id='rewrite-False'
        ),
    ]
)
def test_rewriting(li1, data, expected_data, rewrite, exception):
    """
    Checks:
    - rewriting a variable with rewrite=True
    - rewriting a variable with rewrite=False
    """

    with exception_handling(exception):
        li1.write(*data, rewrite=rewrite)
        assert li1._data == expected_data


# ============================================================================================================== reading
"""_reading_data = {
                    Datum('n', 1.5, 'mole'),
                    Datum('mps', 10, 'g'),
                    Datum('NA', 6.02*10**23, 'mole**-1')
                }
"""
@pytest.mark.parametrize(
    "var, units, expected",
    [
        pytest.param(
            'n',
            None,
            Datum('n', 1.5, 'mole'),
            id='read-without-units'
        ),
        pytest.param(
            'n',
            'mmole',
            Datum('n', 1500, 'mmole'),
            id='read-with-units'
        ),
        pytest.param(
            ['n', 'M'],
            None,
            [
                Datum('n', 1.5, 'mole'),
                Datum('M', 18, 'g/mole'),
            ],
            id='read-many-without-units'
        ),
        pytest.param(
            ['n', 'M'],
            ['mmole', 'kg/mole'],
            [
                Datum('n', 1500, 'mmole'),
                Datum('M', 0.018, 'kg/mole'),
            ],
            id='read-many-with-units'
        ),
    ]
)
def test_basic_read(li1, data, var, units, expected):
    """
    Checks:
    - reading a single variable without units
    - reading a single variable with units
    - reading multiple variables without units
    - reading multiple variables with units
    """

    li1._data = data
    res = li1.read(var=var, units=units)
    assert res == expected

@pytest.mark.parametrize(
    "var, units, expected, exception",
    [
        pytest.param(
            'p',
            None,
            None,
            UnusedSymbolError,
            id='read-wrong-symbol'
        ),
        pytest.param(
            '',
            None,
            None,
            InvalidSymbol,
            id='read-var=empty-string'
        ),
        pytest.param(
            None,
            None,
            None,
            TypeError,
            id='read-var=None'
        ),
        pytest.param(
            'n',
            'kg',
            None,
            IncompatibleUnitsError,
            id='read-incompatible-units'
        ),
        pytest.param(
            2,
            None,
            None,
            TypeError
        ),
        pytest.param(
            ['n', 'mps'],
            ['mole'],
            None,
            ValueError
        )
    ]
)
def test_read_exceptions(li1, data, var, units, expected, exception):
    """
    Checks:
    - reading with wrong symbol
    - reading without symbol
    - reading with incompatible units
    - reading with variable of wrong type (e.g. int or bool)
    - reading vars and units as lists of different lengths
    """

    with exception_handling(exception):
        li1._data = data
        res = li1.read(var, units)
        assert res == expected


# ============================================================================================================== erasing
@pytest.mark.parametrize(
    "var, expected_data, exception",
    [
        pytest.param(
            None,
            set(),
            None,
            id='erase-all'
        ),
        pytest.param(
            'n',
            {
                Datum('M', 18, 'g/mole'),
                Datum('NA', 6.02 * 10 ** 23, 'mole**-1'),
                Datum('wmm', 0.25, '')
            },
            None,
            id='erase-one-var'
        ),
        pytest.param(
            'p',
            set(),
            UnusedSymbolError,
            id='erase-unused-var'
        ),
        pytest.param(
            'V0',
            None,
            NoValueError,
            id='erase-no-value-var'
        )
    ]
)
def test_erase(li1, data, var, expected_data, exception):
    """
    Checks:
    - using without var (var is None)
    - using with var
    - erasing variable that is not present
    - erasing a variable that does not have a value
    """
    
    with exception_handling(exception):
        li1._data = data
        li1.erase(var)
        assert li1._data == expected_data


# ============================================================================================================= ANALYSIS
@pytest.mark.parametrize(
    "var, expected, exception",
    [
        pytest.param(
            'n',
            True,
            None,
        ),
        pytest.param(
            'p',
            False,
            UnusedSymbolError
        ),
        pytest.param(
            '',
            False,
            InvalidSymbol
        )
    ]
)
def test_has_value(li1, data, var, expected, exception):
    """
    Checks:
    - variable that is in the _data set
    - variable that is not in the _data set
    - invalid variable
    """

    with exception_handling(exception):
        li1._data = data
        assert li1.has_value(var) == expected


# ========================================================================================================= CALCULATIONS
def test_iter(li1, data):
    li1.write(*data)  # because it writes in both _data and the formulas
    res = li1.iter()
    assert res == {
        Datum('mps', 27, 'g'),
        Datum('Np', 9.03*10**23, ''),
    }

@pytest.mark.parametrize(
    "target, expected_return, expected_data, exception",
    [
        pytest.param(
            Datum('mps', 0.01, 'g'),
            Datum('mps', 27.0, 'g'),
            {
                Datum('n', 1.5, 'mole'),
                Datum('M', 18, 'g/mole'),
                Datum('NA', 6.02e23, 'mole**-1'),
                Datum('wmm', 0.25, ''),
                Datum('mps', 27.0, 'g'),
                Datum('Np', 9.03e23, '')
            },
            None,
            id='solve-with-target-default-units'
        ),

        pytest.param(
            Datum('mps', 0.01, 'kg'),
            Datum('mps', 27.0, 'g'),
            {
                Datum('n', 1.5, 'mole'),
                Datum('M', 18, 'g/mole'),
                Datum('NA', 6.02e23, 'mole**-1'),
                Datum('wmm', 0.25, ''),
                Datum('mps', 0.027, 'kg'),
                Datum('Np', 9.03e23, '')
            },
            None,
            id='solve-with-target-compatible-units'
        ),

        pytest.param(
            None,
            None,
            {
                Datum('n', 1.5, 'mole'),
                Datum('M', 18, 'g/mole'),
                Datum('NA', 6.02e23, 'mole**-1'),
                Datum('wmm', 0.25, ''),
                Datum('mps', 27.0, 'g'),
                Datum('Np', 9.03e23, ''),
                Datum('msm', 108, 'g')
            },
            None,
            id='solve-without-target'
        ),

        pytest.param(
            Datum('V0', 0.01, 'L/mole'),
            None,
            {
                Datum('n', 1.5, 'mole'),
                Datum('M', 18, 'g/mole'),
                Datum('NA', 6.02e23, 'mole**-1'),
                Datum('wmm', 0.25, ''),
                Datum('mps', 27.0, 'g'),
                Datum('Np', 9.03e23, ''),
                Datum('msm', 108, 'g')
            },
            UnreachableTarget,
            id='solve-unreachable-target'
        ),
    ]
)
def test_solve(li1, data, target, expected_return, expected_data, exception):
    """
    Checks:
    - solving with target, default units (stops at target)
    - solving with target, compatible units (stops at target)
    - solving without target (stops when no possible solutions are left)
    - solving when target cannot be reached
    """

    with exception_handling(exception):
        li1.write(*data)

        if target is not None:
            li1.target = target

        res = li1.solve()
        assert res == expected_return
        assert li1._data == expected_data


# =========================================================================================================== PROPERTIES
def test_solvables(li1, data):
    """
    Checks:
    - That only the Formulas that have **one** missing variable are returned
    - That the Formulas with no missing variables are not returned (hence "complete_data")
    """

    expected = {
        Formula('n = Np/NA', ref_units=units1),
        Formula('wmm = mps/msm', ref_units=units1)
    }

    complete_data = data.union({Datum('mps', 27, 'g')})
    li1.write(*complete_data)
    assert li1.solvables == expected

def test_data(li1, data):
    """
    Checks:
    - Whether the set returned is genuinely the one stored in _data
    - Whether affecting **obtained** set does not change the _data set
    """

    li1._data = data
    assert li1.data == data

    d = li1.data
    d.pop()
    assert li1.data == data


def test_symbols(li1):
    assert li1.symbols == {'n', 'mps', 'M', 'Vpg', 'V0', 'wmm', 'msm', 'Np', 'NA'}

def test_formulas(li1):
    """
    Checks:
    - That the returned set of Formulas is genuinely the set of stored formulas
    - That changing the **obtained** set does not affect the stored set
    """

    assert li1.formulas == set([Formula(f) for f in formulas1])

    s = li1.formulas
    s.pop()
    assert li1.formulas == set([Formula(f) for f in formulas1])

def test_target(li1):
    t = Datum('n', 0.01, 'mole')
    li1._target = t
    assert li1.target == t

# ============================================================================================================== SETTERS
@pytest.mark.parametrize(
    "target, expected_target, exception",
    [
        pytest.param(
            Datum('n', 0.01, 'mole'),
            Datum('n', 0.01, 'mole'),
            None,
            id='Datum-as-target'
        ),

        pytest.param(
            'n = 0.01 mole',
            Datum('n', 0.01, 'mole'),
            None,
            id='string-as-target'
        ),

        pytest.param(
            42,
            None,
            TypeError,
            id='other-type-as-target'
        ),

        pytest.param(
            Datum('p', 0.01, 'kPa'),
            None,
            UnusedSymbolError,
            id='unused-symbol-as-target'
        ),

        pytest.param(
            '= 0.01 kPa',
            None,
            InitializationError,
            id='invalid-symbol-as-target-1'
        ),

        pytest.param(
            'S = 0.01 m',
            None,
            InitializationError,
            id='invalid-symbol-as-target-2'
        ),

        pytest.param(
            Datum('mps', 0.01, 'kPa'),
            None,
            IncompatibleUnitsError,
            id='incompatible-units'
        ),
    ]
)
def test_target_setter(li1, target, expected_target, exception):
    """
    Checks:
    - Target setting with Datum
    - Target setting with a string
    - Target setting with another (invalid) type
    - Target setting with unused symbol
    - Target setting with invalid symbol (x2)
    - Target setting with incompatible units
    """

    with exception_handling(exception):
        li1.target = target
        assert li1._target == expected_target