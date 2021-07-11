# Fields

Even if we tried to most of the native Django fields, we had to override some of them to be more fit for RESTful
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
- Error message keys: `not_field`, `not_list`, `min_length`, `max_length`
- Required arguments:
    - `field`: Instance of a form field representing children
    - `min_length`: Minimum length of field size in integer (optional)
    - `max_length`: Maximum length of field size in integer (optional)

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
- Error message keys: `not_list`, `min_length`, `max_length`
- Required arguments:
    - `form`: Type of a nested form
    - `min_length`: Minimum length of field size in integer (optional)
    - `max_length`: Maximum length of field size in integer (optional)

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

**Tip**: Django has pretty cool implementation of the
[enumeration types](https://docs.djangoproject.com/en/3.1/ref/models/fields/#enumeration-types).

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
from django_api_forms import Form, EnumField
from django.forms import fields
from django.db.models import TextChoices


class AlbumType(TextChoices):
    CD = 'cd', 'CD'
    VINYL = 'vinyl', 'Vinyl'


class AlbumForm(Form):
    title = fields.CharField(required=True, max_length=100)
    type = EnumField(enum=AlbumType)
```

## DictionaryField

Field created for containing typed value pairs (currently library supports only value validation, see
[Key validation in DictionaryField](https://github.com/Sibyx/django_api_forms/issues/21)).

- Normalizes to: A Python dictionary
- Error message keys: `not_dict`
- Required arguments:
    - `value_field`: Type of a nested form

**JSON example**

```json
{
  "my_dict": {
    "b061bb03-1eaa-47d0-948f-3ce1f15bf3bb": 2.718,
    "0a8912f0-6c10-4505-bc27-bbb099d2e395": 42
  }
}
```

**Python representation**

```python
from django_api_forms import Form, DictionaryField
from django.forms import fields


class DictionaryForm(Form):
    my_typed_dict = DictionaryField(value_field=fields.DecimalField())
```

## AnyField

Field without default validators.

- Normalizes to: Type according to the
[chosen request payload parser](https://github.com/Sibyx/django_api_forms/blob/master/django_api_forms/forms.py#L19)

**JSON example**

```json
{
  "singer": {
    "name": "Johnny",
    "surname": "Rotten",
    "age": 64,
    "born_at": "1956-01-31"
  }
}
```

**Python representation**

```python
from django_api_forms import Form, DictionaryField, AnyField


class BandForm(Form):
    singer = DictionaryField(value_field=AnyField())
```

## FileField

This field contains [BASE64](https://tools.ietf.org/html/rfc4648) encoded file.

- Normalizes to: A Django [File](https://docs.djangoproject.com/en/3.1/ref/files/file/) object
- Error message keys: `max_length`, `invalid_mime`
- Arguments:
    - `max_length`: Maximum files size in bytes (optional)
    - `mime`: List (should be a tuple in future) of allowed mime types (optional - if present, value must be in form of
    [Data URI](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs))
- Extra normalised attributes:
    - `file_field.clean(payload).content_type`: Mime type (`str` - e.g. `audio/mpeg`) of containing file (`None` if
    unable to detect - if payload is not in DATA URI format)

**JSON example**

```json
{
  "title": "Disorder",
  "type": "data:audio/mpeg;base64,SGVsbG8sIFdvcmxkIQ=="
}
```

**Python representation**

```python
from django_api_forms import Form, FileField
from django.conf import settings
from django.forms import fields


class SongForm(Form):
    title = fields.CharField(required=True, max_length=100)
    audio = FileField(max_length=settings.DATA_UPLOAD_MAX_MEMORY_SIZE, mime=['audio/mpeg'])
```

## ImageField

This field contains [BASE64](https://tools.ietf.org/html/rfc4648) encoded image. Depends on
[Pillow](https://pypi.org/project/Pillow/) because normalized value contains `Image` object. Pillow is also used for
image validation [Image.verify()](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.verify)
is called.

- Normalizes to: A Django [File](https://docs.djangoproject.com/en/3.1/ref/files/file/) object
- Error message keys: `max_length`, `invalid_mime`, `invalid_image` (if Image.verify() failed)
- Arguments:
    - `max_length`: Maximum files size in bytes (optional)
    - `mime`: List (should be a tuple in future) of allowed mime types (optional, value must be in
    [Data URI](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs))
- Extra normalised attributes:
    - `image_field.clean(payload).content_type`: Mime type (`str` - e.g. `audio/mpeg`) of containing file (`None` if
    unable to detect - if payload is not in DATA URI format). Value is filled using Pillow
    `Image.MIME.get(image.format)`)
    - `image_field.clean(payload).image`: A Pillow
    [Image](https://pillow.readthedocs.io/en/stable/reference/Image.html) object instance

**JSON example**

```json
{
  "title": "Unknown pleasures",
  "cover": "data:image/png;base64,SGVsbG8sIFdvcmxkIQ=="
}
```

**Python representation**

```python
from django_api_forms import Form, ImageField
from django.conf import settings
from django.forms import fields


class AlbumForm(Form):
    title = fields.CharField(required=True, max_length=100)
    cover = ImageField(max_length=settings.DATA_UPLOAD_MAX_MEMORY_SIZE, mime=['image/png'])
```
