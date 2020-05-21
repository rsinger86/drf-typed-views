from typing import Union

from django.http import QueryDict
from rest_framework.exceptions import ValidationError


class TypeSystemValidator(object):
    def __init__(self, TypeSystemSchemaClass):
        self.TypeSystemSchemaClass = TypeSystemSchemaClass

    def run_validation(self, data: Union[dict, QueryDict]):
        if isinstance(data, QueryDict):
            # Note that QueryDict is subclass of dict
            data = data.dict()
        instance, errors = self.TypeSystemSchemaClass.validate_or_error(data)

        if errors:
            raise ValidationError(dict(errors))

        return instance
