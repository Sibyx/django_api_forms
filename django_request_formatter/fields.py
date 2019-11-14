import copy
import datetime
import math
import re
import typing
from decimal import Decimal, DecimalException
from enum import Enum
from typing import List

from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.utils import from_current_timezone
from django.utils import formats
from django.utils.dateparse import parse_duration

from django.utils.translation import gettext_lazy as _


class Field:
    default_error_messages = {
        'required': _('This field is required.')
    }
    empty_values = list(validators.EMPTY_VALUES)

    def __init__(self, required: bool = True, default_validators: List = None, error_messages: List[str] = None):
        self.required = required
        self.validators = default_validators or []

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

        super().__init__()

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

    def validate(self, value):
        super().validate(value)

        try:
            int(self.re_decimal.sub('', str(value)))
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages['invalid'], code='invalid')


class FloatField(IntegerField):
    default_error_messages = {
        'invalid': _('Enter a number.'),
    }

    def to_python(self, value):
        """
        Validate that float() can be called on the input. Return the result
        of float() or None for empty values.
        """
        value = super(IntegerField, self).to_python(value)
        if value in self.empty_values:
            return None
        try:
            value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value

    def validate(self, value):
        super().validate(value)
        if value in self.empty_values:
            return
        if not math.isfinite(value):
            raise ValidationError(self.error_messages['invalid'], code='invalid')


class DecimalField(IntegerField):
    default_error_messages = {
        'invalid': _('Enter a number.'),
    }

    def __init__(self, *, max_value=None, min_value=None, max_digits=None, decimal_places=None, **kwargs):
        self.max_digits, self.decimal_places = max_digits, decimal_places
        super().__init__(max_value=max_value, min_value=min_value, **kwargs)
        self.validators.append(validators.DecimalValidator(max_digits, decimal_places))

    def to_python(self, value):
        if value in self.empty_values:
            return None
        value = str(value).strip()
        try:
            value = Decimal(value)
        except DecimalException:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value

    def validate(self, value):
        super().validate(value)
        if value in self.empty_values:
            return
        if not value.is_finite():
            raise ValidationError(self.error_messages['invalid'], code='invalid')


class BaseTemporalField(Field):

    def __init__(self, *, input_formats=None, **kwargs):
        super().__init__(**kwargs)
        if input_formats is not None:
            self.input_formats = input_formats

    def to_python(self, value):
        value = value.strip()
        for format in self.input_formats:
            try:
                return self.strptime(value, format)
            except (ValueError, TypeError):
                continue
        raise ValidationError(self.error_messages['invalid'], code='invalid')

    def strptime(self, value, format):
        raise NotImplementedError('Subclasses must define this method.')


class DateField(BaseTemporalField):
    input_formats = formats.get_format_lazy('DATE_INPUT_FORMATS')
    default_error_messages = {
        'invalid': _('Enter a valid date.'),
    }

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        return super().to_python(value)

    def strptime(self, value, format):
        return datetime.datetime.strptime(value, format).date()


class TimeField(BaseTemporalField):
    input_formats = formats.get_format_lazy('TIME_INPUT_FORMATS')
    default_error_messages = {
        'invalid': _('Enter a valid time.')
    }

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.time):
            return value
        return super().to_python(value)

    def strptime(self, value, format):
        return datetime.datetime.strptime(value, format).time()


class DateTimeField(BaseTemporalField):
    input_formats = formats.get_format_lazy('DATETIME_INPUT_FORMATS')
    default_error_messages = {
        'invalid': _('Enter a valid date/time.'),
    }

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.datetime):
            return from_current_timezone(value)
        if isinstance(value, datetime.date):
            result = datetime.datetime(value.year, value.month, value.day)
            return from_current_timezone(result)
        result = super().to_python(value)
        return from_current_timezone(result)

    def strptime(self, value, format):
        return datetime.datetime.strptime(value, format)


class DurationField(Field):
    default_error_messages = {
        'invalid': _('Enter a valid duration.'),
        'overflow': _('The number of days must be between {min_days} and {max_days}.')
    }

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.timedelta):
            return value
        try:
            value = parse_duration(str(value))
        except OverflowError:
            raise ValidationError(self.error_messages['overflow'].format(
                min_days=datetime.timedelta.min.days,
                max_days=datetime.timedelta.max.days,
            ), code='overflow')
        if value is None:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value


