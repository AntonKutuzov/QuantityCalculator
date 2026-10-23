## Scope
The `Formula` class is used to express a mathematical relation between several Datums. It is based on `sympy` and allows to solve numerically and symbolically simple equations. Moreover, `Formula` allows to automatically filter obtained solutions (although this must be done with care). The class handles units as well as numerical values since it is built to work with Datums.

`Formula` supports work with [[Datum Definition String and DatumDefString class|DatumDefString]] and [[Datum class|Datum]], but it also can be used entirely with strings. The strings are automatically converted to necessary types.

`Formula` represents exactly **one** relationship and once created the expression in the instance cannot be changed. For work with several Formulas see [[LinearIterator class]].


## Public API
```python
class Formula:
	"""
	All values in Formula are stored in the respective base units (determined via Datum.base property). The .read() method therefore returns only the base units. Convertion of units can be done on the returned object.
	"""
	
	filters.
		REAL_ONLY
		POSITIVES
		NEGATIVES
		NON_NEG
		NON_POS
		ZERO
		NO_FILTER
	
	DEF_UNITS: Optional[Dict[Tuple[str, ...], str] | Dict[str, str]] = None
	UNIT_BY_SYMBOL: bool = True
	
	
	def __init__(
		formula: str,
		*,
		def_units: Optional[Dict[Tuple[str, ...], str|Unit] | Dict[str, str] = None
	) -> None
	
	
	# magic methods
	def __contains__(item: str | Datum | DatumDefString) -> bool
	
	def __str__() -> str
	
	def __eq__(other: Formula) -> bool
	
	# read, write, erase
	def write(
		*dds: Datum | DatumDefString | str,
		rewrite: bool = False
	) -> None
	
	def read(*var: str, force_list: bool = False) -> Datum | Tuple[Datum]:
	
	def erase(*var: str) -> None
	
	
	# checkers
	def is_consistent(silent_missing_value_error: bool = True) -> bool
	
	def has_value(*var: str, force_list: bool = False) -> bool | List[bool]
	
	
	# evaluate, solve
	def eval_symbolic() -> List[sp.Eq]
	
	def eval_numeric(*filters) -> List[sp.Eq | float]
	
	def solve(
		*filters,
		auto_determine_unknown: bool = True,
		round_to: int = 15,
		units: Optional[str] = None
	) -> List[Datum]
	
	
	# getters
	def default_units(var: str) -> Optional[str]
	
	def unknown(
		round_to: int = 15,
		units: Optional[str] = None,
		var_only: bool = False
	) -> str
	
	
	# properties
	def min_num_decimals -> float
	
	def solvable -> bool
	
	def all_values -> bool
	
	def data -> List[Datum]
	
	def variables -> List[str]
	
	def eq -> sp.Eq
	
	def target -> Optional[Datum]
	
	@setter
	def target(datum: Datum | str | DatumDefString | None) -> None
```


## General class structure
The class is build to serve a single mathematical relationship. It uses external functions defined in the [[_util file]], such as
- validate_type
- validate_match
- unpack_keys
For more see the respective file.

Before reading this section, look at the [[Formula class#Usage examples|use examples]] of `Formula` to grasp the idea of how it is supposed to be used.

The class is build around a single sympy Eq instance, which represents the relation between several `Datum` instances. In general the use strategy is the following:
- Define `Formula`
- Write the necessary data
- Evaluate numerically or symbolically, or solve (see precise meanings in respective section)

Hence, the class is divided into the following sections:
1) Constructor
2) Input and output of data
3) Evaluation, solving
4) Checkers
5) Properties

### Input and output of data
The `Formula` class allows to write, read and erase data which always are instances of Datum or are compatible with Datum (i.e. are either a DDS or a respectively formatted string).

#### Definition of "piece of data"
In this document by "piece of data" we call a named physical quantity, same as in [[Datum class]] document. Hence, piece of data can be defined via Datum, DatumDefString or plain (properly formatted) str. In case `str` is used, it must always be checked to comply with DDS rules for defining valid "pieces of data".

When we say that two pieces of data are equal in this class, we mean *that the base Datums of the two pieces of data are equal.* Note that this is difference from equality of two Datums in general, which is more strict. Basically, equality of two pieces of data means the following:

