# Django API Forms

**Django API Forms** is a Python library that brings the [Django Forms](https://docs.djangoproject.com/en/4.1/topics/forms/) approach to processing RESTful HTTP request payloads (such as [JSON](https://www.json.org/) or [MessagePack](https://msgpack.org/)) without the HTML front-end overhead.

## Overview

Django API Forms provides a declarative way to:

- Define request validation schemas using a familiar Django-like syntax
- Parse and validate incoming API requests
- Handle nested data structures and complex validation rules
- Convert validated data into Python objects
- Populate Django models or other objects with validated data

The library is designed to work seamlessly with Django REST APIs while maintaining the elegant syntax and validation capabilities of Django Forms.

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

## Quick Example

```python
from django.forms import fields
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

## Running Tests

```shell
# install all dependencies
poetry install

# run code-style check
poetry run flake8 .

# run the tests
poetry run python runtests.py
```

## License

Django API Forms is released under the MIT License.
