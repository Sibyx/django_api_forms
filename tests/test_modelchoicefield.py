from django.forms import ModelChoiceField, fields
from django.test import TestCase, RequestFactory
from django_api_forms import Form, EnumField
from tests.testapp.models import Album, Artist


class FormTests(TestCase):
    def setUp(self) -> None:
        self._my_artist = Artist.objects.create(
            id=1,
            name='Joy Division',
            genres=['rock', 'punk'],
            members=4
        )

    def test_no_prefix(self):
        class MyAlbumForm(Form):
            title = fields.CharField(max_length=100)
            year = fields.IntegerField()
            artist = ModelChoiceField(queryset=Artist.objects.all())
            type = EnumField(enum=Album.AlbumType, required=True)

        request_factory = RequestFactory()
        data = {
            'title': 'Unknown Pleasures',
            'year': 1979,
            'artist': 1,
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

        form.fill(my_model)
        self.assertIsInstance(my_model.artist, Artist)
        self.assertEqual(my_model.artist.pk, self._my_artist.pk)
        self.assertEqual(my_model.artist, self._my_artist)

    def test_field_name(self):
        class MyAlbumForm(Form):
            title = fields.CharField(max_length=100)
            year = fields.IntegerField()
            artist_name = ModelChoiceField(queryset=Artist.objects.all(), to_field_name='name')
            type = EnumField(enum=Album.AlbumType, required=True)

        request_factory = RequestFactory()
        data = {
            'title': 'Unknown Pleasures',
            'year': 1979,
            'artist_name': 'Joy Division',
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

        form.fill(my_model)
        self.assertIsInstance(my_model.artist, Artist)
        self.assertEqual(my_model.artist.pk, self._my_artist.pk)
        self.assertEqual(my_model.artist, self._my_artist)

    def test_pk(self):
        class MyAlbumForm(Form):
            title = fields.CharField(max_length=100)
            year = fields.IntegerField()
            artist_id = ModelChoiceField(queryset=Artist.objects.all())
            type = EnumField(enum=Album.AlbumType, required=True)

        request_factory = RequestFactory()
        data = {
            'title': 'Unknown Pleasures',
            'year': 1979,
            'artist_id': 1,
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

        form.fill(my_model)
        self.assertIsInstance(my_model.artist, Artist)
        self.assertEqual(my_model.artist.pk, self._my_artist.pk)
        self.assertEqual(my_model.artist, self._my_artist)
