from typing import Union

from django.http import QueryDict
from rest_framework.exceptions import ValidationError


class MarshMallowValidator(object):
    def __init__(self, MashMallowSchemaClass):
        self.MashMallowSchemaClass = MashMallowSchemaClass

    def run_validation(self, data: Union[dict, QueryDict]):
        from marshmallow import ValidationError as MarshMallowValidationError

        try:
            if isinstance(data, QueryDict):
                # Note that QueryDict is subclass of dict
                return self.MashMallowSchemaClass().load(data.dict())
            return self.MashMallowSchemaClass().load(data)
        except MarshMallowValidationError as err:
            raise ValidationError(err.messages)
