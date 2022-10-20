"""
Based on Django's field tests:
https://github.com/django/django/tree/stable/3.0.x/tests/forms_tests/field_tests
"""
import datetime
import logging
from decimal import Decimal
from enum import Enum

from unittest import mock
from uuid import UUID

from django.conf import settings
from django.core.files import File
from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError, fields
from django.test import SimpleTestCase
from django_api_forms import AnyField, BooleanField, DictionaryField, EnumField, FieldList, Form, FormField, \
    FormFieldList, FileField, ImageField
from django_api_forms.exceptions import ApiFormException


def log_input(val):
    """
    Logs info about attempted form field input values.

    Mainly for tests that can raise ValidationError, because ValidationError
    sometimes doesn't show the attempted value and a raised exception doesn't
    return a value for assert (which does show the attempted value).

    Also helpful for showing attempted input with assertRaisesMessage where
    the input value is defined in a loop.
    """
    logging.info('attempted input: "%s", type: "%s"', val, type(val))


class BooleanFieldTests(SimpleTestCase):
    FALSEY_VALUES = [
        False,
        0,
        '0',
        'False',
        'false',
        #  'FaLsE',
    ]
    TRUTHY_VALUES = [
        1,
        '1',
        True,
        'true',
        'True',
        #  'django_api_forms rocks',
    ]

    def test_booleanfield_required(self):
        bool_field = BooleanField()

        # TEST: required=True - falsy values return False
        for falsey_val in self.FALSEY_VALUES:
            log_input(falsey_val)
            self.assertFalse(bool_field.clean(falsey_val))

        # TEST: required=True - empty values throw error
        expected_error = "'This field is required.'"
        for empty_val in list(EMPTY_VALUES):  # (None, '', [], (), {})
            with self.assertRaisesMessage(ValidationError, expected_error):
                log_input(empty_val)
                bool_field.clean(empty_val)

        # TEST: truthy values return True
        for truthy_val in self.TRUTHY_VALUES:
            log_input(truthy_val)
            self.assertTrue(bool_field.clean(truthy_val))

    def test_booleanfield_required_false(self):
        bool_field = BooleanField(required=False)

        # TEST: required=False - falsy values return False
        for falsey_val in self.FALSEY_VALUES:
            log_input(falsey_val)
            self.assertFalse(bool_field.clean(falsey_val))

        # TEST: required=False - empty values return false
        for empty_val in EMPTY_VALUES:
            log_input(empty_val)
            self.assertFalse(bool_field.clean(empty_val))

        # TEST: truthy values return True
        for truthy_val in self.TRUTHY_VALUES:
            log_input(truthy_val)
            self.assertTrue(bool_field.clean(truthy_val))


class FieldListTests(SimpleTestCase):
    def test_fieldlist_init(self):
        # TEST: initialize FieldList with an instance of Field
        FieldList(field=fields.IntegerField())

        # TEST: initialize FieldList with non-Fields - throws an error
        expected_error = FieldList.default_error_messages['not_field']
        for non_field in [1, 'blah'] + list(EMPTY_VALUES):
            with self.assertRaisesMessage(ApiFormException, str(expected_error)):
                log_input(non_field)
                FieldList(field=non_field)

    def test_fieldlist_required(self):
        field_list = FieldList(field=fields.IntegerField())

        # TEST: valid input
        valid_val = [1, 2, 3]
        self.assertEqual(valid_val, field_list.clean(valid_val))

        # TEST: invalid input (individual non-list truthy values)
        invalid_vals = [True, 1, datetime.datetime.now(), 'blah', {'blah'}]
        expected_error = FieldList.default_error_messages['not_list']
        for invalid_val in invalid_vals:
            with self.assertRaisesMessage(ValidationError, str(expected_error)):
                field_list.clean(invalid_val)

        # TEST: invalid input (list of values the FieldList's IntegerField considers invalid)
        invalid_vals = [False, datetime.datetime.now(), 'blah', {'blah'}]
        expected_error = str(['Enter a whole number.'] * len(invalid_vals))
        with self.assertRaisesMessage(ValidationError, expected_error):
            field_list.clean(invalid_vals)

        # TEST: invalid input (list of values that the FieldList's IntegerField considers empty)
        invalid_vals = list(EMPTY_VALUES)
        expected_error = str(['This field is required.'] * len(invalid_vals))
        with self.assertRaisesMessage(ValidationError, expected_error):
            field_list.clean(invalid_vals)

        # TEST: required=True - empty values outside of a list throw error
        for empty_value in EMPTY_VALUES:
            with self.assertRaisesMessage(ValidationError, "['This field is required.']"):
                field_list.clean(empty_value)

    def test_fieldlist_required_false(self):
        field_list = FieldList(field=fields.IntegerField(), required=False)

        # TEST: list of values matching the FieldList's field
        test_val = [1, 2, 3, 4]
        self.assertEqual(test_val, field_list.clean(test_val))

        # TEST: required=False - empty values outside of a list return []
        for empty_val in EMPTY_VALUES:
            self.assertEqual([], field_list.clean(empty_val))

    def test_min_length(self):
        form_field_list = FieldList(field=fields.IntegerField(), min_length=2)

        # TEST: valid input
        valid_val = [1, 2]
        self.assertEqual(valid_val, form_field_list.clean(valid_val))

        # TEST: invalid input (values more than the defined max length)
        valid_val = [1]
        with self.assertRaises(ValidationError):
            form_field_list.clean(valid_val)

    def test_max_length(self):
        form_field_list = FieldList(field=fields.IntegerField(), max_length=3)

        # TEST: valid input
        valid_val = [1, 2, 3]
        self.assertEqual(valid_val, form_field_list.clean(valid_val))

        # TEST: invalid input (values more than the defined max length)
        valid_val = [1, 2, 3, 4]
        with self.assertRaises(ValidationError):
            form_field_list.clean(valid_val)


