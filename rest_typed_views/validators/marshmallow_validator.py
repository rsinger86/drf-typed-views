from rest_framework.exceptions import ValidationError


class MarshMallowValidator(object):
    def __init__(self, MashMallowSchemaClass):
        self.MashMallowSchemaClass = MashMallowSchemaClass

    def run_validation(self, data: dict):
        from marshmallow import ValidationError as MarshMallowValidationError

        try:
            return self.MashMallowSchemaClass().load(data)
        except MarshMallowValidationError as err:
            raise ValidationError(err.messages)
