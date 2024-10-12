from django.forms import fields
from django.test import TestCase
from django.test.client import RequestFactory

from django_api_forms import Form, EnumField, FormField
from django_api_forms.exceptions import ApiFormException
from tests import settings
from tests.testapp.forms import AlbumForm, BandForm, ArtistForm, ConcertForm
from tests.testapp.models import Album, Artist, Band


class PopulationTests(TestCase):
    def test_populate(self):
        # Create form from request
        with open(f"{settings.BASE_DIR}/data/valid.json") as f:
            payload = f.read()
        request_factory = RequestFactory()
        request = request_factory.post(
            '/test/',
            data=payload,
            content_type='application/json'
        )
        form = AlbumForm.create_from_request(request)
        self.assertTrue(form.is_valid())

        # Populate form
        album = Album()
        form.populate(album)

        self.assertEqual(album.title, form.cleaned_data['title'])
        self.assertEqual(album.year, form.cleaned_data['year'])
        self.assertEqual(album.type, form.cleaned_data['type'])
        self.assertIsInstance(album.type, Album.AlbumType)
        self.assertEqual(album.metadata, form.cleaned_data['metadata'])

        # Populate method tests
        self.assertIsInstance(album.artist, Artist)
        self.assertEqual(album.artist.name, "Joy Division")

    def test_meta_class_populate(self):
        # Create form from request
        request_factory = RequestFactory()
        request = request_factory.post(
            '/test/',
            data={
                'name': 'Queen',
                'formed': '1870',
                'has_award': False
            },
            content_type='application/json'
        )
        form = BandForm.create_from_request(request)
        self.assertTrue(form.is_valid())

        # Populate form
        band = Band()
        form.populate(band)

        self.assertEqual(band.name, form.cleaned_data['name'])
        self.assertEqual(band.formed, 2000)
        self.assertEqual(band.has_award, True)

    def test_invalid_populate(self):
        # Create form from request
        with open(f"{settings.BASE_DIR}/data/valid.json") as f:
            payload = f.read()
        request_factory = RequestFactory()
        request = request_factory.post(
            '/test/',
            data=payload,
            content_type='application/json'
        )
        form = AlbumForm.create_from_request(request)

        album = Album()
        with self.assertRaisesMessage(ApiFormException, str('No clean data provided! Try to call is_valid() first.')):
            form.populate(album)

    def test_form_method_populate(self):
        class MyAlbumForm(Form):
            title = fields.CharField(max_length=100)
            year = fields.IntegerField()
            artist = FormField(form=ArtistForm)
            type = EnumField(enum=Album.AlbumType, required=True)

            def populate_year(self, obj, value: int) -> int:
                return 2020

            def populate_artist(self, obj, value: dict) -> Artist:
                artist = Artist()

                artist.name = value['name']
                artist.genres = value['genres']
                artist.members = value['members']

                obj.artist = artist

                return artist

        request_factory = RequestFactory()
        data = {
            'title': 'Unknown Pleasures',
            'year': 1979,
            'artist': {
                "name": "Punk Pineapples",
                "genres": ["Punk", "Tropical Rock"],
                "members": 5
            },
            'type': 'vinyl'
        }

        request = request_factory.post(
            '/test/',
            data=data,
            content_type='application/json'
        )

        my_model = Album()
        form = MyAlbumForm.create_from_request(request)
        self.assertTrue(form.is_valid())

        form.populate(my_model)
        self.assertIsInstance(my_model.artist, Artist)
        self.assertEqual(my_model.year, 2020)
        self.assertEqual(my_model.artist.name, 'Punk Pineapples')

    def test_alias_strategy(self):
        request_factory = RequestFactory()
        data = {
            'name': "Frank",
            'genres': ["Rock", "Alternative"],
            'members': 4,
            'has_label': True
        }

        request = request_factory.post(
            '/test/',
            data=data,
            content_type='application/json'
        )

        artist = Artist()
        form = ArtistForm.create_from_request(request)
        self.assertTrue(form.is_valid())

        form.populate(artist)
        self.assertIsInstance(artist, Artist)
        self.assertEqual(artist.has_own_label, data['has_label'])
        self.assertEqual(artist.name, data['name'])
