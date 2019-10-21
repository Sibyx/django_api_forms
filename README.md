# DjangoRequestFormatter

[Django Forms](https://docs.djangoproject.com/en/2.2/topics/forms/) approach in validation of request payload 
(especially for content type like [JSON](https://www.json.org/) or [MessagePack](https://msgpack.org/)) 
without HTML front-end.

## Motivation

Main idea was to create a simple and declarative way to specify format of expecting request with ability to validate them.
Firstly I tried to use [Django Forms](https://docs.djangoproject.com/en/2.2/topics/forms/) to validate my API request
(I use pure Django in my APIs). I have encountered a problem with nesting my requests without huge boilerplate. Also, 
the whole HTML thing was pretty useless in my RESTful APIs. 

I wanted something to: 

- define my requests as object (`RequestForm`)
- pass the request to my defined object (`form = RequestForm(request)`)
- validate my request `form.is_valid()`
- extract data `form.payload`

I wanted to keep:

- friendly Django syntax ([DeclarativeFieldsMetaclass](https://github.com/django/django/blob/master/django/forms/forms.py#L22) is beautiful)
- [Django Validators](https://docs.djangoproject.com/en/2.2/ref/validators/)
- [ValidationError](https://docs.djangoproject.com/en/2.2/ref/exceptions/#validationerror)

So I decided to create simple python package to cover all my expectations.

## Installation

```shell script
# Using pip
pip install django_request_formatter

# Using pipenv
pipenv install django_request_formatter

# Using setup.py
python setup.py install
```

## Example

**Simple nested JSON request**

```json
{
  "title": "Unknown Pleasures",
  "artist": {
    "name": "Joy division",
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
      "duration": "4:48"
    }
  ],
  "created_at": "2019-10-21T18:57:03+00:00"
}
```

**DjangoRequestFormatter equivalent**

```python
from django_request_fromatter.forms import Form
from django_request_fromatter.fields import CharField


class ArtistForm(Form):
    name = CharField(required=True, max_length=100)


class SongForm(Form):
    title = CharField(required=True, max_length=100)
    duration = CharField(required=False, max_length=10, empty_value=None)


class AlbumForm(Form):
    pass
```

**Parsing and validation**

```python
```



---
Made with ❤️ by Jakub Dubec & [BACKBONE s.r.o.](https://www.backbone.sk/en/)
