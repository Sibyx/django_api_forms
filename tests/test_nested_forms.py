from django.test import TestCase, RequestFactory

from django.conf import settings

from tests.testapp.forms import ConcertForm
from tests.testapp.models import Artist


class NestedFormsTests(TestCase):

    def setUp(self) -> None:
        self._my_artist = Artist.objects.create(
            id=1,
            name='Organizer',
            genres=['rock', 'punk'],
            members=4
        )

    def test_nested_forms(self):
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
        print()
        self.assertEqual(error, expected)
