```python
class DatumDefString(AbstractDDS):  
    _DDS_pg = PatternGenerator(('', ' +', ' +', ' +', ''))  
    spec = DSpec(_DDS_pg.pattern, sympy_safe=True)  
	  
	# properties
    def whole(self) -> int
    def decimal(self) -> float 
    def sign(self) -> Literal[1, -1] 
    def exponent(self) -> int
    def num_decimals(self) -> int 
    def string(self) -> str
```

DatumDefString inherits from [[AbstractDDS]], and hence retains all its methods. In addition, several properties are added.

DatumDefString uses the pattern specified above as well as is sympy safe. The other spec values are defaults.

Since the class does not introduce new methods (only properties), no new exceptions are needed.

## Class' attributes
The DatumDefString adds several properties to the AbstractDDS – the ones responsible for parsing the numerical value. See [[Datum definition string]] for what the properties must return.
- The properties `whole` and `decimal` return the match obtained from the `match` property, but converted to the necessary Python's data type.
- The `exponent` property returns the number, or 0 if exponent match is None
- The `num_decimals` property returns the number of significant digits after the decimal point in the given value

The `string` property is an abstract property of `AbstractDDS`, and returns in this case the following string: `f'{self.variable} = {self.value} {self.units}'`, i.e. exactly one space between each inserted value.


## Invariants
New properties also introduce new invariants.

```python
value = dds.value
composed = dds.sign * (dds.whole + dds.decimal) * 10 ** dds.exponent
math.isclose(value, composed, abs_tol=1e-15)
```

```python
dds.value * dds.sign >= 0.0
```

```python
dds.whole >= 0
```

```python
0.0 <= dds.decimal < 1.0
```

```python
dds.num_decimals >= 0
```
