from QCalculator import Formula, Datum
from QCalculator.Exceptions.DatumExceptions import InitializationError
from QCalculator.Exceptions.FormulaExceptions import (
    ConsistencyError,
    InvalidUnitError,
    SymbolNotFound,
    NoValueError,
    FailedConsistencyCheck,
    OverlappingVariables,
    TargetNotFound,
    UnknownNotFound,
    EquationNotSolvable,
    WrongUnitEquation
)

import pytest
from sympy import Eq, Symbol
from contextlib import nullcontext
from dataclasses import dataclass


# ============================================================================================= PRESET DATA AND FIXTURES
@dataclass(frozen=True)
class PresetData1:
    df: Datum
    C1: Datum
    C2: Datum
    df_str: str
    C1_str: str
    C2_str: str
    C2_alt: Datum   # is needed to test consistency
    C2_alt_str: str


PD = PresetData1(
    Datum('df', 2.5, ''),
    Datum('C1', 1.2, 'M'),
    Datum('C2', 0.48, 'M'),
    'df = 2.5',
    'C1 = 1.2 M',
    'C2 = 0.48 M',
    Datum('C2', 0.56, 'M'),
    'C2 = 0.56 M'
)

TS = PresetData1(
    Datum('df', 0.001, ''),
    Datum('C1', 0.001, 'M'),
    Datum('C2', 0.001, 'M'),
    'df = 0.001',
    'C1 = 0.001 M',
    'C2 = 0.001 M',
    Datum('C2', 0.1, 'M'),
    'C2 = 0.1 M'
)

@pytest.fixture
def f1():
    return Formula('df = C1/C2', ref_units={'df':'', 'C1':'mole/L', 'C2':'mole/L'})

@pytest.fixture
def f2():
    return Formula('y = x**2 + 5*x + 6')

def exception_handling(exception):
    return (
        nullcontext()
        if exception is None
        else
        pytest.raises(exception)
    )

# ========================================================================================================= INITIALIZING
# test for correct exception when incompatible units are given!
@pytest.mark.parametrize(
    "formula, equation, ref_units, symbols, exception",
    [
        pytest.param('df = C1/C2', 'df = C1/C2', {'df':'', 'C1':'M', 'C2':'M'}, {'df', 'C1', 'C2'}, None, id='init-with-eq'),
        pytest.param('df - C1/C2', '-C1/C2 + df = 0', {'df':'', 'C1':'M', 'C2':'M'}, {'df', 'C1', 'C2'}, None, id='init-with-minus'),
        pytest.param('df - C1/C2', '-C1/C2 + df = 0', {'df':'L', 'C1':'M', 'C2':'M'}, {'df', 'C1', 'C2'}, WrongUnitEquation, id='WrongUnitEquation')
    ]
)
def test_init_Formula(formula, equation, ref_units, symbols, exception):
    with exception_handling(exception):
        f = Formula(formula, ref_units=ref_units)
        assert f.eq_str == equation
        assert f._ref_units == ref_units
        assert f.symbols == symbols



# ================================================================================================== WRITING AND READING
# ============================================================================================================== writing
def _assert_write_case(f1, data, *, rewrite=False, force_inc=False, exception=None, expected_data):
    with exception_handling(exception):
        f1.write(*data, rewrite=rewrite, force_inconsistent=force_inc)
        assert f1._data == expected_data

@pytest.mark.parametrize(
    "data, expected_data",
    [
        # the test function (_assert_write_case) unpacks the data list with a * expression. Hence, to get several
        # arguments passed, a list is required. If a string is passed, then it is also unpacked which leads to errors.
        # NOTE: the .write() method does not unpack with *, but accepts *data parameter, so the **method** accepts strings.
        pytest.param([PD.df],                   {PD.df},        id='single-write-Datum'),
        pytest.param([PD.df, PD.C1],            {PD.df, PD.C1}, id='multiple-write-Datum'),
        pytest.param([PD.df_str],               {PD.df},        id='single-write-str'),
        pytest.param([PD.df_str, PD.C1_str],    {PD.df, PD.C1}, id='multiple-write-str'),
    ]
)
def test_basic_write(f1, data, expected_data):
    _assert_write_case(f1, data=data, expected_data=expected_data)

