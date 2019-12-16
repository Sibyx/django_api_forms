import os

from django.core.exceptions import ValidationError
from django.test import RequestFactory

from tests.testapp.forms import AlbumForm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_invalid(rf: RequestFactory):
    expected = {
        'songs': [
            {
                'title': [
                    ValidationError("This field is required.", code='required')
                ]
            }
        ],
        '__all__': [
            ValidationError("Sounds like a bullshit", code='time-travelling')
        ],
    }

    with open(f"{BASE_DIR}/tests/data/invalid.json") as f:
        request = rf.post('/foo/bar', data=f.read(), content_type='application/json')

    form = AlbumForm.create_from_request(request)

    assert form.is_valid() is False
    assert form.errors.__repr__() == expected.__repr__()
