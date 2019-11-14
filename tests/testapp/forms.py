from django.core.exceptions import ValidationError

from django_request_formatter.forms import Form
from django_request_formatter import fields


class ArtistForm(Form):
    name = fields.CharField(required=True, max_length=100)
    genres = fields.FieldList(field=fields.CharField(max_length=30))
    members = fields.IntegerField()


class SongForm(Form):
    title = fields.CharField(required=True, max_length=100)
    duration = fields.DurationField(required=False)


class AlbumForm(Form):
    title = fields.CharField(max_length=100)
    year = fields.IntegerField()
    artist = fields.FormField(form=ArtistForm)
    songs = fields.FormFieldList(form=SongForm)
    metadata = fields.DictionaryField(fields.DateTimeField())

    def validate_year(self, value):
        if value == "1992":
            raise ValidationError("Year 1992 is forbidden!")

    def validate(self):
        if (self._data['year'] == "1998") and (self._data['artist'] == "Nirvana"):
            raise ValidationError("Sounds like a bullshit")
