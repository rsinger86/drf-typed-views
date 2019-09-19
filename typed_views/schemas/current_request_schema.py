import inspect
from typing import Any

from typed_views.classes import GenericRequest, Missing
from typed_views.param_settings import CurrentRequestParam
from typed_views.schemas import TypedParamSchema


class CurrentRequestSchema(TypedParamSchema):
    type = "current_request"

    def __init__(
        self,
        name: str,
        param: inspect.Parameter,
        request: GenericRequest,
        settings: CurrentRequestParam,
    ):
        self.name = name
        self.param = param
        self.request = request
        self.settings = settings
