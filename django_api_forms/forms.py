import copy
from typing import List, Tuple

from django.core.exceptions import ValidationError
from django.forms import fields_for_model
from django.forms.forms import DeclarativeFieldsMetaclass as DjangoDeclarativeFieldsMetaclass
from django.forms.models import ModelFormOptions
from django.utils.translation import gettext as _

from .exceptions import UnsupportedMediaType, ApiFormException, DetailValidationError
from .settings import Settings
from .utils import resolve_from_path


class BaseForm:
    def __init__(self, data=None, request=None, settings: Settings = None, **kwargs):
        if data is None:
            self._data = {}
        else:
            self._data = data
        self.fields = copy.deepcopy(getattr(self, 'base_fields'))
        self._errors = None
        self._dirty = []
        self.cleaned_data = None
        self._request = request
        self.settings = settings or Settings()
        self.extras = kwargs

        if isinstance(self.Meta, type):
            if hasattr(self.Meta, 'field_type_strategy'):
                for key in self.Meta.field_type_strategy.keys():
                    self.settings.POPULATION_STRATEGIES[key] = self.Meta.field_type_strategy[key]
            if hasattr(self.Meta, 'mapping'):
                for key in data.copy():
                    if key in self.Meta.mapping.keys():
                        data[self.Meta.mapping[key]] = data.pop(key)

        if isinstance(data, dict):
            for key in data.keys():
                if key in self.fields.keys():
                    self._dirty.append(key)

    def __getitem__(self, name):
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError(
                "Key '{}' not found in '{}'. Choices are: {}.".format(
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
    def create_from_request(cls, request, **kwargs):
        """
        :rtype: BaseForm
        """
        if not request.body:
            return cls()

        settings = Settings()

        all_attributes = request.META.get('CONTENT_TYPE', '').replace(' ', '').split(';')
        content_type = all_attributes.pop(0)

        optional_attributes = {}
        for attribute in all_attributes:
            key, value = attribute.split('=')
            optional_attributes[key] = value

        if content_type not in settings.PARSERS:
            raise UnsupportedMediaType()

        parser = resolve_from_path(settings.PARSERS[content_type])
        data = parser(request.body)

        return cls(data, request, settings, **kwargs)

    @property
    def dirty(self) -> List:
        return self._dirty

    @property
    def errors(self) -> dict:
        if not self._errors:
            self.full_clean()
        return self._errors

    def is_valid(self) -> bool:
        return not self.errors

    def add_error(self, field: Tuple, errors: ValidationError):
        if hasattr(errors, 'error_dict'):
            for key, items in errors.error_dict.items():
                for error in items:
                    if isinstance(error, DetailValidationError):
                        error.prepend(field)
                        self.add_error(error.path, error)
                    elif isinstance(error, ValidationError):
                        self.add_error(field + (key, ), error)
        elif not hasattr(errors, 'message') and isinstance(errors.error_list, list):
            for item in errors.error_list:
                if isinstance(item, DetailValidationError):
                    item.prepend(field)
                    self.add_error(item.path, item)
                elif isinstance(item, ValidationError):
                    path = field
                    if hasattr(item, 'path'):
                        path = field + item.path
                    self.add_error(path, item)
        else:
            self._errors.append(
                DetailValidationError(errors, (field,) if isinstance(field, str) else field)
            )

            if field in self.cleaned_data:
                del self.cleaned_data[field]

    def full_clean(self):
        """
        Clean all of self.data and populate self._errors and self.cleaned_data.
        """
        self._errors = []
        self.cleaned_data = {}

        for key, field in self.fields.items():
            try:
                if key in self.dirty or field.required:
                    validated_form_item = field.clean(self._data.get(key, None))

                    self.cleaned_data[key] = validated_form_item

                    if hasattr(self, f"clean_{key}"):
                        self.cleaned_data[key] = getattr(self, f"clean_{key}")()
            except ValidationError as e:
                self.add_error((key, ), e)
            except (AttributeError, TypeError, ValueError):
                self.add_error((key, ), ValidationError(_("Invalid value")))

        if not self._errors:
            try:
                self.cleaned_data = self.clean()
            except ValidationError as e:
                self.add_error(('$body',), e)

    def clean(self):
        """
        Hook for doing any extra form-wide cleaning after Field.clean() has been
        called on every field. Any ValidationError raised by this method will
        not be associated with a particular field; it will have a special-case
        association with the field named '$body'.
        """
        return self.cleaned_data

    def populate(self, obj, exclude: List[str] = None):
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

            field_class = f"{field.__class__.__module__}.{field.__class__.__name__}"
            strategy = resolve_from_path(
                self.settings.POPULATION_STRATEGIES.get(
                    field_class, "django_api_forms.population_strategies.BaseStrategy"
                )
            )
            if isinstance(self.Meta, type):
                if hasattr(self.Meta, 'field_strategy'):
                    if key in self.Meta.field_strategy.keys():
                        strategy = resolve_from_path(
                            self.Meta.field_strategy[key]
                        )

            strategy()(field, obj, key, self.cleaned_data[key])

        return obj


class DeclarativeFieldsMetaclass(DjangoDeclarativeFieldsMetaclass):
    """Collect Fields declared on the base classes."""
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        new_class.Meta = attrs.pop('Meta', None)

        return new_class


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
