import datetime

from django.conf import settings
from django.test import RequestFactory, TestCase

from django_api_forms.exceptions import DetailedValidationError
from tests.testapp.forms import AlbumForm
from tests.testapp.models import Album


class ValidationTests(TestCase):
    def test_invalid(self):
        rf = RequestFactory()
        expected = [
            DetailedValidationError(
                message="This field is required.",
                path=('songs', 1, 'title'),
                code='required'
            ),
            DetailedValidationError(
                message="List has to contains at least %(min_length)s items.",
                path='songs',
                code='too-short',
                params={'min_length': 3}
            ),
            DetailedValidationError(
                message="Sounds like a bullshit.",
                path='$body',
                code='time-travelling'
            )
        ]

        with open(f"{settings.BASE_DIR}/data/invalid.json") as f:
            request = rf.post('/foo/bar', data=f.read(), content_type='application/json')

        form = AlbumForm.create_from_request(request)

        self.assertFalse(form.is_valid())
        self.assertListEqual(form.errors, expected)

    def test_valid(self):
        rf = RequestFactory()
        expected = {
            'title': "Unknown Pleasures",
            'year': 1979,
            'type': Album.AlbumType.VINYL,
            'artist': {
                'name': "Joy Division",
                'genres': ['rock', 'punk', 'post-punk'],
                'members': 4
            },
            'songs': [
                {
                    'title': "Disorder",
                    'duration': datetime.timedelta(seconds=209)
                },
                {
                    'title': "Day of the Lords",
                    'duration': datetime.timedelta(seconds=288),
                    'metadata': {
                        '_section': {
                            "type": "ID3v2",
                        },
                        'header': {
                            "majorVersion": 3,
                            "size": 2038
                        }
                    }
                }
            ],
            'metadata': {
                'created_at': datetime.datetime.strptime('2019-10-21T18:57:03+0100', "%Y-%m-%dT%H:%M:%S%z"),
                'updated_at': datetime.datetime.strptime('2019-10-21T18:57:03+0100', "%Y-%m-%dT%H:%M:%S%z"),
            }
        }

        with open(f"{settings.BASE_DIR}/data/valid.json") as f:
            request = rf.post('/foo/bar', data=f.read(), content_type='application/json')

        form = AlbumForm.create_from_request(request)

        self.assertTrue(form.is_valid())
        self.assertDictEqual(form.cleaned_data, expected)
