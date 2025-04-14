from pathlib import Path
from Calculator.Storage import CONSTANTS


def baseDir() -> Path:
    absolute_path = Path(__file__)
    path = str(absolute_path).strip('/').split('/')
    index = path.index(CONSTANTS.PACKAGE_NAME)
    base_path = ''

    for i in range(index+1):
        base_path += f'/{path[i]}'

    return Path(base_path)


def read(file_name: str) -> str:
    if file_name not in CONSTANTS.FILES:
        raise Exception(f'Invalid file path: {file_name}')

    file = open(baseDir() / file_name, 'r')

    for line in file:
        yield line.strip('\n')

    file.close()


def write(file_name: str, *lines: str) -> None:
    if file_name not in CONSTANTS.FILES:
        raise Exception(f'Invalid file path: {file_name}')

    file = open(baseDir() / file_name, 'a')

    for line in lines:
        file.write(line)

    file.close()
