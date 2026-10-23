## Scope
One of the [[Datum]] class' constructors uses only a string to create Datum instance. The string used to create Datum instance is called "Datum definition string", and must follow a set of rules to be parsed into a Datum instance successfully. The DatumDefString class checks the dds, but does not create a Datum instance. Moreover, a DatumDefString instance is used in Datum class to parse a dds, and to avoid cyclic imports, the DatumDefString file must not import from Datum file.

The DatumDefString instance therefore
- Checks that a dds is valid and *can* be used to create a Datum instance
- Provides all necessary properties to create a Datum instance (i.e. `variable`, `value`, and `units`)
- Provides all the methods needed to perform the necessary checks
- Does NOT create a Datum instance

### What is Datum definition string?
A typical dds looks like this: `m = 5 kg` or `g_Moon1 = 1.365 m/s**2`. A dds has three main groups: `variable`, `value`, and `units`. They are separated by spaces in the examples above. The first two groups have several subgroups and are discussed in respective section of this document.

**NOTE**: A dds is considered valid only if it matches fully with the rules provided below. If part of the string matches the rules, and another part does not, the whole string is said to be invalid.

### General structure of the class
DatumDefString uses regular expressions (regexs) to ensure that a dds is valid. A `pint.UnitRegistry` is used to test whether units passed to the constructor are valid. The class can be split into three main parts:

1) Constructor that creates the string
2) Checkers that verify that the string is valid
3) Properties that allow to access parts of the string

Each section is indicated below in public API section.

The DatumDefString class is a subclass of `str`, hence every method applicable to regular Python strings is also applicable to DatumDefString. **NOTE that changing DatumDefString via native `str` methods generates native Python's string and may result in it becoming an invalid DDS!**

<div class="page-break" style="page-break-before: always;"></div>

## Public API
```python
class DatumDefString(str):
	# class attributes
	patterns
		.variable
		.symbol
		.subscript
		.value
		.dds
	
	ureg: UnitRegistry
	
	# Constructor
	def __init__(dds: str) -> None
	
	# Checkers
	@classmethod
	def check_unit_validity(u: str|Unit) -> None
	
	# properties
	def variable -> str
	def symbol -> str
	def subscript -> str
	
	def value -> float
	def whole -> int
	def decimal -> float
	def sign -> Literal[-1, 1]
	def exponent -> int
	def num_decimals -> int
	
	def units -> str
	
	def raw_string -> str
	def string -> str
```

<div class="page-break" style="page-break-before: always;"></div>

## Class inputs
The class takes in only an instance of `str` when an instance is created. The input is a dds which is checked by the constructor whether it is valid or not. **The rules here are exhaustive and whatever is not allowed by the rules below is forbidden (AFIC[^1] assumption).**

[^1]: *All-forbidden initial condition* assumption.

### Clarifying vocabulary for defining regex
The following four words in this document mean the following:
- **"Must" is prescriptive.** If something *must* be true, then failure to satisfy this condition means failure of complying with the rule.
- **"May" is permissive.** If something "may" be true, then whether this condition is true or not does not cause general failure (hence, may-rules are usually extensions of must-rules that add more detail to them).
- **"Be" is exhaustive.** If something *(must/may) be* or something *is* that means all other "be-rules" must be false (be-rules are usually mutually exclusive and cannot be true at the same time).
- **"Contain" is not exhaustive.** If something *contains* something, that does **not** mean that all other "contain-rules" must be false.

When discussing groups (see below), their names may overlap with respective words (such as "symbol" being just the word "symbol" or the group named "symbol"). To distinguish between the two meanings, when relevant, the groups are indicated with the following notation: `group`.

### Structure of a dds
A Datum definition string consists of three main groups: `variable`, `value`, and `units`. Each group has its own rules and some also have subgroups. General structure of a dds looks like this (including the spaces)

`<variable> = <value> <units>`

If split to the smallest groups, then the structure is the following:

`<symbol>_<subscript> = <whole>.<decimal>E<exponent> <units>`

