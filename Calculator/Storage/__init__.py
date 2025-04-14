from Calculator.Storage.CONSTANTS import UNITS_FILE, NAMES_FILE, DEFAULTS_FILE
from Calculator.Utils.Files import read

UNIT_REGISTRY = dict( [(line.split(':')) for line in read(UNITS_FILE)] )
VARIABLE_NAMES = dict( [(line.split(':')) for line in read(NAMES_FILE)] )
DEFAULT_VALUES = dict( [(line.split(':')) for line in read(DEFAULTS_FILE)] )
