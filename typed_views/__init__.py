import functools
import inspect
from functools import wraps
from typing import Any, Dict, List, Mapping, Optional, Tuple

from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.request import Request
from rest_framework.views import APIView

from typed_views.utils import parse_complex_type

from .param_settings import ParamSettings
from .params import BodyParam, CurrentUserParam, PassThruParam, PathParam, QueryParam


def Query(*args, **kwargs):
    return ParamSettings("query_param", *args, **kwargs)


def Path(*args, **kwargs):
    return ParamSettings("path", *args, **kwargs)


def CurrentUser(*args, **kwargs):
    return ParamSettings("current_user", *args, **kwargs)


def Body(*args, **kwargs):
    return ParamSettings("body", *args, **kwargs)


def Param(*args, **kwargs):
    return ParamSettings(*args, **kwargs)


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


def is_implicit_view_set_param(param: inspect.Parameter, original_args: list) -> bool:
    if param.name != "self":
        return False

    for arg in original_args:
        if issubclass(type(arg), APIView):
            return True

    return False


def find_request(original_args: list) -> Request:
    for arg in original_args:
        if isinstance(arg, Request):
            return arg
    raise Exception("Could not find request in args:" + str(original_args))


def find_view_set(original_args: list) -> Request:
    for arg in original_args:
        if issubclass(type(arg), APIView):
            return arg
    raise Exception("Could not find view set in args:" + str(original_args))


def build_explicit_view_param(
    param: inspect.Parameter,
    request: Request,
    settings: ParamSettings,
    original_kwargs: dict,
):
    default_value = get_default_value(param)

    if settings.param_type == "path":
        return PathParam(
            param, request, settings=settings, raw_value=original_kwargs.get(param.name)
        )
    elif settings.param_type == "body":
        return BodyParam(param, request, settings=settings)
    elif settings.param_type == "current_user":
        return CurrentUserParam(param, request, settings=settings)
    elif settings.param_type == "query_param":
        return QueryParam(param, request, settings=settings)


def get_view_param(
    param: inspect.Parameter,
    request: Request,
    original_args: list,
    original_kwargs: dict,
):
    explicit_settings = get_explicit_param_settings(param)
    default = get_default_value(param)

    if explicit_settings:
        return build_explicit_view_param(
            param, request, explicit_settings, original_kwargs
        )
    elif is_explicit_request_param(param):
        return PassThruParam(request)
    elif param.name in original_kwargs:
        return PathParam(
            param,
            request,
            settings=ParamSettings(param_type="path", default=default),
            raw_value=original_kwargs.get(param.name),
        )
    elif is_implicit_body_param(param):
        return BodyParam(
            param, request, settings=ParamSettings(param_type="body", default=default)
        )
    elif is_implicit_request_param(param):
        return PassThruParam(request)
    elif is_implicit_view_set_param(param, original_args):
        return PassThruParam(find_view_set(original_args))
    else:
        return QueryParam(
            param,
            request,
            settings=ParamSettings(param_type="query_param", default=default),
        )


def transform_view_params(typed_func, original_args: list, original_kwargs: dict):
    validated_params = []
    errors: Dict[str, Any] = {}
    request = find_request(original_args)

    for name, param in inspect.signature(typed_func).parameters.items():
        p = get_view_param(param, request, original_args, original_kwargs)
        value, error = p.validate_or_error()

        if error:
            errors.update(error)
        else:
            validated_params.append(value)

    if len(errors) > 0:
        raise ValidationError(errors)

    return validated_params


def prevalidate(view_func):
    arg_info = inspect.getfullargspec(view_func)

    if arg_info.varargs is not None or arg_info.varkw is not None:
        raise Exception(
            f"{view_func.__name__}: variable-length argument lists and dictionaries cannot be used with typed views"
        )


def typed_api_view(methods):
    def wrap_validate_and_render(view):
        prevalidate(view)

        @api_view(methods)
        def wrapper(*original_args, **original_kwargs):
            transformed = transform_view_params(view, original_args, original_kwargs)
            return view(*transformed)

        return wrapper

    return wrap_validate_and_render


def typed_action(**action_kwargs):
    def wrap_validate_and_render(view):
        prevalidate(view)

        @action(**action_kwargs)
        @wraps(view)
        def wrapper(*original_args, **original_kwargs):
            transformed = transform_view_params(view, original_args, original_kwargs)
            return view(*transformed)

        return wrapper

    return wrap_validate_and_render


def typed_view(view):
    prevalidate(view)

    def wrap_validate_and_render(*original_args, **original_kwargs):
        transformed = transform_view_params(view, original_args, original_kwargs)
        return view(*transformed)

    return wrap_validate_and_render
