from typing import Any

from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty


class DefaultValidator(object):
    def __init__(self, default: Any):
        self.default = default

    def run_validation(self, data: Any):
        value = self.default if data is empty else data

        if value is empty:
            raise ValidationError("A value for this parameter is required")

        return value
