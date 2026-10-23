# About Quantity Calculator 

This document presents overview of the Quantity Calculator project.

# Features
- Iteratively solves a system of (linear) equations
- Has a custom class for keeping and managing variable's symbol, magnitude and units in one instance
- Allows to search for a specific target through the system of equations, and optionally stop when the target is found
- Uses both sympy and pint packages to solve the equations while taking care of units

## Description
Quantity Calculator is a small Python package that can be used to solve many linear equations iteratively at once. That means, the code can run through a system of equations, record the obtained results, and run the system again. The system stops either when a target variable is found, or when all the possible variables are found. The process automatically takes care of units and performs checks for unit consistency.

This approach is very useful if many equations depend on each other and as many as possible variables need to be found from a given set of conditions. See more in LINK1 use cases.

## Structure
The package is built around three main classes: ```Datum```, ```Formula``` and ```LinearIterator```. This section discusses each class briefly to provide an idea of what each class is used for.

### Datum
Datum class is used to manage pint.Quantity and the symbol linked to a variable in one place. An instance of it is created by specifying three important quantities: variable's symbol (such as "m" or mass, "v" for velocity, etc.), magnitude in a form of integer or float, and he units in a form of a string or pint Unit. To make initiation simpler, Datum accepts a single string, called *datum definition string* (further – DDS), which is a native Python string built according to specific rules. A typical DDS looks like `m = 5 kg` with `m` being variable's symbol, `5` – magnitude, and `kg` – units. The exact rules that all DDS's must obey are listed in the `DatumDefString` class' contract file. LINK1

For example
```python
from QCaluator import Datum

v = Datum('v = 3.6 m/s')
print(v.to('km/h'))
'v = 12.96 km/h'

v_new = v.scale(2)
print(v_new)
'v = 7.2 m/s'
```

For arithmetical operations Datum's `quantity` property should be used. 

### Formula
```Formula``` class joins several ```Datum``` instances into one formula, such as 
```F=m*a```, ```S=v*t```, or ```p*V=n*R*T```. Each variable in a formula is linked 
to an individual ```Datum``` class. The Formula class makes it possible to evaluate the 
missing variable if all the others are given, and detect whether an equation of this 
formula is solvable (=if one variable is missing). The simplest use examples is given below:

```python
from QCalculator import Formula

f = Formula('n = mps/M')
f.write(
    'mps = 36 g',
    'M = 18 g/mole'
)
f.target = 'n = 0.01 mole'  # the number of decimal places specifies rounding
result = f.solve()  # returns a set of Datum instances

print(*result)
```

The output will be

```commandline
n = 2.0 mole
```

The ```.solve()``` method does not write down any variables. Hence, to store the obtained result, the
```.write()``` must be explicitly called. That allows to use ```Formula``` instances in two
ways:

- Single-use as shown here (the obtained result can be then written down)
- Iterative use, when the same target is found repeatedly with different data written in (the old data are erased by ```.earse()``` method)

### LinearIterator
Finally, the LinearIterator class takes a set of equations and Datum instances. 
It writes the Datums into each ```Formula``` where respective variable is present and 
then iteratively solves the system accumulating more and more avaiable variables 
(generating new ```Datum``` instances) up to the point when no more ```Datums``` can 
be generated.

Again, a simple example is given below.

```python
from QCalculator import LinearIterator

formulas = [
    'n = mps/M',
    'n = Vpg/V0',
    'n = Np/NA',
    'wmm = mps/msm',
]

data = [
    'wmm = 0.12',  # mass fraction of a substance in a mixture
    'msm = 20 g'  # mass of the mixture
    'M = 18 g/mole'  # molar mass of the substance
    'NA = 6.02e23 mole**-1'  # Avogadro's constant
]

units = {
    'n': 'mole',
    'mps': 'g',
    'M': 'g/mole',
    'Vpg': 'L',
    'V0': 'L/mole',
    'Np': '',
    'NA': 'mole**-1',
    'wmm': '',
    'msm': 'g'
}

li = LinearIterator(formulas, units)
li.target = 'Np = 0.001'
result = li.solve()
print(*result)
```

With these formulas and initial data, Linear Iterator can follow that path:

- ```wmm, msm -> mps```
- ```mps, M -> n```
- ```n, NA -> Np```

If we now set the ```Np``` as target.

```python
li = LinearIterator(formulas, units)

li.write(*data)
li.target = 'Np = 0.001'

result = li.solve()

print(result)
```

The result is

```commandline
Np = 8.026666666666678e+22 dimensionless
```

Even though it was not possible to find directly in a single iteration.

**NOTE**: To solve for _all_ possible variables, do not specify the target of Linear Iterator. 

# Notes
If you ever found bugs or ways to improve the code, feel free 
to contact the author.
