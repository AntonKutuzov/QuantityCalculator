from pathlib import Path
from QCalculator.Storage import CONSTANTS
from typing import Tuple, Literal


def _file_present_check(file_name: str) -> None:
    if file_name not in CONSTANTS.FILES:
        raise Exception(f'Invalid file path: {file_name}')


def baseDir() -> Path:
    absolute_path = Path(__file__)
    path = str(absolute_path).strip('/').split('/')
    index = path.index(CONSTANTS.PACKAGE_NAME)
    base_path = ''

    for i in range(index+1):
        base_path += f'/{path[i]}'

    return Path(base_path)


def read(file_name: str) -> str:
    _file_present_check(file_name)

    file = open(baseDir() / file_name, 'r')

    for line in file:
        yield line.strip('\n')

    file.close()


def write(
        file_name: str,
        *lines: str,
        add_new_line: bool = True
        ) -> None:
    _file_present_check(file_name)

    file = open(baseDir() / file_name, 'a')

    for line in lines:
        if add_new_line:
            line += '\n'
        file.write(line)

    file.close()

def find(
        file_name: str,
        target_line: str,
        search: Literal['BY LINE', 'BY SYMBOL'] = 'BY LINE'
        ) -> bool:

    _file_present_check(file_name)

    for read_line in read(file_name):
        if search == 'BY LINE' and read_line == target_line:
            return True
        elif search == 'BY SYMBOL' and target_line in read_line:
            return True
    else:
        return False


def erase(file_name: str) -> None:
    _file_present_check(file_name)

    file = open(baseDir() / file_name, 'w')
    file.close()


def copy(
        from_file: str,
        to_file: str,
        *,
        except_lines: Tuple[str, ...] = tuple()
        ) -> None:

    ffile = open(baseDir() / from_file, 'r')
    tfile = open(baseDir() / to_file, 'w')

    lines = ffile.read()
    lines = lines.strip('\n').split('\n')

    for read_line in lines:
        if read_line not in except_lines:
            tfile.write(read_line+'\n')

    ffile.close()
    tfile.close()


def remove(file_name: str, line: str) -> None:
    import os
    _file_present_check(file_name)

    copy(file_name, CONSTANTS.TEMPORARY_FILE, except_lines=(line + '\n',))
    copy(CONSTANTS.TEMPORARY_FILE, file_name)

    os.remove(baseDir() / CONSTANTS.TEMPORARY_FILE)
