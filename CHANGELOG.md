# Changelog

## 1.0.0-rc.3 : 04.09.2022

- **Fixed**: Removed validation of non-required fields if they are not present in the request

## 1.0.0-rc.2 : 31.05.2022

- **Fixed**: Fixed "weird" behaviour with missing `clean_data` values if using `ListField`

## 1.0.0-rc.1 : 28.04.2022

This release has been inspired by [Problem Details for HTTP APIs - RFC7807](https://tools.ietf.org/html/rfc7807) and
blog post [Structuring validation errors in REST APIs](https://medium.com/engineering-brainly/structuring-validation-errors-in-rest-apis-40c15fbb7bc3)
 written by [@k3nn7](https://github.com/k3nn7).

The main idea has been to simplify validation process on the client side by flattening errors output. To achieve such
a goal, the whole validation process has been rewritten (and luckily for us, much simplified).

- **Changed**: Positional validation errors for lists
- **Changed**: `ImageField` and `FileField` requires [Data URI](https://datatracker.ietf.org/doc/html/rfc2397)
  (issue [Raise ValidationError in invalid Data URI by default](https://github.com/Sibyx/django_api_forms/issues/22))
- **Removed**: `Form.fill()` method replaced by `Form.populate()`
- **Removed**: `fill_` methods replaced by population strategies

## 0.21.1 : 14.02.2022

- **Changed**: Raw base64 payload in `FileField` and `ImageField` fires `DeprecationWarning`. Use Data URI instead.

## 0.21.0 : 03.02.2022

- **Added**: Introduced `mapping`
- **Added**: Override strategies using `field_type_strategy` and `field_strategy`

## 0.20.1 : 13.1.2022

- **Fixed**: `DictionaryField` was unable to raise validation errors for keys

## 0.20.0 : 14.10.2021

Anniversary release 🥳

- **Added**: Population strategies introduced
- **Added**: `fill` method is deprecated and replaced by `populate`
- **Added**: `Settings` object introduced (`form.settings`)
- **Added**: Pluggable content-type parsers using `DJANGO_API_FORMS_PARSERS` setting

## 0.19.1 : 17.09.2021

- **Changed**: `mime` argument in `FileField` is supposed to be a `tuple`

## 0.19.0 : 12.07.2021

- **Added**: `FieldList` and `FormFieldList` now supports optional min/max constrains using `min_length`/`max_length`

## 0.18.0 : 16.04.2021

- **Added**: `ModelForm` class introduced (experimental, initial support - not recommended for production)

## 0.17.0 : 24.02.2021

- **Added**: `fill_method` introduced

## 0.16.4 : 20.12.2020

- **Fixed**: Pillow image object have to be reopened after `Image.verify()` call in `ImageField::to_python`

## 0.16.3 : 13.11.2020

- **Fixed**: `ApiFormException('No clean data provided! Try to call is_valid() first.')` was incorrectly raised if
request payload was empty during `Form::fill` method call
- **Changed**: `clean_data` property is by default `None` instead of empty dictionary

## 0.16.2 : 06.11.2020

- **Fixed**: Fixed issue with `clean_` methods returning values resolved as False (`False`, `None`, `''`)

## 0.16.1 : 29.10.2020

- **Fixed**: Ignore `ModelMultipleChoiceField` in `Form::fill()`

## 0.16.0 : 14.09.2020

One more step to get rid of `pytest` in project (we don't need it)

- **Changed**: Correctly resolve key postfix if `ModelChoiceField` is used in `Form::fill()`
- **Changed**: `DjangoApiFormsConfig` is created

## 0.15.1 : 29.08.2020

- **Added**: `FileField.content_type` introduced (contains mime)

## 0.15.0 : 23.08.2020

- **Added**: `FileField` and `ImageField` introduced
- **Added**: Defined extras in `setup.py` for optional `Pillow` and `msgpack` dependencies
- **Added**: Working `Form::fill()` method for primitive data types. Introduced `IgnoreFillMixin`

## 0.14.0 : 07.08.2020

- **Added**: `BaseForm._request` property introduced (now it's possible to use request in `clean_` methods)

## 0.13.0 : 09.07.2020

- **Fixed**: Fixed `Content-Type` handling if `charset` or `boundary` is present

## 0.12.0 : 11.06.2020

- **Fixed**: Do not call resolvers methods, if property is not required and not present in request

## 0.11.0 : 10.06.2020

- **Changed**: Non specified non-required fields will no longer be available in the cleaned_data form attribute.

## 0.10.0 : 01.06.2020

- **Changed**: All package exceptions inherits from `ApiFormException`.
- **Fixed**: Specifying encoding while opening files in `setup.py` (failing on Windows OS).

## 0.9.0 : 11.05.2020

- **Changed**: Moved field error messages to default_error_messages for easier overriding and testing.
- **Fixed**: Fix KeyError when invalid values are sent to FieldList.
- **Fixed**: Removed unnecessary error checking in FieldList.

## 0.8.0 : 05.05.2020

- **Added**: Tests for fields
- **Changed**: Remove DeclarativeFieldsMetaclass and import from Django instead.
- **Changed**: Msgpack dependency is no longer required.
- **Changed**: Empty values passed into a FormField now return {} rather than None.
- **Fixed**: Throw a more user friendly error when passing non-Enums or invalid values to EnumField.

## 0.7.1 : 13.04.2020

- **Changed** Use [poetry](https://python-poetry.org/) instead of [pipenv](https://github.com/pypa/pipenv)
- **Changed**: Library renamed from `django_api_forms` to `django-api-forms` (cosmetic change without effect)

## 0.7.0 : 03.03.2020

- **Changed**: Library renamed from `django_request_formatter` to `django_api_forms`
- **Changed**: Imports in main module `django_api_forms`

## 0.6.0 : 18.02.2020

- **Added**: `BooleanField` introduced

## 0.5.8 : 07.01.2020

- **Fixed**: Pass `Invalid value` as `ValidationError` not as a `string`

## 0.5.7 : 07.01.2020

- **Fixed**: Introduced generic `Invalid value` error message, if there is `AttributeError`, `TypeError`, `ValueError`

## 0.5.6 : 01.01.2020

- **Fixed**: Fixing issue from version `0.5.5` but this time for real
- **Changed**: Renamed version file from `__version__.py` to `version.py`

## 0.5.5 : 01.01.2020

- **Fixed**: Check instance only if there is a value in `FieldList` and `FormFieldList`

## 0.5.4 : 24.12.2019

- **Fixed**: Added missing `msgpack`` dependency to `setup.py`

## 0.5.3 : 20.12.2019

- **Added**: Introduced generic `AnyField`

## 0.5.2 : 19.12.2019

- **Fixed**: Skip processing of the `FormField` if value is not required and empty

## 0.5.1 : 19.12.2019

- **Fixed**: Process `EnumField` even if it's not marked as required

## 0.5.0 : 16.12.2019

- **Changed**: Use native `django.form.fields` if possible
- **Changed**: Removed `kwargs` propagation from release `0.3.0`
- **Changed**: Changed syntax back to `django.forms` compatible (e.g. `form.validate_{key}()` -> `form.clean_{key}()`)
- **Changed**: `FieldList` raises `ValidationError` instead of `RuntimeException` if there is a type  in validation
- **Changed**: Use private properties for internal data in field objects
- **Fixed**: `FieldList` returns values instead of `None`
- **Fixed**: Fixed validation in `DictionaryField`
- **Added**: Basic unit tests

## 0.4.3 : 29.11.2019

- **Fixed**: Fixed `Form` has no attribute `self._data`

## 0.4.2 : 29.11.2019

- **Fixed**: If payload is empty, create empty dictionary to avoid `NoneType` error

## 0.4.1 : 14.11.2019

- **Added**: Introduced `UUIDField`

## 0.4.0 : 13.11.2019

- **Added**: Introduced `DictionaryField`

## 0.3.0 : 11.11.2019

- **Added**: Propagate `kwargs` from `Form.is_valid()` to `Form.validate()` and `Form.validate_{key}()` methods

## 0.2.1 : 4.11.2019

- **Fixed**: Fixed `to_python()` in FormFieldList

## 0.2.0 : 31.10.2019

- **Changed**: `Form.validate()` replaced by `Form.is_valid()`
- **Added**: `Form.validate()` is now used as a last step of form validation and it's aimed to be overwritten if
needed
- **Added**: Unit tests initialization

## 0.1.6 : 24.10.2019

- **Fixed**: Non-required EnumField is now working
- **Added**: WIP: Initial method for filling objects `Form::fill()`

## 0.1.5 : 23.10.2019

- **Fixed**: Assign errors to form before raising `ValidationError`

## 0.1.4 : 23.10.2019

- **Fixed**: Do not return empty error records in `Form:errors`

## 0.1.3 : 23.10.2019

- **Fixed**: Use custom `DeclarativeFieldsMetaclass` because of custom `Field` class
- **Fixed**: Do not return untouched fields in `Form::payload`
- **Fixed**: Fix for None `default_validators` in `Field`

## 0.1.2 : 22:10.2019

- **Added**: Support for `validation_{field}` methods in `Form` (initial support)

## 0.1.1 : 22.10.2019

- **Added**: `EnumField`

## 0.1.0 : 22.10.2019

- **Added**: First version of `Form` class
- **Added**: `CharField`
- **Added**: `IntegerField`
- **Added**: `FloatField`
- **Added**: `DecimalField`
- **Added**: `DateField`
- **Added**: `TimeField`
- **Added**: `DateTimeField`
- **Added**: `DurationField`
- **Added**: `RegexField`
- **Added**: `EmailField`
- **Added**: `BooleanField`
- **Added**: `RegexField`
- **Added**: `FieldList`
- **Added**: `FormField`
- **Added**: `FormFieldList`
