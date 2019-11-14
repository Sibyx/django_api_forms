
class RequestValidationError(Exception):
    def __init__(self, message, code=None, params=None):
        super().__init__(message, code, params)
