# Tutorial

This library helps you to handle basic RESTful API use-cases with Django Forms fashion. Library kinda replaces
`django.forms.Form` with `django_api_forms.Form` and introduces few extra fields (boolean handling, BASE64
images/files, nesting).

`django_api_forms.Form` defines format of the request and help you with:

- payload parsing (according to the `Content-Type` HTTP header)
- data validation and normalisation (using [Django validators](https://docs.djangoproject.com/en/3.1/ref/validators/)
or custom `clean_` method)
- BASE64 file/image upload
- construction of the basic validation response
- filling objects attributes (if possible, see exceptions) using `setattr` function (super handy for Django database
models)

## Construction

You can create form objects using class method `Form.create_from_request(request: Request) -> Form` which creates form
instance from Django requests using appropriate parser from
[Content-Type](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type) HTTP header.

```python
from tests.testapp.forms import AlbumForm

def my_view(request):
    form = AlbumForm.create_from_request(request)
```

Currently, supports:

- JSON
- [msgpack](https://msgpack.org/) (requires [msgpack](https://pypi.org/project/msgpack/) package)

**TODO**: Add possibility to have custom parsers (or override them)

During construction `Form.dirty: List[str]` property is populated with property keys presented in obtained payload
(sluts!!).

## Validation and normalisation

This process is much more simple than in classic Django form. It consists of:

1. Iterating over form attributes:
    - calling `Field.clean(value)` method
    - calling `Form.clean_<field_name>` method
    - calling `Form.add_error(field_name, error)` in case of failures in clean methods
    - if field is marked as dirty, normalized attribute is saved to `Form.clean_data` property
2. Calling `Form.clean` method which returns final normalized values which will be presented in `Form.clean_data`
(feel free to override it, by default does nothing, useful for conditional validation, you can still add errors u
sing `Form.add_error()`)

Normalized data are available in `Form.clean_data` property (keys suppose to correspond with values from `Form.dirty`).

Validation errors are presented for each field in `Form.errors: Dictionary[str, List[ValidationError]]` property after
`Form.is_valid()` method is called.

As was mentioned above, you can extend property validation or normalisation by creating form method like
`clean_<property_name>`. You can add additional
[ValidationError](https://docs.djangoproject.com/en/3.1/ref/forms/validation/#raising-validationerror)
objects using `Form.add_error(field: str, error: ValidationError)` method. Result is final normalised value of the
attribute.

```python
from django.forms import fields
from django.core.exceptions import ValidationError
from django_api_forms import Form

class BookForm(Form):
    title = fields.CharField(max_length=100)
    year = fields.IntegerField()

    def clean_title(self):
        if self.cleaned_data['title'] == "The Hitchhiker's Guide to the Galaxy":
            self.add_error('title', ValidationError("Too cool!", code='too-cool'))
        return self.cleaned_data['title'].upper()

    def clean(self):
        if self.cleaned_data['title'] == "The Hitchhiker's Guide to the Galaxy" and self.cleaned_data['year'] < 1979:
            # Non field validation errors are present under key `__all__` in Form.errors property
            self.add_error(None, ValidationError("Is it you Doctor?", code='time-travelling'))

        # Last chance to do some touchy touchy with self.clean_data

        return self.cleaned_data
```

## Nesting

## Database relationships

## Fill method

**IMPORTANT**: Form fields `FormField`, `FormFieldList`, `FileField` and `ImageField` doesn't support this feature.
You have to define `fill_` method, if you want these fields populated.

Form object method `MyForm.fill(obj: Any, exclude: List[str] = None)` which fills input `obj` using `setattr` according
to the form fields. Only data present in `clean_data` property (data from request) will be populated. You can use it
like this:

```python
from tests.testapp.forms import AlbumForm
from tests.testapp.models import Album

def my_view(request):
    form = AlbumForm.create_from_request(request)

    if not form.is_valid():
        # Raise validation error
        pass

    album = Album()
    form.fill(album)
    album.save()
```

### ModelChoiceField

Field name is expected to have format like this: `{field_name}(_{to_field_name})?` so library is able to automatically
resolve payload key postfix according to the `to_field_name` attribute. If there is no `to_field_name` provided,
field name should be `{field_name}` or `{field_name}_id`. Normalised data are present in `clean_data` under key
`{field_name}` (e.g. `clean_data['{field_name}']`).

Few examples (normalized data are in `clean_data['artist']` in all use-cases):

```python
from django.forms import ModelChoiceField
from django_api_forms import Form

from tests.testapp.models import Artist

class MyFormNoPostfix(Form):
    artist = ModelChoiceField(queryset=Artist.objects.all())

class MyFormFieldName(Form):
    artist_name = ModelChoiceField(
        queryset=Artist.objects.all(), to_field_name='name'
    )

class MyFormWithId(Form):
    artist_id = ModelChoiceField(queryset=Artist.objects.all())
```

### Customization

If you want to override default filling behaviour, you can define custom `fill_{field}` method inside your form class:

```python
from django.forms import fields

from django_api_forms import Form, FormField, EnumField, DictionaryField
from tests.testapp.models import Album, Artist
from tests.testapp.forms import ArtistForm

class AlbumForm(Form):
    title = fields.CharField(max_length=100)
    year = fields.IntegerField()
    artist = FormField(form=ArtistForm)
    type = EnumField(enum=Album.AlbumType, required=True)
    metadata = DictionaryField(fields.DateTimeField())

    def fill_year(self, obj, value: int) -> int:
        return 2020

    def fill_artist(self, obj, value: dict) -> Artist:
        artist = Artist.objects.get_or_create(
            name=value['name']
        )
        artist.genres = value['genres']
        artist.members = value['members']
        artist.save()
        return artist
```

## File uploads