@pytest.mark.parametrize(
    "data, rewrite, expected_data",
    [
        pytest.param([PD.C2, PD.C2_alt], True, {PD.C2_alt}, id='rewrite-Datum'),
        pytest.param([PD.C2_str, PD.C2_alt_str], True, {PD.C2_alt}, id='rewrite-str'),
    ]
)
def test_rewrite(f1, data, rewrite, expected_data):
    _assert_write_case(f1, data=data, rewrite=rewrite, expected_data=expected_data)

@pytest.mark.parametrize(
    "data, force_inc, exception, expected_data",
    [
        pytest.param([PD.df, PD.C1, PD.C2],     False,  None,               {PD.df, PD.C1, PD.C2},      id='consistency-check-normal'),
        pytest.param([PD.df, PD.C1, PD.C2_alt], False,  ConsistencyError,   set(),                      id='consistency-check-error'),
        pytest.param([PD.df, PD.C1, PD.C2_alt], True,   None,               {PD.df, PD.C1, PD.C2_alt},  id='consistency-check-force')
    ]
)
def test_write_consistency_check(f1, data, force_inc, exception, expected_data):
    _assert_write_case(f1, data=data, force_inc=force_inc, exception=exception, expected_data=expected_data)

@pytest.mark.parametrize(
    "data, exception, expected_data",
    [
        pytest.param(['df = 2.5 L'],    InvalidUnitError,       {}, id='InvalidUnitError'),
        pytest.param(['V0 = 22.4 L'],   SymbolNotFound,         {}, id='SymbolNotFound'),
        pytest.param([2],               TypeError,              {}, id='TypeError_int'),
        pytest.param([True],            TypeError,              {}, id='TypeError_bool'),
        pytest.param(['Hi'],            InitializationError,    {}, id='Datum_InitializationError'),
    ]
)
def test_type_exceptions_for_write(f1, data, exception, expected_data):
    _assert_write_case(f1, data=data, exception=exception, expected_data=expected_data)


# ============================================================================================================== reading
def _assert_read_case(f1, data, *, units=None, exception=None, expected):
    f1._data = {PD.df, PD.C1}

    with exception_handling(exception):
        res = f1.read(data, units)
        print('\n', *f1._data)
        assert res == expected

@pytest.mark.parametrize(
    "data, units, expected",
    [
        pytest.param('df', None, PD.df, id='default-from-str'),
        pytest.param(['df', 'C1'], None, [PD.df, PD.C1], id='default-from-list'),
    ]
)
def test_default_read(f1, data, units, expected):
    _assert_read_case(f1, data, units=units, expected=expected)

@pytest.mark.parametrize(
    "data, units, expected",
    [
        pytest.param('df',          '',                 PD.df,                                                         id='single'),
        pytest.param(['df', 'C1'],  [None, 'mmol/L'],   [PD.df, Datum('C1', 1200, 'mmol/L')],   id='incomplete-unit-list'),
        pytest.param(['df', 'C1'],  ['', 'mmol/L'],     [PD.df, Datum('C1', 1200, 'mmol/L')],   id='complete-unit-list'),
    ]
)
def test_read_with_units(f1, data, units, expected):
    _assert_read_case(f1, data, units=units, expected=expected)

@pytest.mark.parametrize(
    "data, units, exception, expected",
    [
        pytest.param('',            None,                   SymbolNotFound,     None,   id='SymbolNotFound-empty-str'),
        pytest.param('V0',          None,                   SymbolNotFound,     None,   id='SymbolNotFound-other'),
        pytest.param('C2',          None,                   NoValueError,       None,   id='NoValueError-single'),
        pytest.param(['C1', 'C2'],  ['mmol/L', 'mmol/L'],   NoValueError,       None,   id='NoValueError-list'),
        pytest.param('C1',          'kHz',                  InvalidUnitError,   None,   id='InvalidUnitError-single'),
        pytest.param(['C1', 'df'],  [None, 'M'],            InvalidUnitError,   None,   id='InvalidUnitError-list')
    ]
)
def test_read_exceptions(f1, data, units, exception, expected):
    _assert_read_case(f1, data, exception=exception, units=units, expected=expected)


