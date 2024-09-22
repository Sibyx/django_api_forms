from django.forms import fields
from django.test import RequestFactory, TestCase

from django_api_forms import Form, FieldList, AnyField, FormField, EnumField
from tests.testapp.models import Album, Song, Artist


class ArtistForm(Form):
    name = fields.CharField(required=True, max_length=100)
    genres = FieldList(field=fields.CharField(max_length=30))
    members = fields.IntegerField()


class AlbumForm(Form):
    title = fields.CharField(max_length=100)
    year = fields.IntegerField()
    type = EnumField(enum=Album.AlbumType, required=True)
    artist = FormField(form=ArtistForm, model=Artist)


class SongForm(Form):
    title = fields.CharField(required=True, max_length=100)
    duration = fields.DurationField(required=True)
    metadata = AnyField(required=False)
    album = FormField(form=AlbumForm, model=Album)


class ValidationTests(TestCase):
    def test_valid(self):
        rf = RequestFactory()

        data = {
            "title": "The Quirky Tune",
            "duration": "00:03:28",
            "metadata": {
                "genre": "Comedy Rock",
                "mood": "Happy",
                "lyricist": "Joe Jokester"
            },
            "album": {
                "title": "Laughter and Chords",
                "year": 2021,
                "type": "vinyl",
                "artist": {
                    "name": "The Chuckle Squad",
                    "genres": ["Comedy Rock", "Parody"],
                    "members": 6,
                }
            }
        }

        request = rf.post('/foo/bar', data=data, content_type='application/json')

        form = SongForm.create_from_request(request)

        self.assertTrue(form.is_valid())

        song = Song()
        form.populate(song)

        self.assertIsInstance(song.album, Album)
        self.assertIsInstance(song.album.artist, Artist)

        self.assertEqual(song.album.title, data['album']['title'])
        self.assertEqual(song.album.artist.name, data['album']['artist']['name'])
