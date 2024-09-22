# Example

## Settings

```python
DJANGO_API_FORMS_POPULATION_STRATEGIES = {
    'django_api_forms.fields.FormFieldList': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django_api_forms.fields.FileField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django_api_forms.fields.ImageField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django_api_forms.fields.FormField': 'django_api_forms.population_strategies.FormFieldStrategy',
    'django.forms.models.ModelMultipleChoiceField': 'django_api_forms.population_strategies.IgnoreStrategy',
    'django.forms.models.ModelChoiceField': 'django_api_forms.population_strategies.ModelChoiceFieldStrategy'
}

DJANGO_API_FORMS_DEFAULT_POPULATION_STRATEGY = 'django_api_forms.population_strategies.BaseStrategy'

DJANGO_API_FORMS_PARSERS = {
    'application/json': 'json.loads',
    'application/x-msgpack': 'msgpack.loads'
}
```

## JSON request

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

## Python implementation

```python
from enum import Enum

from django.core.exceptions import ValidationError
from django.forms import fields

from django_api_forms import FieldList, FormField, FormFieldList, DictionaryField, EnumField, AnyField, Form
from tests.testapp.models import Artist, Album


class AlbumType(Enum):
    CD = 'cd'
    VINYL = 'vinyl'


class ArtistForm(Form):
    class Meta:
        mapping = {
            '_name': 'name'
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
    artist = FormField(form=ArtistForm, model=Artist)
    songs = FormFieldList(form=SongForm)
    type = EnumField(enum=AlbumType, required=True)
    metadata = DictionaryField(value_field=fields.DateTimeField())

    def clean_year(self):
        if 'param' not in self.extras:
            raise ValidationError("You can use request GET params in form validation!")

        if self.cleaned_data['year'] == 1992:
            raise ValidationError("Year 1992 is forbidden!", 'forbidden-value')
        return self.cleaned_data['year']

    def clean(self):
        if (self.cleaned_data['year'] == 1998) and (self.cleaned_data['artist']['name'] == "Nirvana"):
            raise ValidationError("Sounds like a bullshit", code='time-traveling')
        if 'param' not in self.extras:
            self.add_error(
                ('param', ),
                ValidationError("You can use extra optional arguments in form validation!", code='param-where')
            )
        return self.cleaned_data


"""
Django view example
"""
def create_album(request):
    form = AlbumForm.create_from_request(request, param=request.GET.get('param'))
    if not form.is_valid():
        # Process your validation error
        print(form.errors)

    # Cleaned valid payload
    payload = form.cleaned_data
    print(payload)

    # Populate cleaned data into Django model
    album = Album()
    form.populate(album)

    # Save populated objects
    album.save()
    album.artist.save()

```
