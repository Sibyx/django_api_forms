import copy
import json
from collections import OrderedDict
from typing import Union

import msgpack
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.forms import MediaDefiningClass, Field
from django.utils.translation import gettext as _

from .exceptions import RequestValidationError


class DeclarativeFieldsMetaclass(MediaDefiningClass):
    """Collect Fields declared on the base classes."""

    def __new__(mcs, name, bases, attrs):
        # Collect fields from current class.
        current_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                current_fields.append((key, value))
                attrs.pop(key)
        attrs['declared_fields'] = OrderedDict(current_fields)

        new_class = super(DeclarativeFieldsMetaclass, mcs).__new__(mcs, name, bases, attrs)

        # Walk through the MRO.
        declared_fields = OrderedDict()
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'declared_fields'):
                declared_fields.update(base.declared_fields)

            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in declared_fields:
                    declared_fields.pop(attr)

        new_class.base_fields = declared_fields
        new_class.declared_fields = declared_fields

        return new_class

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        # Remember the order in which form fields are defined.
        return OrderedDict()


class BaseForm(object):
    def __init__(self, data=None):
        if data is None:
            self._data = {}
        else:
            self._data = data
        self.fields = copy.deepcopy(getattr(self, 'base_fields'))
        self._errors = None
        self._dirty = []
        self.cleaned_data = {}

        if isinstance(data, dict):
            for key in data.keys():
                self._dirty.append(key)

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
        """
        :rtype: BaseForm
        """
        if not request.body:
            return cls(None)

        if request.META.get('CONTENT_TYPE') and 'application/json' in request.META.get('CONTENT_TYPE'):
            data = json.loads(request.body)
        elif request.META.get('CONTENT_TYPE') and 'application/x-msgpack' in request.META.get('CONTENT_TYPE'):
            data = msgpack.loads(request.body)
        else:
            raise RuntimeError("Unable to parse request!")

        return cls(data)

    @property
    def errors(self) -> dict:
        if self._errors is None:
            self.full_clean()
        return self._errors

    def is_valid(self) -> bool:
        return not self.errors

    def add_error(self, field: Union[str, None], error: Union[ValidationError, RequestValidationError]):
        if isinstance(error, RequestValidationError):
            self._errors[field] = error.errors
            return

        if hasattr(error, 'error_dict'):
            if field is not None:
                raise TypeError(
                    "The argument `field` must be `None` when the `error` "
                    "argument contains errors for multiple fields."
                )
            else:
                error = error.error_dict
        else:
            error = {field or NON_FIELD_ERRORS: error.error_list}

        for field, error_list in error.items():
            if field not in self.errors:
                if field != NON_FIELD_ERRORS and field not in self.fields:
                    raise ValueError("'%s' has no field named '%s'." % (self.__class__.__name__, field))
                if field == NON_FIELD_ERRORS:
                    self._errors[field] = []
                else:
                    self._errors[field] = []
            self._errors[field].extend(error_list)
            if field in self.cleaned_data:
                del self.cleaned_data[field]

    def full_clean(self):
        """
        Clean all of self.data and populate self._errors and self.cleaned_data.
        """
        self._errors = {}
        self.cleaned_data = {}

        for key, field in self.fields.items():
            try:
                self.cleaned_data[key] = field.clean(self._data.get(key, None))
                if hasattr(self, f"clean_{key}"):
                    self.cleaned_data[key] = getattr(self, f"clean_{key}")()
            except (ValidationError, RequestValidationError) as e:
                self.add_error(key, e)
            except (AttributeError, TypeError, ValueError):
                self.add_error(key, ValidationError(_("Invalid value")))

        try:
            cleaned_data = self.clean()
        except ValidationError as e:
            self.add_error(None, e)
        else:
            if cleaned_data is not None:
                self.cleaned_data = cleaned_data

    def clean(self):
        """
        Hook for doing any extra form-wide cleaning after Field.clean() has been
        called on every field. Any ValidationError raised by this method will
        not be associated with a particular field; it will have a special-case
        association with the field named '__all__'.
        """
        return self.cleaned_data

    def fill(self, obj):
        """
        WIP
        TODO: Resolve embedded forms
        :param obj:
        :return:
        """
        for key, item in self._data.items():
            setattr(obj, key, item)


class Form(BaseForm, metaclass=DeclarativeFieldsMetaclass):
    """A collection of Fields, plus their associated data."""
