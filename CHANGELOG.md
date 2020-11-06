# Changelog

## 0.16.2 : 06.11.2020

- **Fix**: Fixed issue with `clean_` methods returning values resolved as False (`False`, `None`, `''`)

## 0.16.1 : 29.10.2020

- **Fix**: Ignore `ModelMultipleChoiceField` in `Form::fill()`

## 0.16.0 : 14.09.2020

- **Change**: Correctly resolve key postfix if `ModelChoiceField` is used in `Form::fill()`
- **Change**: `DjangoApiFormsConfig` is created
- **Note**: One more step to get rid of `pytest` in project (we don't need it)

## 0.15.1 : 29.08.2020

- **Feature**: `FileField.content_type` introduced (contains mime)

## 0.15.0 : 23.08.2020

- **Feature**: `FileField` and `ImageField` introduced
- **Note**: Defined extras in `setup.py` for optional `Pillow` and `msgpack` dependencies
- **Feature**: Working `Form::fill()` method for primitive data types. Introduced `IgnoreFillMixin`

## 0.14.0 : 07.08.2020

- **Feature**: `BaseForm._request` property introduced (now it's possible to use request in `clean_` methods)

## 0.13.0 : 09.07.2020

- **Fix**: Fixed `Content-Type` handling if `charset` or `boundary` is present

## 0.12.0 : 11.06.2020

- **Fix**: Do not call resolvers methods, if property is not required and not present in request

## 0.11.0 : 10.06.2020

- **Change**: Non specified non-required fields will no longer be available in the cleaned_data form attribute.

## 0.10.0 : 01.06.2020

- **Change**: All package exceptions inherits from `ApiFormException`.
- **Fix**: Specifying encoding while opening files in `setup.py` (failing on Windows OS).

## 0.9.0 : 11.05.2020

- **Change**: Moved field error messages to default_error_messages for easier overriding and testing.
- **Fix**: Fix KeyError when invalid values are sent to FieldList.
- **Fix**: Removed unnecessary error checking in FieldList.

## 0.8.0 : 05.05.2020

- **Maintenance**: Add tests for fields
- **Change**: Remove DeclarativeFieldsMetaclass and import from Django instead.
- **Change**: Msgpack dependency is no longer required.
- **Change**: Empty values passed into a FormField now return {} rather than None.
- **Fix**: Throw a more user friendly error when passing non-Enums or invalid values to EnumField.

## 0.7.1 : 13.04.2020

- **Change** Use [poetry](https://python-poetry.org/) instead of [pipenv](https://github.com/pypa/pipenv)
- **Change**: Library renamed from `django_api_forms` to `django-api-forms` (cosmetic change without effect)

## 0.7.0 : 03.03.2020

- **Change**: Library renamed from `django_request_formatter` to `django_api_forms`
- **Change**: Imports in main module `django_api_forms`

## 0.6.0 : 18.02.2020

- **Feature**: `BooleanField` introduced

## 0.5.8 : 07.01.2020

- **Fix**: Pass `Invalid value` as `ValidationError` not as a `string`

## 0.5.7 : 07.01.2020

- **Fix**: Introduced generic `Invalid value` error message, if there is `AttributeError`, `TypeError`, `ValueError`

## 0.5.6 : 01.01.2020

- **Fix**: Fixing issue from version `0.5.5` but this time for real
- **Change**: Renamed version file from `__version__.py` to `version.py`

## 0.5.5 : 01.01.2020

- **Fix**: Check instance only if there is a value in `FieldList` and `FormFieldList`

## 0.5.4 : 24.12.2019

- **Fix**: Added missing `msgpack`` dependency to `setup.py`

## 0.5.3 : 20.12.2019

- **Feature**: Introduced generic `AnyField`

## 0.5.2 : 19.12.2019

- **Fix**: Skip processing of the `FormField` if value is not required and empty

## 0.5.1 : 19.12.2019

- **Fix**: Process `EnumField` even if it's not marked as required

## 0.5.0 : 16.12.2019

- **Change**: Use native `django.form.fields` if possible
- **Change**: Removed `kwargs` propagation from release `0.3.0`
- **Change**: Changed syntax back to `django.forms` compatible (e.g. `form.validate_{key}()` -> `form.clean_{key}()`)
- **Change**: `FieldList` raises `ValidationError` instead of `RuntimeException` if there is a type  in validation
- **Change**: Use private properties for internal data in field objects
- **Fixed**: `FieldList` returns values instead of `None`
- **Fix**: Fixed validation in `DictionaryField`
- **Maintenance**: Basic unit tests

## 0.4.3 : 29.11.2019

- **Fix**: Fixed `Form` has no attribute `self._data`

## 0.4.2 : 29.11.2019

- **Fix**: If payload is empty, create empty dictionary to avoid `NoneType` error

## 0.4.1 : 14.11.2019

- **Feature**: Introduced `UUIDField`

## 0.4.0 : 13.11.2019

- **Feature**: Introduced `DictionaryField`

## 0.3.0 : 11.11.2019

- **Feature**: Propagate `kwargs` from `Form.is_valid()` to `Form.validate()` and `Form.validate_{key}()` methods

## 0.2.1 : 4.11.2019

- **Fix**: Fixed `to_python()` in FormFieldList

## 0.2.0 : 31.10.2019

- **Change**: `Form.validate()` replaced by `Form.is_valid()`
- **Feature**: `Form.validate()` is now used as a last step of form validation and it's aimed to be overwritten if
needed
- **Note**: Unit tests initialization

## 0.1.6 : 24.10.2019

- **Fix**: Non-required EnumField is now working
- **Feature**: WIP: Initial method for filling objects `Form::fill()`

## 0.1.5 : 23.10.2019

- **Fix**: Assign errors to form before raising `ValidationError`

## 0.1.4 : 23.10.2019

- **Fix**: Do not return empty error records in `Form:errors`

## 0.1.3 : 23.10.2019

- **Fix**: Use custom `DeclarativeFieldsMetaclass` because of custom `Field` class
- **Fix**: Do not return untouched fields in `Form::payload`
- **Fix**: Fix for None `default_validators` in `Field`

## 0.1.2 : 22:10.2019

- **Feature**: Support for `validation_{field}` methods in `Form` (initial support)

## 0.1.1 : 22.10.2019

- **Feature**: `EnumField`

## 0.1.0 : 22.10.2019

- **Feature**: First version of `Form` class
- **Feature**: `CharField`
- **Feature**: `IntegerField`
- **Feature**: `FloatField`
- **Feature**: `DecimalField`
- **Feature**: `DateField`
- **Feature**: `TimeField`
- **Feature**: `DateTimeField`
- **Feature**: `DurationField`
- **Feature**: `RegexField`
- **Feature**: `EmailField`
- **Feature**: `BooleanField`
- **Feature**: `RegexField`
- **Feature**: `FieldList`
- **Feature**: `FormField`
- **Feature**: `FormFieldList`