The `subscript`, `decimal`, `exponent` and `units` groups may be absent and are optional. In case they are not present in a dds, their respective properties return their default values (see [[Datum Definition String and DatumDefString#Class outputs (properties)|properties section]]). If the units group is absent, the dds is said to represent a dimensionless quantity. So, the minimal possible dds structure looks like

`<symbol> = <whole>`

Every special symbol coming in front of a group (such as "\_", "E", and ".") is present **only** if the following group is present and is **not** part of any group. The exponent sign "E" may also be lower-case "e".

`DDS-1` – the groups `variable`, `value`, `units`, and the equal sign ("=") must be separated by one or more spaces (**not** whitespace characters)
`DDS-2` – groups `subscript`, `decimal`, `exponent`, and `units` are optional and may be absent
`DDS-3` – the underscore ("\_") must be followed by `subscript` group and must not be placed if this group is omitted
`DDS-4` – the decimal dot (".") must be followed by `decimal` group and must not be placed if this group is omitted
`DDS-5` – the exponent sign ("E" or "e") must be followed by `exponent` group and must not be placed if this group is omitted
`DDS-6` – the space between `value` and `units` must be followed by `units` group and must not be placed if this group is omitted
`DDS-7` – leading and trailing spaces are not allowed for dds of any structure

#### Variable group

`<Variable> := <symbol>_<subscript>`

The variable group consists of two subgroups: "symbol" and "subscript". This groups mimics real naming of variables in science (although with stricter rules to keep simplicity). The "symbol" group denotes the main symbol of a variable, while subscript indicates specialization of the symbol. For example,

`V_0` – here `V` is "symbol" group and `0` is "subscript" group. The variable `V_0` hence is volume (V) which is either initial value or the molar volume of a gas, $V_0 = 22.4\ mol/L$ (subscript 0).
`m_Pete` – here `m` is "symbol" group and denotes mass. The "subscript" group is `Pete` which indicates to whom the mass belongs.

The symbol and subscript must obey the following rules:

**Rules for symbol**
`SYM-1` – `symbol` must consist of latin letters only
`SYM-2` – `symbol` must contain one or more symbols
`SYM-3` – `symbol` may be a single lower-case letter
`SYM-4` – `symbol` may be one or more upper-case letters

**Rules for subscript**
`SUB-1` – `subscript` must consist of latin letters or numbers only
`SUB-2` – `subscript` must contain one or more symbols
`SUB-3` – `subscript` may contain one or more lower-case letters
`SUB-4` – `subscript` may contain one or more upper-case letters
`SUB-5` – `subscript` may contain one or more numbers

#### value group

`<value> := <whole>.<decimal>E<exponent>`

The value group consists of three subgroups: `whole`, `decimal`, and `exponent`, the last two being optional. The `whole` and `decimal` groups together encode a float number which in this class is called "magnitude" (ignoring the exponent even if present). When integer is used in a dds, it all goes to `whole` with `decimal` group being empty.

**Rules for whole**
`WHL-1` – The `whole` group must consist of numbers only \[0-9]
`WHL-2` – The `whole` group may be preceded by a minus sign
`WHL-3` – The minus sign, if present, does not belong to the `whole` group
`WHL-4` – The `whole` group may contain zeroes at the beginning of the group, but they will be cut off (i.e. `00550` is equivalent to `550`)
`WHL-5` – The `whole` group must consist of at least one number

**Rules for decimal**
`DEC-1` – The decimal group must consist of numbers only \[0-9]
`DEC-2` – The `decimal` group may contain zeroes at the end of the group, but they will be cut off (i.e. `0.010000` is equivalent to `0.01`)

**Rules for exponent**
`EXP-1` – The `exponent` group must consist of numbers only \[0-9]
`EXP-2` – The `exponent` group may be preceded by a minus sign
`EXP-3` – The `exponent` group may be preceded by a plus sign
`EXP-4` – The sign, if present, belongs to the `exponent` group

*The exponent hence must be an integer and must not contain decimal point.*

#### Units group
Since units may be very different, it is hard to determine exact rules they must follow. Hence, we rely on checking units validity via `UnitRegistry.parse_units` method. Therefore the rules for unit group are

`UNT-1` – The `unit` group must **not** be an empty string or a whitespace character
`UNT-2` – The `unit` group is everything that follows a space(s) after the `value` group

The `unit` group is passed directly to the `parse_units` method and if no exceptions were raised, the units are considered to be valid.


### Methods
The class has two methods:
```python
def __init__(dds: str) -> None
def check_unit_validity(u: str|Unit) -> None
```
#### \_\_init__
The constructor of DatumDefString accepts one argument – the potential dds as an instance of `str`. The constructor

`CST-1` – Checks the data type of the `dds` parameter to be an instance of `str`. If not, raises `TypeError`
`CST-2` – Tries to match the obtained parameter with a full dds regex (private equivalent of `.patterns.dds`). If failed, raises `InvalidDatumDefString`
`CST-3` – Checks validity of units by using `.check_unit_validity` method
`CST-4` – Does not catch any exceptions raised by `.check_unit_validity`

#### check_unit_validity
The `check_unit_validity` method accepts as an attribute
- An instance of `str`
- An instance of `pint.Unit` belonging to any UnitRegistry

The method then 
`CUV-1` – Checks the type of accepted parameter. It if it not either `str` or `pint.Unit`, raises `TypeError`
`CUV-2` – Uses `cls.ureg.parse_units` method to validate units
`CUV-3` – Maps raised exceptions to the following two exceptions: `UnvalidUnitExpression`, `UndefinedUnit` when the exception raised is within to their [[Datum Definition String and DatumDefString class#Errors|application scope]]. Lets other exceptions escape

Based on version of `pint`, the exact mapping may differ and must be determined experimentally.

<div class="page-break" style="page-break-before: always;"></div>

## Class outputs (properties)
The properties of the class are used to get respective parts of the dds. They are, therefore, split into four groups: *variable*, *value*, *units*, and *rest*. There are also several class attributes that contain an internal `UnitRegistry` used to confirm validity of units, and to store complied regexs.

### Variable group
This group consists of three properties:
```python
def variable -> str
def symbol -> str
def subscript -> str
```
The properties return respective dds groups as detected by regex, without any further adjustments or normalization. The `variable` group does **not** return the space that goes after it.

`VRG-1` – The properties 'variable', 'symbol', and 'subscript' return respective groups of a dds in the form detected by regex
`VRG-2` – No actions are made on the detected groups
`VRG-3` – The 'variable' property does not return the space that goes after the `variable` group
`VRG-4` – The 'subscript' property returns an empty string if the `subscript` group was absent

### Value group
This group consists of the following properties:
```python
def value -> float
def whole -> int
def decimal -> float
def sign -> Literal[-1, 1]
def exponent -> int
def num_decimals -> int
```
The properties return respective dds groups as detected by regex, converted to the indicated number type.

`VLG-1` – The 'whole' and 'exponent' properties return respective dds groups as detected by regex, converted to their respective type
`VLG-2` – The 'value' group returns Python's `float` obtained by converting the `value` group of the dds[^2].
`VLG-3` – The 'decimal' property returns a float between 0.0 and 1.0 (not including) where the decimal digits of the float are ones found in the `decimal` group of the dds[^3].
`VLG-4` – The 'sign' property returns either '1' or '-1' depending on whether the minus sign was present in front of the `whole` group in the dds
`VLG-5` – The 'num_decimals' property returns the number of decimal digits equal to the one in the `decimal` groups of the dds, except the trailing zeroes (i.e. after the trailing zeroes were removed, see `DEC-2`)
`VLG-6` – In case `decimal` and/or `exponent` dds groups are absent, the respective properties return 0 (respectively either `float` or `int`)

[^2]: Note that it means that the exponent indicator ("E" or "e") is not necessarily preserved. If conversion to `float` produces a typical float (without power), then the 'value' property will return that float (e.g. from the `value` group equal to `"1.62E4"`, the property will return `16200`).
[^3]: Note that since the property returns Python's `float`, the trailing zeroes at the end of the `decimal` group are already removed. See `DEC-2`.

### Units group
The units group consists of only one property
```python
def units -> str
```

`UNG-1` – The 'units' property returns a string detected by the regex with all spaces removed from it [^4]
`UNG-2` – In case the `units` group was absent, the 'units' property returns a string `"dimensionless"`[^5]

The units are, however, parsed inside the constructor and hence the property should not return any malformed unit strings, because exceptions are raised from constructors.

[^4]: That is necessary to make comparisons of units from different dds's possible.
[^5]: Note that if the `units` group itself is `"dimensionless"`, then the property returns that same string due to `UNG-1`.

### Other properties
There are also two other properties
```python
def raw_string -> str
def string -> str
```
The properties return the dds passed to the constructor.

`OPP1` – The 'raw_string' property returns the exact same string given to the constructor
`OPP2` – The 'string' property returns a normalized string

`NS-1` – The normalized string must have exactly one space as indicated in `DDS-1`
`NS-2` – The normalized string must not have spaces in the `units` group
`NS-3` – The normalized string must be compiled by using the following template, and using respective properties of the class: `f{dds.variable} = {dds.value} units` with "units" variable being modified property `dds.units` according to the requirements above
`NS-4` – The normalized string uses small exponent sign (small "e")

### Class attributes – UnitRegistry
The class contains a public class attribute called `ureg`. It is `pint`'s UnitRegistry that is used to check units validity. The attribute is made public to make it possible create custom units for `DatumDefString` or assign to it another UnitRegistry.

### Class attributes – compiled regexs
The DatumDefString class should have several publicly available attributes which contain compiled regex expressions. This is done to allows checking smaller groups (only variables or magnitudes). The attributes are accessible via the following notation
```python
dds = DatumDefString("m = 5 kg")
dds.patterns.variable
dds.patterns.symbol
dds.patterns.subscript
dds.patterns.value
dds.patterns.dds  # regex to match a complete dds
```
The attributes are compiles regex expressions, so it must be possible to use them to verify whether a certain string matches the respective group. For example
```python
s = "V_0"
dds.patterns.variable.fullmatch(s)

ddef = "g_Moon = 1.635 m/s**2"
dds.patterns.dds.fullmatch(ddef)
```
At the same time,

`CCR-1` – Reassigning the attribute must not change the original regex used inside the class

<div class="page-break" style="page-break-before: always;"></div>

## Errors
The DatumDefString class is tightly linked to Datum class and thus uses exceptions of the Datum class. The Exceptions used have the following hierarchy:
```  
DatumException  
├── UnitsException   
│   ├── UndefinedUnit  
│   └── InvalidUnitExpression  
└── InvalidDatumDefString  
```
*NOTE: The Datum class has more exceptions. Only the ones used in DatumDefString are shown here.*

`UndefinedUnit` is raised whenever the unit string follows the rules of unit definition, but the unit itself is unknown. This applies to  
  
- Custom units that are not present in the UnitRegistry of DatumDefString
- Arbitrary strings containing only latin letters (such as "notaunit" or "huh")
- Any combination of the previous two points via arithmetical operations (e.g. "huh / notaunit")
- Is used to replace `pint`'s `UndefinedUnitError`
  
`InvalidUnitExpression` is raised whenever the unit string is malformed, i.e. is not parsed as a unit string by `pint`. That includes  
  
- Not pure units, e.g. scaled units ("7 meter")
- Numbers only
- Presence of arithmetical operators without operands (e.g. "meter / " or "second \*")
- Is used to catch `pint`'s `ValueError` (as from "7 meter") and `AssertionError` (as from "/85*")

For when each exception is raised see [[Datum Definition String and DatumDefString class#Methods|description of methods]].

## Invariants
The following conditions must hold all the time for DatumDefString class regardless what string is passed to the constructor.

`INV-1` – The string from the 'string' property must always produce the same dds as the one it describes (within the floating point error limit)[^6]
```python
ddef1 = DatumDefString(dds)  
ddef2 = DatumDefString(ddef1.string)  
  
assert ddef1.variable == ddef2.variable  
assert isclose(ddef1.value, ddef2.value)  
```

[^6]: Since floating point errors may arise when working with float numbers, the invariant does not require direct comparison of the strings. The units property is also not compared since it depends on the way units were written in the raw dds.

`INV-2`
```python
value = dds.value
composed = dds.sign * (dds.whole + dds.decimal) * 10 ** dds.exponent
math.isclose(value, composed, abs_tol=1e-15)
```

`INV-3`
```python
DatumDefString.check_unit_validity(dds.units) is None
```
(This never raises exceptions)

`INV-4`
```python
if dds.subscript:
	dds.variable == dds.symbol + '_' + dds.subscript
else:
	dds.variable == dds.symbol
```

`INV-5`
```python
dds.value * dds.sign >= 0.0
```

`INV-6`
```python
DatumDefString(s).raw_string == s
```

`INV-7`
```python
dds.whole >= 0
```

`INV-8`
```python
0.0 <= dds.decimal < 1.0
```

`INV-9`
```python
dds.num_decimals >= 0
```

<div class="page-break" style="page-break-before: always;"></div>

## Examples and typical use cases
```python
from QCalculator.Datum import Datum
from pint import UnitRegistry

ureg = UnitRegistry()


# Creating a DatumDefString instance
dds = f"g_Moon1 = {9.81/6} m / s ** 2"
ddef = DatumDefString(dds)
print(ddef.raw_string)
# "g_Moon1 = 1.635 m / s ** 2"
print(ddef.string)
# "g_Moon1 = 1.635 m/s**2"


# Creating Datum instance
var = ddef.variable
val = ddef.value
unt = ddef.units

d = Datum(var, val, unt)
print(d)
# "g_Moon1 = 1.635 m/s**2"


# Checking units without creating a dds
u = "definitely not a unit"

try:
	DatumDefString.check_unit_validity(u)
except InvalidUnitExpression:
	print('Unlucky')
# "Unlucky"

u = ureg.Unit('m/s')
DatumDefString.check_unit_validity(u)
# None


# Matching "variable" group
v = "g_Moon1"
res = DatumDefString.patterns.variable.fullmatch(v)
print(res)
# <re.Match object; span=(0, 7), match='g_Moon1'>
```

