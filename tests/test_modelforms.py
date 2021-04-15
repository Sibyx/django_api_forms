from django_api_forms import ModelForm
from tests.testapp.models import Artist


class ArtistModelForm(ModelForm):
    class Meta:
        model = Artist


wtf = ArtistModelForm()
