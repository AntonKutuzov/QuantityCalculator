## Scope
The Datum class represents a named physical quantity, such as `m = 5.2 kg`. The word "Datum" stands for singular of "Data" and must be understood as "a piece of data". The string representing a Datum instance (such as `m = 5.2 kg`) is called a "Datum definition string" (dds for short).

The Datum class is used to create and operate on a single named physical quantity (a single datum). The dds's (Datum definition strings) are parsed by a separate class called [[Datum definition string]].

### General structure of the class
Since Datum is created to operate on a single physical quantity, the class consists of the following parts:
- Constructors that let create Datum instance
- Comparison methods that allow to compare two different Datum instances
- Converters that take care of unit conversion and respective change in numerical value
- Properties that allow to access several important attributes of the instance

## Public API
```python
class Datum:
# class attributes
ddef: AbstractDDS = DatumDefString
spec: DSPec = DatumDefString.spec

# Constructors
def __init__(dds: str) -> None

@classmethod
def from_quantity(s: str, q: Quantity) -> Datum

# Magic methods
def __str__() -> str
def __eq__(other: Datum) -> bool

# Comparison
def compatible_units(other: Datum|Quantity|str|Unit) -> bool

# Converters
'''Alters the dds as well!'''
def to(units: str|Unit) -> Datum
def scale(factor: float|int) -> Datum

# properties
def quantity -> Quantity
def variable -> str
def value -> float
def units -> Unit
def base -> Datum
def dds -> DatumDefString
```