```python
pod1 = 'm = 0.05 kg'
pod2 = DatumDefString('m = 50 g')

d1 = Datum(pod1)
d2 = Datum(pod2)

d1.base == d2.base
True
```

#### Units
To make the code easier, the following requirements are implied regarding units
- The class always stores obtained quantities in their base units
- The class always performs all calculations with the quantities in their base units
- Unit conversion takes place only right after writing data or when reading

Since the `solve` method can decide itself what the unknown variable is, it also needs to determine the units of the unknown variable. To do this, a dictionary of default units is implemented **both on the instance and class level**. The dict is accessed whenever units of the unknown variable are necessary. The dict can be provided directly to the instance, to the class, or can be omitted. The following must be always true
- Instance-level dict has higher priority over class-level dict and hence, if present, is used regardless of whether class-level dict is present
- Class-level dict is used only when instance-level dict is None
- If neither of the dicts is present (both are None), respective exceptions are raised when the code tries to determine the units of the unknown variable

To make it faster to define default units, the keys with the same units may be combined in a single key of type `Tuple[str]`. It is then unpacked by using `unpack_keys` function. Note: it must be exactly tuple, not list or set.

#### Parsing the DatumDefString
Apart from writing data, it may also be necessary to define `target` attribute. This attribute determines which variable such methods as `eval_numeric`, `eval_symbolic`, and `solve` are looking for (`solve` can determine unknown variable automatically). The attribute can be set in the following way
```python
f = Formula('n = m/M')
f.target = 'm = 0.001 g'
```
Here variable of the DDS is the target variable that we will search for, the value indicates the number of significant digits to which the final result is rounded, and units indicate final units.
NOTE: `eval_numeric` does not round the result. `solve` does, and if rounding is unnecessary either write the 15 digits in the DDS, or avoid explicitly setting the target and rather specify target units in the default units dict.

#### Default unit dict and UNIT_BY_SYMBOL
Sometimes it is necessary to use formulas like
$$\frac{p_1V_1}{T_1} = \frac{p_2V_2}{T_2}$$
In this case we understand that $p_1$ and $p_2$ have the same units, because they are the same quantity – pressure. To make it easier to define units in such cases, `UNIT_BY_SYMBOL` was implemented.
- When `True`, the class requires the default unit dict to contain strings that match `symbol` as defined in `DatumDefString` class. When units are determined by `solve` or any other method, they use only `symbol` part of the variable to search for units in the dict. That way, specifying units for `p` as `kPa` will give the units for both `p_1` and `p_2`.
- When `False`, the default unit dict may contain full `variable` strings. The `solve` method and the like search in the dict for the full variable name, not only `symbol` part.


### Checkers
There are several checkers. They are all discussed in their respective methods.

### Solvers
The three methods that can solve internal sympy.Eq and return a result are
- `eval_symbolic`
- `eval_numeric`
- `solve`

`eval_symbolic` just rearranges the equation and returns the result. If sympy's solve cannot do this, the `eval_symbolic` cannot as well.

`eval_numeric` takes all the written data of `Formula` class (all the Datums) and substitutes into the sympy.Eq. It is not necessary to have all values. In such a case `eval_numeric` will just return an equation with less variables. In case all variables were present, it returns a `float`.

Both methods above require `target` to be explicitly set.

`solve` method wraps `eval_numeric`, but instead of raw sympy.Eq or `float` it returns a list of Datum instances. `solve` requires that the equation is solvable, i.e. that all variables except the target have a value. Hence, `solve` can automatically determine the target.

#### Filters
The `Formula` class has a set of builtin filters used by `eval_numeric` and `solve` to filter out unnecessary solutions. E.g. filter `REAL_ONLY` will make the functions return only real results by filtering out complex numbers. For example

```python
f = Formula('y = -2*x**2 + 3*x + 6')  
f.write('y = 0')  
f.target = 'x = 0.1'  
  
print(*f.eval_numeric())
-1.1374586088176875 2.6374586088176875

print(*f.eval_numeric(Formula.filters.POSITIVES))
2.6374586088176875
```

**NOTE**: *use of filters may cause errors. For example, if the root is complex and `POSITIVES` filter is used, it may cause an error, because complex number cannot be classified as positive or negative (in a sense as real numbers can)*

Finally, filters are a class attribute and must always be accessed via `Formula.filters.<FILTER>` notation, **not via instances** (such as `f.filters.<FILTER>`). This causes exceptions and should not be done.


