import inspect
import operator
from enum import Enum
from functools import reduce
from typing import Any, List, Optional, Tuple

from django.conf import settings
from rest_framework.fields import empty
from rest_framework.request import Request

from .param_settings import ParamSettings


def parse_list_annotation(annotation) -> Tuple[bool, Any]:
    if "List[" in str(annotation):
        return True, annotation.__args__[0]
    return False, None


def parse_enum_annotation(annotation) -> Tuple[bool, List[Any]]:
    if inspect.isclass(annotation) and issubclass(annotation, Enum):
        return True, [_.value for _ in annotation]
    return False, []


def parse_complex_type(annotation) -> Tuple[bool, Optional[str]]:
    if hasattr(settings, "DRF_TYPED_VIEWS"):
        enabled = settings.DRF_TYPED_VIEWS.get("schema_packages", [])
    else:
        enabled = []

    if "pydantic" in enabled:
        from pydantic import BaseModel as PydanticBaseModel

        if inspect.isclass(annotation) and issubclass(annotation, PydanticBaseModel):
            return True, "pydantic"

    if "typesystem" in enabled:
        from typesystem import Schema as TypeSystemSchema

        if inspect.isclass(annotation) and issubclass(annotation, TypeSystemSchema):
            return True, "typesystem"

    if "marshmallow" in enabled:
        from marshmallow import Schema as MarshmallowSchema

        if inspect.isclass(annotation) and issubclass(annotation, MarshmallowSchema):
            return True, "marshmallow"
    return False, None


def get_nested_value(dic: dict, path: str, fallback=None) -> Any:
    try:
        return reduce(operator.getitem, path.split("."), dic)
    except (TypeError, KeyError, ValueError):
        return fallback


def get_default_value(param: inspect.Parameter) -> Any:
    if (
        not is_default_used_to_pass_settings(param)
        and param.default is not inspect.Parameter.empty
    ):
        return param.default
    return empty


def is_default_used_to_pass_settings(param: inspect.Parameter) -> bool:
    return get_explicit_param_settings(param) is not None


def get_explicit_param_settings(param: inspect.Parameter) -> Optional[ParamSettings]:
    try:
        param_type = param.default.param_type
        return param.default
    except AttributeError:
        return None


def is_implicit_body_param(param: inspect.Parameter) -> bool:
    is_complex_type, package = parse_complex_type(param.annotation)
    return is_complex_type


def is_explicit_request_param(param: inspect.Parameter) -> bool:
    return param.annotation is Request


def is_implicit_request_param(param: inspect.Parameter) -> bool:
    return param.name == "request" and param.annotation is inspect.Parameter.empty


def find_request(original_args: list) -> Request:
    for arg in original_args:
        if isinstance(arg, Request):
            return arg
    raise Exception("Could not find request in args:" + str(original_args))