class FormFieldTests(SimpleTestCase):
    class TestFormWithRequiredField(Form):
        name = fields.CharField(required=True, max_length=100)

    class TestFormWithoutRequiredField(Form):
        name = fields.CharField(required=False, max_length=100)

    def test_formfield_required(self):
        form_field = FormField(form=self.TestFormWithRequiredField)

        # TEST: valid input
        valid_val = {'name': 'blah'}
        self.assertEqual(valid_val, form_field.clean(valid_val))

        # TEST: invalid input (values the FormField considers invalid)
        invalid_vals = ['0', 1, datetime.datetime.now(), 'blah', {'blah'}, ['blah']]
        expected_error = "['Invalid value']"
        for invalid_val in invalid_vals:
            with self.assertRaisesMessage(ValidationError, expected_error):
                log_input(invalid_val)
                form_field.clean(invalid_val)

        # TEST: required=True, form WITH required field - invalid input (empty value)
        invalid_val = {'name': None}
        expected_error = "({'name': [ValidationError(['This field is required.'])]}, None, None)"
        with self.assertRaisesMessage(ValidationError, "['This field is required.']"):
            form_field.clean(invalid_val)

        # TEST: required=True, form WITH required field - invalid input (unexpected dict key)
        invalid_val = {'unexpected key': 'blah'}
        expected_error = "['This field is required.']"
        with self.assertRaisesMessage(ValidationError, expected_error):
            form_field.clean(invalid_val)

        # TEST: required=True, form WITHOUT required field - unexpected dict key returns blanks with keys
        # Django returns a normalized empty value when required=False rather than raising ValidationError
        invalid_val = {'unexpected key': 'blah'}
        form_field_no_required_fields = FormField(required=False, form=self.TestFormWithoutRequiredField)

        self.assertEqual({}, form_field_no_required_fields.clean(invalid_val))

        # TEST: required=True - empty values throw an error
        for empty_val in EMPTY_VALUES:
            with self.assertRaisesMessage(ValidationError, "['This field is required.']"):
                log_input(empty_val)
                form_field.clean(empty_val)

    def test_formfield_required_false(self):
        form_field = FormField(form=self.TestFormWithRequiredField, required=False)

        # TEST: valid input
        valid_val = {'name': 'blah'}
        self.assertEqual(valid_val, form_field.clean(valid_val))

        # TEST: required=False - empty values return {}
        for empty_val in EMPTY_VALUES:
            self.assertEqual({}, form_field.clean(empty_val))


