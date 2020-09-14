import json

import msgpack
from django.test import TestCase
from django.test.client import RequestFactory
from django_api_forms import Form
from django_api_forms.exceptions import UnsupportedMediaType
from tests import settings
from tests.testapp.forms import AlbumForm
from tests.testapp.models import Album


class FormTests(TestCase):
    def test_create_from_request(self):
        # TEST: Form.create_from_request with VALID JSON data
        request_factory = RequestFactory()
        valid_test_data = {'message': ['turned', 'into', 'json']}
        request = request_factory.post(
            '/test/',
            data=valid_test_data,
            content_type='application/json'
        )
        form = Form.create_from_request(request)
        self.assertEqual(form._data, valid_test_data)

        # TEST: Form.create_from_request with INVALID JSON data
        request_factory = RequestFactory()
        invalid_test_data = '[1, 2,'
        request = request_factory.post(
            '/test/',
            data=invalid_test_data,
            content_type='application/json'
        )
        with self.assertRaises(json.JSONDecodeError):
            form = Form.create_from_request(request)

        # TEST: Form.create_from_request with VALID msgpack data
        request_factory = RequestFactory()
        valid_test_data = [1, 2, 3]
        packed_valid_test_data = msgpack.packb(valid_test_data)
        request = request_factory.post(
            '/test/',
            data=packed_valid_test_data,
            content_type='application/x-msgpack'
        )
        form = Form.create_from_request(request)
        self.assertEqual(form._data, valid_test_data)

        # TEST: Form.create_from_request with INVALID msgpack data
        request_factory = RequestFactory()
        invalid_test_data = 'invalid msgpack'
        request = request_factory.post(
            '/test/',
            data=invalid_test_data,
            content_type='application/x-msgpack'
        )
        with self.assertRaises(msgpack.exceptions.ExtraData):
            form = Form.create_from_request(request)

        # TEST: Form.create_from_request with unsupported content_type
        request_factory = RequestFactory()
        request = request_factory.post(
            '/test/',
            data='blah',
            content_type='blah'
        )
        with self.assertRaises(UnsupportedMediaType):
            form = Form.create_from_request(request)

        # TEST: Form.create_from_request with VALID JSON data and charset
        request_factory = RequestFactory()
        valid_test_data = {'message': ['turned', 'into', 'json']}
        request = request_factory.post(
            '/test/',
            data=valid_test_data,
            content_type='application/json; charset=utf-8'
        )
        form = Form.create_from_request(request)
        self.assertEqual(form._data, valid_test_data)

    def test_fill(self):
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

        # Fill form
        album = Album()
        form.fill(album)

        self.assertEqual(album.title, form.cleaned_data['title'])
        self.assertEqual(album.year, form.cleaned_data['year'])
        self.assertEqual(album.type, form.cleaned_data['type'])
        self.assertIsInstance(album.type, Album.AlbumType)
        self.assertEqual(album.metadata, form.cleaned_data['metadata'])
