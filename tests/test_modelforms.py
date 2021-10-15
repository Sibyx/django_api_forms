from django.conf import settings
from django.test import RequestFactory, TestCase

from tests.testapp.forms import ArtistModelForm


class ValidationTests(TestCase):
    def test_valid(self):
        rf = RequestFactory()
        expected = {
            'name': "Joy Division",
            'genres': ['rock', 'punk', 'post-punk'],
            'members': 4
        }

        with open(f"{settings.BASE_DIR}/data/valid_artist.json") as f:
            request = rf.post('/foo/bar', data=f.read(), content_type='application/json')

        form = ArtistModelForm.create_from_request(request)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, expected)
