from typing import Union


class RequestValidationError(Exception):
    def __init__(self, errors: Union[list, dict], code=None, params=None):
        super().__init__(errors, code, params)
        self._errors = errors

    @property
    def errors(self):
        return self._errors

    def __repr__(self):
        return self.errors
