import os

import pytest
from django.core.exceptions import ValidationError
from django.test import RequestFactory

from tests.testapp.forms import AlbumForm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_invalid(rf: RequestFactory):
    with open(f"{BASE_DIR}/tests/data/invalid.json") as f:
        request = rf.post('/foo/bar', data=f.read(), content_type='application/json')

    form = AlbumForm.create_from_request(request)

    assert form.is_valid(False) is False

    try:
        form.is_valid()
    except ValidationError as e:
        print(e)

    # with pytest.raises(ValidationError):
    #     form.is_valid()

