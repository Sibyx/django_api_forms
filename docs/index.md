# Django API Forms

[Django Forms](https://docs.djangoproject.com/en/3.0/topics/forms/) approach in validation of request payload
(especially for content type like [JSON](https://www.json.org/) or [MessagePack](https://msgpack.org/))
without HTML front-end.

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

## Community examples

- [django_api_forms_modelchoicefield_example](https://github.com/pawl/django_api_forms_modelchoicefield_example):
Example usage of the
[ModelChoiceField](https://docs.djangoproject.com/en/3.0/ref/forms/fields/#django.forms.ModelChoiceField) with
Django API Forms created by [pawl](https://github.com/pawl)

## Tests

```shell
# install all dependencies
poetry install

# run the tests
poetry run pytest
```
