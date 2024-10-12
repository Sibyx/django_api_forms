from django.core.exceptions import ValidationError
from django.forms import fields, ModelChoiceField

from django_api_forms import Form, FieldList, AnyField, FormField, FormFieldList, EnumField, DictionaryField, \
    ModelForm, BooleanField
from django_api_forms.population_strategies import AliasStrategy
from tests.testapp.models import Album, Artist


class ArtistForm(Form):
    class Meta:
        field_strategy = {
            'has_label': AliasStrategy(property_name='has_own_label'),
        }

    has_label = BooleanField(required=False)
    name = fields.CharField(required=True, max_length=100)
    genres = FieldList(field=fields.CharField(max_length=30))
    members = fields.IntegerField()

class SongForm(Form):
    title = fields.CharField(required=True, max_length=100)
    duration = fields.DurationField(required=True)
    metadata = AnyField(required=False)


class AlbumForm(Form):
    class Meta:
        field_strategy = {
            'artist': 'tests.testapp.population_strategies.PopulateArtistStrategy'
        }

    title = fields.CharField(max_length=100)
    year = fields.IntegerField()
    artist = FormField(form=ArtistForm)
    songs = FormFieldList(form=SongForm)
    type = EnumField(enum=Album.AlbumType, required=True)
    metadata = DictionaryField(value_field=fields.DateTimeField())

    def clean_year(self):
        if self.cleaned_data['year'] == 1992:
            raise ValidationError("Year 1992 is forbidden!", 'forbidden-value')
        return self.cleaned_data['year']

    def clean(self):
        if (self.cleaned_data['year'] == 1998) and (self.cleaned_data['artist']['members'] == 4):
            raise ValidationError("Sounds like a bullshit", code='time-traveling')
        else:
            return self.cleaned_data


class ArtistModelForm(ModelForm):
    class Meta:
        model = Artist


class BandForm(Form):
    class Meta:
        field_type_strategy = {
            'django_api_forms.fields.BooleanField': 'tests.testapp.population_strategies.BooleanField'
        }

        field_strategy = {
            'formed': 'tests.testapp.population_strategies.FormedStrategy'
        }

    name = fields.CharField(max_length=100)
    formed = fields.IntegerField()
    has_award = BooleanField()
    emails = DictionaryField(value_field=fields.EmailField(max_length=14), required=False)
    albums = FormFieldList(form=AlbumForm, required=False)


class ConcertForm(Form):
    class Meta:
        field_type_strategy = {
            'django_api_forms.fields.BooleanField': 'tests.testapp.population_strategies.BooleanField'
        }

        field_strategy = {
            'artist': 'tests.testapp.population_strategies.PopulateArtistStrategy',
            'formed': 'tests.testapp.population_strategies.FormedStrategy'
        }

    place = fields.CharField(max_length=15)
    bands = FormFieldList(form=BandForm)
    organizer_id = ModelChoiceField(queryset=Artist.objects.all())
    emails = FieldList(fields.EmailField(max_length=14))
