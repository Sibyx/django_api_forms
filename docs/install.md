# Installation

Library is published on PyPi index as [django-api-forms](https://pypi.org/project/django-api-forms/). You can add it to
your project using your favorite package manager. Few examples:

```shell
# Using pip
pip install django-api-forms

# Using poetry
peotry add django-api-forms

# Using pipenv
pipenv install django-api-forms

# Local installation
python -m pip install .
```

## Extra functionality

If you want to use some extra functionality, you have to install additional dependencies.

### msgpack

Library checks for `application/x-msgpack` HTTP content type. To work it properly you have to install
[msgpack](https://pypi.org/project/msgpack/). We support `extras_require`, so you can do it by executing
`pip install django-api-forms[msgpack]` while installing `django-api-forms` or individually by `pip install msgpack`
inside your environment.

### Pillow

Library provides `FileField` and `ImageField`, which are pretty similar to
[Django native implementation](https://docs.djangoproject.com/en/4.1/ref/models/fields/#filefield). There fields
require [Pillow](https://pypi.org/project/Pillow/) to be installed inside of your environment.

- `pip install django-api-forms[Pillow]`
- `pip install Pillow`

## Fun fact

You can install all extra dependencies using one call `pip install django-api-forms[Pillow,msgpack]`.
