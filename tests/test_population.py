from django.test import TestCase
from django.test.client import RequestFactory
from tests import settings
from tests.testapp.forms import AlbumForm, BandForm
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
        self.assertWarns(DeprecationWarning, lambda: form.fill(album))
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
                'name': "Queen",
                'formed': '1870',
                'has_award': 'False'
            },
            content_type='application/json'
        )
        form = BandForm.create_from_request(request)
        self.assertTrue(form.is_valid())

        # Populate form
        band = Band()
        self.assertWarns(DeprecationWarning, lambda: form.fill(band))
        form.populate(band)

        self.assertEqual(band.name, form.cleaned_data['name'])
        self.assertEqual(band.formed, 2000)
        self.assertEqual(band.has_award, True)
