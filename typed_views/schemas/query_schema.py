import inspect

from typed_views.classes import GenericRequest
from typed_views.param_settings import QueryParam
from typed_views.schemas import TypedParamSchema


class QuerySchema(TypedParamSchema):
    type = "query"

    def __init__(
        self,
        name: str,
        param: inspect.Parameter,
        request: GenericRequest,
        settings: QueryParam,
    ):
        self.name = name
        self.param = param
        self.request = request
        self.settings = settings
