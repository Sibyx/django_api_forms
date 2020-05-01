import json

import msgpack
from django.test import TestCase
from django.test.client import RequestFactory
from django_api_forms import Form
from django_api_forms.exceptions import UnsupportedMediaType


class FormTests(TestCase):
    def test_create_from_request(self):
        # TEST: Form.create_from_request with VALID JSON data
        request_factory = RequestFactory()
        valid_test_data = {'message': ['turned', 'into', 'json']}
        request = request_factory.post(
            '/test/',
            data=valid_test_data,
            content_type='application/json')
        form = Form.create_from_request(request)
        self.assertEqual(form._data, valid_test_data)

        # TEST: Form.create_from_request with INVALID JSON data
        request_factory = RequestFactory()
        invalid_test_data = '[1, 2,'
        request = request_factory.post(
            '/test/',
            data=invalid_test_data,
            content_type='application/json')
        with self.assertRaises(json.JSONDecodeError):
            form = Form.create_from_request(request)

        # TEST: Form.create_from_request with VALID msgpack data
        request_factory = RequestFactory()
        valid_test_data = [1, 2, 3]
        packed_valid_test_data = msgpack.packb(valid_test_data)
        request = request_factory.post(
            '/test/',
            data=packed_valid_test_data,
            content_type='application/x-msgpack')
        form = Form.create_from_request(request)
        self.assertEqual(form._data, valid_test_data)

        # TEST: Form.create_from_request with INVALID msgpack data
        request_factory = RequestFactory()
        invalid_test_data = 'invalid msgpack'
        request = request_factory.post(
            '/test/',
            data=invalid_test_data,
            content_type='application/x-msgpack')
        with self.assertRaises(msgpack.exceptions.ExtraData):
            form = Form.create_from_request(request)

        # TEST: Form.create_from_request with unsupported content_type
        request_factory = RequestFactory()
        request = request_factory.post(
            '/test/',
            data='blah',
            content_type='blah')
        with self.assertRaises(UnsupportedMediaType):
            form = Form.create_from_request(request)
