This file contains description of the helper functions used throughout the module. The following functions are present in the file:

```python
validate_type(check_vars: Any, check_types: type|Tuple[type, ...]) -> None

validate_types(check_vars: List[Any], check_types: List[type|Tuple[type,...]]) -> None

must_match(
    pattern: Literal['symbol', 'variable', 'value', 'units', 'dds', 'other'],
    string: str | int | float,
    custom_pattern: Optional[Pattern] = None
) -> Match

unpack_keys(d: Dict[Tuple[Any, ...] | Any, Any]) -> Dict[Any, Any]

check_unit_validity(cls, unit: str|Unit) -> None

check_sympy_safety(symbol: str) -> None
```

All checker functions return `None` which means they raise exceptions if the check is failed, and do nothing if the check was passed.

## validate_type and validate_types
`validate_type` and `validate_types` are functions that raise `TypeError` in case provided variable(s) is not an instance of one of the provided classes. The functions are written to avoid multiple hard-coded type checks.

`validate_type` checks type of a single variable. `check_types` can be a tuple of types and in this case the variable can belong to any of the provided types.

`validate_types`, however, is capable of checking several variables at once being instances of different classes. Here the choice of collection (list or tuple) matters. Since several variables can be checked, even a single variable is given in a list[^1]. Depending on how types are provided, the function behaves in two different ways:
1) If type is simply a member of a list, then it corresponds to the variable in variable list that is on the same position. I.e. if variable list contains three variables, then there must be three types in the type list, each belonging to respective variable based on position.
2) If instead of a type a tuple of types is given inside a type list, the function checks a single variable to be an instance of either of all types from the tuple.

For example, in the first case variables `a`, `b`, and `c` must be integers, while variables `d` and `e` – strings.
```python
vars = [a, b, c, d, e]
types = [int, int, int, str, str]

check_types(vars, types)
```

For the second mode consider this example
```python
vars = [a, b, c, d, e]
types = [int, (int, float), (int, float, str), str, str]

check_types(vars, types)
```

In this case variable `a` must be an integer; variable `b` – either an integer, or a float; variable `c` can be int, float or string. Variables `d` and `e` must be strings.

Obviously, lengths of both lists must coincide. In case this is not the case, a `ValueError` is raised.

In case either of variables is not a list, `TypeError` is raised.

[^1]: Note that giving a plain string to this function will result in treating this string as a collection of symbols, which is not what we want.


## must_match
This function checks whether the provided string matches with a pre-set pattern (custom pattern is also possible). The function uses regexs from [[patterns]] file and fullmatch from re module. The function returns a Match object in case the string matched.

In the case `pattern` is set to `other`, and `custom_pattern` is still `None`, raises `ValueError`. If `pattern` is not among specified values, and if there is no match – also `ValueError`.

## unpack_keys
This function is used to compactly write dicts where several keys have the same value. The function turns `dict1` into `dict2`.

```python
dict1 = {
	(1, 2, 3): 'a',
	(4, 5): 'b',
	6: 'c'
}

dict2 = {
	1: 'a',
	2: 'a',
	3: 'a',
	4: 'b',
	5: 'b',
	6: 'c'
}
```

In case the function does not receive a dict, raises `TypeError`.

## check_unit_validity
This function tries to parse units by using UnitRegistry of the provided class. It maps all pint errors onto `InvalidUnitsExpression` and `UndefinedUnits`. The function raises `TypeError` if receives neither a `str`, nor a `pint.Unit`.

## check_sympy_safety
There are several symbols in sympy that are reserved and cannot be used in expressions, for example 'N' and 'S'. The function checks if the symbol is one of these, and raises `SymbolSympyUnsafe` exception.

