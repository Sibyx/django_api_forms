from enum import Enum

from django.core.exceptions import ValidationError
from django.forms import fields

from django_request_formatter.fields import FieldList, FormField, FormFieldList, DictionaryField, EnumField
from django_request_formatter.forms import Form


class AlbumType(Enum):
    CD = 'cd'
    VINYL = 'vinyl'


class ArtistForm(Form):
    name = fields.CharField(required=True, max_length=100)
    genres = FieldList(field=fields.CharField(max_length=30))
    members = fields.IntegerField()


class SongForm(Form):
    title = fields.CharField(required=True, max_length=100)
    duration = fields.DurationField(required=False)


class AlbumForm(Form):
    title = fields.CharField(max_length=100)
    year = fields.IntegerField()
    artist = FormField(form=ArtistForm)
    songs = FormFieldList(form=SongForm)
    type = EnumField(enum=AlbumType, required=True)
    metadata = DictionaryField(fields.DateTimeField())

    def clean_year(self):
        if self.cleaned_data['year'] == 1992:
            raise ValidationError("Year 1992 is forbidden!", 'forbidden-value')
        return self.cleaned_data['year']

    def clean(self):
        if (self.cleaned_data['year'] == 1998) and (self.cleaned_data['artist']['name'] == "Nirvana"):
            raise ValidationError("Sounds like a bullshit", code='time-traveling')
        return self.cleaned_data