class RegexField(CharField):
    def __init__(self, regex, **kwargs):
        """
        regex can be either a string or a compiled regular expression object.
        """
        kwargs.setdefault('strip', False)
        super().__init__(**kwargs)
        self._set_regex(regex)

    def _get_regex(self):
        return self._regex

    def _set_regex(self, regex):
        if isinstance(regex, str):
            regex = re.compile(regex)
        self._regex = regex
        if hasattr(self, '_regex_validator') and self._regex_validator in self.validators:
            self.validators.remove(self._regex_validator)
        self._regex_validator = validators.RegexValidator(regex=regex)
        self.validators.append(self._regex_validator)

    regex = property(_get_regex, _set_regex)


class EmailField(CharField):
    default_validators = [validators.validate_email]

    def __init__(self, **kwargs):
        super().__init__(strip=True, **kwargs)


class BooleanField(Field):
    def to_python(self, value):
        if isinstance(value, str) and value.lower() in ('false', '0'):
            value = False
        else:
            value = bool(value)
        return super().to_python(value)

    def validate(self, value):
        if not value and self.required:
            raise ValidationError(self.error_messages['required'], code='required')


class FieldList(Field):
    default_error_messages = {
        'not-list': _('This field have to be a list of objects!'),
    }

    def __init__(self, field, **kwargs):
        if not isinstance(field, Field):
            raise RuntimeError("Invalid Field type passed into FieldList!")

        self._field = field

        super().__init__(**kwargs)

    def to_python(self, value):
        result = []
        for item in value:
            result.append(self._field.to_python(item))
        return result

    def validate(self, value):
        if not isinstance(value, list):
            raise ValidationError(self.error_messages['not_list'], code='not_list')

        for item in value:
            if isinstance(self._field, Field):
                self._field.validate(item)
            else:
                raise ValidationError(f"Invalid field_type {type(self._field)} in FieldList", code='type_mismatch')


class FormField(Field):
    def __init__(self, form: typing.Type, **kwargs):
        self._form = form

        super().__init__(**kwargs)

    def to_python(self, value):
        form = self._form(value)
        return form.payload

    def validate(self, value):
        form = self._form(value)
        form.is_valid(True)


class FormFieldList(FormField):
    default_error_messages = {
        'not_list': _('This field have to be a list of objects!')
    }

    def to_python(self, value):
        result = []
        for item in value:
            form = self._form(item)
            result.append(form.payload)
        return result

    def validate(self, value):
        if not isinstance(value, list):
            raise ValidationError(self.error_messages['not_list'], code='not_list')

        errors = []

        for item in value:
            form = self._form(item)
            try:
                form.is_valid()
            except ValidationError as e:
                errors.append(e)

        if errors:
            e = ValidationError(errors)
            raise e


class EnumField(Field):
    default_error_messages = {
        'not_enum': _('This field have to be a subclass of enum.Enum')
    }

    def __init__(self, enum: typing.Type, **kwargs):
        if not issubclass(enum, Enum):
            raise RuntimeError("Invalid Field type passed into FieldList!")

        self.enum = enum

        super().__init__(**kwargs)

    def to_python(self, value):
        return self.enum(value)

    def validate(self, value):
        super().validate(value)

        if self.required and value is not None:
            try:
                self.enum(value)
            except ValueError:
                raise ValidationError(f"Invalid enum value {value} passed to {type(self.enum)}")


class DictionaryField(Field):
    def __init__(self, value, **kwargs):
        if not isinstance(value, Field):
            raise RuntimeError("Invalid Field type passed into DictionaryField!")
        self._value = value
        super().__init__(**kwargs)

    def to_python(self, value) -> dict:
        result = {}

        for key, item in value.items():
            result[key] = self._value.to_python(item)

        return result

    def validate(self, value):
        if not isinstance(value, dict):
            raise ValidationError(f"Invalid value passed to DictionaryField (got {type(value)}, expected dict)")

        errors = {}

        for key, item in value.items():
            try:
                self._value.validate(item)
            except ValidationError as e:
                errors[key] = e

        if errors:
            raise ValidationError(errors)