class FormFieldListTests(SimpleTestCase):
    class TestFormWithRequiredField(Form):
        number = fields.IntegerField(required=True)

    class TestFormWithoutRequiredField(Form):
        number = fields.IntegerField(required=False)

    def test_formfieldlist_required(self):
        form_field_list = FormFieldList(form=self.TestFormWithRequiredField)

        # TEST: valid input
        valid_val = [{'number': 1}, {'number': 2}, {'number': 0}]
        self.assertEqual(valid_val, form_field_list.clean(valid_val))

        # TEST: invalid input (non-list values the FormFieldList considers invalid)
        invalid_vals = [datetime.datetime.now(), 'blah', {'blah'}, 1]
        expected_error = str([FormFieldList.default_error_messages['not_list']])
        for invalid_val in invalid_vals:
            with self.assertRaisesMessage(ValidationError, expected_error):
                log_input(invalid_val)
                form_field_list.clean(invalid_val)

        # TEST: invalid input (non-list values the FormFieldList considers empty)
        invalid_vals = [None, '', (), {}, False, 0]
        for invalid_val in invalid_vals:
            with self.assertRaisesMessage(ValidationError, "['This field is required.']"):
                log_input(invalid_val)
                form_field_list.clean(invalid_val)

        # TEST: invalid input (values the FormFieldList's Form's IntegerField considers invalid)
        invalid_vals = [False, datetime.datetime.now(), 'blah', {'blah'}, ['blah']]
        expected_form_errors = [{'number': [ValidationError(['Enter a whole number.'])]}]
        expected_error = str((expected_form_errors, None, None))
        for invalid_val in invalid_vals:
            with self.assertRaisesMessage(ValidationError, "['Enter a whole number.']"):
                log_input(invalid_val)
                form_field_list.clean([{'number': invalid_val}])

        # TEST: invalid input (values the FieldList's Form's IntegerField considers empty)
        expected_form_errors = [{'number': [ValidationError(['This field is required.'])]}]
        expected_error = str((expected_form_errors, None, None))
        for empty_val in EMPTY_VALUES:
            with self.assertRaisesMessage(ValidationError, "['This field is required.']"):
                log_input(empty_val)
                form_field_list.clean([{'number': empty_val}])

        # TEST: required=True, form WITHOUT required field - list of {} with unexpected key is allowed
        invalid_val = [{'unexpected key': 'blah'}, {'unexpected': 'blah2'}]
        form_field_no_required_fields = FormFieldList(form=self.TestFormWithoutRequiredField)
        expected_result = [{}] * len(invalid_val)
        self.assertEqual(expected_result, form_field_no_required_fields.clean(invalid_val))

        # TEST: required=True - [] is not allowed
        with self.assertRaisesMessage(ValidationError, "['This field is required.']"):
            form_field_list.clean([])

    def test_formfieldlist_required_false(self):
        form_field_list = FormFieldList(form=self.TestFormWithRequiredField, required=False)

        # TEST: valid input
        test_val = [{'number': 1}, {'number': 2}]
        self.assertEqual(test_val, form_field_list.clean(test_val))

        # TEST: required=False, form WITHOUT required field - list of {} values is allowed
        empty_vals = [{}, {}]
        form_field_no_required_fields = FormFieldList(form=self.TestFormWithoutRequiredField)
        expected_result = [{}] * len(empty_vals)
        self.assertEqual(expected_result, form_field_no_required_fields.clean(empty_vals))

        # TEST: required=False - [] allowed
        self.assertEqual([], form_field_list.clean([]))

    def test_min_length(self):
        form_field_list = FormFieldList(form=self.TestFormWithRequiredField, min_length=2)

        # TEST: valid input
        valid_val = [{'number': 1}, {'number': 2}]
        self.assertEqual(valid_val, form_field_list.clean(valid_val))

        # TEST: invalid input (values more than the defined max length)
        valid_val = [{'number': 1}]
        with self.assertRaises(ValidationError):
            form_field_list.clean(valid_val)

    def test_max_length(self):
        form_field_list = FormFieldList(form=self.TestFormWithRequiredField, max_length=3)

        # TEST: valid input
        valid_val = [{'number': 1}, {'number': 2}, {'number': 0}]
        self.assertEqual(valid_val, form_field_list.clean(valid_val))

        # TEST: invalid input (values more than the defined max length)
        valid_val = [{'number': 1}, {'number': 2}, {'number': 0}, {'number': 4}]
        with self.assertRaises(ValidationError):
            form_field_list.clean(valid_val)


