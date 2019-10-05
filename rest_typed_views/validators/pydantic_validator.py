from rest_framework.exceptions import ValidationError


class PydanticValidator(object):
    def __init__(self, PydanticModelClass):
        self.PydanticModelClass = PydanticModelClass

    def run_validation(self, data: dict):
        from pydantic import ValidationError as PydanticValidationError

        try:
            return self.PydanticModelClass(**data)
        except PydanticValidationError as e:
            raise ValidationError(e.errors())
