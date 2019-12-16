import datetime
import os

from django.test import RequestFactory

from tests.testapp.forms import AlbumForm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_valid(rf: RequestFactory):
    expected = {
        'title': "Unknown Pleasures",
        'year': 1979,
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
                'duration': datetime.timedelta(seconds=288)
            }
        ],
        'metadata': {
            'created_at': datetime.datetime.strptime('2019-10-21T18:57:03+01:00', "%Y-%m-%dT%H:%M:%S%z"),
            'updated_at': datetime.datetime.strptime('2019-10-21T18:57:03+01:00', "%Y-%m-%dT%H:%M:%S%z"),
        }
    }

    with open(f"{BASE_DIR}/tests/data/valid.json") as f:
        request = rf.post('/foo/bar', data=f.read(), content_type='application/json')

    form = AlbumForm.create_from_request(request)

    assert form.is_valid() is True
    assert form.cleaned_data == expected