# ============================================================================================================== erasing
def _assert_erase_case(f1, data, var, *, exception=None, expected):
    f1._data = data

    with exception_handling(exception):
        f1.erase(var)
        assert f1._data == expected

def test_erase(f1):
    data = {PD.df, PD.C1, PD.C2}
    _assert_erase_case(f1, data, var='df', expected={PD.C1, PD.C2})

@pytest.mark.parametrize(
    "data, var, exception",
    [
        pytest.param({PD.C1, PD.C2}, 'df', NoValueError),
        pytest.param({PD.C1, PD.C2}, 'V0', SymbolNotFound)
    ]
)
def test_erase_exceptions(f1, data, var, exception):
    _assert_erase_case(f1, data, var, exception=exception, expected=None)



# ===================================================================================================== FORMULA ANALYSIS
# ==================================================================================================== consistency_check
def _assert_consistency_check(f1, data, *, silent_failure, raise_exception, exception=None, expected):
    with exception_handling(exception):
        f1._data = data
        assert f1.consistency_check(silent_failure=silent_failure, raise_exception=raise_exception) is expected

@pytest.mark.parametrize(
    "data, expected",
    [
        pytest.param({PD.df, PD.C1, PD.C2}, True, id='consistent-no-ex'),
        pytest.param({PD.df, PD.C1, PD.C2_alt}, False, id='inconsistent-no-ex')
    ]
)
def test_basic_consistency_check(f1, data, expected):
    _assert_consistency_check(f1, data, silent_failure=False, raise_exception=False, expected=expected)

@pytest.mark.parametrize(
    "data, expected, exception, silent_failure",
    [
        pytest.param({PD.df, PD.C1, PD.C2_alt}, None,   ConsistencyError,       False,  id='ConsistencyError-sf=False'),
        pytest.param({PD.df, PD.C1, PD.C2_alt}, None,   ConsistencyError,       True,   id='ConsistencyError-sf=True'),
        pytest.param({PD.df, PD.C1},            None,   FailedConsistencyCheck, False,  id='FailedConsistencyCheck-sf=False'),
        pytest.param({PD.df, PD.C1},            True,   None,                   True,   id='FailedConsistencyCheck-sf=True'),
    ]
)
def test_consistency_errors(f1, data, expected, exception, silent_failure):
    _assert_consistency_check(
        f1,
        data,
        raise_exception=True,
        expected=expected,
        silent_failure=silent_failure,
        exception=exception
    )


# ============================================================================================================ has_value
def _assert_has_value(f1, data, var, *, expected, exception=None):
    with exception_handling(exception):
        f1._data = data
        assert f1.has_value(var) == expected

@pytest.mark.parametrize(
    "data, var, expected",
    [
        pytest.param({PD.df, PD.C1},    'C1',           True,           id='True-single'),
        pytest.param({PD.df, PD.C1},    ['df', 'C1'],   [True, True],   id='True-list'),
        pytest.param({PD.df, PD.C1},    'C2',           False,          id='False-single'),
        pytest.param({PD.df, PD.C1},    ['df', 'C2'],   [True, False],  id='False-list')
    ]
)
def test_basic_has_value(f1, data, var, expected):
    _assert_has_value(f1, data, var, expected=expected, exception=None)

@pytest.mark.parametrize(
    "data, var, exception",
    [
        pytest.param({PD.C2, PD.C2_alt}, 'C2', OverlappingVariables),
        pytest.param({PD.df, PD.C1}, 2, TypeError)
    ]
)
def test_has_value_exceptions(f1, data, var, exception):
    _assert_has_value(f1, data, var, exception=exception, expected=None)



# ========================================================================================================= COMPUTATIONS
# ================================================================================================================= eval
def _assert_eval(f, data, *, target, filters, symbolic, expected, exception=None):
    with exception_handling(exception):
        f._data = data
        f._target = target
        res = f.eval(*filters, symbolic=symbolic)
        assert res == expected

