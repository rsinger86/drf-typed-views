import functools
import inspect

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


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
            return view(*raw_args, **raw_kwargs)
        return wrapper

    return wrap_validate_and_render


@typed_api_view(["GET"])
def get_logs(request):
    return Response({"status": "OK"})

