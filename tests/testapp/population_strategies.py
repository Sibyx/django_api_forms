from django_api_forms.population_strategies import BaseStrategy
from tests.testapp.models import Artist


class BooleanField(BaseStrategy):
    def __call__(self, field, obj, key: str, value):
        if value is True:
            value = False
        else:
            value = True

        setattr(obj, key, value)


class FormedStrategy(BaseStrategy):
    def __call__(self, field, obj, key: str, value):
        if value > 2021 or value < 1900:
            value = 2000

        setattr(obj, key, value)


class PopulateArtistStrategy(BaseStrategy):
    def __call__(self, field, obj, key: str, value):
        artist = Artist(
            name=value.get('name'),
            genres=value.get('genres'),
            members=value.get('members')
        )

        setattr(obj, key, artist)