class EnumFieldTests(SimpleTestCase):
    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    def test_enumfield_init(self):
        # TEST: initialize EnumField with an instance of Enum
        EnumField(enum=self.Color)
        EnumField(self.Color)

        # TEST: initialize EnumField with non-Enum - throws an error
        expected_error = EnumField.default_error_messages['not_enum']
        for non_enum in [1, 'blah'] + list(EMPTY_VALUES):
            with self.assertRaisesMessage(ApiFormException, str(expected_error)):
                log_input(non_enum)
                EnumField(enum=non_enum)

    def test_enumfield_required(self):
        enum_field = EnumField(enum=self.Color)

        # TEST: valid enum value
        valid_val = self.Color.GREEN
        self.assertEqual(valid_val, enum_field.clean(valid_val))

        # TEST: invalid enum value
        invalid_val = 4
        expected_error = EnumField.default_error_messages['invalid']
        expected_error = str([expected_error.format(invalid_val, self.Color)])
        with self.assertRaisesMessage(ValidationError, expected_error):
            enum_field.clean(invalid_val)

        # TEST: required=True - non-None empty values throw an error
        for empty_val in ['', [], (), {}]:
            expected_error = EnumField.default_error_messages['invalid']
            expected_error = str([expected_error.format(empty_val, self.Color)])
            with self.assertRaisesMessage(ValidationError, expected_error):
                log_input(empty_val)
                enum_field.clean(empty_val)

        # TEST: required=True - None throws error
        with self.assertRaisesMessage(ValidationError, "['This field is required.']"):
            self.assertEqual(valid_val, enum_field.clean(None))

    def test_enumfield_required_false(self):
        enum_field = EnumField(enum=self.Color, required=False)

        # TEST: valid enum value
        valid_val = self.Color.BLUE
        self.assertEqual(valid_val, enum_field.clean(valid_val))

        # TEST: required=False - non-None empty values throw an error
        for empty_val in ['', [], (), {}]:
            expected_error = EnumField.default_error_messages['invalid']
            expected_error = str([expected_error.format(empty_val, self.Color)])
            with self.assertRaisesMessage(ValidationError, expected_error):
                log_input(empty_val)
                enum_field.clean(empty_val)

        # TEST: required=False - None allowed
        self.assertIsNone(enum_field.clean(None))


class DictionaryFieldTests(SimpleTestCase):
    def test_dictionaryfield_init(self):
        # TEST: initialize DictionaryField with an instance of Field
        DictionaryField(fields.IntegerField())
        DictionaryField(value_field=fields.IntegerField())

        # TEST: initialize DictionaryField with non-Field - throws an error
        expected_error = DictionaryField.default_error_messages['not_field']
        for non_field in [1, 'blah']:
            with self.assertRaisesMessage(ApiFormException, str(expected_error)):
                log_input(non_field)
                DictionaryField(non_field)

    def test_dictionaryfield_required(self):
        dict_field = DictionaryField(fields.DateTimeField())

        # TEST: valid value (type of dict values match DictionaryField)
        now = datetime.datetime(2020, 5, 2, 22, 31, 32, tzinfo=datetime.timezone.utc)
        expected_result = {
            "created_at": now,
            "updated_at": now,
        }
        now_formatted = now.strftime(settings.DATETIME_INPUT_FORMATS[0])
        test_input = {
            "created_at": now_formatted,
            "updated_at": now_formatted,
        }
        self.assertEqual(expected_result, dict_field.clean(test_input))

        # TEST: invalid value (type of dict values DO NOT match DictionaryField)
        test_input = {"created_at": "blah"}
        with self.assertRaisesMessage(
            ValidationError, "{'created_at': ['Enter a valid date/time.']}"
        ):
            dict_field.clean(test_input)

        # TEST: required=True - all empty non-dict values throw an error
        for empty_val in [None, '', [], ()]:
            expected_error = DictionaryField.default_error_messages['not_dict']
            expected_error = expected_error.format(type(empty_val))
            with self.assertRaisesMessage(ValidationError, expected_error):
                log_input(empty_val)
                dict_field.clean(empty_val)

        # TEST: required=True - {} throws error
        with self.assertRaisesMessage(ValidationError, "['This field is required.']"):
            dict_field.clean({})

    def test_dictionaryfield_required_false(self):
        dict_field = DictionaryField(fields.IntegerField(), required=False)

        # TEST: valid dict value (type of dict values match DictionaryField)
        test_val = {"foo": 1}
        self.assertEqual(test_val, dict_field.clean(test_val))

        # TEST: required=False - {} allowed
        self.assertEqual({}, dict_field.clean({}))

        # TEST: non-{} empty values throw an error
        for empty_val in [None, '', [], ()]:
            expected_error = DictionaryField.default_error_messages['not_dict']
            expected_error = expected_error.format(type(empty_val))
            with self.assertRaisesMessage(ValidationError, expected_error):
                log_input(empty_val)
                dict_field.clean(empty_val)

    def test_dictionaryfield_key_field(self):
        dict_field = DictionaryField(value_field=fields.IntegerField(), key_field=fields.UUIDField())

        # TEST: valid dict value and key
        valid_dict = {'41aaf965-8417-448d-bd1f-c2578a933dad': 1}
        expected_result = {UUID('41aaf965-8417-448d-bd1f-c2578a933dad'): 1}
        self.assertEqual(expected_result, dict_field.clean(valid_dict))

        invalid_dict = {'41aaf965-8417-448d-bd1f-': '1'}
        expected_error = fields.UUIDField.default_error_messages['invalid']
        expected_error = expected_error.format(type(invalid_dict))
        with self.assertRaisesMessage(ValidationError, expected_error):
            log_input(expected_error)
            dict_field.clean(invalid_dict)

    def test_dictionaryfield_init_not_field(self):
        valid_dict = {'41aaf965-8417-448d-bd1f-c2578a933dad': 1}
        expected_error = DictionaryField.default_error_messages['not_field']
        expected_error = expected_error.format(type(valid_dict))
        with self.assertRaisesMessage(ApiFormException, expected_error):
            DictionaryField(value_field=int, key_field=Decimal)


