import typing
from base64 import b64decode
from enum import Enum
from io import BytesIO
from mimetypes import guess_type

from django.core.exceptions import ValidationError
from django.core.files import File
from django.forms import Field
from django.utils.translation import gettext_lazy as _

from .exceptions import RequestValidationError


class IgnoreFillMixin:
    @property
    def ignore_fill(self) -> bool:
        return True


class BooleanField(Field):
    def to_python(self, value):
        if value in (True, 'True', 'true', '1', 1):
            return True
        elif value in (False, 'False', 'false', '0', 0):
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
        'max_length': _('Ensure this list has at most %(max)d values (it has %(length)d).'),
        'min_length': _('Ensure this list has at least %(min)d values (it has %(length)d).'),
        'not_field': _('Invalid Field type passed into FieldList!'),
        'not_list': _('This field needs to be a list of objects!'),
    }

    def __init__(self, field, min_length=None, max_length=None, **kwargs):
        super().__init__(**kwargs)

        if not isinstance(field, Field):
            raise RuntimeError(self.error_messages['not_field'])

        self._min_length = min_length
        self._max_length = max_length
        self._field = field

    def to_python(self, value) -> typing.List:
        if not value:
            return []

        if not isinstance(value, list):
            raise ValidationError(self.error_messages['not_list'], code='not_list')

        if self._min_length is not None and len(value) < self._min_length:
            params = {'min': self._min_length, 'length': len(value)}
            raise ValidationError(self.error_messages['min_length'], code='min_length', params=params)

        if self._max_length is not None and len(value) > self._max_length:
            params = {'max': self._max_length, 'length': len(value)}
            raise ValidationError(self.error_messages['max_length'], code='max_length', params=params)

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


class FormField(Field, IgnoreFillMixin):
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


class FormFieldList(FormField, IgnoreFillMixin):
    def __init__(self, form: typing.Type, min_length=None, max_length=None, **kwargs):
        self._min_length = min_length
        self._max_length = max_length
        super().__init__(form, **kwargs)

    default_error_messages = {
        'max_length': _('Ensure this list has at most %(max)d values (it has %(length)d).'),
        'min_length': _('Ensure this list has at least %(min)d values (it has %(length)d).'),
        'not_list': _('This field needs to be a list of objects!')
    }

    def to_python(self, value):
        if not value:
            return []

        if not isinstance(value, list):
            raise ValidationError(self.error_messages['not_list'], code='not_list')

        if self._min_length is not None and len(value) < self._min_length:
            params = {'min': self._min_length, 'length': len(value)}
            raise ValidationError(self.error_messages['min_length'], code='min_length', params=params)

        if self._max_length is not None and len(value) > self._max_length:
            params = {'max': self._max_length, 'length': len(value)}
            raise ValidationError(self.error_messages['max_length'], code='max_length', params=params)

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

    def __init__(self, value_field, **kwargs):
        super().__init__(**kwargs)

        if not isinstance(value_field, Field):
            raise RuntimeError(self.error_messages['not_field'])

        self._value_field = value_field

    def to_python(self, value) -> dict:
        if not isinstance(value, dict):
            msg = self.error_messages['not_dict'].format(type(value))
            raise ValidationError(msg)

        result = {}
        errors = {}

        for key, item in value.items():
            try:
                result[key] = self._value_field.clean(item)
            except ValidationError as e:
                errors[key] = e

        if errors:
            raise ValidationError(errors)

        return result


class AnyField(Field):
    def to_python(self, value) -> typing.Union[typing.Dict, typing.List]:
        return value


class FileField(Field, IgnoreFillMixin):
    default_error_messages = {
        'max_length': _('Ensure this file has at most %(max)d bytes (it has %(length)d).'),
        'invalid_mime': _("The submitted file is empty."),
    }

    def __init__(self, max_length=None, mime: typing.List[str] = None, **kwargs):
        self._max_length = max_length
        self._mime = mime
        super().__init__(**kwargs)

    def to_python(self, value: str) -> typing.Optional[File]:
        if not value:
            return None

        mime = None

        if ',' in value:
            mime, strict = guess_type(value)
            value = value.split(',')[-1]

        if self._mime and mime not in self._mime:
            params = {'allowed': ', '.join(self._mime), 'received': mime}
            raise ValidationError(self.error_messages['invalid_mime'], code='invalid_mime', params=params)

        file = File(BytesIO(b64decode(value)))

        if self._max_length is not None and file.size > self._max_length:
            params = {'max': self._max_length, 'length': file.size}
            raise ValidationError(self.error_messages['max_length'], code='max_length', params=params)

        file.content_type = mime

        return file


class ImageField(FileField, IgnoreFillMixin):
    default_error_messages = {
        'invalid_image': _("Upload a valid image. The file you uploaded was either not an image or a corrupted image.")
    }

    def to_python(self, value) -> typing.Optional[File]:
        f = super(ImageField, self).to_python(value)

        if f is None:
            return None

        # Pillow is required for ImageField
        from PIL import Image

        file = BytesIO(f.read())  # Create fp for Pillow

        try:
            image = Image.open(file)
            image.verify()
            f.image = Image.open(file)  # Image have to be reopened after Image.verify() call
            f.content_type = Image.MIME.get(image.format)
        except Exception:
            raise ValidationError(
                self.error_messages['invalid_image'],
                code='invalid_image'
            )

        if self._mime and f.content_type not in self._mime:
            params = {'allowed': ', '.join(self._mime), 'received': f.content_type}
            raise ValidationError(self.error_messages['invalid_mime'], code='invalid_mime', params=params)

        f.seek(0)  # Return to start of the file

        return f
