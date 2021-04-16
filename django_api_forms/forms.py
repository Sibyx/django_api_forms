import copy
import json
from typing import Union, List

from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.forms import ModelChoiceField, ModelMultipleChoiceField, fields_for_model
from django.forms.forms import DeclarativeFieldsMetaclass
from django.forms.models import ModelFormOptions
from django.utils.translation import gettext as _

from .exceptions import RequestValidationError, UnsupportedMediaType, ApiFormException

try:
    import msgpack

    is_msgpack_installed = True
except ImportError:
    is_msgpack_installed = False

parsers_by_content_type = {'application/json': json.loads}
if is_msgpack_installed:
    parsers_by_content_type['application/x-msgpack'] = msgpack.loads


class BaseForm(object):
    def __init__(self, data=None, request=None):
        if data is None:
            self._data = {}
        else:
            self._data = data
        self.fields = copy.deepcopy(getattr(self, 'base_fields'))
        self._errors = None
        self._dirty = []
        self.cleaned_data = None
        self._request = request

        if isinstance(data, dict):
            for key in data.keys():
                if key in self.fields.keys():
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
            return cls()

        all_attributes = request.META.get('CONTENT_TYPE', '').replace(' ', '').split(';')
        content_type = all_attributes.pop(0)

        optional_attributes = {}
        for attribute in all_attributes:
            key, value = attribute.split('=')
            optional_attributes[key] = value

        parser = parsers_by_content_type.get(content_type)

        if parser:
            data = parser(request.body)
        else:
            raise UnsupportedMediaType

        return cls(data, request)

    @property
    def dirty(self) -> List:
        return self._dirty

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
                validated_form_item = field.clean(self._data.get(key, None))

                if key in self.dirty:
                    self.cleaned_data[key] = validated_form_item

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

    def fill(self, obj, exclude: List[str] = None):
        """
        :param exclude:
        :param obj:
        :return:
        """
        if exclude is None:
            exclude = []

        if self.cleaned_data is None:
            raise ApiFormException("No clean data provided! Try to call is_valid() first.")

        for key, field in self.fields.items():
            # Skip if field is in exclude
            if key in exclude:
                continue

            # Skip if field is not in validated data
            if key not in self.cleaned_data.keys():
                continue

            # Skip default behaviour if there is fill_ method available
            if hasattr(self, f"fill_{key}"):
                setattr(obj, key, getattr(self, f"fill_{key}")(obj, self.cleaned_data[key]))
                continue

            # Skip if field is not fillable
            if hasattr(field, 'ignore_fill') and field.ignore_fill:
                continue

            # ModelMultipleChoiceField is not fillable (yet)
            if isinstance(field, ModelMultipleChoiceField):
                continue

            """
            We need to changes key postfix if there is ModelChoiceField (because of _id etc.)
            We always try to assign whole object instance, for example:
            artis_id is normalized as Artist model, but it have to be assigned to artist model property
            because artist_id in model has different type (for example int if your are using int primary keys)
            If you are still confused (sorry), try to check docs
            """
            if isinstance(field, ModelChoiceField):
                model_key = key
                if field.to_field_name:
                    postfix_to_remove = f"_{field.to_field_name}"
                else:
                    postfix_to_remove = "_id"
                if key.endswith(postfix_to_remove):
                    model_key = key[:-len(postfix_to_remove)]
                setattr(obj, model_key, self.cleaned_data[key])
            else:
                setattr(obj, key, self.cleaned_data[key])

        return obj


class ModelForm(BaseForm, metaclass=DeclarativeFieldsMetaclass):
    """
    SUPER EXPERIMENTAL
    """
    def __new__(cls, *args, **kwargs):
        new_class = super().__new__(cls, **kwargs)
        config = getattr(cls, 'Meta', None)

        model_opts = ModelFormOptions(getattr(config.model, '_meta', None))
        model_opts.exclude = getattr(config, 'exclude', tuple())

        fields = fields_for_model(
            model=model_opts.model,
            fields=None,
            exclude=model_opts.exclude,
            widgets=None,
            formfield_callback=None,
            localized_fields=model_opts.localized_fields,
            labels=model_opts.labels,
            help_texts=model_opts.help_texts,
            error_messages=model_opts.error_messages,
            field_classes=model_opts.field_classes,
            apply_limit_choices_to=False,
        )

        # AutoField has to be added manually
        # Do not add AutoFields right now
        # if config.model._meta.auto_field and config.model._meta.auto_field.attname not in model_opts.exclude:
        #     fields[config.model._meta.auto_field.attname] = IntegerField()

        fields.update(new_class.declared_fields)
        # Remove None value keys
        fields = {k: v for k, v in fields.items() if v is not None}

        new_class.base_fields = fields
        new_class.declared_fields = fields

        return new_class


class Form(BaseForm, metaclass=DeclarativeFieldsMetaclass):
    """A collection of Fields, plus their associated data."""
