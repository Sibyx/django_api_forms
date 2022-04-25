from typing import Union, Tuple

from django.core.exceptions import ValidationError


class ApiFormException(Exception):
    """Generic Django API Form exception"""
    pass


class UnsupportedMediaType(ApiFormException):
    """Unable to parse the request (based on the Content-Type)"""
    pass


class RequestValidationError(ApiFormException):
    def __init__(self, errors: Union[list, dict], code=None, params=None):
        super().__init__(errors, code, params)
        self._errors = errors

    @property
    def errors(self):
        return self._errors

    def __repr__(self):
        return self.errors


class DetailValidationError(ValidationError):
    def __init__(self, error: ValidationError, path: Union[Tuple, str]):
        super().__init__(error.message, error.code, error.params)
        if isinstance(path[0], Tuple):
            path = path[0]
        self._path = path

    @property
    def path(self) -> Tuple:
        return self._path

    def prepend(self, key: str):
        self._path = (key, ) + self._path

    def to_list(self) -> list:
        return list(self.path)

    def to_dict(self) -> dict:
        return {
            'code': self.code,
            'message': self.message,
            'path': self.to_list()
        }


def build(form):
    error_list = []
    for error in form.errors:
        error_list.append(
            error.to_dict()
        )

    message = {
        'errors': error_list
    }

    return message
