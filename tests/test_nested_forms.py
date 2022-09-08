import datetime

from django.test import TestCase, RequestFactory
from django.conf import settings

from tests.testapp.forms import ConcertForm
from tests.testapp.models import Artist, Album


class NestedFormsTests(TestCase):

    def setUp(self) -> None:
        self._my_artist = Artist.objects.create(
            id=1,
            name='Organizer',
            genres=['rock', 'punk'],
            members=4
        )

    def test_invalid(self):
        expected = {
            "errors": [
                {
                    'code': 'invalid',
                    'message': 'Enter a valid email address.',
                    'path': ['bands', 0, 'emails', '0']
                },
                {
                    'code': 'max_length',
                    'message': '',
                    'path': ['bands', 0, 'emails', '0']
                },
                {
                    'code': 'max_length',
                    'message': '',
                    'path': ['bands', 0, 'emails', '1']
                },
                {
                    "code": "required",
                    "message": "This field is required.",
                    "path": ["bands", 1, "albums", 0, "songs", 0, "title"]
                },
                {
                    "code": "required",
                    "message": "This field is required.",
                    "path": ["bands", 1, "albums", 0, "songs", 0, "duration"]
                },
                {
                    "code": "required",
                    "message": "This field is required.",
                    "path": ["bands", 1, "albums", 0, "songs", 1, "title"]
                },
                {
                    "code": "invalid",
                    "message": "Enter a valid date/time.",
                    "path": ["bands", 1, "albums", 0, "metadata", "error_at"]
                },
                {
                    "code": "time-traveling",
                    "message": "Sounds like a bullshit",
                    "path": ["bands", 1, "albums", 0, "$body"]
                },
                {
                    "code": "invalid",
                    "message": "Enter a valid email address.",
                    "path": ["emails", 0]
                },
                {
                    "code": "max_length",
                    "message": "",
                    "path": ["emails", 0]
                },
                {
                    "code": "max_length",
                    "message": "",
                    "path": ["emails", 1]
                }
            ]
        }
        rf = RequestFactory()

        with open(f"{settings.BASE_DIR}/data/invalid_concert.json") as f:
            request = rf.post('/foo/bar', data=f.read(), content_type='application/json')

        form = ConcertForm.create_from_request(request)

        self.assertFalse(form.is_valid())
        error = {
            'errors': [item.to_dict() for item in form._errors]
        }
        self.assertEqual(error, expected)

    def test_valid(self):
        expected = {
            "place": "Bratislava",
            "bands": [
                {
                    "name": "Queen",
                    "formed": 1970,
                    "has_award": False,
                    "emails": {
                        "0": "em@il.com",
                        "1": "v@lid.com"
                    },
                    "albums": [
                        {
                            "title": "Unknown Pleasures",
                            "year": 1979,
                            "artist": {
                                "name": "Joy Division",
                                "genres": [
                                    "rock",
                                    "punk"
                                ],
                                "members": 4
                            },
                            "songs": [
                                {
                                    "title": "Disorder",
                                    "duration": datetime.timedelta(seconds=209)
                                },
                                {
                                    "title": "Day of the Lords",
                                    "duration": datetime.timedelta(seconds=288),
                                    "metadata": {
                                        "_section": {
                                            "type": "ID3v2",
                                            "offset": 0,
                                            "byteLength": 2048
                                        }
                                    }
                                }
                            ],
                            "type": Album.AlbumType.VINYL,
                            "metadata": {
                                "created_at": datetime.datetime.strptime(
                                    "2019-10-21T18:57:03+0100", "%Y-%m-%dT%H:%M:%S%z"
                                ),
                                "updated_at": datetime.datetime.strptime(
                                    "2019-10-21T18:57:03+0100", "%Y-%m-%dT%H:%M:%S%z"
                                ),
                            }
                        }
                    ]
                },
                {
                    "name": "The Beatles",
                    "formed": 1960,
                    "has_award": True,
                    "albums": [
                        {
                            "title": "Unknown Pleasures",
                            "year": 1997,
                            "artist": {
                                "name": "Nirvana",
                                "genres": [
                                    "rock",
                                    "punk"
                                ],
                                "members": 4
                            },
                            "songs": [
                                {
                                    "title": "Hey jude",
                                    "duration": datetime.timedelta(seconds=140)
                                },
                                {
                                    "title": "Let it be",
                                    "duration": datetime.timedelta(seconds=171)
                                },
                                {
                                    "title": "Day of the Lords",
                                    "duration": datetime.timedelta(seconds=288),
                                    "metadata": {
                                        "_section": {
                                            "type": "ID3v2",
                                            "offset": 0,
                                            "byteLength": 2048
                                        }
                                    }
                                }
                            ],
                            "type": Album.AlbumType.VINYL,
                            "metadata": {
                                "created_at": datetime.datetime.strptime(
                                    "2019-10-21T18:57:03+0100", "%Y-%m-%dT%H:%M:%S%z"
                                ),
                                "updated_at": datetime.datetime.strptime(
                                    "2019-10-21T18:57:03+0100", "%Y-%m-%dT%H:%M:%S%z"
                                ),
                            }
                        }
                    ]
                }
            ],
            "organizer_id": self._my_artist,
            "emails": [
                "em@il.com",
                "v@lid.com"
            ]
        }

        rf = RequestFactory()

        with open(f"{settings.BASE_DIR}/data/valid_concert.json") as f:
            request = rf.post('/foo/bar', data=f.read(), content_type='application/json')

        form = ConcertForm.create_from_request(request)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, expected)
