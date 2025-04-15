from Calculator.SETTINGS import COMMENTS_ON


def comment(*text, end: str = '\n') -> None:
    if COMMENTS_ON:
        print(*text, end=end)
    else:
        pass
