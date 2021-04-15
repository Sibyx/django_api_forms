from django.core.exceptions import ValidationError
from django.forms import fields

from django_api_forms import Form, FieldList, AnyField, FormField, FormFieldList, EnumField, DictionaryField, ModelForm
from tests.testapp.models import Album, Artist


class ArtistForm(Form):
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
    artist = FormField(form=ArtistForm)
    songs = FormFieldList(form=SongForm)
    type = EnumField(enum=Album.AlbumType, required=True)
    metadata = DictionaryField(fields.DateTimeField())

    def clean_year(self):
        if self.cleaned_data['year'] == 1992:
            raise ValidationError("Year 1992 is forbidden!", 'forbidden-value')
        return self.cleaned_data['year']

    def clean(self):
        if (self.cleaned_data['year'] == 1998) and (self.cleaned_data['artist']['name'] == "Nirvana"):
            raise ValidationError("Sounds like a bullshit", code='time-traveling')
        return self.cleaned_data

    def fill_artist(self, obj, value: dict):
        return Artist(
            name=value.get('name'),
            genres=value.get('genres'),
            members=value.get('members')
        )


class ArtistModelForm(ModelForm):
    class Meta:
        model = Artist
