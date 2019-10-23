## 0.1.5: 23.10.2019

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
