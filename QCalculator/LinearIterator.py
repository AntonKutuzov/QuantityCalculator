from QCalculator.Datum import Datum
from QCalculator.Formula import Formula
# from QCalculator.Exceptions.LinearIteratorExceptions import *

from typing import List, Dict, Literal, Optional
from copy import copy, deepcopy


class LinearIterator:
    def __init__(self,
                 formulas: List[Formula | str],
                 units: Dict[str, Datum.ureg.Unit | str]
                ) -> None:

        self._formulas: List[Formula] = [Formula(f) if isinstance(f, str) else f for f in formulas]
        self._tempex: List[Formula] = deepcopy(self._formulas)
        self._data: List[Datum] = list()

        self._variables: List[str] = self._get_symbols()

        self._units: Dict[str, Datum.ureg.Unit] = dict()

        var_set = set(self.vars)
        units_set = set(units.keys())

        if not var_set == units_set:
            # compute the variables missing in either of the sets
            v_dif_u = var_set.difference(units_set)
            u_dif_v = units_set.difference(var_set)
            missing = v_dif_u.union(u_dif_v)
            raise Exception(f'The sets of variables from formula and units list are not the same. Missing variables: {missing}.')

        for s, u in units.items():
            u = Datum.domesticate_units(u)
            if s in self.vars:
                self._units.update({s : u})
            else:
                raise Exception(f'Variable "{s}" is not present in the formula list, while is in the units list.')

        self._default_units: Dict[str, Datum.ureg.Unit] = dict()

        self._ZERO_TOLERANCE_EXPONENT: int = 7

        self._target: Optional[str] = None
        self._round_target_to: bool = False
        self._return_units: Optional[Datum.ureg.Unit] = None

    # =============================================================================================== initiation helpers
    def _get_symbols(self) -> List[str]:
        symbols = list()

        for f in self.formulas:
            symbols.extend(f.symbols)

        return list(set(symbols))

    # ========================================================================================================= checkers
    def _select_data(self,
                         criteria: Literal['symbol', 'value', 'units'],
                         value: str|int|float|Datum.ureg.Unit,
                         data_list: Optional[List[Datum]] = None
                     ) -> List[Datum]:
        """Allows to sort a list of Datum objects by the three attributes of Datum instances. self._data used by default"""

        if data_list is None:
            data_list = deepcopy(self._data)

        if criteria == 'symbol' and isinstance(value, str):
            res = filter(lambda d: d.symbol == value, data_list)

        elif criteria == 'value' and isinstance(value, (int, float)):
            res = filter(lambda d: d.value == value, data_list)

        elif criteria == 'units' and isinstance(value, (str, Datum.ureg.Unit)):
            v = Datum.domesticate_units(value)
            res = filter(lambda d: d.units == v, data_list)

        else:
            raise Exception('Could not select data according to the provided criteria.')

        return list(res)

    def _duplicates(self, data_list: Optional[List[Datum]] = None) -> List[str]:
        dup: List[str] = list()

        if data_list is None:
            l = deepcopy(self._data)
        else:
            l = deepcopy(data_list)

        for d in l:
            res = self._select_data('symbol', d.symbol, data_list=l)
            if len(list(res)) > 1:
                dup.append(d.symbol)

        return list(set(dup))

    def nof_solvable_equations(self) -> int:
        return sum([f.solvable for f in self._tempex])

    def is_consistent(self,
                          d: Datum | str | List[Datum | str],
                          raise_exception: bool = False,
                          zte: Optional[int] = None
                      ) -> bool:
        """
        This functions has two modes of operation.\n
        **(1)** If Datum or string is passed, then the function looks in the written datums for a datum with the same symbol,
        and if present, compares the values of the found and the new one. The datum is said to be consistent with the
        set of (written) data if these values are the same.\n
        **(2)** If a list of Datums or strings is received, the function checks if the list is consistent with the formulas
        stored in the linear iterator object. A list of datum objects is said to be consistent with the list of formulas
        if substitution of the datums does not lead to invalid equations (when LHS is not equal to RHS).\n
        NOTE: *this check does not include any data written to the linear interator!*

        :param d: An object(s) to be checked for consistency with this instance of linear iterator
        :param zte: stands for zero_tolerance_exponent. Determines the degree of error that can be accepted. Will be removed in future versions
        :param raise_exception: if True, the InconsistentFormula exception will be raised with indication on the Formula instance which first appeared to be inconsistent.
        :return: True if test passed (the data are consistent), False if not
        """

        if zte is None:
            zte = self._ZERO_TOLERANCE_EXPONENT

        if isinstance(d, (Datum, str)):
            # Just check if there is a value written with that symbol. If yes, the values must be the same.
            datum = Datum.to_datum(d)
            symbol, value = datum.symbol, datum.value

            if self.has_value(symbol):
                d = self.read(symbol)
                return Formula._is_close(value, d.value, zte)
            else:
                return True

        elif isinstance(d, list):
            data = [Datum.to_datum(datum) for datum in d]

            if not self._data:
                # if there are NO data written, we can directly perform the test
                IS_CONSISTENT: bool = True

                if self._duplicates(data):
                    # If there are duplicates, we cannot assess consistency as well as compute anything. Hence, inconsistent
                    return False
                else: # if no duplicates...
                    # write in all the data we need to check (.write() also calls ._push() at the end, so the data)
                    # will end up substituted into the temporary expressions (._tempex)
                    self.write(*data)
                    for f in self._tempex:
                        # If at least one formula is inconsistent, the whole set is inconsistent
                        if not f.consistency_check(silent_failure=True, raise_exception=raise_exception, zte=zte):
                            IS_CONSISTENT = False

                # We don't want to keep the data we had to check, so erase them
                self.erase(*data)

                return IS_CONSISTENT

            else: # if there ARE some data written, we create another instance of LI because we need to write in new data
                temporary_li = LinearIterator(self.formulas, self.units)
                d = deepcopy(data)  # use deepcopy() to avoid changing the original list of data
                return temporary_li.is_consistent(d, raise_exception=raise_exception, zte=zte)
        else:
            raise TypeError(f'Parameter "d" has wrong type. Expected "Datum" or "str" or lists of them, got "{type(d)}".')

    # ============================================================================================ internal modificators
    def _push(self, data: List[Datum], rewrite: bool = False) -> None:
        """Substitutes all the data from ._data list into Formulas in the ._tempex list."""
        for d in data:
            for f in self._tempex:
                if d.symbol in f:
                    f.write(d, rewrite=rewrite)

    def _resolve_duplicates(self, data_list: Optional[List[Datum]] = None) -> List[Datum]:
        dup = self._duplicates(data_list=data_list)  # ._duplicates uses deepcopy, so data_list will stay unaffected
        final = list()

        for d in dup:
            lst = self._select_data('symbol', d, data_list=data_list)
            lst = [datum.to_base_units() for datum in lst]
            values = [datum.value for datum in lst]

            if not Formula._is_close(sum(values)/len(values), values[0], zte=self._ZERO_TOLERANCE_EXPONENT):
                raise Exception(f'The list contains different values for the same variable: {[str(d) for d in lst]}.')
            else:
                final.append(lst[0])

        return final


    # ========================================================================================= reading and writing data
    def write(self,
                  *data: Datum|str,
                  rewrite: bool = False
              ) -> None:
        """
        Adds the datums from the *data to the ._data list (linear iterator's "memory"). The datum is always stored in
        the base units regardless of units it had when passed to the .write() method. The latter are stored and used
        as default in .read() method if units parameter is not specified.\n
        By default rewriting a variable is forbidden (to avoid changes in values of which we are not aware). To enable
        rewriting (writing for variables that already have values), set rewrite to True.

        **NOTE**: When rewrite is set to True, *all* previous values with that symbol are overwritten and only the one
        given in *data is left.

        :param data: Datum or string to be written into the linear iterator
        :param rewrite: if True, allows to write for variables where a value is already stored
        :return:
        """

        data = [Datum.to_datum(d) for d in data]
        rtw_data = list()  # ready-to-write data list

        for datum in data:
            if len(self._select_data('symbol', datum.symbol, data_list=data)) > 1:
                raise Exception(f'Cannot write two datums with the same symbol: {", ".join([str(d) for d in data])}.')

            if not datum.is_compatible(self.units[datum.symbol]):
                raise Exception(f'Variable "{datum.symbol}" cannot have units "{datum.units_str}".')

            self._default_units.update({datum.symbol: datum.units})
            datum.ito_base_units()

            if self.has_value(datum):
                datums = self._select_data('symbol', datum.symbol)

                if rewrite:
                    for dtm in datums:
                        i = self._data.index(dtm)
                        self._data.pop(i)
                else:
                    raise Exception(f'Cannot rewrite variable "{datum.symbol}". Current value(s): {", ".join([d.__str__() for d in datums])}')

            rtw_data.append(datum)
            self._data.append(datum)


        self._push(rtw_data, rewrite=rewrite)

    def read(self,
                    var: str | List[str],
                    units: Optional[str | List[str]] = None,
                    rounding: bool = False,
                    round_to: int = 2
             ) -> Datum | List[Datum]:
        """
        Returns a Datum object with data read from the linear iterator memory (._data dict).

        :param var: symbol of the variable to be read
        :param units: units in which the variable should be expressed. If None, the units provided when writing the variable will be used
        :param rounding: if True, the variable will be rounded to the *round_to* number of digits
        :param round_to: the number of digits to which the value of the datum is rounded. Only if rounding=True
        :return:
        """

        if isinstance(var, str):
            var = [var]
            if units is None:
                units = [None]
        if isinstance(units, str):
            units = [units]
        elif units is None:
            units = len(var)*[None]

        read_data = list()
        for v, u in zip(var, units):
            d = self._select_data('symbol', v)

            if len(d) == 0:
                raise Exception(f'The variable "{v}" has no value.')
            elif len(d) > 1:
                raise Exception(f'The internal set of data is not consistent. More than one value is found for variable "{v}".')
            else:  # if len(d) == 1
                datum = copy(d[0])  # again, not to change the original Datum object (keep it expressed in base units)

                if u is not None:
                    datum.ito(u)
                else:
                    def_units = self._default_units[datum.symbol]
                    datum.ito(def_units)

                if rounding:
                    datum._value = round(datum._value, round_to)

                read_data.append(datum)

        if len(var) == len(read_data) == 1:
            return read_data[0]
        else:
            return  read_data

    def erase(self, *var: str|Datum) -> None:
        for v in var:
            if isinstance(v, Datum):
                v = v.symbol

            if self.has_value(v):
                # NOTE: this code allows to erase multiple datums with the same symbol (usually this would result in an exception)
                data = self._select_data('symbol', v)
                for d in data:
                    self._data.remove(d)

            for ex in self._tempex:
                if v in ex:
                    ex.erase(v)

        # NOTE2: there's no need to erase ._default_units() dict since we either overwrite the units when use .write()
        # method, or write them from scratch.

    def has_value(self, d: Datum|str) -> bool:
        if isinstance(d, Datum):
            symbol = d.symbol
        elif not d.isalnum():
            raise Exception(f'The symbol "{d}" cannot be treated as a variable.')
        else:
            symbol = d

        res = self._select_data('symbol', symbol)
        return len(res) > 0

    def clear(self) -> None:
        """Resets the whole linear iterator instance. Removed ALL data, all changes to temporary expressions and
        also resets the default units dict."""

        self._data = list()
        self._tempex = deepcopy(self._formulas)
        self._default_units = dict()

    # ================================================================================================ main calculations
    def solve(self,
              stop_at_target: bool = True,
              rounding: bool = True
              ) -> Datum:

        """


        :param stop_at_target:
        :param rounding:
        :return:
        """

        if self.target is None:
            raise Exception('Target is not set for the .solve() method.')

        self.is_consistent(self._data, raise_exception=True)

        while self.solvable:
            tempdata: List[Datum] = list()
            pure_tempdata: List[Datum] = tempdata  # here we use the fact that lists are mutable. These two will change together

            for tx in self._tempex:
                if tx.solvable:
                    unk = tx.unknown
                    unk_units = str(self.units[unk])
                    tx.target = f'{unk} = 0.001 {unk_units}'

                    res = tx.eval(rounding=False, num_only=True)
                    tempdata.extend(res)

            if self._duplicates(tempdata):
                pure_tempdata = self._resolve_duplicates(tempdata)

            if not self.is_consistent(pure_tempdata):
                # if there are different values that make a formula inconsistent
                raise Exception('The set of obtained solutions is inconsistent.')
            else:
                self.write(*pure_tempdata)

            if stop_at_target and self.has_value(self.target):
                break

        return self.read(self.target, units=self._return_units, rounding=rounding, round_to=self._round_target_to)


    # ======================================================================================================= properties
    @property
    def formulas(self) -> List[Formula]:
        """Returns deepcopy of the list with Formula instances. Hence, cannot be used to alter the Formula list."""
        return deepcopy(self._formulas)

    @property
    def vars(self) -> List[str]:
        """Returns a copy of the list with variable symbols. Hence, cannot be used to alter the list."""
        return copy(self._variables)

    @property
    def solvable(self) -> bool:
        return self.nof_solvable_equations() > 0

    @property
    def units(self) -> Dict[str, Datum.ureg.Unit]:
        """Returns deepcopy of the dict with Unit objects for each variable. Hence, cannot be used to alter the dict."""
        return deepcopy(self._units)

    @property
    def units_str(self) -> Dict[str, str]:
        return dict([(s, str(u)) for s, u in self._units])

    @property
    def target(self) -> str:
        return self._target

    @target.setter
    def target(self, d: Datum|str) -> None:
        if isinstance(d, str):
            d = Datum.to_datum(d)

        self._target = d.symbol
        self._round_target_to = d.num_decimals
        self._return_units = d.units_str
        self._units[self._target] = d.to_base_units().units

if __name__ == '__main__':
    data = ['v = 1.0 m/s', 'u = 0 m/s', 't = 10 s']
    formulas = ['v - u - a*t', 's - u*t - 0.5*a*t**2', 'v**2 - u**2 - 2*a*s', 's - t*(v+u)/2', 's - v*t + 0.5*a*t**2']
    units = {'v': 'm/s', 'u': 'm/s', 'a': 'm/s**2', 't': 's', 's': 'm'}

    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    li = LinearIterator(formulas, units)
    li.write(*data)

    for v in values:
        li.clear()
        li.write(*data)

        datum = f'v = {v} m/s'
        li.write(datum, rewrite=True)
        li.target = 's = 0.001 m'
        print(li.solve())
