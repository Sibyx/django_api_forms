from django.core.exceptions import ValidationError
from django.forms import fields
from django import forms

from django_api_forms import Form, FieldList, AnyField, FormField, FormFieldList, EnumField, DictionaryField, \
    ModelForm, BooleanField
from tests.testapp.models import Album, Artist


class ArtistForm(Form):
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
    metadata = DictionaryField(fields.DateTimeField())

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


class NewAlbumForm(Form):
    album_id = forms.ModelChoiceField(queryset=Album.objects.all(), required=True)
    scheduled_at = fields.DateField(required=True)

    def clean_album_id(self):
        if self.cleaned_data.get('album_id').type in [Album.AlbumType.CD]:
        # if self.cleaned_data.get('album_id').type != Album.AlbumType.CD:
            self.add_error(
                'album_id',
                ValidationError('You did not select CD', code='not-cd')
            )
        else:
            return self.cleaned_data['album_id']


class ReleasesForm(Form):
    albums = FormFieldList(form=NewAlbumForm, required=False)
