class QCException(BaseException):
    def __init__(self, message:str, comment: str):
        self._message = message
        self._comment = comment

    def __str__(self):
        return self._message + '\n' + self._comment
