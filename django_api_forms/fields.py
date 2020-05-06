import typing
from enum import Enum

from django.core.exceptions import ValidationError
from django.forms import Field
from django.utils.translation import gettext_lazy as _

from .exceptions import RequestValidationError


class BooleanField(Field):
    def to_python(self, value):
        if value in (True, 'True', 'true', '1'):
            return True
        elif value in (False, 'False', 'false', '0'):
            return False
        else:
            return None

    def validate(self, value):
        if value is None and self.required:
            raise ValidationError(self.error_messages['required'], code='required')

    def has_changed(self, initial, data):
        if self.disabled:
            return False

        return self.to_python(initial) != self.to_python(data)


class FieldList(Field):
    default_error_messages = {
        'not_field': _('Invalid Field type passed into FieldList!'),
        'not_list': _('This field needs to be a list of objects!'),
    }

    def __init__(self, field, **kwargs):
        super().__init__(**kwargs)

        if not isinstance(field, Field):
            raise RuntimeError(self.error_messages['not_field'])

        self._field = field

    def to_python(self, value) -> typing.List:
        if not value:
            return []

        if not isinstance(value, list):
            raise ValidationError(self.error_messages['not_list'], code='not_list')

        result = []
        errors = []

        for item in value:
            try:
                self._field.clean(item)
                result.append(self._field.to_python(item))
            except ValidationError as e:
                errors.append(e)

        if errors:
            raise ValidationError(errors)

        return result


class FormField(Field):
    def __init__(self, form: typing.Type, **kwargs):
        self._form = form

        super().__init__(**kwargs)

    @property
    def form(self):
        return self._form

    def to_python(self, value) -> typing.Union[typing.Dict, None]:
        if not value:
            return {}

        form = self._form(value)
        if form.is_valid():
            return form.cleaned_data
        else:
            raise RequestValidationError(form.errors)


class FormFieldList(FormField):
    default_error_messages = {
        'not_list': _('This field needs to be a list of objects!')
    }

    def to_python(self, value):
        if not value:
            return []

        if not isinstance(value, list):
            raise ValidationError(self.error_messages['not_list'], code='not_list')

        result = []
        errors = []

        for item in value:
            form = self._form(item)
            if form.is_valid():
                result.append(form.cleaned_data)
            else:
                errors.append(form.errors)

        if errors:
            raise RequestValidationError(errors)

        return result


class EnumField(Field):
    default_error_messages = {
        'not_enum': _('Invalid Enum type passed into EnumField!'),
        'invalid': _('Invalid enum value "{}" passed to {}'),
    }

    def __init__(self, enum: typing.Type, **kwargs):
        super().__init__(**kwargs)

        # isinstance(enum, type) prevents "TypeError: issubclass() arg 1 must be a class"
        # based on: https://github.com/samuelcolvin/pydantic/blob/v0.32.x/pydantic/utils.py#L260-L261
        if not (isinstance(enum, type) and issubclass(enum, Enum)):
            raise RuntimeError(self.error_messages['not_enum'])

        self.enum = enum

    def to_python(self, value) -> typing.Union[typing.Type[Enum], None]:
        if value is not None:
            try:
                return self.enum(value)
            except ValueError:
                msg = self.error_messages['invalid'].format(value, self.enum)
                raise ValidationError(msg)
        return None


class DictionaryField(Field):
    default_error_messages = {
        'not_field': _('Invalid Field type passed into DictionaryField!'),
        'not_dict': _('Invalid value passed to DictionaryField (got {}, expected dict)'),
    }

    def __init__(self, value, **kwargs):
        super().__init__(**kwargs)

        if not isinstance(value, Field):
            raise RuntimeError(self.error_messages['not_field'])

        self._value = value

    def to_python(self, value) -> dict:
        if not isinstance(value, dict):
            msg = self.error_messages['not_dict'].format(type(value))
            raise ValidationError(msg)

        result = {}
        errors = {}

        for key, item in value.items():
            try:
                result[key] = self._value.clean(item)
            except ValidationError as e:
                errors[key] = e

        if errors:
            raise ValidationError(errors)

        return result


class AnyField(Field):
    def to_python(self, value) -> typing.Union[typing.Dict, typing.List]:
        return value
