# Tutorial

This library helps you to handle basic RESTful API use-cases with Django Forms fashion. Library kinda replaces
`django.forms.Form` with `django_api_forms.Form` and introduces few extra fields (boolean handling, BASE64
images/files, nesting).

`django_api_forms.Form` defines the format of the request and help you with:

- payload parsing (according to the `Content-Type` HTTP header)
- data validation and normalisation (using [Django validators](https://docs.djangoproject.com/en/4.1/ref/validators/)
or custom `clean_` method)
- BASE64 file/image upload
- construction of the basic validation response
- filling objects attributes (if possible, see exceptions) using `setattr` function (super handy for Django database
models)

## Construction

You can create form objects using class method `Form.create_from_request(request: Request) -> Form` which creates form
instance from Django requests using appropriate parser from
[Content-Type](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type) HTTP header. You can also pass
any extra argument into `Form.create_from_request(request, param1=request.GET.get('param'), param2=param2) -> Form`

```python
from tests.testapp.forms import AlbumForm

def my_view(request):
    form = AlbumForm.create_from_request(request=request, param=request.GET.get('param'))
```

Library by default keeps configuration for handling:

- JSON (using `jsong.loads`),
- [msgpack](https://msgpack.org/) (requires [msgpack](https://pypi.org/project/msgpack/) package).

You can extend or override that behavior by setting the `DJANGO_API_FORMS_PARSERS` variable in your `settings.py`.
Default settings for such variables are listed in the
[Example documentation page](https://sibyx.github.io/django_api_forms/example/#settings).

During construction `Form.dirty: List[str]` property is populated with property keys presented in the obtained payload
(dirty sluts!!).

### Mapping

You can use `Meta` class in specific `Form` class with optional dictionary type attribute `mapping = {}` which allows
you to map JSON attributes to `Form` attributes:

**JSON example**

```json
{
    "_name": "Queen",
    "formed": "1970",
    "has_award": true
}
```

**Python representation**

```python

from django.forms import fields

from django_api_forms import BooleanField, Form


class BandForm(Form):
    class Meta:
        mapping = {
            '_name': 'name'
        }

    name = fields.CharField(max_length=100)
    formed = fields.IntegerField()
    has_award = BooleanField()
```

## Validation and normalisation

This process is much more simple than in classic Django form. It consists of:

1. Iterating over form attributes:
   - calling `Field.clean(value)` method
   - calling `Form.clean_<field_name>` method
   - calling `Form.add_error((field_name, ), error)` in case of failures in clean methods
   - if field is marked as dirty, normalized attribute is saved to `Form.clean_data` property
2. Calling `Form.clean` method which returns final normalized values which will be presented in `Form.clean_data`
(feel free to override it, by default does nothing, useful for conditional validation, you can still add errors
using `Form.add_error()`). `Form.clean` is only called when there are no errors from previous section.

Normalized data are available in `Form.clean_data` property (keys suppose to correspond with values from `Form.dirty`).
Extra optional arguments are available in `Form.extras` property (keys suppose to correspond with values
from `Form` initialization)

Validation errors are presented for each field in `Form.errors: List[ValidationError]` property after
`Form.is_valid()` method is called.

As was mentioned above, you can extend property validation or normalisation by creating form method like
`clean_<property_name>`. You can add additional
[ValidationError](https://docs.djangoproject.com/en/4.1/ref/forms/validation/#raising-validationerror)
objects using `Form.add_error(field: Tuple, error: ValidationError)` method. Result is final normalised
value of the attribute.

```python
from django.forms import fields
from django.core.exceptions import ValidationError
from django_api_forms import Form

class BookForm(Form):
    title = fields.CharField(max_length=100)
    year = fields.IntegerField()

    def clean_title(self):
        if self.cleaned_data['title'] == "The Hitchhiker's Guide to the Galaxy":
            self.add_error(('title', ), ValidationError("Too cool!", code='too-cool'))

        if 'param' not in self.extras:
            raise ValidationError("You can use extra optional arguments in form validation!")
        return self.cleaned_data['title'].upper()

    def clean(self):
        if self.cleaned_data['title'] == "The Hitchhiker's Guide to the Galaxy" and self.cleaned_data['year'] < 1979:
            # Non field validation errors are present under key `$body` in Form.errors property
            raise ValidationError("Is it you Doctor?", code='time-travelling')

        if 'param' not in self.extras:
            self.add_error(
                ('param', ),
                ValidationError("You can use extra optional arguments in form validation!", code='param-where')
            )
        # The last chance to do some touchy touchy with the self.clean_data

        return self.cleaned_data
```

## Nesting

Django API Forms provides powerful support for nested data structures through specialized fields like `FormField` and `FormFieldList`. This allows you to validate complex JSON structures with nested objects and arrays.

### Nested Objects with FormField

The `FormField` allows you to embed one form inside another, enabling validation of nested objects:

```python
from django.forms import fields
from django_api_forms import Form, FormField

# Define a nested form
class AddressForm(Form):
    street = fields.CharField(max_length=100)
    city = fields.CharField(max_length=50)
    postal_code = fields.CharField(max_length=10)
    country = fields.CharField(max_length=50)

# Use the nested form in a parent form
class UserForm(Form):
    name = fields.CharField(max_length=100)
    email = fields.EmailField()
    address = FormField(form=AddressForm)  # Nested form
```

This setup can validate JSON like:

```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "address": {
        "street": "123 Main St",
        "city": "New York",
        "postal_code": "10001",
        "country": "USA"
    }
}
```

### Nested Arrays with FormFieldList

The `FormFieldList` field allows you to validate arrays of objects, where each object is validated against a specified form:

```python
from django.forms import fields
from django_api_forms import Form, FormFieldList

# Define a form for each item in the list
class PhoneNumberForm(Form):
    type = fields.CharField(max_length=20)
    number = fields.CharField(max_length=20)

# Use the form list in a parent form
class ContactForm(Form):
    name = fields.CharField(max_length=100)
    phone_numbers = FormFieldList(form=PhoneNumberForm)  # List of nested forms
```

This setup can validate JSON like:

```json
{
    "name": "John Doe",
    "phone_numbers": [
        {
            "type": "home",
            "number": "555-1234"
        },
        {
            "type": "work",
            "number": "555-5678"
        }
    ]
}
```

### Validation in Nested Forms

Each nested form performs its own validation. If a nested form fails validation, the errors are propagated to the parent form with the appropriate path:

```python
class AddressForm(Form):
    street = fields.CharField(max_length=100)

    def clean_street(self):
        if "PO Box" in self.cleaned_data['street']:
            raise ValidationError("PO Boxes are not accepted")
        return self.cleaned_data['street']
```

If validation fails, the error will be available in the parent form's errors with the path to the nested field.

## Database relationships

Django API Forms provides support for working with Django model relationships through Django's `ModelChoiceField` and `ModelMultipleChoiceField`.

### Single Relationships with ModelChoiceField

You can use `ModelChoiceField` to handle foreign key relationships:

```python
from django.forms import ModelChoiceField
from django_api_forms import Form
from myapp.models import Author

class BookForm(Form):
    title = fields.CharField(max_length=100)
    author = ModelChoiceField(queryset=Author.objects.all())
```

By default, this expects the primary key of the related object. You can customize this with the `to_field_name` parameter:

```python
class BookForm(Form):
    title = fields.CharField(max_length=100)
    author_username = ModelChoiceField(
        queryset=Author.objects.all(),
        to_field_name='username'
    )
```

### Many-to-Many Relationships with ModelMultipleChoiceField

For many-to-many relationships, you can use `ModelMultipleChoiceField`:

```python
from django.forms import ModelMultipleChoiceField
from django_api_forms import Form
from myapp.models import Tag

class ArticleForm(Form):
    title = fields.CharField(max_length=100)
    tags = ModelMultipleChoiceField(queryset=Tag.objects.all())
```

This expects a list of primary keys for the related objects.

### Populating Model Relationships

When using `populate()` with model relationships, the appropriate population strategy is used based on the field type. For `ModelChoiceField`, the `ModelChoiceFieldStrategy` is used by default, which handles setting the relationship correctly.

## Populate objects

Django API Forms provides a convenient way to populate objects (such as Django models) with validated form data using the `populate()` method.

**IMPORTANT**: Form fields `FormField`, `FormFieldList`, `FileField` and `ImageField` don't support automatic population.
You have to define a `populate_` method if you want these fields populated.

The `MyForm.populate(obj: Any, exclude: List[str] = None)` method fills the input `obj` using `setattr`
according to the form fields. Only data present in `cleaned_data` property (data from request) will be populated. You
can use it like this:

```python
from myapp.forms import AlbumForm
from myapp.models import Album

def my_view(request):
    form = AlbumForm.create_from_request(request)

    if not form.is_valid():
        # Handle validation error
        return JsonResponse({"errors": form.errors}, status=400)

    album = Album()
    form.populate(album)
    album.save()

    return JsonResponse({"id": album.id})
```

### Population strategies

Library provides ability to change population strategy for each field using `DJANGO_API_FORMS_POPULATION_STRATEGIES`
setting, or you can access settings directly `form.settings.POPULATION_STRATEGIES`. If there is no population strategy
provided for field type, the `DJANGO_API_FORMS_DEFAULT_POPULATION_STRATEGY` is used. Default values are listed bellow:

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
```

#### BaseStrategy

Object property is populated using `1:1` mapping and
[setattr](https://docs.python.org/3/library/functions.html#setattr) function.

#### IgnoreStrategy

If this strategy is used, the target object is kept untouched.

#### ModelChoiceField

Field name is expected to have format like this: `{field_name}(_{to_field_name})?` so library is able to automatically
resolve payload key postfix according to the `to_field_name` attribute. If there is no `to_field_name` provided,
field name should be `{field_name}` or `{field_name}_id`. Normalised data are present in `clean_data` under key
`{field_name}` (e.g. `clean_data['{field_name}']`).

Few examples (normalized data are in `clean_data['artist']` in all use-cases):

```python
from django.forms import ModelChoiceField
from django_api_forms import Form

from tests.testapp.models import Artist

class MyFormNoPostfix(Form):
    artist = ModelChoiceField(queryset=Artist.objects.all())

class MyFormFieldName(Form):
    artist_name = ModelChoiceField(
        queryset=Artist.objects.all(), to_field_name='name'
    )

class MyFormWithId(Form):
    artist_id = ModelChoiceField(queryset=Artist.objects.all())
```

### Customization

#### Creating custom strategy

You can create your own population strategy by inheriting `BaseStrategy` and overriding it's
`__call__(self, field, obj, key: str, value)` method.

```python
from django_api_forms.population_strategies import BaseStrategy


class ExampleStrategy(BaseStrategy):
    def __call__(self, field, obj, key: str, value):
        # Do your logic here
        setattr(obj, key, value)
```

#### Override strategy

You can override settings population strategies by creating your own population strategy in specific local `From` class using
`Meta` class with optional attributes `field_type_strategy = {}` or `field_strategy = {}`:
- `field_type_strategy`: Dictionary for overriding populate strategy on `Form` type attributes
- `field_strategy`: Dictionary for overriding populate strategies on `Form` attributes

```python
from django.forms import fields

from django_api_forms import BooleanField, Form
from django_api_forms.population_strategies import AliasStrategy


class BandForm(Form):
    class Meta:
        field_type_strategy = {
            'django_api_forms.fields.BooleanField': 'app.population_strategies.ExampleStrategy1'
        }

        field_strategy = {
            'formed': 'app.population_strategies.ExampleStrategy2',
            'has_award': AliasStrategy(property_name='awarded')
        }

    name = fields.CharField(max_length=100)
    formed = fields.IntegerField()
    has_award = BooleanField()
```

#### Using populate_ method

If you want to override population strategy for explicit field, you can define custom `populate_{field}` method inside
your form class:

```python
from django.forms import fields

from django_api_forms import Form, FormField, EnumField, DictionaryField
from tests.testapp.models import Album, Artist
from tests.testapp.forms import ArtistForm

class AlbumForm(Form):
    title = fields.CharField(max_length=100)
    year = fields.IntegerField()
    artist = FormField(form=ArtistForm)
    type = EnumField(enum=Album.AlbumType, required=True)
    metadata = DictionaryField(value_field=fields.DateTimeField())

    def populate_year(self, obj, value: int) -> int:
        return 2020

    def populate_artist(self, obj, value: dict) -> Artist:
        artist = Artist.objects.get_or_create(
            name=value['name']
        )
        artist.genres = value['genres']
        artist.members = value['members']
        artist.save()
        return artist
```

## File uploads

Django API Forms provides support for file uploads through BASE64-encoded data using the `FileField` and `ImageField` fields. This approach is particularly useful for RESTful APIs where traditional multipart form data might not be the preferred method.

### Using FileField

The `FileField` allows you to handle BASE64-encoded files in your API requests:

```python
from django.forms import fields
from django_api_forms import Form, FileField
from django.conf import settings

class DocumentForm(Form):
    title = fields.CharField(max_length=100)
    document = FileField(
        max_length=settings.DATA_UPLOAD_MAX_MEMORY_SIZE,
        mime=('application/pdf', 'application/msword')
    )
```

The client would send a request with the file encoded as a [Data URI](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs):

```json
{
    "title": "My Document",
    "document": "data:application/pdf;base64,JVBERi0xLjQKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVuZ3RoIDMgMCBSL0ZpbHRlci9GbGF0ZURlY29kZT4+CnN0cmVhbQp4nDPQM1Qo5ypUMFAw0DMwslAwtTTVMzIxV7AwMdSzMDNUKErlCtdSyOMyVADBonQuAJEWCTcKZW5kc3RyZWFtCmVuZG9iagoKMyAwIG9iago2OQplbmRvYmoKCjUgMCBvYmoKPDwKPj4KZW5kb2JqCgo2IDAgb2JqCjw8L0ZvbnQgNSAwIFIKL1Byb2NTZXRbL1BERi9UZXh0XQo+PgplbmRvYmoKCjEgMCBvYmoKPDwvVHlwZS9QYWdlL1BhcmVudCA0IDAgUi9SZXNvdXJjZXMgNiAwIFIvTWVkaWFCb3hbMCAwIDU5NSA4NDJdL0dyb3VwPDwvUy9UcmFuc3BhcmVuY3kvQ1MvRGV2aWNlUkdCL0kgdHJ1ZT4+L0NvbnRlbnRzIDIgMCBSPj4KZW5kb2JqCgo0IDAgb2JqCjw8L1R5cGUvUGFnZXMKL1Jlc291cmNlcyA2IDAgUgovTWVkaWFCb3hbIDAgMCA1OTUgODQyIF0KL0tpZHNbIDEgMCBSIF0KL0NvdW50IDE+PgplbmRvYmoKCjcgMCBvYmoKPDwvVHlwZS9DYXRhbG9nL1BhZ2VzIDQgMCBSCi9PcGVuQWN0aW9uWzEgMCBSIC9YWVogbnVsbCBudWxsIDBdCi9MYW5nKGVuLVVTKQo+PgplbmRvYmoKCjggMCBvYmoKPDwvQ3JlYXRvcjxGRUZGMDA1NzAwNzIwMDY5MDA3NDAwNjUwMDcyPgovUHJvZHVjZXI8RkVGRjAwNEMwMDY5MDA2MjAwNzIwMDY1MDA0RjAwNjYwMDY2MDA2OTAwNjMwMDY1MDAyMDAwMzYwMDJFMDAzMT4KL0NyZWF0aW9uRGF0ZShEOjIwMjMwMzEwMTIzNDU2KzAxJzAwJyk+PgplbmRvYmoKCnhyZWYKMCA5CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDI1MyAwMDAwMCBuIAowMDAwMDAwMDE5IDAwMDAwIG4gCjAwMDAwMDAxNTkgMDAwMDAgbiAKMDAwMDAwMDM5MSAwMDAwMCBuIAowMDAwMDAwMTc4IDAwMDAwIG4gCjAwMDAwMDAxOTkgMDAwMDAgbiAKMDAwMDAwMDQ4OSAwMDAwMCBuIAowMDAwMDAwNTg1IDAwMDAwIG4gCnRyYWlsZXIKPDwvU2l6ZSA5L1Jvb3QgNyAwIFIKL0luZm8gOCAwIFIKL0lEIFsgPEY3RDc3QjNEMjJCOUY5MjgyOTQ2QTNCQTYxRDk3NjEzPgo8RjdENzdCM0QyMkI5RjkyODI5NDZBM0JBNjFEOTc2MTM+IF0KL0RvY0NoZWNrc3VtIC9BQjQwRDdGOUE3QkIwQkIwMTlDNEQ4NkJCNkFDQkM1Qgo+PgpzdGFydHhyZWYKNzU5CiUlRU9GCg=="
}
```

### Using ImageField

The `ImageField` is similar to `FileField` but specifically for images. It performs additional validation to ensure the file is a valid image:

```python
from django.forms import fields
from django_api_forms import Form, ImageField
from django.conf import settings

class ProfileForm(Form):
    name = fields.CharField(max_length=100)
    avatar = ImageField(
        max_length=settings.DATA_UPLOAD_MAX_MEMORY_SIZE,
        mime=('image/jpeg', 'image/png')
    )
```

The client would send a request with the image encoded as a Data URI:

```json
{
    "name": "John Doe",
    "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFdwI2Q4g02QAAAABJRU5ErkJggg=="
}
```

### Handling Uploaded Files

When a form with a `FileField` or `ImageField` is validated, the field's value in `cleaned_data` is a Django `File` object. For `ImageField`, there's also an `image` attribute containing a Pillow `Image` object:

```python
def upload_profile(request):
    form = ProfileForm.create_from_request(request)

    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    # Access the file
    avatar_file = form.cleaned_data['avatar']

    # For ImageField, you can access the Pillow Image object
    image = avatar_file.image

    # Get the content type
    content_type = avatar_file.content_type  # e.g., 'image/png'

    # Save the file to disk or cloud storage
    with open(f"media/avatars/{form.cleaned_data['name']}.png", 'wb') as f:
        f.write(avatar_file.read())

    return JsonResponse({"status": "success"})
```

### Populating Models with File Fields

As mentioned in the "Populate objects" section, `FileField` and `ImageField` don't support automatic population. You need to define a custom `populate_` method:

```python
from django.forms import fields
from django_api_forms import Form, ImageField
from myapp.models import Profile

class ProfileForm(Form):
    name = fields.CharField(max_length=100)
    avatar = ImageField(max_length=10485760, mime=('image/jpeg', 'image/png'))

    def populate_avatar(self, obj, value):
        # Save the file to the model's ImageField
        filename = f"{obj.id}_avatar.png"
        obj.avatar.save(filename, value, save=False)
        return obj.avatar
```

This approach allows you to handle file uploads in a RESTful way without relying on multipart form data.
