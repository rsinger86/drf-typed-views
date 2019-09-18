import functools
import inspect
from typing import Any, Dict, List, Tuple, Mapping

from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


class GenericRequest(object):
    def __init__(self, request):
        self.request = request


class NoValue(object):
    pass


## Params


class TypedInputParam(object):
    def __init__(
        self,
        name: str,
        param: inspect.Parameter,
        request: GenericRequest,
        schema,
        raw_value: Any = NoValue(),
    ):
        self.name = name
        self.param = param
        self.request = request
        self.schema = schema
        self.raw_value = raw_value

    def is_required(self):
        if is_param_default_used_to_pass_schema(self.param):
            return self.schema.required
        return self.param.default is inspect.Parameter.empty

    def get_default(self) -> Any:
        if is_param_default_used_to_pass_schema(self.param):
            return self.schema.default
        if self.param.default is inspect.Parameter.empty:
            return NoValue
        else:
            return self.param.default

    def get_value(self):
        value = self.raw_value
        value = self.cast_value(value)
        self.validate_value(value)
        return value

    def cast_value(self, value: Any):
        return value

    def validate_value(self, value: Any):
        if self.is_required() and isinstance(value, NoValue):
            raise Exception(f"Must pass value for {self.name}")


class PathParam(TypedInputParam):
    pass


class QueryParam(TypedInputParam):
    pass


class BodyParam(TypedInputParam):
    pass


class CurrentUserParam(TypedInputParam):
    pass


class CurrentRequestParam(TypedInputParam):
    pass


## Schemas


class PathSchema(object):
    type = "path"

    def __init__(self, required: bool = True):
        self.required = required


class QuerySchema(object):
    type = "query"

    def __init__(self, required: bool = False):
        self.required = required


class BodySchema(object):
    type = "body"

    def __init__(self, required: bool = False):
        self.required = required


class CurrentUserSchema(object):
    type = "current_user"

    def __init__(self, required: bool = False):
        self.required = required


class CurrentRequestSchema(object):
    type = "current_request"

    def __init__(self, required: bool = False):
        self.required = required


Path = PathSchema
Query = QuerySchema
Body = BodySchema
CurrentUser = CurrentUserSchema
CurrentRequest = CurrentRequestSchema


def is_param_default_used_to_pass_schema(param: inspect.Parameter) -> bool:
    return get_declared_schema(param) is not None


def is_value_set(value: Any) -> bool:
    return isinstance(value, NoValue) is False


def get_declared_schema(param: inspect.Parameter):
    if (
        isinstance(param.default, PathSchema)
        or isinstance(param.default, QuerySchema)
        or isinstance(param.default, BodySchema)
        or isinstance(param.default, CurrentUserSchema)
        or isinstance(param.default, CurrentRequestSchema)
    ):
        return param.default
    else:
        return None


def is_implicit_body_param(param: inspect.Parameter) -> bool:
    return False


def transform_path_param(
    request: GenericRequest, name: str, param: inspect.Parameter, original_kwargs: dict
) -> PathParam:
    schema = get_declared_schema(param) or PathSchema()

    return PathParam(
        name, param, request, raw_value=original_kwargs.get(name), schema=schema
    )


def transform_non_path_param(
    request: GenericRequest, name: str, param: inspect.Parameter
):
    schema = get_declared_schema(param)

    if schema and schema.type == "body":
        return BodyParam(name, param, request, schema=schema)
    elif schema and schema.type == "query":
        return QueryParam(name, param, request, schema=schema)
    elif schema and schema.type == "current_request":
        return CurrentRequestParam(name, param, request, schema=schema)
    elif schema and schema.type == "current_user":
        return CurrentUserParam(name, param, request, schema=schema)
    elif is_implicit_body_param(param):
        return BodyParam(name, param, request, schema=BodySchema())
    else:
        return QueryParam(name, param, request, schema=QuerySchema())


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
        declared_schema = get_declared_schema(param)

        if declared_schema and declared_schema.type != "path":
            raise Exception(
                f"{name} was passed into the view as a path parameter"
                f"but you've declared it with a schema of type {declared_schema.type}"
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
        transformed_args.append(
            transform_path_param(request, name, param, original_kwargs)
        )

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


@typed_api_view(["GET"])
def get_logs(id: int, title: str = None, user: User = CurrentUser()):
    return Response({"status": "OK"})


# CurrentUser, Path, QP, QueryParam
# required, default, list_format=csv|repeated|repeated_w_brackets
