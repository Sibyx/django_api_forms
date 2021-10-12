from django.test import TestCase, override_settings

from django_api_forms.settings import Settings, DEFAULTS


class SettingsTests(TestCase):
    def test_invalid_attribute(self):
        settings = Settings()
        self.assertRaises(AttributeError, lambda: settings.INVALID_SETTING)

    @override_settings(DJANGO_API_FORMS_PARSERS={
        'application/json': 'json.loads',
        'application/x-msgpack': 'msgpack.unpackb',
        'application/bson': 'bson.loads'
    })
    def test_extend_dict(self):
        settings = Settings()
        self.assertEqual(settings.PARSERS['application/x-msgpack'], 'msgpack.unpackb')
        self.assertEqual(settings.PARSERS['application/bson'], 'bson.loads')

    @override_settings(
        DJANGO_API_FORMS_DEFAULT_POPULATION_STRATEGY='django_api_forms.population_strategies.IgnoreStrategy'
    )
    def test_override_simple(self):
        settings = Settings()
        self.assertEqual(
            settings.DEFAULT_POPULATION_STRATEGY, 'django_api_forms.population_strategies.IgnoreStrategy'
        )

    def test_default(self):
        settings = Settings()
        self.assertEqual(settings.POPULATION_STRATEGIES, DEFAULTS['POPULATION_STRATEGIES'])
