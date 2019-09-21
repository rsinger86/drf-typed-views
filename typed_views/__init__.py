import functools
import inspect
from typing import Any, Dict, List, Mapping, Optional, Tuple

from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.request import Request

from .param_settings import ParamSettings
from .params import BodyParam, CurrentUserParam, PathParam, QueryParam


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
    return get_declared_param_settings(param) is not None


def get_declared_param_settings(param: inspect.Parameter) -> Optional[ParamSettings]:
    try:
        param_type = param.default.param_type
        return param.default
    except AttributeError:
        return None


def is_implicit_body_param(param: inspect.Parameter) -> bool:
    return False


def transform_path_param(
    name: str, param: inspect.Parameter, request: Request, original_kwargs: dict
) -> PathParam:
    param_settings = get_declared_param_settings(param) or ParamSettings(
        param_type="path", default=get_default_value(param)
    )

    return PathParam(
        name,
        param,
        request,
        settings=param_settings,
        raw_value=original_kwargs.get(name),
    )


def transform_non_path_param(request: Request, name: str, param: inspect.Parameter):
    param_settings = get_declared_param_settings(param)
    default_value = get_default_value(param)

    if param_settings and param_settings.param_type == "body":
        return BodyParam(name, param, request, settings=param_settings)
    if param_settings and param_settings.param_type == "current_user":
        return CurrentUserParam(name, param, request, settings=param_settings)
    if param_settings and param_settings.param_type == "query_param":
        return QueryParam(name, param, request, settings=param_settings)
    elif is_implicit_body_param(param):
        return BodyParam(
            name,
            param,
            request,
            settings=ParamSettings(param_type="body", default=default_value),
        )
    else:
        return QueryParam(
            name,
            param,
            request,
            settings=ParamSettings(param_type="query_param", default=default_value),
        )


def divide_path_and_non_path_params(
    typed_params: Mapping[str, inspect.Parameter], original_kwargs: dict
) -> Tuple[list, list]:
    params = list(typed_params.items())
    kwarg_count = len(original_kwargs)

    if len(params) < kwarg_count:
        raise Exception(
            f"{kwarg_count} keyword arguments were captured as path parameters "
            f"and passed to your typed view function, but the function's "
            f"signature only has {len(params)} arguments."
        )

    path_params, non_path_params = params[:kwarg_count], params[kwarg_count:]
    validate_path_params(path_params, original_kwargs)
    return path_params, non_path_params


def validate_path_params(
    path_params: List[Tuple[str, inspect.Parameter]], original_kwargs: dict
):
    param_names = [name for name, param in path_params]

    for kwarg_name in original_kwargs:
        if kwarg_name not in param_names:
            raise Exception(
                f"The argument {kwarg_name} was captured as a path parameter "
                f"and passed to your typed view function, "
                f"but is unspecified in the function's signature"
            )

    for name, param in path_params:
        declared_settings = get_declared_param_settings(param)

        if declared_settings and declared_settings.param_type != "path":
            raise Exception(
                f"{name} was passed into the view as a path parameter but you've "
                f"declared it with parameter settings for {declared_settings.type}"
            )


def transform_args(original_func, original_args: List[Any], original_kwargs: dict):
    request = original_args[0]
    typed_params = inspect.signature(original_func).parameters
    transformed_args = []

    path_params, non_path_params = divide_path_and_non_path_params(
        typed_params, original_kwargs
    )

    params, errors = [], {}

    for name, param in path_params:
        params.append(transform_path_param(name, param, request, original_kwargs))

    for name, param in non_path_params:
        params.append(transform_non_path_param(request, name, param))

    for param in params:
        value, error = param.validate_or_error()

        if error:
            errors.update(error)
        else:
            transformed_args.append(value)

    if len(errors) > 0:
        raise ValidationError(errors)

    return transformed_args


def typed_api_view(methods):
    def wrap_validate_and_render(view):
        @api_view(methods)
        def wrapper(*original_args, **original_kwargs):
            transformed = transform_args(view, original_args, original_kwargs)
            return view(*transformed)

        return wrapper

    return wrap_validate_and_render
