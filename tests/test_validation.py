import datetime

from django.conf import settings
from django.test import RequestFactory, TestCase

from tests.testapp.forms import AlbumForm
from tests.testapp.models import Album


class ValidationTests(TestCase):
    def test_invalid(self):
        rf = RequestFactory()

        expected = {
            "errors": [
                {
                    "code": "required",
                    "message": "This field is required.",
                    "path": [
                        "songs",
                        0,
                        "title"
                    ]
                },
                {
                    "code": "required",
                    "message": "This field is required.",
                    "path": [
                        "songs",
                        0,
                        "duration"
                    ]
                },
                {
                    "code": "required",
                    "message": "This field is required.",
                    "path": [
                        "songs",
                        1,
                        "title"
                    ]
                },
                {
                    "code": "invalid",
                    "message": "Enter a valid date/time.",
                    "path": [
                        "metadata",
                        "error_at"
                    ]
                },
                {
                    "code": "time-traveling",
                    "message": "Sounds like a bullshit",
                    "path": [
                        "$body"
                    ]
                }
            ]
        }

        with open(f"{settings.BASE_DIR}/data/invalid.json") as f:
            request = rf.post('/foo/bar', data=f.read(), content_type='application/json')

        form = AlbumForm.create_from_request(request)

        self.assertFalse(form.is_valid())
        error = {
            'errors': [item.to_dict() for item in form._errors]
        }
        self.assertEqual(error, expected)

    def test_valid(self):
        rf = RequestFactory()
        expected = {
            'title': "Unknown Pleasures",
            'year': 1979,
            'type': Album.AlbumType.VINYL,
            'artist': {
                'name': "Joy Division",
                'genres': ['rock', 'punk'],
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
                            "offset": 0,
                            "byteLength": 2048
                        },
                        'header': {
                            "majorVersion": 3,
                            "minorRevision": 0,
                            "flagsOctet": 0,
                            "unsynchronisationFlag": False,
                            "extendedHeaderFlag": False,
                            "experimentalIndicatorFlag": False,
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
        self.assertEqual(form.cleaned_data, expected)
