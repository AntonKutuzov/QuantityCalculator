# About Quantity Calculator 

**TABLE OF CONTENTS**
- [Features](#features)
- [Applications](#applications)
- [Principle of work (Example)](#principle-of-work-example)
- [Notes](#notes)


# Features
- Iteratively solves a system of linear equations
- Has a custom class for keeping variable's symbol, value and units in one instance
- Allows to search for a specific target through the system of equations, and stop when the target is found
- Uses both sympy and pint packages to solve the equations, taking care of units

## Description
Quantity Calculator is a small Python package that can be used to solve many linear equations iteratively at once. That means, the code can run through a system of equations, record the obtained results, and run the system again.

This approach is very useful if many equations depend on each other and as many as possible variables need to be found from a given set of conditions.

The package's main part is LinearIterator class which takes in the values for all the variables, automatically writes them down in the equations, and solves for a specific target. 

## Structure
The package consists of three main classes: Datum, Formula and LinearIterator. The three classes form three layers at which we can present the data.

Datum class stores and allows to modify individual variables. An instance of it is created by specifying three important quantities: variable's symbol (such as "m" for mass, "v" for velocity, etc.), value in a form of integer or float, and the units in a form of a string. The class then allows to convert the quantity into different units (using pint inside the class). It also supports multiple arithmetic operations with other Datum instances, pint quantities and native Python integers or floats.

Formula class joins several Datum instances into one formula, such as F=ma, S=vt, or pV=nRT. Each variable in a formula is linked to an individual Datum class. The Formula class makes it possible to evaluate the missing variable if all the others are given, and detect whether an equation of this formula is solvable (=if one variable is missing).

Finally, the LinearIterator class takes a set of equations and Datum instances. It writes the Datums into each Formula where respective variable is present and then iteratively solves the system accumulating more and more avaiable variables (generating new Datum instances) up to the point when no more Datums can be generated.

Formula also allows to stop at a certain (preset) target Datum, without solving the equations to the very end, if the target is already obtained.

Since both Formula and linearIterator store multiple instances of lower-level classes, they all can be accessed and managed via respective methods.

# Applications
The Quantity Calculator package can be used to solve any kind of linear system with more than one iteration (otherwise, sympy is simpler and more powerful to use).

The author of the code used this package in a larger project called [miniChemistry](https://github.com/AntonKutuzov/miniChemistry2). The code is used there to iteratively solve the typical equations for chemistry (such as C=Vn, n=m/M, etc.) and thus obtain the value of n (number of moles) which is crucial in all stoichiometric calculations in chemistry.

# Principle of work (Example)
The code below gives an idea of how this module is used in the miniChemistry project to derive the number of moles (n) from any other variable without manually solving multiple equations.

For example, we need to convert molar concentration (C) into mass fraction (conventionally omega, but here it's "w"). We don't have a specific formula for this, however we have many typical formulas from chemistry that technically allow us to do this. Below is a short explanation of how this is done by hand.

### Solution by hand
Molar concentration (C) is expressed in moles per liter. We calculate it according to
$$C = n/V_{sm}$$
Where $V_{sm}$ is volume of the solution (sm stands for "solid mixture", which is required for miniChemistry project. The name of the variables can indeed be arbitrary)

To find mass of the solution, we can use the formula for density (given that we have its mass)
$$p_{sm} = m_{sm}/V_{sm}$$
Next, we can find the mass of pure substance by using $m_{ps} = n*M$ (where $M$ is molar mass), and the mass fraction from
$$\omega = m_{ps}/m_{sm}$$
So, in total we use four formulas one after another. In a more complicated case we might need to perform some calculations parallel to each other. Solution with the code makes it much easier.

### Solution with Quantity Calculator

The code is purely illustrative, so all irrelevant equations were not added, however they can be present.

The "add_formula" and "add_variable" functions are needed to define the set of formulas, and indicate variable's units.

```Python
from QCalculator import LinearIterator, Datum
from QCalculator.database import add_formula, add_variable
from QCalculator._settings import SETTINGS


SETTINGS['COMMENTS ON'] = True  # if set to True, each major actions will be presented in the console. False by default

# FORMULAS
"""
The names of the variables are given in such a way to distinguish different substances: pure substance is dissolved
and the solution. The "-ps" part stands for "pure substance", the "sm" for "solid mixture". You can ignore the word
"solid" as it is needed for the miniChemistry project, and the author decided not to change the naming.
"""
add_formula('n - mps/M')
add_formula('psm - msm/Vsm')
add_formula('w - mps/msm')
add_formula('C - n/Vsm')

# VARIABLES
"""You don't need to explicitly define variables that will be given in your data as Datum instances."""
add_variable('n', 'mole')
add_variable('mps', 'g')
# add_variable('msm', 'g')
# add_variable('M', 'g/mole')
add_variable('w', 'dimensionless')
add_variable('Vsm', 'L')
# add_variable('C', 'mole/L')


# DATA in the form of Datum instances
C = Datum('C', 1, 'mole/L')
psm = Datum('psm', 1, 'g/mL')
msm = Datum('msm', 100, 'g')
M = Datum('M', 58.5, 'g/mole')

# WRITING DATA IN
li = LinearIterator()
li.write(C)
li.write(psm)
li.write(msm)
li.write(M)

# SELECTING THE TARGET
"""The target is indicated as a Datum instance, ASSIGNED to a .target property of a LinearInterator instance.
The symbol, value and units of the Datum instance specify respectively the target variable, the number of significant
digits that the result will be rounded to (is needed), and the units in which you want to get the answer."""
li.target = Datum('w', 0.01, 'percent')

# SOLVING THE EQUATIONS
"""The "stop_at_target" parameter interrupts the process as soon as the target variable is found. Recommended to set to
True in searching for a specific variable, like we do here. The "alter_target" parameter alters the .target property
of LinearIterator instance if set to True. The "rounding" attribute, if True, rounds the result to the number of
significant digits indicated in the Datum instance used to define the .target property."""
li.solve(stop_at_target=True, alter_target=True, rounding=True)

# PRINTING THE SOLUTION
print('\nThe solution is: ', li.target)
```

The output then will look like
```commandline
The solution is:  w = 5.85 percent
```
If the SETTINGS['COMMENT ON'] is set to False. If set to True the output will be as follows
```commandline
	Computing, considering new data...
		Solving psm - msm/Vsm for Vsm: got Vsm = 0.0001 meter ** 3
	INTERMEDIATE:  Vsm = 0.0001 meter ** 3
	Writing in new data...
	OVERALL: Vsm = 0.0001 meter ** 3
New iteration...
	Computing, considering new data...
		Solving C - n/Vsm for n: got n = 0.1 mole
	INTERMEDIATE:  n = 0.1 mole
	Writing in new data...
	OVERALL: n = 0.1 mole
New iteration...
	Computing, considering new data...
		Solving n - mps/M for mps: got mps = 0.0058499999999999976 kilogram
	INTERMEDIATE:  mps = 0.0058499999999999976 kilogram
	Writing in new data...
	OVERALL: mps = 0.0058499999999999976 kilogram
New iteration...
	Computing, considering new data...
		Solving -mps/msm + w for w: got w = 0.0585 dimensionless
	INTERMEDIATE:  w = 0.0585 dimensionless
	Writing in new data...
	OVERALL: w = 0.0585 dimensionless
New iteration...
w = 5.85 percent

The solution is:  w = 5.85 percent
```

# Notes
Currently, the code is still being developed, and is not final. Thus, bugs and errors may occur. Also, the author is aware of how inconvenient it is to write so much lines of code.
 The code will become more convenient to use later.

If you ever found bugs or ways to improve the code, feel free to contact the author.

Please note that the author of these lines is not a professional coder, rather an amateur. So, be cautious when using this code as I might have missed something. Still, if you ever used the code in any of your projects, I would love to see its use (although, this is not a must, of course.)
