# Changelog

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
