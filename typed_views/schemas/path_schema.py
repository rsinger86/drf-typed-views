import inspect
from typing import Any

from typed_views.classes import GenericRequest, Missing
from typed_views.param_settings import PathParam
from typed_views.schemas import TypedParamSchema


class PathSchema(TypedParamSchema):
    type = "path"

    def __init__(
        self,
        name: str,
        param: inspect.Parameter,
        settings: PathParam,
        raw_value: Any = Missing,
    ):
        self.name = name
        self.param = param
        self.settings = settings
        self.raw_value = raw_value