class AnyFieldTests(SimpleTestCase):
    NON_EMPTY_VALUES = [
        1,
        '1',
        1.5,
        {'test': {'nested': 'dict'}},
        [123, 456],
        {123, 456},
        '0',
    ]

    def test_anyfield_required(self):
        any_field = AnyField()

        # TEST: required=True - empty values throw an error
        for empty_val in EMPTY_VALUES:
            with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
                log_input(empty_val)
                any_field.clean(empty_val)

        # TEST: non-empty values return the same value
        for non_empty_val in self.NON_EMPTY_VALUES:
            self.assertIs(non_empty_val, any_field.clean(non_empty_val))

    def test_anyfield_required_false(self):
        any_field = AnyField(required=False)

        # TEST: required=False - empty values are allowed
        for empty_val in EMPTY_VALUES:
            self.assertIs(empty_val, any_field.clean(empty_val))

        # TEST: non-empty values return the same value
        for non_empty_val in self.NON_EMPTY_VALUES:
            self.assertIs(non_empty_val, any_field.clean(non_empty_val))


class NonRequiredTestCase(SimpleTestCase):
    class TestFormWithNonRequiredFields(Form):
        number = fields.IntegerField(required=False)
        name = fields.CharField(required=False, empty_value=None)

    def test_non_required_fields(self):
        form_field_list = FormFieldList(form=self.TestFormWithNonRequiredFields)

        # TEST: valid input
        valid_val = [
            {'name': 'aaa'},
            {'number': 2},
            {'number': 0, 'name': 'ccc'}
        ]
        self.assertEqual(valid_val, form_field_list.clean(valid_val))


class FileFieldTests(SimpleTestCase):
    def setUp(self) -> None:
        with open(f"{settings.BASE_DIR}/data/kitten.txt") as f:
            self._payload = f.read().strip('\n')
        pass

    def test_simple(self):
        file_field = FileField()
        django_file = file_field.clean(self._payload)

        self.assertIsInstance(django_file, File)
        self.assertEqual(django_file.size, 12412)

    def test_mime(self):
        file_field = FileField(mime=('image/jpeg', ))
        django_file = file_field.clean(self._payload)

        self.assertTrue(isinstance(django_file, File))
        self.assertEqual(django_file.size, 12412)

    def test_max_length(self):
        file_field = FileField(mime=('image/jpeg', ), max_length=1000)

        with self.assertRaises(ValidationError):
            log_input(self._payload)
            file_field.clean(self._payload)

    def test_invalid_mime(self):
        file_field = FileField(mime=('image/png', 'image/gif'))

        expected_error = FileField.default_error_messages['invalid_mime']
        expected_error = expected_error.format('image/png, image/gif', 'image/jpeg')
        with self.assertRaisesMessage(ValidationError, expected_error):
            log_input(self._payload)
            file_field.clean(self._payload)

    def test_missing_mime(self):
        file_field = FileField(mime=('image/jpeg', 'image/gif'))

        with open(f"{settings.BASE_DIR}/data/kitten_missing.txt") as f:
            kitten = f.read().strip('\n')

        expected_error = FileField.default_error_messages['invalid_uri']
        expected_error = expected_error.format('image/png, image/gif', 'image/jpeg')
        with self.assertRaisesMessage(ValidationError, expected_error):
            log_input(kitten)
            file_field.clean(kitten)

    def test_large_file(self):
        file_field = FileField(required=False)

        with open(f"{settings.BASE_DIR}/data/valid_pdf.txt") as f:
            content = f.read().strip('\n')

        result = file_field.clean(content)

        self.assertEqual(result.content_type, 'application/pdf')

    @mock.patch("django_api_forms.fields.version", "1.0.0")
    def test_valid_data_uri(self):
        file_field = FileField()

        django_file = file_field.clean(self._payload)
        self.assertIsInstance(django_file, File)

        # Simple values
        django_file = file_field.clean("data:;base64;sdfgsdfgsdfasdfa=s,UEsDBBQAAAAI")
        self.assertTrue(isinstance(django_file, File))
        self.assertEqual(django_file.size, 9)

        django_file = file_field.clean("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHE"
                                       "lEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==")
        self.assertTrue(isinstance(django_file, File))
        self.assertEqual(django_file.size, 85)

        # with meta key=value
        django_file = file_field.clean("data:image/jpeg;key=value;base64,UEsDBBQAAAAI")
        self.assertTrue(isinstance(django_file, File))
        self.assertEqual(django_file.size, 9)

        # without base64 key name
        django_file = file_field.clean("data:image/jpeg;key=value,UEsDBBQAAAAI")
        self.assertTrue(isinstance(django_file, File))
        self.assertEqual(django_file.size, 9)

        # without mime-type
        django_file = file_field.clean("data:;base64;sdfgsdfgsdfasdfa=s,UEsDBBQAAAAI")
        self.assertTrue(isinstance(django_file, File))
        self.assertEqual(django_file.size, 9)

        # without mime-type , base64 and meta key=value
        django_file = file_field.clean("data:,UEsDBBQAAAAI")
        self.assertTrue(isinstance(django_file, File))
        self.assertEqual(django_file.size, 9)


