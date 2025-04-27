# Django API Forms

[![PyPI version](https://badge.fury.io/py/django-api-forms.svg)](https://badge.fury.io/py/django-api-forms)
[![codecov](https://codecov.io/gh/Sibyx/django_api_forms/branch/master/graph/badge.svg)](https://codecov.io/gh/Sibyx/django_api_forms)

**Django API Forms** is a Python library that brings the [Django Forms](https://docs.djangoproject.com/en/4.1/topics/forms/) approach to processing RESTful HTTP request payloads (such as [JSON](https://www.json.org/) or [MessagePack](https://msgpack.org/)) without the HTML front-end overhead.

## Overview

Django API Forms provides a declarative way to:

- Define request validation schemas using a familiar Django-like syntax
- Parse and validate incoming API requests
- Handle nested data structures and complex validation rules
- Convert validated data into Python objects
- Populate Django models or other objects with validated data

[**📚 Read the full documentation**](https://sibyx.github.io/django_api_forms/)

## Key Features

- **Declarative Form Definition**: Define your API request schemas using a familiar Django Forms-like syntax
- **Request Validation**: Validate incoming requests against your defined schemas
- **Nested Data Structures**: Handle complex nested JSON objects and arrays
- **Custom Field Types**: Specialized fields for common API use cases (BooleanField, EnumField, etc.)
- **File Uploads**: Support for BASE64-encoded file and image uploads
- **Object Population**: Easily populate Django models or other objects with validated data
- **Customizable Validation**: Define custom validation rules at the field or form level
- **Multiple Content Types**: Support for JSON, MessagePack, and extensible to other formats

## Motivation

The main idea was to create a simple and declarative way to specify the format of expected requests with the ability
to validate them. Firstly, I tried to use [Django Forms](https://docs.djangoproject.com/en/4.1/topics/forms/) to
validate my API requests (I use pure Django in my APIs). I encountered a problem with nesting my requests without
a huge boilerplate. Also, the whole HTML thing was pretty useless in my RESTful APIs.

I wanted to:

- Define my requests as objects (`Form`)
- Pass the request to my defined object (`form = Form.create_from_request(request, param=param))`)
  - With the ability to pass any extra optional arguments
- Validate my request (`form.is_valid()`)
- Extract data (`form.cleaned_data` property)

I wanted to keep:

- Friendly declarative Django syntax
  ([DeclarativeFieldsMetaclass](https://github.com/django/django/blob/master/django/forms/forms.py#L22) is beautiful)
- [Validators](https://docs.djangoproject.com/en/4.1/ref/validators/)
- [ValidationError](https://docs.djangoproject.com/en/4.1/ref/exceptions/#validationerror)
- [Form fields](https://docs.djangoproject.com/en/4.1/ref/forms/fields/) (In the end, I had to "replace" some of them)

So I created this Python package to cover all these expectations.

## Installation

```shell
# Using pip
pip install django-api-forms

# Using poetry
poetry add django-api-forms

# Local installation from source
python -m pip install .
```

### Requirements

- Python 3.9+
- Django 2.0+

### Optional Dependencies

Django API Forms supports additional functionality through optional dependencies:

```shell
# MessagePack support (for Content-Type: application/x-msgpack)
pip install django-api-forms[msgpack]

# File and Image Fields support
pip install django-api-forms[Pillow]

# RRule Field support
pip install django-api-forms[rrule]

# GeoJSON Field support
pip install django-api-forms[gdal]

# Install multiple extras at once
pip install django-api-forms[Pillow,msgpack]
```

For more detailed installation instructions, see the [Installation Guide](https://sibyx.github.io/django_api_forms/install/).

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

## Quick Example

Here's a simple example demonstrating how to use Django API Forms:

```python
from django.forms import fields
from django.http import JsonResponse
from django_api_forms import Form, FormField, FieldList

# Define a nested form
class ArtistForm(Form):
    name = fields.CharField(required=True, max_length=100)
    genres = FieldList(field=fields.CharField(max_length=30))
    members = fields.IntegerField()

# Define the main form
class AlbumForm(Form):
    title = fields.CharField(max_length=100)
    year = fields.IntegerField()
    artist = FormField(form=ArtistForm)

# In your view
def create_album(request):
    form = AlbumForm.create_from_request(request)
    if not form.is_valid():
        # Handle validation errors
        return JsonResponse({"errors": form.errors}, status=400)

    # Access validated data
    album_data = form.cleaned_data
    # Do something with the data...

    return JsonResponse({"status": "success"})
```

This form can validate a JSON request like:

```json
{
  "title": "Unknown Pleasures",
  "year": 1979,
  "artist": {
    "name": "Joy Division",
    "genres": ["rock", "punk"],
    "members": 4
  }
}
```

### More Examples

For more comprehensive examples, check out the documentation:

- [Basic Example with Nested Data](https://sibyx.github.io/django_api_forms/example/#basic-example-music-album-api)
- [User Registration with File Upload](https://sibyx.github.io/django_api_forms/example/#example-user-registration-with-file-upload)
- [API with Django Models](https://sibyx.github.io/django_api_forms/example/#example-api-with-django-models)
- [ModelChoiceField Example](https://github.com/pawl/django_api_forms_modelchoicefield_example) - External repository by [pawl](https://github.com/pawl)

## Documentation

Comprehensive documentation is available at [https://sibyx.github.io/django_api_forms/](https://sibyx.github.io/django_api_forms/)

The documentation includes:

- [Installation Guide](https://sibyx.github.io/django_api_forms/install/)
- [Tutorial](https://sibyx.github.io/django_api_forms/tutorial/)
- [Field Reference](https://sibyx.github.io/django_api_forms/fields/)
- [Examples](https://sibyx.github.io/django_api_forms/example/)
- [API Reference](https://sibyx.github.io/django_api_forms/api_reference/)
- [Contributing Guide](https://sibyx.github.io/django_api_forms/contributing/)

## Running Tests

```shell
# Install all dependencies
poetry install

# Run code-style check
poetry run flake8 .

# Run the tests
poetry run python runtests.py

# Run tests with coverage
poetry run coverage run runtests.py
poetry run coverage report
```

## License

Django API Forms is released under the MIT License.

---
Made with ❤️ and ☕️ by Jakub Dubec, [BACKBONE s.r.o.](https://www.backbone.sk/en/) &
[contributors](https://github.com/Sibyx/django_api_forms/graphs/contributors).
