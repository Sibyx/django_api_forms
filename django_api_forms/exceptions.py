from typing import Union, Tuple, Dict

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


class DetailedValidationError(ValidationError):
    def __init__(self, message: str, path: Union[Tuple, str], code: str = None, params: Dict = None):
        super().__init__(message, code, params)
        self._path = path

    def path(self) -> Union[Tuple, str]:
        return self._path

    def prepend(self, key: Union[Tuple, str]):
        if isinstance(key, str):
            self._path = (key,) + self._path
        elif isinstance(key, tuple):
            self._path = key + self._path

    def to_dict(self):
        return {
            'code': self.code,
            'message': self.message,
            'path': self.path
        }
