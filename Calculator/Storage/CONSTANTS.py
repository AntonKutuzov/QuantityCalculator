PACKAGE_NAME: str = 'Calculator'

# ============================================================================================== FILES AND PATHS TO THEM
# When adding a new file here, don't forget to add its path (variable) to the FILES tuple.
FORMULAS_FILE: str = 'Storage/Formulas'
NAMES_FILE: str = 'Storage/Names'
UNITS_FILE: str = 'Storage/Units'
DEFAULTS_FILE: str = 'Storage/Defaults'
ASSUMPTIONS_FILE: str = 'Storage/Assumptions'
TEMPORARY_FILE: str = 'Storage/temporary_file_for_string_removal'

FILES: tuple = (FORMULAS_FILE, NAMES_FILE, UNITS_FILE, DEFAULTS_FILE, ASSUMPTIONS_FILE)

ZERO_TOLERANCE_EXPONENT: int = 5
