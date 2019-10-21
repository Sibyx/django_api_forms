import copy
import re
import typing
from abc import ABC
from typing import List

from django.core import validators
from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _


class Field(ABC):
    default_error_messages = {
        'required': _('This field is required.')
    }
    empty_values = list(validators.EMPTY_VALUES)

    def __init__(self, required: bool = True, default_validators: List = None, error_messages: List[str] = None):
        self.required = required
        self.validators = default_validators

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

    def to_python(self, value):
        return value

    def validate(self, value):
        errors = []

        if value in self.empty_values and self.required:
            raise ValidationError(self.error_messages['required'], code='required')

        for v in self.validators:
            try:
                v(value)
            except ValidationError as e:
                if hasattr(e, 'code') and e.code in self.default_error_messages:
                    e.message = self.default_error_messages[e.code]
                errors.extend(e.error_list)

    def __deepcopy__(self, memo):
        result = copy.copy(self)
        memo[id(self)] = result
        result.error_messages = self.error_messages.copy()
        result.validators = self.validators[:]

        return result


class CharField(Field):
    def __init__(self, *, max_length=None, min_length=None, strip=True, empty_value='', **kwargs):
        self._max_length = max_length
        self._min_length = min_length
        self._strip = strip
        self._empty_value = empty_value

        super().__init__(**kwargs)

        if min_length is not None:
            self.validators.append(validators.MinLengthValidator(int(min_length)))

        if max_length is not None:
            self.validators.append(validators.MaxLengthValidator(int(max_length)))

        self.validators.append(validators.ProhibitNullCharactersValidator())

    def to_python(self, value):
        if value not in self.empty_values:
            value = str(value)
            if self._strip:
                value = value.strip()
        if value in self.empty_values:
            return self._empty_value
        return value


class IntegerField(Field):
    default_error_messages = {
        'invalid': _('Enter a whole number.'),
    }
    re_decimal = re.compile(r'\.0*\s*$')

    def __init__(self, *, max_value=None, min_value=None, **kwargs):
        self.max_value, self.min_value = max_value, min_value

        super().__init__(**kwargs)

        if max_value is not None:
            self.validators.append(validators.MaxValueValidator(max_value))
        if min_value is not None:
            self.validators.append(validators.MinValueValidator(min_value))

    def to_python(self, value):
        value = super().to_python(value)
        if value in self.empty_values:
            return None

        try:
            value = int(self.re_decimal.sub('', str(value)))
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value


class FieldList(Field):
    default_error_messages = {
        'not-list': _('This field have to be a list of objects!'),
    }

    def __init__(self, field, **kwargs):
        if not isinstance(field, Field):
            raise RuntimeError("Invalid Field type passed into FieldList!")

        self.field = field

        super().__init__(**kwargs)

    def to_python(self, value):
        result = ()
        for item in value:
            result += self.field.to_python(item)

    def validate(self, value):
        if not isinstance(value, list):
            raise ValidationError(self.error_messages['not_list'], code='not_list')

        for item in value:
            if isinstance(self.field, Field):
                self.field.validate(item)
            else:
                raise RuntimeError(f"Invalid field_type {type(self.field)} in FieldList")


class FormField(Field):
    def __init__(self, form: typing.Type, **kwargs):
        """
        TODO: what if there is invalid type?
        :param form:
        :param kwargs:
        """
        self.form = form

        super().__init__(**kwargs)

    def to_python(self, value):
        form = self.form(value)
        return form.payload

    def validate(self, value):
        form = self.form(value)
        form.validate()


class FormFieldList(FormField):
    default_error_messages = {
        'not_list': _('This field have to be a list of objects!')
    }

    def to_python(self, value):
        result = ()
        for item in value:
            form = self.form(item)
            result += form.payload

    def validate(self, value):
        if not isinstance(value, list):
            raise ValidationError(self.error_messages['not_list'], code='not_list')

        for item in value:
            form = self.form(item)
            form.validate()