## Methods
### Constructors
#### `__init__`
```python
	def __init__(
		formula: str,
		def_units: Optional[Dict[Tuple[str, ...], str|Unit] | Dict[str, str] = None
	) -> None
```
	
The constructor accepts a string defining the formula and, optionally, the [[Formula class#General class structure#Units|instance-level default unit dict]]. The method does the following

- Checks the type of 'formula' parameter to be an instance of `str`
- If any key in default unit dict is not `str` or `Tuple[str]`, raises `TypeError`
- If any value in default unit dict is not `str`, raises `TypeError`
- Converts the string to the sympy.Eq, which is then accessible via `eq` property
- In case conversion fails, raises `InvalidFormula` exception
- Chooses appropriate default unit dict (see the link above for the rules)
- Normalizes the default units, i.e. (if the dict is not None)
	- Replaces spaces and empty strings with 'dimensionless'
	- If `UNIT_BY_SYMBOL` is `True`, checks that all keys in the dict match with `DatumDefString.patterns.symbol`
	- If `UNIT_BY_SYMBOL` is `False`, checks that all keys in the dict match with `DatumDefString.patterns.variable`

### Magic methods
The following magic methods are defined for `Formula` class
- \_\_str__
- \_\_contains__

**NOTE**: be careful with`__contains__` since its behaviour is tricky.

#### \_\_str__
The `__str__` method returns a string of the form "LHS = RHS". The equation must obey the following properties:
- No spaces between variables and arithmetic symbols
- One space on both sides of the equal sign
- No leading or trailing spaces

It must always hold that (see also invariant section)
```python
f1 = Formula('n = m/M')
f2 = Formula(f1.__str__())

assert f1 == f2
True
```

#### \_\_contains__
```python
def __contains__(item: str | Datum | DatumDefString) -> bool
```
The behaviour of the `__contains__` method depends on the type of `item` parameter.
- In case `item` is an instance of str, the method checks whether the variable indicated by `item` is present among the variables of the `Formula` instance.
- In case `item` is an instance of `Datum` or `DatumDefString`, the method checks whether *a piece of data* indicated by `item` is present in the internal data list.

For example,
```python
f = Formula('n = m/M')  
  
m_str = 'm = 5 g'  
m = Datum(m_str)  
m_dds = DatumDefString(m_str)
M_dds = DatumDefString('M = 0.04 kg/mole')
  
v = 'm'  
  
f.write('m = 10 g', 'M = 40 g/mole')  
  
print(m_str in f)
False  # because m_str does not represent a variable (such as 'm' or 'n')
print(m in f)
False  # because 'm = 10 g', not 'm = 5 g' was written to f
print(m_dds in f)
False  # because 'm = 10 g', not 'm = 5 g' was written to f
print(v in f)
True   # because variable 'm' is present in the Formula f
print(M_dds in f)
True   # because the piece of data for 'M = 40 g/mole' is present in f
```

The method thus
- Checks the type of `item`. If not one of the types indicated in the signature, raises `TypeError`

- IF type of `item` is `str`:
	- Checks that `item` matches with `DatumDefString.patterns.variable`. If not, raises `MatchError`
	- Checks that the variable indicated by `item` is present among the variables of `Formula` instance. Returns a boolean value: True is present, False if not.

- IF type of `item` is `Datum` or `DatumDefString`:
	- Checks if the piece of data is present in the `Formula` instance (see [[Formula class#Definition of "piece of data"|the definition of "piece of data"]] for exact condition of equality).
	- Returns a boolean value: True if present, False if not.

### Input and output of data
The input and output section contains three methods
- read
- write
- erase

#### Write
```python
def write(
	*dds: Datum | DatumDefString | str,
	rewrite: bool = False
) -> None
```

The `write` method accepts arbitrary number of pieces of data and **to each** does the following:
- Checks type of each piece of data to be `Datum`, `DatumDefString` or `str`. If not, raises `TypeError`
- Checks type of `rewrite` to be `bool`. If not, raises `TypeError`
- Converts the piece of data to respective base `Datum` instance
- If `rewrite` is `False`
	- If the variable already has a value, [[Formula class#Exceptions|raises]] `RewritingError`
	- If the variable does not have a value, appends the Datum instance to the internal data list
- If `rewrite` is `True`
	- Erases the old value if present
	- appends the Datum instance to the internal data list
- If default units are specified,
	- Checks that the units of the written `Datum` are compatible with the default units for that variable/symbol (choice depends on the value of `UNIT_BY_SYMBOL` flag). If units are not compatible, raises `IncompatibleUnits` error. The value then is **not** written.


#### Read
```python
def read(
	var: str | List[str]
) -> Datum | Tuple[Datum]:
```

The `read` method is overloaded to make it possible reading one variable or several at a time. Depending on whether a single variable or a collection of them was given to the method, it returns a single Datum or a tuple of Datum instances respectively. 

In case the type is `List[str]`,  the method just applies itself to each element of the list separately and collects the responses into a tuple which is then returned.

If case the type is `str`, the method does the following:
- Tries to match `var` with `DatumDefString.patterns.variable`. If no match, raises `MatchError`
- Checks that the variable `var` is present in the `Formula` instance. If not, raises `VarNotFound`
- In case the variable does not have a value yet (the respective Datum instance has not been written), raises `ValueError`
- In case a duplicate is found (more than one Datum instance with exactly that variable), raises `DuplicateFoundError`
- Returns the Datum instance in its base units[^1]

[^1]: It should not be implemented in the method itself, but rather in the `write` method. However, this is a good invariant to check

#### Erase
```python
def erase(*var: str) -> None
```
The `erase` method removes one or more variables from the internal data list. The default value for `var` is intentionally not given so that it is harder to accidentally erase all variables (which the default value formerly was used for).

For each provided variable the method
- Checks the type to be `str`
- Tries to match `var` with `DatumDefString.patterns.variable`. If no match, raises `MatchError`
- Checks that the variable `var` is present in the `Formula` instance. If not, raises `VarNotFound`
- In case the variable does not have a value yet (the respective Datum instance has not been written), raises `ValueError`
- In case duplicates are found, erases all of them and throws a warning saying that more than one variable was erased
- Removes the (found) variable(s) from the internal data list


### Checkers
The checkers are methods that returns a Boolean value stating some important information about the state of the instance. The methods are
- has_value
- is_consistent

The `has_value` checks that an indicated variable has a value written in the internal data list. The `is_consistent` method checks that the written values are consistent with the relation specified by the formula. That is, in case *all* variables have values, it is possible that the equation does not hold (since the values can be arbitrary). To check that it *does* hold, `is_consistent` is called.

#### has_value
```python
def has_value(var: str | List[str]) -> bool | Tuple[bool]
```

The method accepts either a `str` or a `List[str]`. In case a list of obtained, the method applies itself to each string separately. The method

- Checks the type of `var`. If not `str` or `List[str]`, raises `TypeError`
- If `List[str]` is obtained, applies itself to each string individually, and then returns the results in a form of a tuple
- If `str` is obtained
	- Tries to match it with a `DatumDefString.patterns.variable`, if not match, raises `MatchError`
	- if variable is not present in the `Formula` instance, raises `VarNotFound` error
	- If multiple values are found, raises `DuplicateFoundError`
	- Returns `True` or `False`, depending on whether the value for that variable is written to `Formula` instance

#### is_consistent




## Warnings and Exceptions
Exceptions
- RewritingError
- MatchError
- VarNotFound
- DuplicateFoundError
- InvalidFormula
- IncompatibleUnits

Warnings
- MultipleVarsErased

## Usage examples
```python
Formula.DEF_UNITS = {'p': 'Pa', 'V': 'm**3', 'n': 'mole', 'R': 'J/mole/K', 'T': 'K'}  
Formula.UNIT_BY_SYMBOL = True  
  
f = Formula('p*V = n*R*T')  
f.write(  
    'p = 101.325 kPa',  
    'R = 8.31 J/mole/K',  
    'n = 1 mole',  
)  
  
Ts = [i*10 for i in range(11)]  
  
for T in Ts:  
    f.write(f'T = {273+T} K', rewrite=True)  
    print(T, ':\t', *f.solve(round_to=3, units='L'))  
  
f2 = Formula('p_1 * V_1 / T_1 = p_2 * V_2 / T_2')  
  
f2.write(  
    'p_1 = 101.325 kPa', 'T_1 = 273 K', 'V_1 = 22.4 L',  
    'p_2 = 300 kPa', 'V_2 = 10 L'  
)  
  
print(*f2.solve(round_to=1))
```

