# Examples

This page provides examples of how to use Django API Forms in different scenarios.

## Configuration Settings

Django API Forms can be configured through Django settings. Here are the default settings:

```python
# Settings for population strategies
DJANGO_API_FORMS_POPULATION_STRATEGIES = {
    'django_api_forms.fields.FormFieldList': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django_api_forms.fields.FileField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django_api_forms.fields.ImageField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django_api_forms.fields.FormField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django.forms.models.ModelMultipleChoiceField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django.forms.models.ModelChoiceField': 'django_api_forms.population_strategies.ModelChoiceFieldStrategy'
}

# Default population strategy
DJANGO_API_FORMS_DEFAULT_POPULATION_STRATEGY = 'django_api_forms.population_strategies.BaseStrategy'

# Content type parsers
DJANGO_API_FORMS_PARSERS = {
    'application/json': 'json.loads',
    'application/x-msgpack': 'msgpack.loads'
}
```

## Basic Example: Music Album API

This example demonstrates a music album API with nested data structures, field mapping, and custom validation.

### JSON Request

```json
{
  "title": "Unknown Pleasures",
  "type": "vinyl",
  "artist": {
    "_name": "Joy Division",
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

### Python Implementation

```python
from enum import Enum

from django.core.exceptions import ValidationError
from django.forms import fields
from django.http import JsonResponse

from django_api_forms import FieldList, FormField, FormFieldList, DictionaryField, EnumField, AnyField, Form


class AlbumType(Enum):
    CD = 'cd'
    VINYL = 'vinyl'


class ArtistForm(Form):
    class Meta:
        mapping = {
            '_name': 'name'  # Map '_name' in JSON to 'name' in form
        }

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
    artist = FormField(form=ArtistForm)  # Nested form
    songs = FormFieldList(form=SongForm)  # List of nested forms
    type = EnumField(enum=AlbumType, required=True)
    metadata = DictionaryField(value_field=fields.DateTimeField())

    def clean_year(self):
        # Field-level validation
        if 'param' not in self.extras:
            raise ValidationError("You can use request GET params in form validation!")

        if self.cleaned_data['year'] == 1992:
            raise ValidationError("Year 1992 is forbidden!", 'forbidden-value')
        return self.cleaned_data['year']

    def clean(self):
        # Form-level validation
        if (self.cleaned_data['year'] == 1998) and (self.cleaned_data['artist']['name'] == "Nirvana"):
            raise ValidationError("Sounds like a bullshit", code='time-traveling')
        if 'param' not in self.extras:
            self.add_error(
                ('param', ),
                ValidationError("You can use extra optional arguments in form validation!", code='param-where')
            )
        return self.cleaned_data


# Django view example
def create_album(request):
    # Create form from request and pass extra parameters
    form = AlbumForm.create_from_request(request, param=request.GET.get('param'))

    if not form.is_valid():
        # Return validation errors
        return JsonResponse({"errors": form.errors}, status=400)

    # Access validated data
    album_data = form.cleaned_data

    # Do something with the data (e.g., save to database)
    # ...

    return JsonResponse({"status": "success", "id": 123})
```

## Example: User Registration with File Upload

This example demonstrates a user registration API with profile image upload.

### JSON Request

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "confirm_password": "securepassword123",
  "profile": {
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Software developer and music enthusiast",
    "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFdwI2Q4g02QAAAABJRU5ErkJggg=="
  }
}
```

### Python Implementation

```python
from django.core.exceptions import ValidationError
from django.forms import fields
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from django_api_forms import Form, FormField, ImageField


class ProfileForm(Form):
    first_name = fields.CharField(max_length=30)
    last_name = fields.CharField(max_length=30)
    bio = fields.CharField(max_length=500, required=False)
    avatar = ImageField(required=False, mime=('image/jpeg', 'image/png'))


class UserRegistrationForm(Form):
    username = fields.CharField(max_length=150)
    email = fields.EmailField()
    password = fields.CharField(min_length=8)
    confirm_password = fields.CharField()
    profile = FormField(form=ProfileForm)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        # Use Django's password validation
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise ValidationError("Passwords do not match")
        return cleaned_data

    def populate_avatar(self, user, value):
        # Custom population for avatar field
        if value and hasattr(user, 'profile'):
            filename = f"{user.username}_avatar.png"
            user.profile.avatar.save(filename, value, save=False)
        return value


def register_user(request):
    form = UserRegistrationForm.create_from_request(request)

    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    # Create user
    user = User(
        username=form.cleaned_data['username'],
        email=form.cleaned_data['email']
    )
    user.set_password(form.cleaned_data['password'])
    user.save()

    # Create profile
    profile_data = form.cleaned_data['profile']
    profile = user.profile  # Assuming a profile is created via signal
    profile.first_name = profile_data['first_name']
    profile.last_name = profile_data['last_name']
    profile.bio = profile_data.get('bio', '')

    # Handle avatar upload
    if 'avatar' in profile_data:
        form.populate_avatar(user, profile_data['avatar'])

    profile.save()

    return JsonResponse({"status": "success", "id": user.id})
```

## Example: API with Django Models

This example demonstrates how to use Django API Forms with Django models.

### Models

```python
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
```

### JSON Request

```json
{
  "title": "Introduction to Django API Forms",
  "content": "Django API Forms is a powerful library for validating API requests...",
  "category_id": 1,
  "tags": [1, 2, 3],
  "published": true
}
```

### Python Implementation

```python
from django.forms import fields, ModelChoiceField, ModelMultipleChoiceField
from django.http import JsonResponse

from django_api_forms import Form, BooleanField
from myapp.models import Article, Category, Tag


class ArticleForm(Form):
    title = fields.CharField(max_length=200)
    content = fields.CharField()
    category_id = ModelChoiceField(queryset=Category.objects.all())
    tags = ModelMultipleChoiceField(queryset=Tag.objects.all())
    published = BooleanField(required=False, default=False)

    def clean_title(self):
        title = self.cleaned_data['title']
        if Article.objects.filter(title=title).exists():
            raise ValidationError("An article with this title already exists")
        return title


def create_article(request):
    form = ArticleForm.create_from_request(request)

    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    # Create article
    article = Article()
    form.populate(article)
    article.save()

    # Many-to-many relationships need to be set after save
    article.tags.set(form.cleaned_data['tags'])

    return JsonResponse({
        "status": "success",
        "id": article.id,
        "title": article.title
    })
```

These examples demonstrate different ways to use Django API Forms in real-world scenarios. You can adapt them to your specific needs and requirements.
