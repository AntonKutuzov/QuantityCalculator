from QCalculator._settings import SETTINGS


def comment(*text, end: str = '\n') -> None:
    if SETTINGS['COMMENTS ON']:
        print(*text, end=end)
    else:
        pass