## Methods
### Constructors
There are two possible constructors in Datum class. The default one accepts a dds and turns it into a Datum instance. An alternative constructor creates a Datum instance from a pint.Quantity instance, and is primarily used after arithmetic operations performed on Datum instances that result in Quantities. See [[Datum#Use cases|examples]].

#### `__init__`
The \_\_init__ method accepts a datum definition string[^1], and turns it into a Datum instance.

- The method checks the type of a dds, and if it is not an instance of string, raises `TypeError`
- In case dds parameter is an instance of `str`, passes it with no changes to DatumDefString constructor. Does not catch any exceptions raised by DatumDefString
- The units of returned Datum instance belong to the UnitRegistry specified in the `spec` attribute

Since Datum possesses many properties that 'disassemble' it (such as `symbol`, `subscript`, `exponent` and others), there is no way to define it by specifying these values separately. To define Datum from the separate variables containing variable, value, and units, use f-strings. See [[Datum#Use cases|examples]].

[^1]: Since [[AbstractDDS]] is a subclass of Python's str, Datum can accept both [[DatumDefString]] and other subclasses of AbstarctDDS, and plain Python's str.

#### from_quantity
The `from_quantity` method accepts a `pint.Quantity` instance and an instance of string which is used as a symbol. 

- The method checks the type of the two parameters and if they are not of indicated types, raises `TypeError`. (You don't need to reject the AbstractDDS instances, since they won't match to the variable [[patterns|pattern]]).
- The method uses `q.magnitude` and `q.units` to construct an f-string, and then passes it to the `__init__` method
- Returns a Datum instance with respective variable, value and units
- The units of returned Datum instance belong to the UnitRegistry specified in the `spec` attribute

### Magic methods
There are two magic methods defined in Datum class: the `__eq__` and `__str__` methods. No arithmetic methods are defined, because they cause hard-to-trace errors when used with Quantity instances, and because they produce Quantity instances which is misleading in both cases.

#### `__eq__`
The two Datum instances can be considered equal iff the following conditions hold:
1) They have exactly the same variables (both symbol and subscript)
2) They have equal values (determined by `math.isclose`)
3) They have the same units
If the units of two Datums are compatible, but different, the `__eq__` method will return `False`. See examples below

```python
# Strict equality
d1 = Datum('V_A = 15 m/s')
d2 = Datum('V_A = 30 m/s')
d2 = d2.scale(0.5)

d1 == d2
# True

d3 = d2.to('km/h')
d2 == d3
# False

d2.base == b3.base
# True
```

The `__eq__` method

- Checks whether the `other` parameter is Datum[^2]. If not, raises `TypeError`
- Returns a boolean indicating whether the two Datum instances are equal

As a result of the requirements above it also must hold that
- The dds's of both Datums are the same (within the floating point precision, so the actual strings may differ slightly, but the properties of respective DatumDefString instances, such as `exponent`, `sign` and other must be the same).
- The value of `quantity` property must be the same

[^2]: That means, it doesn't use `isinsance`, but rather `type(other) is Datum`, because subclasses are most likely have other equality requirements.

#### `__str__`
The `__str__` method returns a dds of the Datum instance by using DatumDefString's property `d.dds.string` (normalized string).

### Comparison methods
Currently there's one comparison method which checks whether the Datum instance is compatible with indicated units – `compatible_unit`. The method

- Checks whether the `other` parameter is an instance of `Datum`, `Quantity`, `str`, or `pint.Unit`. Otherwise, raises `TypeError`.
- If the parameter is an instance of `str`, and it obeys the [[patterns|rules]] of units-defining strings, but defined an unknown unit, raises `UndefinedUnit` exception
- If the parameter is an instance of `str`, and the string is malformed, raises `InvalidUnitExpression` exception
- Returns `True` if the units are compatible, otherwise returns `False`.

### Converters
Datum instances are immutable (see [[Datum#Invariants|invariants]]), but there are two methods that are shortcuts for the following code in python:
```python
# instead of
d = Datum('v = 10 m/s')
newq = d.quantity.to('km/h')
d = Datum.from_quantity(newq, d.variable)
# use
d = Datum.to('km/h')

# instead of
d = Datum('v = 10 m/s')
val = d.value / 2
d = Datum(f'{d.variable} = {val} {d.units}')
# use
d = Datum.scale(0.5)
```

Hence the method behaviour.

#### to
The `to` method converts units of the Datum instance to the units indicated.

- Checks that the type of the `units` parameter is either `str` or `pint.Unit`. Otherwise, raises `TypeError`.
- If the parameter is an instance of `str`, and it obeys the [[patterns|rules]] of units-defining string, but defines an unknown unit, raises `UndefinedUnit` exception
- If the parameter is an instance of `str`, and the string is malformed, raises `InvalidUnitExpression` exception
- If the units cannot be converted to one another, raises `IncompatibleUnits` exception
- returns a Datum instance converted to the new units
-  returns a new Datum with a new `dds` property (see [[Datum#Properties|properties]])
- returns a new Datum with changed `quantity`, `value`, and `units` properties

#### scale
The `scale` method allows to change numerical value of Datum without writing full redefinition.

- Checks that the `factor` parameter is an instance of `float` or `int`, otherwise raises `TypeError`.
- In case `factor` is `nan`,  `inf`, or `-inf`, raises `ValueError`
- Returns a Datum instance with value equal to the old value multiplied by `factor`

## Properties
The properties provide access to the most important Datum attributes such as variable, value, unit and some others. NOTE: to access details about the dds, use `.dds` property. To access all the same properties of a Datum converted to its base units, use `.base` property.

### `quantity` property
- Returns a `pint.Quantity` that Datum currently possesses (value multiplied by units)
- Changes if value or units of Datum change

### `variable` property
- The `variable` property just copies the `dds.variable` property.

### `value` property
- The `value` property just copies the `dds.value` property.

### `units` property
- Returns the value of `dds.units`, but parsed with the UnitRegistry specified in `spec` attribute

### `base` property
The `base` property returns a Datum instance converted to respective base units.

- Returns a Datum instance converted to base units
- If the original Datum instance was already in base units, returns a new Datum equal to the old one

**Note**: yes, you can do it `self.base.base.base.base. ...`

### `dds` property
The `dds` property returns a DatumDefString object with respective values.

- Returns a `DatumDefString` object
- The DDS is created during initialization from the provided data

## Errors
The structure of exceptions used in Datum class is the following. Some of the exceptions are also used in [[AbstractDDS]] class.

```
DatumException  
├── SymbolException  
│   ├── SymbolSympyUnsafe
│   └── InvalidVarName
├── UnitsException
│   ├── IncompatibleUnits
│   ├── UndefinedUnit
│   └── InvalidUnitExpression
└── InvalidDatumDefString
```

## Invariants

- Neither of the actions change any of the properties of the same Datum instance (Datum instances are immutable)
- DDS from the `.dds` property always represents up-to-date value and units (i.e. it changes after value or units were changed)
- `d.quantity == d.value * d.units`

The following expressions must always be True
- `d.compatible_units(d.base.units)`
- `d.compatible_units(d.base)`
- `d.compatible_units(d.base.quantity)`
- `d.compatible_units(d.units)`
- `d.compatible_units(d.quantity)`
- `d.compatible_units(d)`
- `d.compatible_units(d.dds.units)`
- `d.compatible_units(d.base.dds.units)`

- `d.dds.value == d.value`
- `d.dds.variable == d.variable`
- `d.units == d.spec.ureg.parse_units(d.dds.units)`

```python
dds = 'm = 5 kg'
d1 = Datum(dds)
d2 = Datum(d1.dds)

d1.dds == d2.dds == dds  # NOT TRUE!
d1 == d2
d1.base.dds == d2.base.dds
```

```python
d1 = Datum('v = 5 m/s')
d2 = Datum.from_quantity(d1.quantity, d1.variable)

d1.dds == d2.dds
d1 == d2
d1.base.dds == d2.base.dds
d1.quantity == d2.quantity
```

```python
d1 = Datum('v = 5 m/s')
d2 = d1.scale(5)
d3 = d2.scale(1/5)
d1 == d3 is True
```

```python
d1 = Datum('v = 5 m/s')
d2 = d1.to('km/h')
d3 = d2.to('m/s')
d1 == d3 is True
```

```python
d = Datum('m = 15 g')
d.unit == d.spec.ureg.parse_units('g')  # raises no exception, i.e. d.units always belongs to the Datum's UnitRegistry
d.quantity == d.spec.ureg('15 g')  # same for d.quantity
```

## Use cases
The Datum class can be used represent named quantities and perform arithmetical operations on them. The code below shows several use cases.

```python
from QCalculator import Datum


v = Datum('v = 40 km/h')
d = Datum('d = 10 km')

# computing a new quantity
'''Since arithmetics creates a new quantity, either of the symbols cannot be directly assigned to the resulting quantity. That is why .from_quantity method is used to assign a new symbol to the quantity and turn it into Datum.'''
qt = d.quantity / v.quantity
t = Datum.from_quantity(qt, 't')
print(t)
# 't = 0.25 h'

# Converting Datum to base units
'''.base property is a Datum instance where units were converted to pint.Quantity's base units.'''
print(v.base.unit)
# <Unit('meter / second')>

print(v.base.quantity)
# <Quantity(11.1111111, 'meter / second')>

# Getting most important properties
d = Datum('m = 15 kg')
print(d.symbol)
# 'm'
print(d.value)
# 15.0
print(d.unit)
# <Unit('kilogram')>
print(d.dds.unit)
# "kg"

# Converting to other units
d = Datum('m = 15 kg')
newd = d.to('g')
print(newd)
# 'm = 15000 g'

other_d = d.scale(2)
print(other_d)
# 'm = 30 kg'

# Defining Datum from separate variables
var = 'm'
val = 15
u = 'kg'

d = Datum(f'{var} = {val} {u}')
print(d)
# 'm = 15 kilogram'
```
