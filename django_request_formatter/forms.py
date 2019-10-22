import copy
import json
from typing import Dict

from django.core.exceptions import ValidationError
from django.forms.forms import DeclarativeFieldsMetaclass


class BaseForm(object):
    def __init__(self, data=None):
        self._data = data
        self.fields = copy.deepcopy(getattr(self, 'base_fields'))
        self._errors = None

    def __getitem__(self, name):
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError(
                "Key '%s' not found in '%s'. Choices are: %s." % (
                    name,
                    self.__class__.__name__,
                    ', '.join(sorted(self.fields)),
                )
            )
        return field

    def __iter__(self):
        for name in self.fields:
            yield self[name]

    @classmethod
    def create_from_request(cls, request):
        if request.META.get('CONTENT_TYPE') and 'application/json' in request.META.get('CONTENT_TYPE'):
            data = (None if request.body is None or request.body is b'' or request.body is b'{}' else json.loads(request.body))
        elif request.META.get('CONTENT_TYPE') and 'application/x-msgpack' in request.META.get('CONTENT_TYPE'):
            raise RuntimeError("Not implemented!")
        else:
            raise RuntimeError("Unable to parse request!")

        return cls(data)

    @property
    def errors(self) -> ValidationError:
        return self._errors

    @property
    def payload(self) -> Dict:
        result = {}

        for key, field in self.fields.items():
            result[key] = field.to_python(self._data.get(key, None))

        return result

    def validate(self):
        errors = {}

        for key, field in self.fields.items():
            field_errors = []
            try:
                field.validate(self._data.get(key, None))
            except ValidationError as e:
                field_errors.append(e)

            if hasattr(self, f"validate_{key}"):
                try:
                    getattr(self, f"validate_{key}")(self._data.get(key, None))
                except ValidationError as e:
                    field_errors.append(e)

            errors[key] = field_errors

        if errors:
            raise ValidationError(errors)


class Form(BaseForm, metaclass=DeclarativeFieldsMetaclass):
    """A collection of Fields, plus their associated data."""
