from typing import Tuple

from django.core.exceptions import ValidationError


class ApiFormException(Exception):
    """Generic Django API Form exception"""


class UnsupportedMediaType(ApiFormException):
    """Unable to parse the request (based on the Content-Type)"""


class DetailValidationError(ValidationError):
    def __init__(self, error: ValidationError, path: Tuple):
        if not hasattr(error, 'message') and isinstance(error.error_list, list):
            for item in error.error_list:
                item.path = path

        super().__init__(error)
        self._path = path

    @property
    def path(self) -> Tuple:
        return self._path

    def prepend(self, key: Tuple):
        self._path = key + self._path

    def to_list(self) -> list:
        return list(self.path)

    def to_dict(self) -> dict:
        return {
            'code': self.code,
            'message': self.message,
            'path': self.to_list()
        }
