
from django.forms import fields
from django.test import TestCase
from django_api_forms import Form


class FormIteratorTests(TestCase):
    def test_iter_fields(self):
        class TestForm(Form):
            field1 = fields.CharField(label='field1')
            field2 = fields.IntegerField(label='field2')

        form = TestForm()
        field_labels = [field.label for field in form]

        # Check that fields can be iterated over and contain the expected field names
        self.assertEqual(sorted(field_labels), ['field1', 'field2'])

    def test_getitem_field(self):
        class TestForm(Form):
            field1 = fields.CharField()
            field2 = fields.IntegerField()

        form = TestForm()

        field1 = form['field1']
        self.assertIsInstance(field1, fields.CharField)

        field2 = form['field2']
        self.assertIsInstance(field2, fields.IntegerField)

        with self.assertRaises(KeyError):
            form['nonexistent_field']
