from rest_framework.exceptions import ValidationError


class TypeSystemValidator(object):
    def __init__(self, TypeSystemSchemaClass):
        self.TypeSystemSchemaClass = TypeSystemSchemaClass

    def run_validation(self, data: dict):
        instance, errors = self.TypeSystemSchemaClass.validate_or_error(data)

        if errors:
            raise ValidationError(dict(errors))

        return instance
