# Django API Forms

[![PyPI version](https://badge.fury.io/py/django-request-formatter.svg)](https://badge.fury.io/py/django-request-formatter)

[Django Forms](https://docs.djangoproject.com/en/3.0/topics/forms/) approach in validation of request payload
(especially for content type like [JSON](https://www.json.org/) or [MessagePack](https://msgpack.org/))
without HTML front-end.

**WIP: Library API is pretty unstable!**

## Motivation

Main idea was to create a simple and declarative way to specify format of expecting request with ability to validate
them. Firstly I tried to use [Django Forms](https://docs.djangoproject.com/en/3.0/topics/forms/) to validate my API
request (I use pure Django in my APIs). I have encountered a problem with nesting my requests without huge boilerplate.
Also, the whole HTML thing was pretty useless in my RESTful APIs.

I wanted something to:

- define my requests as object (`Form`)
- pass the request to my defined object (`form = Form.create_from_request(request)`)
- validate my request `form.is_valid()`
- extract data `form.clean_data` property

I wanted to keep:

- friendly declarative Django syntax
([DeclarativeFieldsMetaclass](https://github.com/django/django/blob/master/django/forms/forms.py#L22) is beautiful)
- [Django Validators](https://docs.djangoproject.com/en/3.0/ref/validators/)
- [ValidationError](https://docs.djangoproject.com/en/3.0/ref/exceptions/#validationerror)

So I decided to create simple Python package to cover all my expectations.

## Installation

```shell script
# Using pip
pip install django_api_forms

# Using pipenv
pipenv install django_api_forms

# Using setup.py
python setup.py install
```

## Example

**Simple nested JSON request**

```json
{
  "title": "Unknown Pleasures",
  "type": "vinyl",
  "artist": {
    "name": "Joy Division",
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
          "flagsOctet": 0,
          "unsynchronisationFlag": false,
          "extendedHeaderFlag": false,
          "experimentalIndicatorFlag": false,
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
    metadata = DictionaryField(fields.DateTimeField())

    def clean_year(self):
        if self.cleaned_data['year'] == 1992:
            raise ValidationError("Year 1992 is forbidden!", 'forbidden-value')
        return self.cleaned_data['year']

    def clean(self):
        if (self.cleaned_data['year'] == 1998) and (self.cleaned_data['artist']['name'] == "Nirvana"):
            raise ValidationError("Sounds like a bullshit", code='time-traveling')
        return self.cleaned_data



"""
Django view example
"""
def create_album(request):
    form = AlbumForm.create_from_request(request)
    if not form.is_valid():
        # Process your validation error
        print(form.errors)

    # Cleaned valid payload
    payload = form.cleaned_data
    print(payload)
```

---
Made with ❤️ and ☕️ by Jakub Dubec & [BACKBONE s.r.o.](https://www.backbone.sk/en/)
