from Calculator.Storage.FileChangers import *
from Calculator.Utils.Files import erase
from Calculator.Utils.Files import baseDir
from Calculator.Storage.CONSTANTS import FILES, ASSUMPTIONS_FILE
from typing import Dict, List
from datetime import datetime
from time import sleep


NAMES: Dict[str, str]
UNITS: Dict[str, str]
DEFAULTS: Dict[str, float|int]
FORMULAS: List[str]


def instructions() -> str:
    file = open(baseDir() / 'Storage/_ParserFiles/Instructions', 'r')
    help_string = file.read()
    file.close()
    return help_string

def generate_file_name(
        file_name: str,
        no_wait: bool = False
        ) -> str:

    full_name = file_name + ' AT ' + str(datetime)

    archive = open(baseDir() / 'Storage/_ParserFiles/Archive', 'a')
    archive.write(full_name+'\n')
    archive.close()

    if not no_wait:
        sleep(0.01)

    return full_name

def save_original_file(file_name: str) -> bool:
    name = generate_file_name(file_name)
    orig = open(file_name, 'r')
    file = open(baseDir() / f'Storage/_ParserFiles/{name}', 'w')

    for line in orig:
        file.write(line)

    orig.close()
    file.close()

    return True


def erasing(
        include_assumptions: bool = False
        ) -> bool:

    for file in FILES:
        if not include_assumptions and file == ASSUMPTIONS_FILE:
            continue
        else:
            erase(file)

    return True


def parsing_the_file(file_text: str) -> bool:
    parts = file_text.split('!')
    print(parts)


def writing_the_file(file_name: str) -> bool:
    pass


def checking_the_files() -> bool:
    pass
