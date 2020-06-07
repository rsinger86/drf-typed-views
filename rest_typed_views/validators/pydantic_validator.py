from typing import Union

from django.http import QueryDict
from rest_framework.exceptions import ValidationError


class PydanticValidator(object):
    def __init__(self, PydanticModelClass):
        self.PydanticModelClass = PydanticModelClass

    def run_validation(self, data: Union[dict, QueryDict]):
        from pydantic import ValidationError as PydanticValidationError

        try:
            if isinstance(data, QueryDict):
                # Note that QueryDict is subclass of dict
                return self.PydanticModelClass(**data.dict())
            return self.PydanticModelClass(**data)
        except PydanticValidationError as e:
            raise ValidationError(e.errors())
