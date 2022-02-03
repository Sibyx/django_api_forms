from django_api_forms.population_strategies import BaseStrategy


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
