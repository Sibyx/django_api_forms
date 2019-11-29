import copy
import json
from collections import OrderedDict
from typing import Dict

import msgpack
from django.core.exceptions import ValidationError
from django.forms import MediaDefiningClass

from django_request_formatter.fields import Field


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
    def errors(self) -> ValidationError:
        return self._errors

    @property
    def payload(self) -> Dict:
        result = {}

        for key, field in self.fields.items():
            if key in self._dirty:
                result[key] = field.to_python(self._data.get(key, None))

        return result

    def fill(self, obj):
        """
        WIP
        TODO: Resolve embedded forms
        :param obj:
        :return:
        """
        for key, item in self._data.items():
            setattr(obj, key, item)

    def is_valid(self, raise_exception: bool = True, **kwargs):
        errors = {}

        for key, field in self.fields.items():
            field_errors = []
            try:
                field.validate(self._data.get(key, None))
            except ValidationError as e:
                field_errors.append(e)

            if hasattr(self, f"validate_{key}"):
                try:
                    getattr(self, f"validate_{key}")(self._data.get(key, None), **kwargs)
                except ValidationError as e:
                    field_errors.append(e)

            if field_errors:
                errors[key] = field_errors

        try:
            self.validate(**kwargs)
        except ValidationError as e:
            errors = {**errors, **e.error_dict}

        if errors:
            self._errors = errors
            if raise_exception:
                raise ValidationError(errors)
            return False

        return True

    def validate(self, **kwargs):
        pass


class Form(BaseForm, metaclass=DeclarativeFieldsMetaclass):
    """A collection of Fields, plus their associated data."""