@pytest.mark.parametrize(
    "fix, data, target, expected",
    [
        pytest.param('f1', {PD.C1, PD.C2}, TS.df, [2.5], id='single-solution'),
        pytest.param(
            'f2',
            {Datum('y', 0.0, '')},
            Datum('x', 0.01, ''),
            [-3.00000000000000, -2.00000000000000],
            id='several-solutions'
        ),
        pytest.param('f1', {PD.C1}, TS.df, [1200.0/Symbol('C2')], id='partial-solution'),
        pytest.param('f1', {PD.df, PD.C1}, TS.df, [PD.df.magnitude], id='target-already-written')
    ]
)
def test_eval_numeric(f1, f2, fix, data, target, expected):
    if fix == 'f1':
        f = f1
    elif fix == 'f2':
        f = f2
    else:
        raise ValueError(f'Expected "fix" being "f1" or "f2", got "{fix}".')

    _assert_eval(f, data, target=target, filters=[lambda l: l], symbolic=False, expected=expected)

def test_eval_symbolic(f1):
    target = Datum('C1', 0.1, 'M')
    expected = [Eq(Symbol('C1'), Symbol('df') * Symbol('C2'))]
    _assert_eval(f1,data={}, target=target, filters=[lambda l:l], symbolic=True, expected=expected)

@pytest.mark.parametrize(
    "f, data, target, filters, expected",
    [
        pytest.param(  # one positive real root, one negative real root; filtering for positive
            Formula('y = x**2 + 5*x - 6'),
            {Datum('y', 0.0, '')},
            Datum('x', 0.1, ''),
            [Formula.POSITIVES],
            [1.0],
            id='filter-for-positives'
        ),

        pytest.param(  # one positive real root, one negative real root; filtering for negative
            Formula('y = x**2 + 5*x - 6'),
            {Datum('y', 0.0, '')},
            Datum('x', 0.1, ''),
            [Formula.NEGATIVES],
            [-6.0],
            id='filter-for-negatives'
        ),

        pytest.param(  # one positive and one zero root; filtering for zero
            Formula('y = x**2 - x'),
            {Datum('y', 0.0, '')},
            Datum('x', 0.1, ''),
            [Formula.ZERO],
            [0.0],
            id='filter-for-zero'
        ),

        pytest.param(  # one positive and one zero root; filtering for non-negative
            Formula('y = x**2 - x'),
            {Datum('y', 0.0, '')},
            Datum('x', 0.1, ''),
            [Formula.NON_NEG],
            [0.0, 1.0],
            id='filter-for-non-negatives'
        ),

        pytest.param(  # one negative and one zero root; filtering for non-positive
            Formula('y = x**2 + x'),
            {Datum('y', 0.0, '')},
            Datum('x', 0.1, ''),
            [Formula.NON_POS],
            [-1.0, 0.0],
            id='filter-for-non-positives'
        ),

        pytest.param(  # two complex roots; filtering for real
            Formula('y = x**2 + 1'),
            {Datum('y', 0.0, '')},
            Datum('x', 0.1, ''),
            [Formula.REAL_ONLY],
            [],
            id='filter-for-real'
        )
    ]
)
def test_eval_preset_filters(f, data, target, filters, expected):
    _assert_eval(f, data, target=target, filters=filters, symbolic=False, expected=expected)

@pytest.mark.parametrize(
    "data, target, exception",
    [
        pytest.param({PD.df, PD.C1}, None, TargetNotFound, id='TargetNotFound'),
        pytest.param({PD.df, PD.C1, PD.C2_alt}, TS.df, ConsistencyError, id='ConsistencyError'),
    ]
)
def test_eval_exceptions(f1, data, target, exception):
    _assert_eval(f1, data, target=target, filters=[Formula.NO_FILTER], exception=exception, expected=None, symbolic=False)

# ================================================================================================================ solve
def _assert_solve(f1, data, *, target, rounding, expected, exception=None, round_to=2):
    # filters are not tested since they are directly passed to the eval() function
    with exception_handling(exception):
        f1._data = data
        f1._target = target
        res = f1.solve(rounding=rounding, round_to=round_to)
        print(*res)
        assert res == expected

@pytest.mark.parametrize(
    "data, target, expected",
    [
        pytest.param({PD.df, PD.C1}, TS.C2, [PD.C2], id='solve-for-target'),
        pytest.param({PD.df, PD.C1}, TS.df, [PD.df], id='solve-for-written-target'),
        pytest.param({PD.df, PD.C1}, None, [PD.C2], id='solve-no-target')
    ]
)
def test_basic_solve(f1, data, target, expected):
    _assert_solve(f1, data, target=target, expected=expected, rounding=False)

