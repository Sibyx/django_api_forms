# Django API Forms

[Django Forms](https://docs.djangoproject.com/en/3.2/topics/forms/) approach in processing of RESTful HTTP request
payload (especially for content type like [JSON](https://www.json.org/) or [MessagePack](https://msgpack.org/))
without HTML front-end.

## Motivation

The main idea was to create a simple and declarative way to specify the format of expecting requests with the ability
to validate them. Firstly I tried to use [Django Forms](https://docs.djangoproject.com/en/3.0/topics/forms/) to
validate my API requests (I use pure Django in my APIs). I have encountered a problem with nesting my requests without
a huge boilerplate. Also, the whole HTML thing was pretty useless in my RESTful APIs.

I wanted to:

- define my requests as object (`Form`),
- pass the request to my defined object (`form = Form.create_from_request(request)`),
- validate my request `form.is_valid()`,
- extract data `form.clean_data` property.

I wanted to keep:

- friendly declarative Django syntax,
([DeclarativeFieldsMetaclass](https://github.com/django/django/blob/master/django/forms/forms.py#L22) is beautiful),
- [Validators](https://docs.djangoproject.com/en/3.1/ref/validators/),
- [ValidationError](https://docs.djangoproject.com/en/3.1/ref/exceptions/#validationerror),
- [Form fields](https://docs.djangoproject.com/en/3.1/ref/forms/fields/) (In the end, I had to "replace" some of them).

So I have decided to create a simple Python package to cover all my expectations.

## Running Tests

```shell script
# install all dependencies
poetry install

# run code-style check
poetry run flake8 .

# run the tests
poetry run python runtests.py
```
