from typing import Optional


class QCException(Exception):
        def __init__(self, message, details: Optional[str] = None):
            if not isinstance(details, str) and details is not None:
                raise TypeError('The "details" parameter for any QCException must be either a string or None.')
            else:
                self.message = message
                self.details = details
                super().__init__(message if details is None else f'{message} \n {details}')
