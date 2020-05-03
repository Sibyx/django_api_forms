"""
Based on Django's field tests:
https://github.com/django/django/tree/stable/3.0.x/tests/forms_tests/field_tests
"""
import datetime
import logging
from enum import Enum

from django.conf import settings
from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError, fields
from django.test import SimpleTestCase
from django_api_forms import (AnyField, BooleanField, DictionaryField, EnumField, FieldList, Form, FormField,
                              FormFieldList, RequestValidationError)


def log_input(val):
    """
    Logs info about attempted form field input values.

    Mainly for tests that can raise ValidationError, because ValidationError
    sometimes doesn't show the attempted value and a raised exception doesn't
    return value for assert (which does show the attempted value).

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
        expected_error = "Invalid Field type passed into FieldList!"
        for non_field in [1, 'blah'] + list(EMPTY_VALUES):
            with self.assertRaisesMessage(RuntimeError, expected_error):
                log_input(non_field)
                FieldList(field=non_field)

    def test_fieldlist_required(self):
        field_list = FieldList(field=fields.IntegerField())

        # TEST: valid input
        valid_val = [1, 2, 3]
        self.assertEqual(valid_val, field_list.clean(valid_val))

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
        expected_error = "({'name': [ValidationError(['Invalid value'])]}, None, None)"
        for invalid_val in invalid_vals:
            with self.assertRaisesMessage(RequestValidationError, expected_error):
                log_input(invalid_val)
                form_field.clean(invalid_val)

        # TEST: required=True, form WITH required field - invalid input (empty value)
        invalid_val = {'name': None}
        expected_error = "({'name': [ValidationError(['This field is required.'])]}, None, None)"
        with self.assertRaisesMessage(RequestValidationError, expected_error):
            form_field.clean(invalid_val)

        # TEST: required=True, form WITH required field - invalid input (unexpected dict key)
        invalid_val = {'unexpected key': 'blah'}
        expected_error = "({'name': [ValidationError(['This field is required.'])]}, None, None)"
        with self.assertRaisesMessage(RequestValidationError, expected_error):
            form_field.clean(invalid_val)

        # TEST: required=True, form WITHOUT required field - unexpected dict key returns blanks with keys
        # Django returns a normalized empty value when required=False rather than raising ValidationError
        invalid_val = {'unexpected key': 'blah'}
        form_field_no_required_fields = FormField(form=self.TestFormWithoutRequiredField)
        self.assertEqual({'name': ''}, form_field_no_required_fields.clean(invalid_val))

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
            with self.assertRaisesMessage(RequestValidationError, expected_error):
                log_input(invalid_val)
                form_field_list.clean([{'number': invalid_val}])

        # TEST: invalid input (values the FieldList's Form's IntegerField considers empty)
        expected_form_errors = [{'number': [ValidationError(['This field is required.'])]}]
        expected_error = str((expected_form_errors, None, None))
        for empty_val in EMPTY_VALUES:
            with self.assertRaisesMessage(RequestValidationError, expected_error):
                log_input(empty_val)
                form_field_list.clean([{'number': empty_val}])

        # TEST: required=True, form WITHOUT required field - list of {} with unexpected keys returns key with blank
        """
        invalid_val = [{'unexpected key': 'blah'}, {'unexpected': 'blah2'}]
        form_field_no_required_fields = FormField(form=self.TestFormWithoutRequiredField)
        expected_result = [{'name': ''}] * len(invalid_val)
        self.assertEqual(expected_result, form_field_no_required_fields.clean(invalid_val))
        """
        # RequestValidationError: ({'number': [ValidationError(['Invalid value'])]}, None, None)

        # TEST: required=True - [] is not allowed
        with self.assertRaisesMessage(ValidationError, "['This field is required.']"):
            form_field_list.clean([])

    def test_formfieldlist_required_false(self):
        form_field_list = FormFieldList(form=self.TestFormWithRequiredField, required=False)

        # TEST: valid input
        test_val = [{'number': 1}, {'number': 2}]
        self.assertEqual(test_val, form_field_list.clean(test_val))

        # TEST: required=False, form WITHOUT required field - list of {} values is allowed
        """
        empty_vals = [{}, {}]
        form_field_no_required_fields = FormField(form=self.TestFormWithoutRequiredField)
        self.assertEqual(empty_vals, form_field_no_required_fields.clean(empty_vals))
        """
        # RequestValidationError: ({'number': [ValidationError(['Invalid value'])]}, None, None)

        # TEST: required=False, form WITHOUT required field - list of {} with unexpected key returns {}
        """
        invalid_val = [{'unexpected key': 'blah'}, {'unexpected': 1}]
        form_field_no_required_fields = FormField(form=self.TestFormWithoutRequiredField)
        self.assertEqual([{}, {}], form_field_no_required_fields.clean(invalid_val))
        """
        # RequestValidationError: ({'number': [ValidationError(['Invalid value'])]}, None, None)

        # TEST: required=False - [] allowed
        self.assertEqual([], form_field_list.clean([]))


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
        for non_enum in [1, 'blah'] + list(EMPTY_VALUES):
            with self.assertRaisesMessage(RuntimeError, "Invalid Enum type passed into EnumField!"):
                log_input(non_enum)
                EnumField(enum=non_enum)

    def test_enumfield_required(self):
        enum_field = EnumField(enum=self.Color)

        # TEST: valid enum value
        valid_val = self.Color.GREEN
        self.assertEqual(valid_val, enum_field.clean(valid_val))

        # TEST: invalid enum value
        invalid_val = 4
        expected_error = '["Invalid enum value {} passed to <class \'enum.EnumMeta\'>"]'
        expected_error = expected_error.format(invalid_val)
        with self.assertRaisesMessage(ValidationError, expected_error):
            enum_field.clean(invalid_val)

        # TEST: required=True - non-None empty values throw an error
        for empty_val in ['', [], (), {}]:
            expected_error = '["Invalid enum value {} passed to <class \'enum.EnumMeta\'>"]'
            expected_error = expected_error.format(empty_val)
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
            expected_error = '["Invalid enum value {} passed to <class \'enum.EnumMeta\'>"]'
            expected_error = expected_error.format(empty_val)
            with self.assertRaisesMessage(ValidationError, expected_error):
                log_input(empty_val)
                enum_field.clean(empty_val)

        # TEST: required=False - None allowed
        self.assertIsNone(enum_field.clean(None))


class DictionaryFieldTests(SimpleTestCase):
    def test_dictionaryfield_init(self):
        # TEST: initialize DictionaryField with an instance of Field
        DictionaryField(fields.IntegerField())
        DictionaryField(value=fields.IntegerField())

        # TEST: initialize DictionaryField with non-Field - throws an error
        expected_error = "Invalid Field type passed into DictionaryField!"
        for non_field in [1, 'blah']:
            with self.assertRaisesMessage(RuntimeError, expected_error):
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
        with self.assertRaisesMessage(ValidationError, "{'created_at': ['Enter a valid date/time.']}"):
            dict_field.clean(test_input)

        # TEST: required=True - all empty non-dict values throw an error
        for empty_val in [None, '', [], ()]:
            expected_error = '["Invalid value passed to DictionaryField (got {}, expected dict)"]'
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
            expected_error = f"Invalid value passed to DictionaryField (got {type(empty_val)}, expected dict)"
            with self.assertRaisesMessage(ValidationError, expected_error):
                log_input(empty_val)
                dict_field.clean(empty_val)


class AnyFieldTests(SimpleTestCase):
    NON_EMPTY_VALUES = [
        1,
        '1',
        1.5,
        {'test': {'nested': 'dict'}},
        [123, 456],
        set([123, 456]),
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
