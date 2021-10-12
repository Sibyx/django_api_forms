from django.conf import settings

DEFAULTS = {
    'POPULATION_STRATEGIES': {
        'django_api_forms.fields.FormFieldList': 'django_api_forms.population_strategies.IgnoreStrategy',
        'django_api_forms.fields.FileField': 'django_api_forms.population_strategies.IgnoreStrategy',
        'django_api_forms.fields.ImageField': 'django_api_forms.population_strategies.IgnoreStrategy',
        'django_api_forms.fields.FormField': 'django_api_forms.population_strategies.IgnoreStrategy',
        'django.forms.models.ModelMultipleChoiceField': 'django_api_forms.population_strategies.IgnoreStrategy',
        'django.forms.models.ModelChoiceField': 'django_api_forms.population_strategies.ModelChoiceFieldStrategy'
    },
    'DEFAULT_POPULATION_STRATEGY': 'django_api_forms.population_strategies.BaseStrategy',
    'PARSERS': {
        'application/json': 'json.loads',
        'application/x-msgpack': 'msgpack.loads'
    }
}


class Settings:
    def __getattr__(self, item):
        if item not in DEFAULTS:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

        django_setting = f"DJANGO_API_FORMS_{item}"
        default = DEFAULTS[item]

        if hasattr(settings, django_setting):
            customized_value = getattr(settings, django_setting)
            if isinstance(default, dict):
                value = {**default, **customized_value}
            else:
                value = customized_value
        else:
            value = default

        setattr(self, item, value)
        return value
