from re import compile


# defining variable
symbol_str = r'(?P<symbol>[a-z]|[A-Z]+)'
subscript_str = r'(?P<subscript>[a-zA-Z0-9]+)'
variable_str = fr"(?P<variable>{symbol_str}(_{subscript_str})?)"

# defining value
whole_str = r'-?(?P<whole>\d+)'
decimal_str = r'(?P<decimal>\d+)'
exponent_str = r'(?P<exponent>[-+]?\d+)'
value_str = fr"(?P<value>{whole_str}(\.{decimal_str})?((E|e){exponent_str})?)"

# defining units
units_str = r'(?P<units>[^\s][a-z]*(.*[^\s])?)'

# general
# default arbitrary group
dag_str = f'.*'  # any number of any characters (except the newline)


# the compiled patterns
symbol = compile(symbol_str)
subscript = compile(subscript_str)
variable = compile(variable_str)
whole = compile(whole_str)
decimal = compile(decimal_str)
value = compile(value_str)
units = compile(units_str)
dag = compile(dag_str)
