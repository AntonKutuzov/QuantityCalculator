from typing import Dict, AnyStr, Match
from abc import ABC
from pint import Unit
from pint.errors import UndefinedUnitError
from re import compile, Pattern
from copy import deepcopy

from QCalculator import DEF_UR
from QCalculator._util import must_match, validate_type, validate_types
from QCalculator.DefStrings.patterns import variable_str, value_str, units_str

from QCalculator.Exceptions.QDefStringExceptions import (
    CannotInstantiateQDS,
    InvalidUnitExpression,
    UndefinedUnit,
    InvalidQDefString
)


class QDefString(str, ABC):
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


    def __new__(cls, string: str, *args, **kwargs) -> object:
        # print('__new__', cls)

        if cls is QDefString:
            raise CannotInstantiateQDS()

        validate_type(string, str)

        for p in cls._PH_dicts_order:
            try:
                must_match('other', string, p)
            except ValueError as e:
                e.add_note('NOTE: Every subclass of QDefString must match not only with the final pattern of the subclass, '
                     'but also with all the patterns of superclasses.')
                e.add_note(f'Failed pattern: {p}')
                raise InvalidQDefString(string)

        return super().__new__(cls, string)


    def __init_subclass__(cls, pattern: Pattern[str], **kwargs):
        """init_subclass methods are ran when the class is constructed, not an instance is created. I.e.
        when the "class" keyword is executed during import of the module/file. So, it is executed before
        "new", which is called when an object is actually created."""

        # print('__init_subclass__ QDS', cls)

        validate_type(pattern, Pattern)

        cls._main_regex = pattern
        cls.ureg = deepcopy(QDefString.ureg)

        # append to tuple, basically
        l = list(cls._PH_dicts_order)
        l.append(pattern)
        cls._PH_dicts_order = tuple(l)

        super().__init_subclass__(**kwargs)


    def __init__(self, qds: str, *args, **kwargs):
        # print('__init__ QDS')

        validate_type(qds, str)

        # if `qds = QDefString('m = 5 kg')` is called, "AttributeError: 'QDefString' object has no attribute '_main_regex'"
        # will be raised. This is OK, since I don't want QDefString to be instantiated. However, turn it into a proper
        # exception saying that QDefString should not be instantiated (otherwise it is very confusing).
        self._match = self.pattern.fullmatch(qds)
        self._raw_string = qds

        unit = self._match.group('unit')

        if unit is not None:
            unit = str(unit)
        else:
            unit = 'dimensionless'

        self.check_unit_validity(unit)
        self._unit = self.ureg.parse_units(unit)

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
    def check_unit_validity(cls, unit: str | Unit) -> None:
        if not isinstance(unit, (str, Unit)):
            raise TypeError(f'Expected "str" or "pint.Unit", got: "{unit}".')

        unit = str(unit)

        try:
            cls.ureg.parse_units(unit)

        except (AssertionError, ValueError, TypeError):
            raise InvalidUnitExpression(unit)

        except UndefinedUnitError:
            raise UndefinedUnit(cls, unit)


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
    def unit(self) -> Unit:
        return self._unit

    @property
    def string(self) -> str:
        return self._raw_string


if __name__ == '__main__':
    pass
