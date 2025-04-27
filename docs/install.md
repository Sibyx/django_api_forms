# Installation

Django API Forms is published on the PyPI index as [django-api-forms](https://pypi.org/project/django-api-forms/). You can add it to your project using your favorite package manager.

## Basic Installation

Choose one of the following methods to install the basic package:

```shell
# Using pip
pip install django-api-forms

# Using poetry
poetry add django-api-forms

# Using pipenv
pipenv install django-api-forms

# Local installation from source
python -m pip install .
```

## Requirements

- Python 3.9+
- Django 2.0+

## Optional Dependencies

Django API Forms supports additional functionality through optional dependencies. You can install these dependencies individually or as extras.

### MessagePack Support

To handle `application/x-msgpack` HTTP content type, you need to install the [msgpack](https://pypi.org/project/msgpack/) package:

```shell
# Install with the msgpack extra
pip install django-api-forms[msgpack]

# Or install msgpack separately
pip install msgpack
```

### File and Image Fields

The library provides `FileField` and `ImageField` which are similar to [Django's native implementation](https://docs.djangoproject.com/en/4.1/ref/models/fields/#filefield). These fields require [Pillow](https://pypi.org/project/Pillow/) to be installed:

```shell
# Install with the Pillow extra
pip install django-api-forms[Pillow]

# Or install Pillow separately
pip install Pillow
```

### RRule Field

To use the `RRuleField` for recurring date rules, you need to install [python-dateutil](https://pypi.org/project/python-dateutil/):

```shell
# Install with the rrule extra
pip install django-api-forms[rrule]

# Or install python-dateutil separately
pip install python-dateutil
```

### GeoJSON Field

To use the `GeoJSONField` for geographic data, you need to install [GDAL](https://pypi.org/project/GDAL/):

```shell
# Install with the gdal extra
pip install django-api-forms[gdal]

# Or install GDAL separately
pip install gdal
```

## Installing Multiple Extras

You can install multiple extras in a single command:

```shell
# Install all extras
pip install django-api-forms[Pillow,msgpack,rrule,gdal]

# Or just the ones you need
pip install django-api-forms[Pillow,msgpack]
```

## Django Settings

No specific Django settings are required to use Django API Forms, but you can customize its behavior by adding settings to your `settings.py` file. See the [Example](example.md) page for available settings.
