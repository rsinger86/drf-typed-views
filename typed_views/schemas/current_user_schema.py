import inspect
from typing import Any

from typed_views.classes import GenericRequest, Missing
from typed_views.param_settings import CurrentUserParam
from typed_views.schemas import TypedParamSchema


class CurrentUserSchema(TypedParamSchema):
    type = "current_user"

    def __init__(
        self,
        name: str,
        param: inspect.Parameter,
        request: GenericRequest,
        settings: CurrentUserParam,
    ):
        self.name = name
        self.param = param
        self.request = request
        self.settings = settings
