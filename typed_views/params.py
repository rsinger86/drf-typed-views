import inspect
from typing import Any, List, Tuple

from rest_framework.exceptions import ValidationError
from rest_framework.fields import Field

from typed_views import Request, empty
from typed_views.param_settings import ParamSettings
from typed_views.utils import get_nested_value, parse_list_annotation
from typed_views.validators import ValidatorFactory


class Param(object):
    def __init__(
        self,
        name: str,
        param: inspect.Parameter,
        request: Request,
        settings: ParamSettings,
        raw_value: Any = empty,
    ):
        self.name = name
        self.param = param
        self.request = request
        self.settings = settings
        self.raw_value = raw_value

    def _get_validator(self) -> Field:
        return ValidatorFactory.make(self.param.annotation, self.settings)

    def _get_raw_value(self):
        raise Exception("Must implement in concrete class!")

    @property
    def _source(self) -> str:
        return self.settings.source or self.name

    def validate_or_error(self) -> Tuple[Any, Any]:
        validator = self._get_validator()

        try:
            value = validator.run_validation(self._get_raw_value())
            return value, None
        except ValidationError as e:
            return None, {self._source: e.detail}


class QueryParam(Param):
    def _get_raw_value(self):
        if self.settings.source == "*":
            raw = self.request.query_params.dict()
        else:
            key = self.settings.source or self.name
            raw = self.request.query_params.get(key, empty)
            raw = empty if raw == "" else raw
            is_list_type, item_type = parse_list_annotation(self.param.annotation)

            if raw is not empty and is_list_type:
                raw = raw.split(self.settings.delimiter)

        return raw


class PathParam(Param):
    def _get_raw_value(self):
        raw = self.raw_value
        return raw


class BodyParam(Param):
    def _get_raw_value(self):
        if self.settings.source in ("*", None):
            return self.request.data
        return get_nested_value(self.request.data, self.settings.source)


class HeaderParam(Param):
    def _get_raw_value(self):
        return self.request.data


class CurrentUserParam(Param):
    def _get_raw_value(self):
        if self.settings.source in ("*", None):
            return self.request.user
        return get_nested_value(self.request.data, self.settings.source)
