from __future__ import annotations

from pint import Quantity, UnitRegistry, DimensionalityError, Unit
from typing import Optional, Literal, Set
from sympy import Symbol
from copy import copy

from QCalculator.Exceptions.DatumExceptions import *


# noinspection PyTypeHints
class Datum:
    """
    The Datum class is an extension of pint.Quantity that also includes a string symbol that represents a variable in
    symbolic calculations (carried out by sympy in Formula class). The three main attributes of Datum class are
    .symbol (variable symbol for sympy), .value (integer or float), and .units. All are implemented as properties. The
    .units property returns a pint.Unit instance taken from class attribute "ureg". All units used with Quantity Calculator
    package must come from Datum.ureg, because pint does not allow operations of units from different unit registries.
    Usually, each method where units can be passed use .domesticate_units() method which makes units compatible with
    other units used in Datum. But you can also use either Datum.ureg.Unit(<your units>) or Datum.domesticate_units().\n

    The class defines methods for arithmetic operations on Datum instances with other Datums, Quantities and integers
    or floats.

    **For detailed documentation print private class attributes:**\n
    - _INIT_DOCSTRING\n
    - _ARITHMETIC_METHODS_DOCSTRING\n
    - _ANALYSIS_DOCSTRING\n
    - _CHANGING_DATUM_DOCSTRING\n
    - _PROPERTIES_DOCSTRING\n
    """

    ureg = UnitRegistry(system='SI')
    _FORBIDDEN_SYMBOLS: Set[str] = {'', ' '}  # symbols that are forbidden for use in defining variables

    _INIT_DOCSTRING = """
        A Datum object can be initialised by using three different methods:
        - Directly from defining variable symbol, value and units
        - By specifying variable symbol and quantity (see .from_quantity())
        - By using a specially formatted string (see .from_string())

        Subsequently, *args can be any of the three
        - three arguments. Variable symbol: str, value: int|float, units: str | Datum.ureg.Unit
        - Two arguments. Variable symbol: str, pint Quantity that specifies both value and units
        - One argument: a correctly formatted string.

        The latter two initialisations can be also done by directly calling .from_quantity and .from_string methods.
        Any other combinations of *args will lead to an InitialisationError.
        
        The methods useful for initialising Datum instance are
        - from_quantity(s: str, q: Quantity) -> Datum
        - from_string(string: str) -> Datum  # format "<symbol> = <int or float number> <units>" including spaces
        These two methods are built into the __init__ method, so their parameters can be passed directly to it.
        
        - domesticate_units(u: str | pint.Unit) -> Datum.ureg.Unit
        Used to convert units of any unit registry to the units of Datum.ureg.
        
        - to_datum(d: Datum|Quantity|str, symbol: str = '') -> Datum
        Used to return Datum whatever is passed to it. Passing Quantity to parameter 'd' also requires passing 'symbol' string.

        NOTE: You can change the _ZERO_TOLERANCE_EXPONENT attribute, but I recommend doing it only if you know
        what you are doing. If you, despite this, changed it and now the code does not work properly, set its value
        back to 7.
        """

    def __init__(self, *args) -> None:
        self._symbol: str
        self._value: int|float
        self._units: Datum.ureg.Unit

        if len(args) == 3 and all(
                [isinstance(args[0], str),
                 isinstance(args[1], (int, float)),
                 isinstance(args[2], (str, Datum.ureg.Unit))
                 ]):
            self._symbol, self._value, self._units = args[0], args[1], Datum.domesticate_units(args[2])

        elif len(args) == 2 and all([isinstance(args[0], str), isinstance(args[1], Quantity)]):
            self._symbol, self._value, self._units = self.from_quantity(args[0], args[1])

        elif len(args) == 1 and isinstance(args[0], str):
            self._symbol, self._value, self._units = self.from_string(args[0])

        else:
            raise InitialisationError('', args)

        self._base_units = self.quantity.to_base_units().units
        self._ZERO_TOLERANCE_EXPONENT = 7




    # ===================================================================================================== initializers
    @staticmethod
    def from_quantity(s: str, q: Quantity) -> Datum:
        if s in Datum._FORBIDDEN_SYMBOLS:
            raise InvalidSymbol('The suggested symbol cannot be used for naming variables.', var=s)

        return Datum(s, q.magnitude, Datum.domesticate_units(q.units))

    @staticmethod
    def from_string(string: str) -> Datum:
        """The general format is "<symbol> = <int or float number> <units>". Spaces are mandatory."""
        try:
            symbol, rest = string.split('=')
            symbol = symbol.strip(' ')
            rest = rest.strip(' ')
            number, units = rest.split(' ', maxsplit=1)

            if '*' in number:
                raise InvalidSymbol('To indicate powers use e-notation (a*10e+b) instead of "**".', '*')

            number = float(number)
            units = Datum.domesticate_units(units)
        except ValueError:
            raise InitialisationError(f'Invalid Datum definition string. Check the format: <symbol> = <value> <units> (including spaces).', string)

        return Datum(symbol, number, units)

    @staticmethod
    def domesticate_units(u: str | Unit) -> Datum.ureg.Unit:
        """Returns the same units, but drawn from Datum's own unit registry."""
        return Datum.ureg.Unit(u)

    @staticmethod
    def to_datum(
            d: Datum|Quantity|str,
            symbol: str = ''
    ) -> Datum:
        """Depending on the type of the parameter "d", uses either .from_string() or .from_quantity(), or just returns
        the copy of the parameter so that the object returned is always a Datum instance. Passing Quantity instance also
        requires passing in "symbol" parameter."""

        if isinstance(d, Datum):
            return copy(d)  # so that interventions on the returned object do not change the original one and the vice versa
        elif isinstance(d, Quantity):
            return Datum.from_quantity(symbol, d)
        elif isinstance(d, str):
            return Datum.from_string(d)
        else:
            raise TypeError(f'The parameter "d" has a wrong type. Expected "Datum", "str" or "pint.Quantity", got "{type(d)}".')




    # ============================================================================================== other magic methods
    def __str__(self) -> str:
        """Returns a string of the form <variable> = <value> <units>. For example, 'm = 10 g' or 'v = 2 m/s'"""
        return f'{self.symbol} = {self.value} {self.units_str}'

    def __eq__(self, other: Datum):
        """
        Two Datums are considered equal if\n
        - They have compatible units\n
        - They have the same value when converted to base units (checked with math.isclose())\n
        - They have the same symbol
        """
        from math import isclose

        if not Datum._ZTE_test(self._ZERO_TOLERANCE_EXPONENT):
            raise InvalidSymbol('The zero tolerance exponent must be between 0 and 20.', str(self._ZERO_TOLERANCE_EXPONENT))

        conditions = (
            self.symbol == other._symbol,
            isclose(self.value, other.value, abs_tol=eval(f'10E-{self._ZERO_TOLERANCE_EXPONENT}')),
            self.quantity.to_base_units() == other.quantity.to_base_units()
        )

        return all(conditions)

    def __iter__(self):
        return [self.symbol, self.value, self.units].__iter__()

    @staticmethod
    def _ZTE_test(zte: int) -> bool:
        if isinstance(zte, int) and 0 < zte < 20:
            return True
        else:
            return False




    # ========================================================================== arithmetical operations (magic methods)
    _ARITHMETIC_OPERATIONS_DOCSTRING = """
    This section defines arithmetic operations on Datum objects. The following methods are defined
    - div(other: Datum|Quantity|float|int, new_datum_symbol: Optional[str] = None) -> Datum | Quantity
    - rdiv(other: Datum|Quantity|float|int, new_datum_symbol: Optional[str] = None) -> Datum | Quantity
    - mul(other: Datum|Quantity|float|int, new_datum_symbol: Optional[str] = None) -> Datum | Quantity
    
    The three methods defined above return a pint Quantity when 'other' is Quantity or Datum AND new_datum_symbol is None
    They return a Datum instance when 'other' is float or int, or when 'other' is a Quantity AND new_datum_symbol is a string.
    The new_datum_symbol is the symbol used to create a variable for Datum instance since dividing/multiplying changes
    units and the same symbol cannot be used. 
    
    (for conciseness, let "Literal['self', 'other'] = 'self'" be called "LIT")
    - add(other: Datum|Quantity, symbol_ex: bool = True, use_units_of: LIT, use_symbol_of: LIT) -> Datum
    - sub(other: Datum|Quantity, symbol_ex: bool = True, use_units_of: LIT, use_symbol_of: LIT) -> Datum
    - rsub(other: Datum|Quantity, symbol_ex: bool = True, use_units_of: LIT, use_symbol_of: LIT) -> Datum
    
    The three methods defined above always return a Datum instance, since adding or subtracting different units is not
    allowed. The rest of the parameters control behaviour of the functions when two Datums with the same units have
    different symbols (which is not normal, but possible).
    - 'symbol_ex' allows to continue the operation if set to False. If True, it will raise an exception.
    If 'symbol_ex' is set to True, then the question is symbol and units of which Datum instance the function needs to use.
    - 'use_units_of' can only take values of 'self' and 'other'. Respective units will be used for returned Datum instance
    - 'use_symbol_of' can only take values of 'self' and 'other'. Respective symbol will be used for returned Datum instance
    
    (Defined in "changing value" section, but relevant here)
    .iscale is just .scale method with 'in_place' parameter set to True. The method's naming is copying pint Quantity.
    - scale(factor: float|int, in_place: bool = False) -> Optional[Datum]
    - iscale(factor: float|int) -> None
    
    
    NOTE: Addition and multiplication are not defined as magic methods because when used with pint.Quantity as the right
    method (i.e. quantity.__add__(datum)), the __add__ method of Quantity is called. Since it can't handle Datum 
    instances, it results in an error that is hard to understand for people who don't know about this problem. Hence, 
    to avoid long debugging, only .add(), .sub(), and .rsub() were kept.
    """

    def __truediv__(self, other) -> Quantity:
        return self.div(other)

    def __rtruediv__(self, other) -> Quantity:
        return self.rdiv(other)

    def __mul__(self, other) -> Quantity:
        return self.mul(other)

    def __rmul__(self, other) -> Quantity:
        return self.__mul__(other)

    def div(self,
            other: Datum | Quantity | float | int,
            new_datum_symbol: Optional[str] = None
            ) -> Datum | Quantity:

        if isinstance(other, (Datum, Quantity)):
            other_q = self._get_quantity(other)
            q = self.quantity / other_q
            q.ito_reduced_units()
            return self._create_datum_ip(q, new_datum_symbol)

        elif isinstance(other, float|int):
            return self.scale(1/other)

        else:
            raise TypeError(f'Invalid type for division with Datum: "{type(other)}".')

    def rdiv(self,
             other: Datum | Quantity | int | float,
             new_datum_symbol: Optional[str] = None
             ) -> Datum | Quantity:

        if isinstance(other, Datum):
            return other.div(self, new_datum_symbol)

        elif isinstance(other, (int, float, Quantity)):
            return other / self.quantity

        else:
            raise TypeError(f'Invalid type for division with Datum: "{type(other)}".')

    def mul(self,
                 other: Datum | Quantity | float | int,
                 new_datum_symbol: Optional[str] = None
             ) -> Datum | Quantity:

        if isinstance(other, (Datum, Quantity)):
            other_q = self._get_quantity(other)
            q = self.quantity * other_q
            q.ito_reduced_units()
            return self._create_datum_ip(q, new_datum_symbol)

        elif isinstance(other, (int, float)):
            return self.scale(other)

        else:
            raise TypeError(f'Invalid type for multiplication with Datum: "{type(other)}".')

    def add(self,
                other: Datum|Quantity,
                symbol_ex: bool = True,
                use_units_of: Literal['self', 'other'] = 'self',
                use_symbol_of: Literal['self', 'other'] = 'self',
            ) -> Datum:

        q = self._get_quantity(other)
        unit_ref = self.units if use_units_of == 'self' else other.units

        try:
            new_q = self.quantity + q
            symbol = self._symbol_analysis(other, symbol_ex, use_symbol_of)
            d = Datum(symbol, new_q)
            d.to(unit_ref, in_place=True)
            return d

        except DimensionalityError:
            raise IncompatibleUnits(comment=f'Cannot sum/subtract incompatible units', from_unit=self.units_str, to_unit=q.units)

    def sub(self,
            other: Datum|Quantity,
            symbol_ex: bool = True,
            use_units_of: Literal['self', 'other'] = 'self',
            use_symbol_of: Literal['self', 'other'] = 'self',
            ) -> Datum:
        return self.add(other.scale(-1), symbol_ex, use_units_of, use_symbol_of)

    def rsub(self,
             other: Datum | Quantity,
             symbol_ex: bool = True,
             use_units_of: Literal['self', 'other'] = 'self',
             use_symbol_of: Literal['self', 'other'] = 'self',
             ) -> Datum:

        if isinstance(other, Datum):
            use_units_of = Datum._swap_self_other(use_units_of)
            use_symbol_of = Datum._swap_self_other(use_symbol_of)
            return other.add(self.scale(-1), symbol_ex, use_units_of, use_symbol_of)

        elif isinstance(other, Quantity):
            try:
                unit_ref = other.units if use_units_of == 'other' else self.units
                new_q = other - self.quantity
                symbol = self._symbol_analysis(other, symbol_ex, use_symbol_of)
                d = Datum(symbol, new_q)
                d.to(unit_ref, in_place=True)
                return d

            except DimensionalityError:
                raise IncompatibleUnits(comment=f'Cannot sum/subtract incompatible units', from_unit=self.units_str,
                                        to_unit=other.units)

        else:
            raise IncompatibleUnits(comment=f'Cannot sum/subtract incompatible units', from_unit=self.units_str,
                                    to_unit=other.units)




    # =============================================================================== helpers to arithmetical operations
    @staticmethod
    def _swap_self_other(var: Literal['self', 'other']) -> Literal['self', 'other']:
        if var == 'self':
            return 'other'
        elif var == 'other':
            return 'self'
        else:
            raise ValueError(f'The "use_units_of" parameter has to be either "self" or "other". Got "{var}".')

    def _symbol_analysis(self,
                         other: Datum | Quantity,
                         symbol_ex: bool = True,
                         use_symbol_of: Literal['self', 'other'] = 'self'
                        ) -> str:
        """
        Helps to .add, and .rsub decide what symbol they should use in case symbol_ex was set to True and two Datums
        had different symbols.

        :param other: Datum or Quantity passed to .add or .rsub for operation with this Datum
        :param symbol_ex: if False, this method raises the DifferentSymbol exception
        :param use_symbol_of: either 'self' or 'other'. Defines which symbol will be used for Datum returned by .add or .rsub
        :return: The symbol which will be used for Datum returned by .add or .rsub
        """

        if isinstance(other, Quantity):
            return self.symbol

        elif isinstance(other, Datum):
            if not self.symbol == other.symbol:
                if symbol_ex:
                    raise DifferentSymbols("", self.symbol, other.symbol)
                elif use_symbol_of == 'self':
                    symbol = self.symbol
                elif use_symbol_of == 'other':
                    symbol = other.symbol
                else:
                    raise InvalidSymbol('Expected either "self" or "other".', use_symbol_of)
            else:
                symbol = self.symbol

            return symbol

        else:
            raise TypeError(f'Expected "Quantity" or "Datum", got "{type(other)}".')

    @staticmethod
    def _create_datum_ip(
                            new_qd: Quantity,
                            new_datum_symbol: Optional[str]
                        ) -> Datum | Quantity:
        """
        Written as a separate method since the same code is used several times. Creates Datum if 'new_datum_symbol' is
        provided, else creates a pint Quantity.

        :param new_qd: Quantity from which Datum may be created
        :param new_datum_symbol: the new symbol to be used for Datum, or None (in this case Quantity is returned)
        :return:
        """

        if new_datum_symbol is not None:
            return Datum.from_quantity(new_datum_symbol, new_qd)
        else:
            return new_qd
        # here copy() is not needed since the quantity used here is internal for .mul and .div, and hence is deleted after the method call is complete

    @staticmethod
    def _get_quantity(other: Datum|Quantity) -> Quantity:
        """
        No matter whether a Datum or a Quantity is passed as an argument, a Quantity is returned.

        :param other: Datum or Quantity from which a Quantity object is to be made
        :return: A Quantity object
        """

        if isinstance(other, Datum):
            other_q = other.quantity
        elif isinstance(other, Quantity):
            other_q = other
        else:
            raise TypeError(f'Incorrect type of "other". Expected "Datum" or "pint.Quantity", got "{type(other)}".')

        return other_q




    # ================================================================================================= analysis methods
    _ANALYSIS_DOCSTRING = """
    This section defines methods used to analyse current Datum instance.
    
    - get_decimals(value: float) -> int
    This method is used for rounding values of the Datum when reading it. The method returns the number of decimal places
    in a non-zero float number by converting it to string and analysing it. I.e. for a number 0.001 it returns 3. For
    0.01 – 2, and for 0.0000001 - 7. This will be used later for quick and convenient definition of target variables 
    in Formula and LinearIterator objects.
    
     - is_compatible(other: Datum|Quantity|str|Datum.ureg.Unit) -> bool
     This method returns a boolean value which states if the units of the current Datum are compatible with the units
     of 'other'. Note that
     - This method does not use .domesticate_units and hence passing any Unit object will result in
     an exception
     - Symbols are not compared even if 'other' has it
    """


    @staticmethod
    def get_decimals(value: float) -> int:
        """Returns a number of decimal places in the provided float number. Works only if the number is not a zero."""

        if value == 0.0:
            raise InvalidSymbol('Cannot determine significant digits. Choose a non-zero value.', str(value))

        str_value = str(float(value))

        if 'e' in str_value:
            decimals = str_value.split('e')[1][1:] # to account for both e+ and e-
            return int(decimals)
        elif 'E' in str_value:
            decimals = str_value.split('E')[1][1:]
            return int(decimals)
        else:
            decimals = str_value.split('.')[1]
            return len(decimals)

    def is_compatible(self, other: Datum|Quantity|str|Datum.ureg.Unit) -> bool:
        """Checks whether the self Datum instance has compatible units with "other" object which encodes units."""

        if isinstance(other, (Datum, Quantity)):
            q = self._get_quantity(other)
            return self.units.is_compatible_with(q)
        elif isinstance(other, (str, Datum.ureg.Unit)):
            return self.units.is_compatible_with(other)
        else:
            raise TypeError(f'Expected "Datum", "pint.Quantity", "str", or "Datum.ureg.Unit", got "{type(other)}"')




    # ========================================================================================== changing value or units
    _CHANGING_DATUM_DOCSTRING = """
    This section defines methods for chaning Datum's value or units. The names mostly copy the Quantity's names.
    
    - to(units: str|Datum.ureg.Unit, in_place: bool = False) -> Optional[Datum]
    - ito(units: str|Datum.ureg.Unit) -> None
    - to_base_units(in_place: bool = False) -> Optional[Datum]
    - ito_base_units() -> None
    
    Are defined to convert Datum into units different from the ones it was created with. The base units are still
    stored in a separate variable. .ito method is .to with 'in_place' set to True. Same applies to .to_base_units, but
    there Datum is converted to the basic SI units. This is useful for comparison and calculations with other Datums.
    
    - scale(factor: float|int, in_place: bool = False) -> Optional[Datum]
    - iscale(factor: float|int) -> None
    
    These methods are defined to scale (multiply by a certain float or int value) current Datum. The .scale method is
    internally used by .mul when its 'other' parameter is merely float or integer. 
    """


    def to(self, unit: str | Datum.ureg.Unit, in_place: bool = False) -> Optional[Datum]:
        try:
            new_q = self.quantity.to(unit)
            if in_place:
                self._value = new_q.magnitude
                self._units = new_q.units
            else:
                return Datum.from_quantity(self.symbol, new_q)
        except DimensionalityError:
            raise IncompatibleUnits(comment='', from_unit=self.units_str, to_unit=unit)

    def ito(self, unit: str | Datum.ureg.Unit) -> None:
        self.to(unit, in_place=True)

    def to_base_units(self, in_place: bool = False) -> Optional[Datum]:
        return self.to(self.base_units_str, in_place=in_place)

    def ito_base_units(self) -> None:
        self.to(self.base_units, in_place=True)

    def scale(self, factor: float|int, in_place: bool = False) -> Optional[Datum]:
        if in_place:
            self._value = factor * self._value
            return None
        else:
            return Datum(self.symbol, self.value * factor, self.units_str)

    def iscale(self, factor: float|int) -> None:
        self.scale(factor, in_place=True)




    # ======================================================================================================= properties
    _PROPERTIES_DOCSTRING = """
    This section describes all the properties of Datum class.
    
    - quantity -> Quantity
    - symbol -> str
    - sp_symbol -> sympy.Symbol  # might be useful later when Datum is used together with sympy
    - value -> float|int
    - magnitude -> float|int  # May b useful if one variable may be both Datum and Quantity. In this case we avoid unnecessary if-statement
    - units_str -> str
    - units -> Datum.ureg.Unit
    - base_units -> Datum.ureg.Unit
    - base_units_str -> str
    - num_decimals -> int  # just automatically applies .get_decimals to the value of the Datum and returns the result
    """

    @property
    def quantity(self) -> Quantity:
        return self.value * self.units

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def sp_symbol(self) -> Symbol:
        return Symbol(self.symbol)

    @property
    def value(self) -> float|int:
        return self._value

    @property
    def magnitude(self) -> float|int:
        """Might be useful when you call that method on a variable that can be both Datum and pint.Quantity"""
        return self._value

    @property
    def units_str(self) -> str:
        return str(self._units)

    @property
    def units(self) -> Datum.ureg.Unit:
        return self._units

    @property
    def base_units(self) -> Datum.ureg.Unit:
        return self._base_units

    @property
    def base_units_str(self) -> str:
        return str(self._base_units)

    @property
    def num_decimals(self) -> int:
        return self.get_decimals(self.value)
