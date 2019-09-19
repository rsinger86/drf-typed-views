import functools
import inspect
from typing import Any, Dict, List, Mapping, Tuple

import typesystem
from django.contrib.auth.models import User
from django.shortcuts import render
from marshmallow import Schema, fields
from rest_framework import viewsets
from rest_framework.response import Response

from typed_views import typed_api_view, CurrentUser


@typed_api_view(["GET"])
def get_logs(id: int, title: str = None, user: User = CurrentUser()):
    return Response({"status": "OK"})


# CurrentUser, Path, QP, QueryParam
# required, default, list_format=csv|repeated|repeated_w_brackets


# UserSchema = Schema.from_dict({"age": fields.Range()})

# data = UserSchema().load({"age": "31.35"})
# print(data)
