# API Reference

This page provides detailed documentation for the core classes and methods in Django API Forms.

## Core Classes

### Form

The `Form` class is the main class for defining API request validation schemas.

```python
from django_api_forms import Form

class MyForm(Form):
    # Field definitions go here
    pass
```

#### Class Methods

##### `create_from_request`

```python
@classmethod
def create_from_request(cls, request, **kwargs)
```

Creates a form instance from a Django request, parsing the request body according to the Content-Type header.

**Parameters:**
- `request`: A Django HttpRequest object
- `**kwargs`: Additional keyword arguments that will be available in `form.extras`

**Returns:**
- A form instance

**Example:**
```python
form = MyForm.create_from_request(request, user=request.user)
```

#### Instance Methods

##### `is_valid`

```python
def is_valid() -> bool
```

Validates the form data and returns True if the data is valid, False otherwise.

**Returns:**
- `bool`: True if the form data is valid, False otherwise

**Example:**
```python
if form.is_valid():
    # Process valid data
    pass
```

##### `add_error`

```python
def add_error(field: Tuple, errors: ValidationError)
```

Adds a validation error to the form.

**Parameters:**
- `field`: A tuple representing the path to the field
- `errors`: A ValidationError instance

**Example:**
```python
from django.core.exceptions import ValidationError
form.add_error(('name',), ValidationError("Invalid name"))
```

##### `clean`

```python
def clean()
```

Hook for performing form-wide validation. Override this method to add custom validation logic.

**Returns:**
- The cleaned data

**Example:**
```python
def clean(self):
    if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
        raise ValidationError("Passwords do not match")
    return self.cleaned_data
```

##### `populate`

```python
def populate(obj, exclude: List[str] = None)
```

Populates an object with the form's cleaned data.

**Parameters:**
- `obj`: The object to populate
- `exclude`: A list of field names to exclude from population

**Returns:**
- The populated object

**Example:**
```python
user = User()
form.populate(user)
user.save()
```

#### Properties

##### `cleaned_data`

A dictionary containing the validated form data.

##### `errors`

A list of validation errors.

##### `dirty`

A list of field names that were present in the request data.

##### `extras`

A dictionary containing the additional keyword arguments passed to `create_from_request`.

### ModelForm

The `ModelForm` class is an experimental class for creating forms from Django models.

```python
from django_api_forms import ModelForm
from myapp.models import MyModel

class MyModelForm(ModelForm):
    class Meta:
        model = MyModel
        exclude = ('created_at',)
```

## Field Classes

Django API Forms provides several custom field classes in addition to the standard Django form fields.

### BooleanField

A field that normalizes to a Python boolean value.

```python
from django_api_forms import BooleanField

class MyForm(Form):
    is_active = BooleanField()
```

### FieldList

A field for lists of primitive values.

```python
from django_api_forms import FieldList
from django.forms import fields

class MyForm(Form):
    tags = FieldList(field=fields.CharField(max_length=50))
```

### FormField

A field for nested objects.

```python
from django_api_forms import FormField

class AddressForm(Form):
    street = fields.CharField(max_length=100)
    city = fields.CharField(max_length=50)

class UserForm(Form):
    name = fields.CharField(max_length=100)
    address = FormField(form=AddressForm)
```

### FormFieldList

A field for lists of nested objects.

```python
from django_api_forms import FormFieldList

class PhoneForm(Form):
    number = fields.CharField(max_length=20)
    type = fields.CharField(max_length=10)

class UserForm(Form):
    name = fields.CharField(max_length=100)
    phones = FormFieldList(form=PhoneForm)
```

### EnumField

A field for enumeration values.

```python
from django_api_forms import EnumField
from enum import Enum

class UserType(Enum):
    ADMIN = 'admin'
    USER = 'user'

class UserForm(Form):
    name = fields.CharField(max_length=100)
    type = EnumField(enum=UserType)
```

### DictionaryField

A field for key-value pairs.

```python
from django_api_forms import DictionaryField

class MetadataForm(Form):
    metadata = DictionaryField(value_field=fields.CharField())
```

### FileField

A field for BASE64-encoded files.

```python
from django_api_forms import FileField

class DocumentForm(Form):
    document = FileField(max_length=10485760, mime=('application/pdf',))
```

### ImageField

A field for BASE64-encoded images.

```python
from django_api_forms import ImageField

class ProfileForm(Form):
    avatar = ImageField(max_length=10485760, mime=('image/jpeg', 'image/png'))
```

### RRuleField

A field for recurring date rules.

```python
from django_api_forms import RRuleField

class EventForm(Form):
    recurrence = RRuleField()
```

### GeoJSONField

A field for geographic data in GeoJSON format.

```python
from django_api_forms import GeoJSONField

class LocationForm(Form):
    geometry = GeoJSONField(srid=4326)
```

## Population Strategies

Django API Forms provides several population strategies for populating objects with form data.

### BaseStrategy

The default strategy that sets object attributes using `setattr`.

### IgnoreStrategy

A strategy that ignores the field during population.

### ModelChoiceFieldStrategy

A strategy for populating model choice fields.

### AliasStrategy

A strategy for populating fields with different names.

```python
from django_api_forms import Form
from django_api_forms.population_strategies import AliasStrategy

class MyForm(Form):
    class Meta:
        field_strategy = {
            'username': AliasStrategy(property_name='name')
        }

    username = fields.CharField(max_length=100)
```

## Settings

Django API Forms can be configured through Django settings.

### `DJANGO_API_FORMS_PARSERS`

A dictionary mapping content types to parser functions.

```python
DJANGO_API_FORMS_PARSERS = {
    'application/json': 'json.loads',
    'application/x-msgpack': 'msgpack.loads'
}
```

### `DJANGO_API_FORMS_POPULATION_STRATEGIES`

A dictionary mapping field types to population strategies.

```python
DJANGO_API_FORMS_POPULATION_STRATEGIES = {
    'django_api_forms.fields.FormFieldList': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django_api_forms.fields.FileField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django_api_forms.fields.ImageField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django_api_forms.fields.FormField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django.forms.models.ModelMultipleChoiceField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django.forms.models.ModelChoiceField': 'django_api_forms.population_strategies.ModelChoiceFieldStrategy'
}
```

### `DJANGO_API_FORMS_DEFAULT_POPULATION_STRATEGY`

The default population strategy to use when no specific strategy is defined.

```python
DJANGO_API_FORMS_DEFAULT_POPULATION_STRATEGY = 'django_api_forms.population_strategies.BaseStrategy'
```
