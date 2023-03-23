# Django API Forms

[![PyPI version](https://badge.fury.io/py/django-api-forms.svg)](https://badge.fury.io/py/django-api-forms)
[![codecov](https://codecov.io/gh/Sibyx/django_api_forms/branch/master/graph/badge.svg)](https://codecov.io/gh/Sibyx/django_api_forms)

[Django Forms](https://docs.djangoproject.com/en/4.1/topics/forms/) approach in the processing of a RESTful HTTP
request payload (especially for content type like [JSON](https://www.json.org/) or [MessagePack](https://msgpack.org/))
without HTML front-end.

## Motivation

The main idea was to create a simple and declarative way to specify the format of expecting requests with the ability
to validate them. Firstly, I tried to use [Django Forms](https://docs.djangoproject.com/en/4.1/topics/forms/) to
validate my API requests (I use pure Django in my APIs). I have encountered a problem with nesting my requests without
a huge boilerplate. Also, the whole HTML thing was pretty useless in my RESTful APIs.

I wanted to:

- define my requests as object (`Form`),
- pass the request with optional arguments to my defined object (`form = Form.create_from_request(request, param=param)`),
- validate my request `form.is_valid()`,
- extract data `form.clean_data` property.

I wanted to keep:

- friendly declarative Django syntax,
([DeclarativeFieldsMetaclass](https://github.com/django/django/blob/master/django/forms/forms.py#L25) is beautiful),
- [Validators](https://docs.djangoproject.com/en/4.1/ref/validators/),
- [ValidationError](https://docs.djangoproject.com/en/4.1/ref/exceptions/#validationerror),
- [Form fields](https://docs.djangoproject.com/en/4.1/ref/forms/fields/) (In the end, I had to "replace" some of them).

So I have decided to create a simple Python package to cover all my expectations.

## Installation

```shell script
# Using pip
pip install django-api-forms

# Using poetry
poetry add django-api-forms

# Local installation
python -m pip install .
```

Optional:
```shell script
# msgpack support (for requests with Content-Type: application/x-msgpack)
poetry add msgpack

# ImageField support
poetry add Pillow
```

Install application in your Django project by adding `django_api_forms` to yours `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django_api_forms'
)
```

You can change the default behavior of population strategies or parsers using these settings (listed with default
values). Keep in mind, that dictionaries are not replaced by your settings they are merged with defaults.

For more information about the parsers and the population strategies check the documentation.

```python
DJANGO_API_FORMS_POPULATION_STRATEGIES = {
    'django_api_forms.fields.FormFieldList': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django_api_forms.fields.FileField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django_api_forms.fields.ImageField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django_api_forms.fields.FormField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django.forms.models.ModelMultipleChoiceField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django.forms.models.ModelChoiceField': 'django_api_forms.population_strategies.ModelChoiceFieldStrategy'
}

DJANGO_API_FORMS_DEFAULT_POPULATION_STRATEGY = 'django_api_forms.population_strategies.BaseStrategy'

DJANGO_API_FORMS_PARSERS = {
    'application/json': 'json.loads',
    'application/x-msgpack': 'msgpack.loads'
}
```

## Example

**Simple nested JSON request**

```json
{
  "title": "Unknown Pleasures",
  "type": "vinyl",
  "artist": {
    "_name": "Joy Division",
    "genres": [
      "rock",
      "punk"
    ],
    "members": 4
  },
  "year": 1979,
  "songs": [
    {
      "title": "Disorder",
      "duration": "3:29"
    },
    {
      "title": "Day of the Lords",
      "duration": "4:48",
      "metadata": {
        "_section": {
          "type": "ID3v2",
          "offset": 0,
          "byteLength": 2048
        },
        "header": {
          "majorVersion": 3,
          "minorRevision": 0,
          "size": 2038
        }
      }
    }
  ],
  "metadata": {
    "created_at": "2019-10-21T18:57:03+0100",
    "updated_at": "2019-10-21T18:57:03+0100"
  }
}
```

**Django API Forms equivalent + validation**

```python
from enum import Enum

from django.core.exceptions import ValidationError
from django.forms import fields

from django_api_forms import FieldList, FormField, FormFieldList, DictionaryField, EnumField, AnyField, Form


class AlbumType(Enum):
    CD = 'cd'
    VINYL = 'vinyl'


class ArtistForm(Form):
    class Meta:
        mapping = {
            '_name': 'name'
        }

    name = fields.CharField(required=True, max_length=100)
    genres = FieldList(field=fields.CharField(max_length=30))
    members = fields.IntegerField()


class SongForm(Form):
    title = fields.CharField(required=True, max_length=100)
    duration = fields.DurationField(required=False)
    metadata = AnyField(required=False)


class AlbumForm(Form):
    title = fields.CharField(max_length=100)
    year = fields.IntegerField()
    artist = FormField(form=ArtistForm)
    songs = FormFieldList(form=SongForm)
    type = EnumField(enum=AlbumType, required=True)
    metadata = DictionaryField(value_field=fields.DateTimeField())

    def clean_year(self):
        if self.cleaned_data['year'] == 1992:
            raise ValidationError("Year 1992 is forbidden!", 'forbidden-value')
        if 'param' not in self.extras:
            self.add_error(
                ('param', ),
                ValidationError("You can use extra optional arguments in form validation!", code='param-where')
            )
        return self.cleaned_data['year']

    def clean(self):
        if (self.cleaned_data['year'] == 1998) and (self.cleaned_data['artist']['name'] == "Nirvana"):
            raise ValidationError("Sounds like a bullshit", code='time-traveling')
        if not self._request.user.is_authenticated():
            raise ValidationError("You can use request in form validation!")
        if 'param' not in self.extras:
            raise ValidationError("You can use extra optional arguments in form validation!")
        return self.cleaned_data



"""
Django view example
"""
def create_album(request):
    form = AlbumForm.create_from_request(request, param=request.GET.get('param'))
    if not form.is_valid():
        # Process your validation error
        print(form.errors)

    # Cleaned valid payload
    payload = form.cleaned_data
    print(payload)
```

If you want example with whole Django project, check out repository created by [pawl](https://github.com/pawl)
[django_api_forms_modelchoicefield_example](https://github.com/pawl/django_api_forms_modelchoicefield_example), where
he uses library with
[ModelChoiceField](https://docs.djangoproject.com/en/4.1/ref/forms/fields/#django.forms.ModelChoiceField).

## Running Tests

```shell script
# install all dependencies
poetry install

# run code-style check
poetry run flake8 .

# run the tests
poetry run python runtests.py
```

---
Made with ❤️ and ☕️ by Jakub Dubec, [BACKBONE s.r.o.](https://www.backbone.sk/en/) &
[contributors](https://github.com/Sibyx/django_api_forms/graphs/contributors).
