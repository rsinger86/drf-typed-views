import functools
import inspect
from typing import Any, Dict

from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


class GenericRequest(object):
    def __init__(self, request):
        self.request = request


class TypedInputParam(object):
    def set_request(self, request: GenericRequest):
        self.request = request

    def set_name(self, name: str):
        self.name = name

    def set_param(self, param: inspect.Parameter):
        self.param = param


class PathParam(TypedInputParam):
    def __init__(self, param: inspect.Parameter, value=None):
        self.param = param
        self.value = value


class QueryParam(TypedInputParam):
    def __init__(self, param: inspect.Parameter, request: GenericRequest = None):
        self.param = param
        self.request = request


class Body(TypedInputParam):
    def __init__(self, param: inspect.Parameter, request: GenericRequest = None):
        self.param = param
        self.request = request


class CurrentUser(TypedInputParam):
    pass


class CurrentRequest(object):
    pass


def get_declared_schema(param: inspect.Parameter):
    if param.default is inspect.Parameter.empty:
        return None, None
    elif isinstance(param.default, PathParam):
        return PathParam, param.default
    elif isinstance(param.default, QueryParam):
        return QueryParam, param.default
    elif isinstance(param.default, Body):
        return Body, param.default
    elif isinstance(param.default, CurrentUser):
        return CurrentUser, param.default
    elif isinstance(param.default, CurrentRequest):
        return CurrentRequest, param.default
    else:
        return None, None


def is_supported_body_type(param: inspect.Parameter) -> bool:
    return False


def transform_param(
    request: GenericRequest, path_values: dict, name: str, param: inspect.Parameter
):
    transformed = None
    SchemaClass, schema = get_declared_schema(param)

    if name in path_values:
        if SchemaClass is None:
            return PathParam(param=param, value=path_values[name])
        elif SchemaClass is PathParam:
            schema.set_name(name)
            schema.set_request(name)
            schema.set_value(path_values[name])
            return schema
    elif SchemaClass in (Body, QueryParam, CurrentRequest, CurrentUser):
        schema.set_request(request)
        return schema
    elif is_supported_body_type(param):
        return Body(param, request=request)

    return QueryParam(param, request=request)


def transform_input_params(
    original_func, original_arg_values: list, original_kwarg_values: dict
):
    transformed_args = []
    request = original_arg_values[0]
    path_values = original_kwarg_values

    for name, param in inspect.signature(original_func).parameters.items():
        transformed_args.append(transform_param(request, path_values, name, param))

    print(transformed_args)
    return [1]


def typed_view(view):
    @functools.wraps(view)
    def validate_and_render(*raw_args, **raw_kwargs):
        data = view(*args, **kwargs)
        return data

    return validate_and_render


def typed_api_view(methods):
    def wrap_validate_and_render(view):
        @api_view(methods)
        def wrapper(*raw_args, **raw_kwargs):
            args = transform_input_params(view, raw_args, raw_kwargs)
            return view(*args)

        return wrapper

    return wrap_validate_and_render


@typed_api_view(["GET"])
def get_logs(id: int, title: str = None, user: User = CurrentUser()):
    return Response({"status": "OK"})


# CurrentUser, Path, QP, QueryParam
# required, default, list_format=csv|repeated|repeated_w_brackets
