import functools
import inspect
from typing import Any, Dict, List, Mapping, Tuple

from rest_framework.decorators import api_view

from .classes import GenericRequest, Missing
from .param_settings import (
    BodyParam,
    CurrentRequestParam,
    CurrentUserParam,
    PathParam,
    QueryParam,
)
from .schemas import (
    BodySchema,
    CurrentRequestSchema,
    CurrentUserSchema,
    PathSchema,
    QuerySchema,
)

Path = PathParam
Query = QueryParam
Body = BodyParam
CurrentUser = CurrentUserParam
CurrentRequest = CurrentRequestParam


def get_default_value(param: inspect.Parameter) -> Any:
    if (
        not is_param_default_used_to_pass_schema(param)
        and param.default is not inspect.Parameter.empty
    ):
        return param.default
    return Missing


def is_param_default_used_to_pass_schema(param: inspect.Parameter) -> bool:
    return get_declared_param_settings(param) is not None


def get_declared_param_settings(param: inspect.Parameter):
    if (
        isinstance(param.default, PathParam)
        or isinstance(param.default, QueryParam)
        or isinstance(param.default, BodyParam)
        or isinstance(param.default, CurrentUserParam)
        or isinstance(param.default, CurrentRequestParam)
    ):
        return param.default
    else:
        return None


def is_implicit_body_param(param: inspect.Parameter) -> bool:
    return False


def transform_path_param(
    name: str, param: inspect.Parameter, original_kwargs: dict
) -> PathSchema:
    param_settings = get_declared_param_settings(param) or PathParam(
        default=get_default_value(param)
    )

    return PathSchema(
        name, param, settings=param_settings, raw_value=original_kwargs.get(name)
    )


def transform_non_path_param(
    request: GenericRequest, name: str, param: inspect.Parameter
):
    param_settings = get_declared_param_settings(param)
    default_value = get_default_value(param)

    if param_settings and param_settings.type == "body":
        return BodySchema(name, param, request, settings=param_settings)
    elif param_settings and param_settings.type == "query":
        return QuerySchema(name, param, request, settings=param_settings)
    elif param_settings and param_settings.type == "current_request":
        return CurrentRequestSchema(name, param, request, settings=param_settings)
    elif param_settings and param_settings.type == "current_user":
        return CurrentUserSchema(name, param, request, settings=param_settings)
    elif is_implicit_body_param(param):
        return BodySchema(
            name, param, request, settings=BodyParam(default=default_value)
        )
    else:
        return QuerySchema(
            name, param, request, settings=QueryParam(default=default_value)
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

        if declared_settings and declared_settings.type != "path":
            raise Exception(
                f"{name} was passed into the view as a path parameter but you've "
                f"declared it with parameter settings for {declared_settings.type}"
            )


def transform_input_params(
    original_func, original_args: List[Any], original_kwargs: dict
):
    request = GenericRequest(original_args[0])
    typed_params = inspect.signature(original_func).parameters
    transformed_args = []

    path_params, non_path_params = divide_path_and_non_path_params(
        typed_params, original_kwargs
    )

    for name, param in path_params:
        transformed_args.append(transform_path_param(name, param, original_kwargs))

    for name, param in non_path_params:
        transformed_args.append(transform_non_path_param(request, name, param))

    return [arg.get_value() for arg in transformed_args]


def typed_view(view):
    @functools.wraps(view)
    def validate_and_render(*raw_args, **raw_kwargs):
        data = view(*args, **kwargs)
        return data

    return validate_and_render


def typed_api_view(methods):
    def wrap_validate_and_render(view):
        @api_view(methods)
        def wrapper(*original_args, **original_kwargs):
            transformed = transform_input_params(view, original_args, original_kwargs)
            print("!!", transformed)
            return view(*transformed)

        return wrapper

    return wrap_validate_and_render
