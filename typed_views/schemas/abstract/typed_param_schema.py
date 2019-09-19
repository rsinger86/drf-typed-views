from typing import Any


class TypedParamSchema(object):
    def get_value(self):
        value = self.raw_value
        return value

    def cast_value(self, value: Any):
        return value

    def validate_value(self, value: Any):
        pass
