from abc import abstractmethod
from typing import Dict, AnyStr, Match, Tuple, Literal
# from abc import ABC  # import if you want to make the class abstract
from re import compile, Pattern
from copy import deepcopy
from sympy import parse_expr

from QCalculator import DEF_UR
from QCalculator.Exceptions.DatumExceptions import InvalidVarName  # must migrate to the DDS exceptions
from QCalculator.util import must_match, validate_type, validate_types, check_unit_validity
from QCalculator.patterns import variable_str, value_str, units_str

from QCalculator.Exceptions.QDefStringExceptions import (
    CannotInstantiateQDS,
    InvalidQDefString,
    VariableNotAllowed,
    UnitNotAllowed
)


class QDefString(str):
    """Note that due to absence of several crucial variables, QDefString cannot be instantiated itself. It should
    only be used for inheritance."""

    ureg = DEF_UR

    # PH stands for 'placeholder'
    _general_pattern = rf'PH0{variable_str}PH1=PH2{value_str}(?:PH3{units_str})?PH4'
    _default_PH = r'.*'
    _nof_PHs = 5  # the number of PHs, NOT the number on the latest PH. If not sure, set it high enough to cover all PHs.

    _base_pattern = _general_pattern  # copy
    for n in range(_nof_PHs):
        _base_pattern = _base_pattern.replace(rf'PH{n}', _default_PH)
    _base_pattern = compile(_base_pattern)

    _PH_dicts_order = (_base_pattern,)  # tuple is used, because it is not mutable, and hence not shared between all classes
    _restrictions = {
        'symbol': tuple(),
        'value': tuple(),
        'units': tuple()
    }

    def __new__(cls, string: str, *args, **kwargs) -> object:
        # print('__new__', cls)

        if cls is QDefString:
            raise CannotInstantiateQDS()

        validate_type(string, str)


        # check that the string matches patterns of all the subclasses
        for p in cls._PH_dicts_order:
            try:
                must_match('other', string, p)
            except ValueError as e:
                e.add_note('NOTE: Every subclass of QDefString must match not only with the final pattern of the subclass, '
                     'but also with all the patterns of superclasses.')
                e.add_note(f'Failed pattern: {p}')
                raise InvalidQDefString(string)


        # check that the string complies with the restrictions
        match = cls._main_regex.fullmatch(string)
        var = match.group('symbol')

        if cls._restrictions['symbol']:
            if var not in cls._restrictions['symbol']:
                raise VariableNotAllowed(cls, var)

        if cls._restrictions['units']:
            unit = match.group('units')
            check_unit_validity(cls, unit)
            unit = cls.ureg.parse_units(unit)

            for u in cls._restrictions['units']:
                if unit.is_compatible_with(u):
                    break
            else:
                raise UnitNotAllowed(cls, unit)


        return super().__new__(cls, string)


    def __init_subclass__(
            cls,
            pattern: Pattern[str] = None,
            restrictions: Dict[str, Tuple[str, ...]] = None,
            **kwargs
    ):
        """init_subclass methods are ran when the class is constructed, not an instance is created. I.e.
        when the "class" keyword is executed during import of the module/file. So, it is executed before
        "new", which is called when an object is actually created."""

        # print('__init_subclass__ QDS', cls)

        # resolve class' pattern
        if pattern is not None:
            validate_type(pattern, Pattern)
            cls._main_regex = pattern
        else:
            pattern = cls._main_regex

        # copy ureg so that it is individual per class
        cls.ureg = deepcopy(QDefString.ureg)

        # append pattern to tuple
        l = list(cls._PH_dicts_order)
        l.append(pattern)
        cls._PH_dicts_order = tuple(l)

        # add restrictions
        if restrictions is not None:
            for k in restrictions.keys():
                validate_type(k, str)

                v = restrictions.get(k)

                if v is not None:
                    validate_type(v, tuple)
                    cls._add_restriction(*v, var_type=k)
                else:
                    continue

        super().__init_subclass__(**kwargs)


    def __init__(self, qds: str, *args, sympy_safe: bool, **kwargs):
        # types of qds and sympy_safe are checked in __new__

        self._match = self.pattern.fullmatch(qds)
        self._sympy_safe = sympy_safe
        self._check_sympy_safety(self.variable)

        units = self._match.group('units')

        if units is not None:
            units = str(units)
        else:
            units = 'dimensionless'

        check_unit_validity(self, units)

        self._units = units
        self._raw_string = qds

        super().__init__()


    @classmethod
    def create_pattern(cls, placeholders: Dict[int, str]) -> Pattern[str]:
        validate_type(placeholders, dict)
        validate_types(list(placeholders.keys()), int)
        validate_types(list(placeholders.values()), str)

        gp = cls._general_pattern

        for n, ph in placeholders.items():
            ph_group = rf'PH{n}'
            gp = gp.replace(ph_group, ph)

        for n in range(cls._nof_PHs):
            gp = gp.replace(rf'PH{n}', cls._default_PH)

        return compile(gp)

    @classmethod
    def _add_restriction(cls, *vs: str | int | float, var_type: Literal['symbol', 'value', 'units']) -> None:
        vlist = list(cls._restrictions[var_type])

        for v in vs:
            validate_type(v, (str, int, float))
            must_match(var_type, str(v))

            if var_type == 'units':
                v = cls.ureg.parse_units(v)
            vlist.append(v)

        cls._restrictions[var_type] = tuple(vlist)


    def _check_sympy_safety(self, symbol: str) -> None:
        if self._sympy_safe:
            try:
                parse_expr(f'{symbol} - 1')
            except TypeError as e:
                raise InvalidVarName(
                    var=symbol,
                    details=f'The symbol "{symbol}" cannot be used in sympy expressions.\nTo ignore, set "sympy_safe" to True in constructor.'
                ) from e
        else:
            return None


    @property
    def regex(self) -> AnyStr:
        return self._main_regex.pattern

    @property
    def pattern(self) -> Pattern[str]:
        return self._main_regex

    @property
    def match(self) -> Match[str]:
        return self._match

    @property
    def variable(self) -> str:
        return str(self._match.group('variable'))

    @property
    def value(self) -> float:
        return float(self._match.group('value'))

    @property
    def units(self) -> str:
        return self._units

    @property
    def raw_string(self) -> str:
        return self._raw_string

    @property
    @abstractmethod
    def string(self) -> str:
        ...
