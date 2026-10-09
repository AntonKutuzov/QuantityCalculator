from typing import Dict, Tuple, Optional, Any, Hashable
from pint import Quantity, Unit
from sympy import Expr, Eq, Symbol, parse_expr, solve

from QCalculator import DEF_UR
from QCalculator._util import must_match



class UnitDict(dict):
    UNITS_DICT = Dict[Tuple[str, ...], str | Unit] | Dict[str, str | Unit]
    _ureg = DEF_UR


    def __init__(
            self,
            du: UNITS_DICT,
            *,
            unit_by_symbol: bool = False
    ) -> None:
        self._ubs = unit_by_symbol

        d = self.parse_unit_dict(du, unit_by_symbol=unit_by_symbol)
        super().__init__(d)


    # ============================================================================= OVERWRITING GETTERS + CUSTOM GETTERS
    def get(self, __key):
        if self._ubs:
            symbol = must_match('symbol', __key)
            return super().get(symbol)
        else:
            return super().get(__key)


    def __getitem__(self, item):
        if self._ubs:
            symbol = must_match('symbol', item)
            return super().__getitem__(symbol)
        else:
            return super().__getitem__(item)


    def __setitem__(self, key: Tuple[str, ...] | str, value: str | Unit):
        # work with value
        if isinstance(value, str):
            if self._is_wrong_dimensionless(value):
                value = 'dimensionless'

        elif isinstance(value, Unit):
            value = str(value)
            if self._is_wrong_dimensionless(value):
                value = 'dimensionless'

        else:
            raise TypeError(f'Expected "str" or "pint.Unit", got "{type(value)}".')

        # work with key
        if isinstance(key, tuple):
            for k in key:
                super().__setitem__(k, value)

        elif isinstance(key, str):
            match = must_match('variable', key)

            if self._ubs:
                symbol = match.group('symbol')
                super().__setitem__(symbol, value)
            else:
                super().__setitem__(key, value)

        else:
            raise TypeError(f'Expected "str" or "Tuple[str]", got "{type(key)}".')


    @staticmethod
    def get_unit(
            var: str,
            unit_dict: Optional[UNITS_DICT] = None,
            *,
            unit_by_symbol: bool = False,
            strict: bool = False
    ) -> Optional[str]:
        """
        Takes into account `unit_by_symbol` attribute and returns respective units.
        In case `unit_by_symbol` is True, searches in the default unit dict by using only `symbol` part (as defined
        in DatumDefString) of the variable. Otherwise, uses full `var` name.

        For example,
        >>> from QCalculator import UnitDict
        >>> du = UnitDict({'m':'g', 'M':'g/mole'})
        >>> vs = ['m_1', 'm_2', 'm_3', 'm_ref']
        >>> du.get_unit(vs[0], unit_dict=du, unit_by_symbol=True)
        'g'
        >>> du.get_unit(vs[1], unit_dict=du, unit_by_symbol=True)
        'g'
        >>> du.get_unit(vs[0], unit_dict=du, unit_by_symbol=False)
        None

        :param var: Variable for which units are looked for.
        :param unit_dict: A dict from where units are taken.
        :param unit_by_symbol: If `True`, units are searched by using only `symbol` part of the variable.
        :param strict: If `True`, raises exception in the case where no units were found.
        :return: Either None, or string representing units for variable `var`.
        """

        ud = UnitDict.parse_unit_dict(unit_dict, unit_by_symbol=unit_by_symbol)

        if unit_by_symbol:
            v = must_match('variable', var)
            symbol = str(v.group('symbol'))
            res = ud.get(symbol)
        else:
            res = ud.get(var)

        if strict:
            if res is None:
                raise ValueError(f'Variable "{var}" is not in the provided unit dict: "{unit_dict}".')

        return res


    def unit_for_solvable_eq(self, eq: Eq, var: str, units: Optional[str] = None) -> str:
        """
        The function resolves the following question: "having solvable equation, what units should I take given this
        DefaultUnits instance?". The function searches for units in the three ways, written below in the order of
        search:\n
        1) Checks that `units` parameter is None. If it is **not**, checks its consistency with the default units
        and returns `units`.\n
        2) In case `units` **is** None, tries to get the units for variable `var` from default units dict. If found,
        returns them.\n
        3) In case default units are not specified for `var`, uses `eq` to deduce units by using `deduce_missing_units`.
        Works *only if the equation provided is solvable*. In case it is not, raises exception.

        :param eq: solvable equation (as defined "solvable" for Formula) from which units are deduced in case no other
        sources are available.
        :param var: Variable for which units are looked for.
        :param units: Units provided to the function for variable `var`. If not None, checked for consistency with
        default units.
        :return: Units for variable `var`. if not possible to find, raises an exception.
        """

        if units is None:
            u = self.get(var)
            if u is not None:
                return u
            else:
                return self.deduce_missing_units(eq, var)
        else:
            if var in self.keys():
                compatible = self.compatible_with_default(var, units)
                defu = self.get(var)
                if not compatible:
                    raise Exception(f'Unit "{units}" for variable "{var}" is not compatible with the default unit "{defu}".')
            return units


    # ================================================================================================== PRIVATE METHODS
    #                                                                                                    general helpers
    @staticmethod
    def _is_wrong_dimensionless(u: str) -> bool:
        return any([
            u.isspace(),
            u == ''
        ])


    #                                                                                                         converters
    @classmethod
    def _str_units_to_sympy_units_expr(cls, u_expr_str: str) -> Expr:
        """
        Converts arbitrary unit expressions into sympy expressions where each unit is represented as a symbol. For
        example, a string "J / mole / K" is first converted to pint's <Unit('joule / mole / kelvin')>, and then
        to sympy's Expr: 'joule/(kelvin*mole)'. The free symbols of that expression consequently are
        '{mole, joule, kelvin}'.

        If the units were not base units, they are converted to base units and any coefficient that arises is ignored.
        Thus, this function does not preserve values, only units.

        :param u_expr_str: an expression of units expressed as Python's str
        :return: sympy.Expr where each unit is a separate Symbol
        """

        u_expr = cls._ureg.parse_units(u_expr_str)
        q = Quantity(1, u_expr)  # Quantity is used instead of plain multiplication to please static type checkers
        u = q.to_base_units().units
        return parse_expr(str(u))


    def _var_expr_to_units(self, eq: Eq, *, units: Dict[str, str]) -> Eq:
        for v in [str(s) for s in eq.free_symbols]:
            u = UnitDict.get_unit(v, unit_dict=units, unit_by_symbol=self._ubs, strict=True)
            u = self._str_units_to_sympy_units_expr(u)
            eq = eq.subs(v, u)

        eq = eq.subs(Symbol('dimensionless'), 1)  # in case it is Eq(dimensionless, 1)
        return eq



    # =================================================================================================== PUBLIC HELPERS
    @staticmethod
    def unpack_keys(d: Dict[Tuple[Any, ...] | Hashable, Any]) -> Dict[Hashable, Any]:
        unpacked = dict()

        for t, u in d.items():
            if isinstance(t, tuple):
                for v in t:
                    unpacked[v] = u
            else:
                unpacked[t] = u

        return unpacked


    @staticmethod
    def normalize_units(
            units: Dict[str, str | Unit],
            unit_by_symbol: bool = False
    ) -> Dict[str, str]:
        """
        1) Replaces blanks and empty strings with 'dimensionless'
        2) If self._ubs (unit_by_symbol): checks that all keys match with DDS.patterns.symbol
        """

        new_units = dict()

        for v, u in units.items():
            u = str(u)

            if UnitDict._is_wrong_dimensionless(u):
                u = 'dimensionless'
                new_units[v] = u
            else:
                new_units[v] = u

            if unit_by_symbol:
                must_match('symbol', v)

        return new_units


    @staticmethod
    def parse_unit_dict(unit_dict: UNITS_DICT, unit_by_symbol: bool = False) -> Dict[str, str]:
        ud = UnitDict.unpack_keys(unit_dict)
        ud = UnitDict.normalize_units(ud, unit_by_symbol=unit_by_symbol)
        return ud


    def get_unit_source(
            self,
            units: Optional[UNITS_DICT]
    ) -> Dict[str, str]:

        final_units = self.copy()

        if units is not None:
            parsed_units = self.parse_unit_dict(units)
            final_units.update(parsed_units)

        return final_units


    # ============================================================================================== OPERATIONS ON UNITS
    def deduce_missing_units(
            self,
            eq: Eq,
            unk: str,
            units: Optional[UNITS_DICT] = None
    ) -> str:

        units = self.get_unit_source(units)
        neq = solve(eq, unk)[0]  # produces a LIST of solutions. ASSUME FIRST-ORDER POLY. LATER IMPLEMENT CHECK
        neq = self._var_expr_to_units(neq, units=units)

        neq = str(neq)
        neq = self._ureg.parse_units(neq)
        return str(neq)


    def is_unit_consistent(
            self,
            eq: Eq,
            units: Optional[UNITS_DICT] = None
    ) -> bool:

        checked_units = self.get_unit_source(units)
        eq = self._var_expr_to_units(eq, units=checked_units)

        # in case the two sides are identical, it reduces to BooleanTrue, otherwise stays Eq
        return eq.is_Boolean


    def compatible_with_default(self, var_for_default: str, units_to_check: str | Unit) -> bool:
        defu = self.get(var_for_default)

        if defu is not None:
            defu = self._ureg.parse_units(defu)
            units = self._ureg.parse_units(str(units_to_check))
            return units.is_compatible_with(defu)
        else:
            raise Exception(f'Default units for variable "{var_for_default}" are not found.')




if __name__ == '__main__':
    from QCalculator import Formula


    du = UnitDict({
        'E': 'J',
        'n': 'mole',
        'T': 'K',
        'p': 'Pa',
        'm': 'g',
        'R': 'J / mole / K',
        # 'M': 'g/mole',
    })

    f = Formula('p*V = n*R*T')

    check = du.deduce_missing_units(f.eq, 'R', units={'V':'L'})
    print(check)
