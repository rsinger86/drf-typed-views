import inspect
from typing import Any, Dict, List

from rest_framework.views import APIView
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.request import Request

from rest_typed_views.utils import (
    find_request,
    get_default_value,
    get_explicit_param_settings,
    is_explicit_request_param,
    is_implicit_body_param,
    is_implicit_request_param,
)

from .param_settings import ParamSettings
from .params import BodyParam, CurrentUserParam, PassThruParam, PathParam, QueryParam, HeaderParam



def wraps_drf(view):
    def _wraps_drf(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.__name__ = view.__name__
        wrapper.__module__ = view.__module__
        wrapper.renderer_classes = getattr(
            view, "renderer_classes", APIView.renderer_classes
        )
        wrapper.parser_classes = getattr(view, "parser_classes", APIView.parser_classes)
        wrapper.authentication_classes = getattr(
            view, "authentication_classes", APIView.authentication_classes
        )
        wrapper.throttle_classes = getattr(
            view, "throttle_classes", APIView.throttle_classes
        )
        wrapper.permission_classes = getattr(
            view, "permission_classes", APIView.permission_classes
        )
        return wrapper

    return _wraps_drf


def build_explicit_param(
    param: inspect.Parameter, request: Request, settings: ParamSettings, path_args: dict
):
    if settings.param_type == "path":
        key = settings.source or param.name
        raw_value = path_args.get(key, empty)
        return PathParam(param, request, settings=settings, raw_value=raw_value)
    elif settings.param_type == "body":
        return BodyParam(param, request, settings=settings)
    elif settings.param_type == "header":
        return HeaderParam(param, request, settings=settings)
    elif settings.param_type == "current_user":
        return CurrentUserParam(param, request, settings=settings)
    elif settings.param_type == "query_param":
        return QueryParam(param, request, settings=settings)


def get_view_param(param: inspect.Parameter, request: Request, path_args: dict):
    explicit_settings = get_explicit_param_settings(param)
    default = get_default_value(param)

    if explicit_settings:
        return build_explicit_param(param, request, explicit_settings, path_args)
    elif is_explicit_request_param(param):
        return PassThruParam(request)
    elif param.name in path_args:
        return PathParam(
            param,
            request,
            settings=ParamSettings(param_type="path", default=default),
            raw_value=path_args.get(param.name),
        )
    elif is_implicit_body_param(param):
        return BodyParam(
            param, request, settings=ParamSettings(param_type="body", default=default)
        )
    elif is_implicit_request_param(param):
        return PassThruParam(request)
    else:
        return QueryParam(
            param,
            request,
            settings=ParamSettings(param_type="query_param", default=default),
        )


def transform_view_params(
    typed_params: List[inspect.Parameter], request: Request, path_args: dict
):
    validated_params = []
    errors: Dict[str, Any] = {}

    for param in typed_params:
        p = get_view_param(param, request, path_args)
        value, error = p.validate_or_error()

        if error:
            errors.update(error)
        else:
            validated_params.append(value)

    if len(errors) > 0:
        raise ValidationError(errors)

    return validated_params


def prevalidate(view_func, for_method: bool = False):
    arg_info = inspect.getfullargspec(view_func)

    if arg_info.varargs is not None or arg_info.varkw is not None:
        raise Exception(
            f"{view_func.__name__}: variable-length argument lists and dictionaries cannot be used with typed views"
        )

    if for_method:
        error_msg = "For typed methods, 'self' must be passed as the first arg with no annotation"

        if (
            len(arg_info.args) < 1
            or arg_info.args[0] != "self"
            or "self" in arg_info.annotations
        ):
            raise Exception(error_msg)


def typed_api_view(methods):
    def wrap_validate_and_render(view):
        prevalidate(view)

        @api_view(methods)
        @wraps_drf(view)
        def wrapper(*original_args, **original_kwargs):
            original_args = list(original_args)
            request = find_request(original_args)
            transformed = transform_view_params(
                inspect.signature(view).parameters.values(), request, original_kwargs
            )
            return view(*transformed)

        return wrapper

    return wrap_validate_and_render


def typed_action(**action_kwargs):
    def wrap_validate_and_render(view):
        prevalidate(view, for_method=True)

        @action(**action_kwargs)
        @wraps_drf(view)
        def wrapper(*original_args, **original_kwargs):
            original_args = list(original_args)
            request = find_request(original_args)
            _self = original_args.pop(0)

            typed_params = [
                p for n, p in inspect.signature(view).parameters.items() if n != "self"
            ]

            transformed = transform_view_params(typed_params, request, original_kwargs)
            return view(_self, *transformed)

        return wrapper

    return wrap_validate_and_render
