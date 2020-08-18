# Fields

Even if we tried to use maximum of native Django field, we had to override some of them to be more fit for RESTful
applications. Also we introduced new ones, to cover extra functionality like nested requests. In this section we will
explain our intentions and describe their usage.

To sum up:

- You can use [Django Form Fields](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#module-django.forms.fields):
    - [CharField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#charfield)
    - [ChoiceField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#choicefield)
    - [TypedChoiceField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#typedchoicefield)
    - [DateField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#datefield)
    - [DateTimeField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#datetimefield)
    - [DecimalField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#decimalfield)
    - [DurationField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#durationfield)
    - [EmailField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#emailfield)
    - [FilePathField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#filepathfield)
    - [FloatField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#floatfield)
    - [IntegerField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#integerfield)
    - [GenericIPAddressField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#genericipaddressfield)
    - [MultipleChoiceField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#multiplechoicefield)
    - [TypedMultipleChoiceField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#typedmultiplechoicefield)
    - [RegexField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#regexfield)
    - [SlugField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#slugfield)
    - [TimeField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#timefield)
    - [URLField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#urlfield)
    - [UUIDField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#uuidfield)
    - [ModelChoiceField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#modelchoicefield)
    - [ModelMultipleChoiceField](https://docs.djangoproject.com/en/3.1/ref/forms/fields/#modelmultiplechoicefield)
- You can use [Django Validators](https://docs.djangoproject.com/en/3.1/ref/validators/).

Fields which are not in the list above were not been tested or been replaced with our customized implementation
(or it just doesn't make sense use them in RESTful APIs).

## BooleanField

## FieldList

## FormField

## FormFieldList

## EnumField

## DictionaryField

## AnyField

## FileField

## ImageField
