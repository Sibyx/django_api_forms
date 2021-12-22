class BaseStrategy:
    def __call__(self, field, obj, key: str, value):
        setattr(obj, key, value)


class IgnoreStrategy(BaseStrategy):
    def __call__(self, field, obj, key: str, value):
        pass


class BooleanField(BaseStrategy):
    def __call__(self, field, obj, key: str, value):
        super().__call__(field, obj, key, value)


class FormedStrategy(BaseStrategy):
    def __call__(self, field, obj, key: str, value):
        model_value = value
        if model_value > 2021 or model_value < 1900:
            model_value = 2000

        setattr(obj, key, model_value)


class ModelChoiceFieldStrategy(BaseStrategy):

    """
    We need to changes key postfix if there is ModelChoiceField (because of _id etc.)
    We always try to assign whole object instance, for example:
    artis_id is normalized as Artist model, but it have to be assigned to artist model property
    because artist_id in model has different type (for example int if your are using int primary keys)
    If you are still confused (sorry), try to check docs
    """
    def __call__(self, field, obj, key: str, value):
        model_key = key
        if field.to_field_name:
            postfix_to_remove = f"_{field.to_field_name}"
        else:
            postfix_to_remove = "_id"
        if key.endswith(postfix_to_remove):
            model_key = key[:-len(postfix_to_remove)]
        setattr(obj, model_key, value)
