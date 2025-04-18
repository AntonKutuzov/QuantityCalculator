from QCalculator.Storage.CONSTANTS import UNITS_FILE, NAMES_FILE, DEFAULTS_FILE
from QCalculator.Storage.Files import *
from warnings import warn

try:
    UNIT_REGISTRY = dict( [(line.split(':')) for line in read(UNITS_FILE)] )
except ValueError:
    warn('\nCould not create "UNIT_REGISTRY". Check the content of "UNITS_FILE" by running the following code:\n'
                    '>>> from QCalculator.Storage.Files import read\n'
                    '>>> from QCalculator.Storage.CONSTANTS import UNITS_FILE\n'
                    r">>> print(*read(UNITS_FILE), sep='\n')")

try:
    VARIABLE_NAMES = dict([(line.split(':')) for line in read(NAMES_FILE)])
except ValueError:
    warn('\nCould not create "VARIABLE_NAMES". Check the content of "NAMES_FILE" by running the following code:\n'
                    '>>> from QCalculator.Storage.Files import read\n'
                    '>>> from QCalculator.Storage.CONSTANTS import NAMES_FILE\n'
                    r">>> print(*read(NAMES_FILE), sep='\n')")

try:
    DEFAULT_VALUES = dict([(line.split(':')) for line in read(DEFAULTS_FILE)])
except ValueError:
    warn(
        '\nCould not create "DEFAULT_VALUES". Check the content of "DEFAULTS_FILE" by running the following code:\n'
        '>>> from QCalculator.Storage.Files import read\n'
        '>>> from QCalculator.Storage.CONSTANTS import DEFAULTS_FILE\n'
        r">>> print(*read(NAMES_FILE), sep='\n')")
