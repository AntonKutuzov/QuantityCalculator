from QCalculator.patterns import variable_str, value_str, units_str
from re import findall, compile
from typing import Tuple, Pattern


class PatternGenerator:
    PH = 'PH'
    _general_pattern = rf'PH{variable_str}PH=PH{value_str}(?:PH{units_str})?PH'
    _general_pattern = _general_pattern.replace('PH', PH)
    _nof_PH = len(findall(PH, _general_pattern))

    def __init__(self, placeholders: Tuple[str, ...]) -> None:
        pattern = self._general_pattern

        for i in range(self._nof_PH):
            pattern = pattern.replace(self.PH, placeholders[i], 1)

        self._regex = pattern

    @classmethod
    def model(cls) -> str:
        return f'{cls.PH}(variable_str){cls.PH}={cls.PH}(value_str)(?:{cls.PH}(units_str))?{cls.PH}'

    @property
    def pattern(self) -> Pattern:
        return compile(self._regex)

    @property
    def regex(self) -> str:
        return self._regex


if __name__ == '__main__':
    phs = (
        '',
        ' +',
        ' +',
        ' +',
        ''
    )

    pg = PatternGenerator(placeholders=phs)
    print(pg.pattern.fullmatch('m = 5 kg'))