@pytest.mark.parametrize(
    "data, target, rounding, round_to, expected",
    [
        # reminder: round_to is used only if target is not specified
        pytest.param({PD.df, PD.C1}, TS.C2_alt, True,   2,  [Datum('C2', 0.5, 'M')],     id='rounding-from-target'),
        pytest.param({PD.df, PD.C1}, None,      True,   1,  [Datum('C2', 0.5, 'M')],     id='rounding-from-round_to'),
        pytest.param({PD.df, PD.C1}, TS.C2_alt, False,  2,  [PD.C2],                                            id='from-target-with-rounding=False'),
        pytest.param({PD.df, PD.C1}, None,      False,  1,  [PD.C2],                                            id='from-round_to-with-rounding=False'),
    ]
)
def test_solve_rounding(f1, data, target, rounding, expected, round_to):
    _assert_solve(f1, data, target=target, rounding=rounding, expected=expected, round_to=round_to)

@pytest.mark.parametrize(
    "data, target, exception",
    [
        pytest.param({PD.C1}, TS.df, EquationNotSolvable, id='EquationNotSolvable'),
        pytest.param({PD.df, PD.C1, PD.C2_alt}, TS.df, UnknownNotFound, id='UnknownNotFound'),
    ]
)
def test_solve_exceptions(f1, data, target, exception):
    _assert_solve(f1, data, target=target, exception=exception, expected=None, rounding=False)



# =========================================================================================================== PROPERTIES
# ============================================================================================= target getter and setter
@pytest.mark.parametrize(
    "target, expected, exception",
    [
        pytest.param(TS.df, TS.df, None, id='normal-set'),
        pytest.param(TS.df_str, TS.df, None, id='string-set'),
        pytest.param('df = 1.2 L', None, InvalidUnitError, id='InvalidUnitError'),
        pytest.param('V0 = 22.4 L', None, SymbolNotFound, id='SymbolNotFound'),
    ]
)
def test_target_setter(f1, target, expected, exception):
    with exception_handling(exception):
        f1.target = target
        assert f1._target == expected

def test_target_getter(f1):
    f1._target = TS.df
    assert f1.target == TS.df

# =============================================================================================================== others
@pytest.mark.parametrize(
    "data, expected",
    [
        pytest.param({PD.df, PD.C1, PD.C2}, {'df':1, 'C1':1, 'C2':2}, id='values-present'),
        pytest.param(dict(), dict(), id='values-absent'),
    ]
)
def test_decimals(f1, data, expected):
    f1._data = data
    print(*data)
    assert f1.decimals == expected

@pytest.mark.parametrize(
    "data, expected",
    [
        pytest.param({PD.df, PD.C1}, True, id='one-value-absent'),
        pytest.param({PD.df}, False, id='several-values-absent'),
        pytest.param({PD.df, PD.C1, PD.C2}, True, id='all-values-present')
    ]
)
def test_solvable(f1, data, expected):
    f1._data = data
    assert f1.solvable == expected

@pytest.mark.parametrize(
    "data, expected, exception",
    [
        pytest.param({PD.df, PD.C1}, 'C2', None, id='normal-behaviour'),
        pytest.param({PD.df}, None, EquationNotSolvable, id='not-enough-variables'),
        pytest.param({PD.df, PD.C1, PD.C2}, None, UnknownNotFound, id='all-variables-present')
    ]
)
def test_unknown(f1, data, expected, exception):
    with exception_handling(exception):
        f1._data = data
        assert f1.unknown == expected

def test_data(f1):
    f1._data = {PD.df, PD.C1, PD.C2}
    assert f1.data == {PD.df, PD.C1, PD.C2}

    # check that affecting copies of the _data does not affect _data itself
    f1.data.pop()
    assert f1.data == {PD.df, PD.C1, PD.C2}

def test_symbols(f1):
    f1._data = {PD.df, PD.C1, PD.C2}
    assert f1.symbols == {'df', 'C1', 'C2'}

def test_eq_str(f1):
    assert f1.eq_str == 'df = C1/C2'
    assert f1.eq == Eq(Symbol('df'), Symbol('C1')/Symbol('C2'))
