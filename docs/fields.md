# Fields

Even if we tried to use maximum of native Django field, we had to override some of them to be more fit for RESTful
applications. Also we introduced new ones, to cover extra functionality like nested requests. In this section we will
explain our intentions and describe their usage.

To sum up:

- You can use [Django Form Fields](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#module-django.forms.fields):
    - [CharField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#charfield)
    - [ChoiceField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#choicefield)
    - [TypedChoiceField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#typedchoicefield)
    - [DateField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#datefield)
    - [DateTimeField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#datetimefield)
    - [DecimalField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#decimalfield)
    - [DurationField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#durationfield)
    - [EmailField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#emailfield)
    - [FilePathField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#filepathfield)
    - [FloatField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#floatfield)
    - [IntegerField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#integerfield)
    - [GenericIPAddressField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#genericipaddressfield)
    - [MultipleChoiceField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#multiplechoicefield)
    - [TypedMultipleChoiceField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#typedmultiplechoicefield)
    - [RegexField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#regexfield)
    - [SlugField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#slugfield)
    - [TimeField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#timefield)
    - [URLField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#urlfield)
    - [UUIDField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#uuidfield)
    - [ModelChoiceField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#modelchoicefield)
    - [ModelMultipleChoiceField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#modelmultiplechoicefield)
- You can use [Django Validators](https://docs.djangoproject.com/en/3.1/ref/validators/).

Fields which are not in the list above were not been tested or been replaced with our customized implementation
(or it just doesn't make sense use them in RESTful APIs).

## BooleanField

- Normalizes to: A Python **True** or **False** value (or **None** if it's not required)

[Django BooleanField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#booleanfield)
[checks only for False](https://github.com/django/django/blob/master/django/forms/fields.py#L712) (`false`, `0`)
values and everything else is suppose to be **True**.

In my point of view this kind of behaviour it's little bit weird, so we decided to check explicitly for **True** and
**False** values. If field is required
[ValidationError](https://docs.djangoproject.com/en/3.1/ref/exceptions/#django.core.exceptions.ValidationError) is
raised or value is normalized as **None**.

Checked values:

- **True**: `True` `'True'` `'true'` `1` `'1'`
- **False**: `False` `'False'` `'false'` `0` `'0'`

**Note: We would like to change this behaviour to support only boolean values and rely on deserializers.**

## FieldList

This field is used to parse list of primitive values (like strings or numbers). If you want to parse list of object,
check `FormFieldList`.

- Normalizes to: A Python list
- Error message keys: `not_field`, `not_list`
- Required arguments:
    - `field`: Instance of a form field representing children

**JSON example**

```json
{
  "numbers": [0, 1, 1, 2, 3, 5, 8, 13]
}
```

**Python representation**

```python
from django_api_forms import Form, FieldList
from django.forms import fields

class FibonacciForm(Form):
    numbers = FieldList(field=fields.IntegerField())
```

## FormField

Field used for embedded objects represented as another API form.

- Normalizes to: A Python dictionary
- Required arguments:
    - `form`: Type of a nested form

**JSON example**

```json
{
  "title": "Unknown Pleasures",
  "year": 1979,
  "artist": {
    "name": "Joy Division",
    "genres": [
      "rock",
      "punk"
    ],
    "members": 4
  }
}
```

**Python representation**

```python
from django_api_forms import Form, FormField, FieldList
from django.forms import fields


class ArtistForm(Form):
    name = fields.CharField(required=True, max_length=100)
    genres = FieldList(field=fields.CharField(max_length=30))
    members = fields.IntegerField()


class AlbumForm(Form):
    title = fields.CharField(max_length=100)
    year = fields.IntegerField()
    artist = FormField(form=ArtistForm)
```

## FormFieldList

Field used for embedded objects represented as another API form.

- Normalizes to: A Python list of dictionaries
- Error message keys: `not_list`
- Required arguments:
    - `form`: Type of a nested form

**JSON example**

```json
{
  "title": "Rock For People",
  "artists": [
    {
      "name": "Joy Division",
      "genres": [
        "rock",
        "punk"
      ],
      "members": 4
    }
  ]
}
```

**Python representation**

```python
from django_api_forms import Form, FormFieldList, FieldList
from django.forms import fields


class ArtistForm(Form):
    name = fields.CharField(required=True, max_length=100)
    genres = FieldList(field=fields.CharField(max_length=30))
    members = fields.IntegerField()


class FestivalForm(Form):
    title = fields.CharField(max_length=100)
    year = fields.IntegerField()
    artists = FormFieldList(form=ArtistForm)
```

## EnumField

This field depends on [django-enum-choices](https://github.com/HackSoftware/django-enum-choices) (because normalized
value is `Enum` object, not a string).

- Normalizes to: A Python `Enum` object
- Error message keys: `not_enum`, `invalid`
- Required arguments:
    - `enum`: Enum class

**JSON example**

```json
{
  "title": "Rock For People",
  "type": "vinyl"
}
```

**Python representation**

```python
from enum import Enum

from django_api_forms import Form, EnumField
from django.forms import fields


class AlbumType(Enum):
    CD = 'cd'
    VINYL = 'vinyl'


class AlbumForm(Form):
    title = fields.CharField(required=True, max_length=100)
    type = EnumField(enum=AlbumType)
```

## DictionaryField

## AnyField

## FileField

## ImageField
