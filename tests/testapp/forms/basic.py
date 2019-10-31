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
    created_at = fields.DateField()
