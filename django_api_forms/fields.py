import typing
import warnings
from base64 import b64decode
from enum import Enum
from io import BytesIO
from mimetypes import guess_type
import re

from django.core.exceptions import ValidationError
from django.core.files import File
from django.forms import Field
from django.utils.translation import gettext_lazy as _

from .exceptions import DetailValidationError, ApiFormException
from .version import __version__ as version

DATA_URI_PATTERN = r"data:((?:\w+\/(?:(?!;).)+)?)((?:;[\w=]*[^;])*),(.+)"


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
            raise ApiFormException(self.error_messages['not_field'])

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

        for position, item in enumerate(value):
            try:
                result.append(self._field.clean(item))
            except ValidationError as e:
                errors.append(DetailValidationError(e, (position,)))

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
            raise ValidationError(form.errors)


class FormFieldList(FormField):
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

        for position, item in enumerate(value):
            form = self._form(item)
            if form.is_valid():
                result.append(form.cleaned_data)
            else:
                for error in form.errors:
                    error.prepend((position, ))
                    errors.append(error)

        if errors:
            raise ValidationError(errors)

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
            raise ApiFormException(self.error_messages['not_enum'])

        self.enum = enum

    def to_python(self, value) -> typing.Union[typing.Type[Enum], None]:
        if value is not None:
            try:
                return self.enum(value)
            except ValueError:
                raise ValidationError(self.error_messages['invalid'].format(value, self.enum), code='invalid')
        return None


class DictionaryField(Field):
    default_error_messages = {
        'not_field': _('Invalid Field type passed into DictionaryField!'),
        'not_dict': _('Invalid value passed to DictionaryField (got {}, expected dict)'),
    }

    def __init__(self, *, value_field, key_field=None, **kwargs):
        super().__init__(**kwargs)

        if not isinstance(value_field, Field):
            raise ApiFormException(self.error_messages['not_field'])

        if key_field and not isinstance(key_field, Field):
            raise ApiFormException(self.error_messages['not_field'])

        self._value_field = value_field
        self._key_field = key_field

    def to_python(self, value) -> dict:
        if not isinstance(value, dict):
            msg = self.error_messages['not_dict'].format(type(value))
            raise ValidationError(msg)

        result = {}
        errors = {}

        for key, item in value.items():
            try:
                if self._key_field:
                    key = self._key_field.clean(key)
                result[key] = self._value_field.clean(item)
            except ValidationError as e:
                errors[key] = DetailValidationError(e, (key, ))

        if errors:
            raise ValidationError(errors)

        return result


class AnyField(Field):
    def to_python(self, value) -> typing.Union[typing.Dict, typing.List]:
        return value


class FileField(Field):
    default_error_messages = {
        'max_length': _('Ensure this file has at most %(max)d bytes (it has %(length)d).'),
        'invalid_uri': _("The given URI is not a valid Data URI."),
        'invalid_mime': _("The submitted file is empty."),
    }

    def __init__(self, max_length=None, mime: typing.Tuple = None, **kwargs):
        self._max_length = max_length
        self._mime = mime
        super().__init__(**kwargs)

    def to_python(self, value: str) -> typing.Optional[File]:
        if not value:
            return None

        if re.fullmatch(DATA_URI_PATTERN, value) is None:
            warnings.warn(
                "Raw base64 inside of FileField/ImageField is deprecated and will throw a validation error from "
                "version >=1.0.0 Provide value as a Data URI.",
                DeprecationWarning
            )
            if version >= "1.0.0":
                raise ValidationError(self.error_messages["invalid_uri"], code="invalid_uri")

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


class ImageField(FileField):
    default_error_messages = {
        'invalid_image': _("Upload a valid image. The file you uploaded was either not an image or a corrupted image.")
    }

    def to_python(self, value) -> typing.Optional[File]:
        f = super().to_python(value)

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


class RRuleField(Field):
    default_error_messages = {
        'invalid_rrule': _('This given RRule String is not in a valid RRule syntax.'),
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def to_python(self, value: str):
        # Dateutil is required for RRuleField
        from dateutil.rrule import rrulestr

        try:
            result = rrulestr(value)
        except Exception:
            raise ValidationError(
                self.error_messages['invalid_rrule'], code='invalid_rrule'
            )

        return result


class GeoJSONField(Field):
    default_error_messages = {
        'not_dict': _('Invalid value passed to GeoJSONField (got {}, expected dict)'),
        'not_geojson': _('Invalid value passed to GeoJSONField'),
        'not_int': _('Value must be integer'),
        'transform_error': _('Error at transform')
    }

    def __init__(self, srid=4326, transform=None, **kwargs):
        super().__init__(**kwargs)

        self._srid = srid
        self._transform = transform

    def to_python(self, value):
        if not self._srid or not isinstance(self._srid, int):
            params = {'srid': self._srid}
            raise ValidationError(self.error_messages['not_int'], code='not_int', params=params)

        if self._transform and not isinstance(self._transform, int):
            params = {'transform': self._transform}
            raise ValidationError(self.error_messages['not_int'], code='not_int', params=params)

        if not isinstance(value, dict):
            msg = self.error_messages['not_dict'].format(type(value))
            raise ValidationError(msg)

        if value == {}:
            raise ValidationError(self.error_messages['not_geojson'], code='not_geojson')

        from django.contrib.gis.gdal import GDALException
        from django.contrib.gis.geos import GEOSGeometry
        try:
            if 'crs' not in value.keys():
                value['crs'] = {
                    "type": "name",
                    "properties": {
                        "name": f"ESRI::{self._srid}"
                    }
                }
            result = GEOSGeometry(f'{value}', srid=self._srid)
        except GDALException:
            raise ValidationError(self.error_messages['not_geojson'], code='not_geojson')

        if self._transform:
            try:
                result.transform(self._transform)
            except GDALException:
                raise ValidationError(self.error_messages['transform_error'], code='transform_error')

        return result
