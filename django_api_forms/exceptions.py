from typing import Union, List, Tuple

from django.core.exceptions import ValidationError


class ApiFormException(Exception):
    """Generic Django API Form exception"""
    pass


class UnsupportedMediaType(ApiFormException):
    """Unable to parse the request (based on the Content-Type)"""
    pass


class RequestValidationError(ApiFormException):
    def __init__(self, errors: Union[List[Tuple[int, List[ValidationError]]], dict], code=None, params=None):
        super().__init__(errors, code, params)
        self._errors = errors

    @property
    def errors(self):
        return self._errors

    def __repr__(self):
        return self.errors