class ImageFieldTests(SimpleTestCase):
    def setUp(self) -> None:
        with open(f"{settings.BASE_DIR}/data/kitten.txt") as f:
            self._payload = f.read().strip('\n')
        pass

    def test_simple(self):
        image_field = ImageField()
        django_image = image_field.clean(self._payload)

        self.assertIsInstance(django_image, File)
        self.assertEqual(django_image.size, 12412)
        self.assertEqual(django_image.content_type, 'image/jpeg')
        self.assertIsNotNone(django_image.image)

    def test_mime_mismatch(self):
        file_field = ImageField(mime=('image/png', 'image/gif'))

        with open(f"{settings.BASE_DIR}/data/kitten_mismatch.txt") as f:
            kitten = f.read().strip('\n')

        expected_error = FileField.default_error_messages['invalid_mime']
        expected_error = expected_error.format('image/png, image/gif', 'image/jpeg')
        with self.assertRaisesMessage(ValidationError, expected_error):
            log_input(kitten)
            file_field.clean(kitten)

    def test_invalid(self):
        file_field = ImageField()

        with open(f"{settings.BASE_DIR}/data/invalid_image.txt") as f:
            kitten = f.read()

        with self.assertRaises(ValidationError):
            log_input(kitten)
            file_field.clean(kitten)

    @mock.patch("django_api_forms.fields.version", "1.0.0")
    def test_valid_data_uri(self):
        file_field = FileField()

        # Simple values
        django_file = file_field.clean("data:;base64;sdfgsdfgsdfasdfa=s,UEsDBBQAAAAI")
        self.assertTrue(isinstance(django_file, File))
        self.assertEqual(django_file.size, 9)

        django_file = file_field.clean("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHE"
                                       "lEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==")
        self.assertTrue(isinstance(django_file, File))
        self.assertEqual(django_file.size, 85)

        # with meta key=value
        django_file = file_field.clean("data:image/jpeg;key=value;base64,UEsDBBQAAAAI")
        self.assertTrue(isinstance(django_file, File))
        self.assertEqual(django_file.size, 9)

        # without base64 key name
        django_file = file_field.clean("data:image/jpeg;key=value,UEsDBBQAAAAI")
        self.assertTrue(isinstance(django_file, File))
        self.assertEqual(django_file.size, 9)

        # without mime-type
        django_file = file_field.clean("data:;base64;sdfgsdfgsdfasdfa=s,UEsDBBQAAAAI")
        self.assertTrue(isinstance(django_file, File))
        self.assertEqual(django_file.size, 9)

        # without mime-type , base64 and meta key=value
        django_file = file_field.clean("data:,UEsDBBQAAAAI")
        self.assertTrue(isinstance(django_file, File))
        self.assertEqual(django_file.size, 9)
