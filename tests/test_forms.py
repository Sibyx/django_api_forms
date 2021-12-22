import json
from typing import Optional

import msgpack
from django.forms import fields
from django.test import TestCase
from django.test.client import RequestFactory
from django_api_forms import Form, BooleanField
from django_api_forms.exceptions import UnsupportedMediaType
from django.db import models


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

    def test_clean_data_keys(self):
        class FunnyForm(Form):
            title = fields.CharField(required=True)
            code = fields.CharField(required=True)
            url = fields.CharField(required=False)
            description = fields.CharField(required=False)

            @classmethod
            def _normalize_url(cls, url: str) -> Optional[str]:
                if not url:
                    return None
                if url.startswith('http://'):
                    url = url.replace('http://', '')

                if not url.startswith('https://'):
                    url = f"https://{url}"

                return url

            def clean_url(self):
                return self._normalize_url(self.cleaned_data['url'])

        request_factory = RequestFactory()
        request = request_factory.post(
            '/test/',
            data={
                'title': "The Question",
                'code': 'the-question',
                'url': ''
            },
            content_type='application/json'
        )
        form = FunnyForm.create_from_request(request)
        self.assertTrue(form.is_valid())
        self.assertTrue(len(form.cleaned_data.keys()) == 3)
        self.assertIsNone(form.cleaned_data['url'])

    def test_meta_class_mapping(self):
        class FunnyForm(Form):
            class Meta:
                # source:destination
                mapping = {
                    'kode': 'code',
                    'titul': 'title'
                }

            title = fields.CharField(required=True)
            code = fields.CharField(required=True)
            url = fields.CharField(required=False)
            description = fields.CharField(required=False)

            @classmethod
            def _normalize_url(cls, url: str) -> Optional[str]:
                if not url:
                    return None
                if url.startswith('http://'):
                    url = url.replace('http://', '')

                if not url.startswith('https://'):
                    url = f"https://{url}"

                return url

            def clean_url(self):
                return self._normalize_url(self.cleaned_data['url'])

        request_factory = RequestFactory()
        request = request_factory.post(
            '/test/',
            data={
                'titul': "The Question",
                'kode': 'the-question',
                'url': ''
            },
            content_type='application/json'
        )
        form = FunnyForm.create_from_request(request)
        self.assertTrue(form.is_valid())
        self.assertTrue(len(form.cleaned_data.keys()) == 3)
        self.assertIsNone(form.cleaned_data['url'])

    def test_meta_class(self):
        class FunnyForm(Form):
            class Meta:
                # source:destination
                mapping = {
                    'kode': 'code',
                    'titul': 'title'
                }

                field_type_strategy = {
                    'django_api_forms.fields.BooleanField': 'django_api_forms.population_strategies.BooleanField'
                }

                field_strategy = {
                    'formed': 'django_api_forms.population_strategies.FormedStrategy'
                }

            title = fields.CharField(required=True)
            code = fields.CharField(required=True)
            url = fields.CharField(required=False)
            description = fields.CharField(required=False)
            formed = fields.IntegerField()
            has_award = BooleanField()


            @classmethod
            def _normalize_url(cls, url: str) -> Optional[str]:
                if not url:
                    return None
                if url.startswith('http://'):
                    url = url.replace('http://', '')

                if not url.startswith('https://'):
                    url = f"https://{url}"

                return url

            def clean_url(self):
                return self._normalize_url(self.cleaned_data['url'])

        request_factory = RequestFactory()
        request = request_factory.post(
            '/test/',
            data={
                'titul': "The Question",
                'kode': 'the-question',
                'url': '',
                'formed': '1970',
                'has_award': 'True'
            },
            content_type='application/json'
        )
        form = FunnyForm.create_from_request(request)
        self.assertTrue(form.is_valid())
        self.assertTrue(len(form.cleaned_data.keys()) == 5)
        self.assertIsNone(form.cleaned_data['url'])



    def test_empty_payload(self):
        class FunnyForm(Form):
            title = fields.CharField(required=False)

        class DummyObject:
            title = None

        request_factory = RequestFactory()
        request = request_factory.post(
            '/test/',
            data={},
            content_type='application/json'
        )
        form = FunnyForm.create_from_request(request)
        my_object = DummyObject()

        self.assertTrue(form.is_valid())
        form.populate(my_object)
