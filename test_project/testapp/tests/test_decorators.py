import inspect
from unittest.mock import MagicMock, patch

from pydantic import BaseModel
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.test import APITestCase

from rest_typed_views import Body, CurrentUser, ParamSettings, Path, Query
from rest_typed_views.decorators import (
    build_explicit_param,
    get_view_param,
    transform_view_params,
)
from rest_typed_views.params import (
    BodyParam,
    CurrentUserParam,
    PassThruParam,
    PathParam,
    QueryParam,
)


class DecoratorTests(APITestCase):
    def fake_request(data={}, query_params={}):
        return MagicMock(data=data, query_params=query_params)

    def get_params(self, func):
        return list(inspect.signature(func).parameters.values())

    def test_transform_view_params_succeeds(self):
        def example_function(id: int, q: str):
            return

        request = self.fake_request(query_params={"q": "cats"})
        typed_params = inspect.signature(example_function).parameters.values()
        result = transform_view_params(typed_params, request, {"id": "1"})
        self.assertEqual(result, [1, "cats"])

    def test_transform_view_params_throws_error(self):
        def example_function(id: int, q: str):
            return

        request = self.fake_request(query_params={})
        typed_params = self.get_params(example_function)

        with self.assertRaises(ValidationError) as context:
            transform_view_params(typed_params, request, {"id": "one"})

        self.assertTrue("A valid integer is required" in str(context.exception))
        self.assertTrue("This field is required" in str(context.exception))

    @patch("rest_typed_views.decorators.build_explicit_param")
    def test_get_view_param_if_explicit_settings(self, mock_build_explicit_param):
        def example_function(body: str = Body(source="name")):
            return

        get_view_param(self.get_params(example_function)[0], self.fake_request(), {})
        mock_build_explicit_param.assert_called_once()

    def test_get_view_param_if_explicit_request_param(self):
        def example_function(request: Request):
            return

        result = get_view_param(
            self.get_params(example_function)[0], self.fake_request(), {}
        )

        self.assertTrue(isinstance(result, PassThruParam))

    def test_get_view_param_if_implicit_path_param(self):
        def example_function(pk: int):
            return

        result = get_view_param(
            self.get_params(example_function)[0], self.fake_request(), {"pk": 1}
        )

        self.assertTrue(isinstance(result, PathParam))

    def test_get_view_param_if_implicit_body_param(self):
        class User(BaseModel):
            id: int
            name = "John Doe"

        def example_function(user: User):
            return

        result = get_view_param(
            self.get_params(example_function)[0], self.fake_request(), {}
        )

        self.assertTrue(isinstance(result, BodyParam))

    def test_get_view_param_if_implicit_query_param(self):
        def example_function(q: str):
            return

        result = get_view_param(
            self.get_params(example_function)[0], self.fake_request(), {}
        )

        self.assertTrue(isinstance(result, QueryParam))

    def test_build_explicit_param_for_query(self):
        def example_function(q: str = Query()):
            return

        result = build_explicit_param(
            self.get_params(example_function)[0],
            self.fake_request(),
            ParamSettings(param_type="query_param"),
            {},
        )

        self.assertTrue(isinstance(result, QueryParam))

    def test_build_explicit_param_for_path(self):
        def example_function(q: str = Path()):
            return

        result = build_explicit_param(
            self.get_params(example_function)[0],
            self.fake_request(),
            ParamSettings(param_type="path"),
            {},
        )

        self.assertTrue(isinstance(result, PathParam))

    def test_build_explicit_param_for_body(self):
        def example_function(q: str = Body()):
            return

        result = build_explicit_param(
            self.get_params(example_function)[0],
            self.fake_request(),
            ParamSettings(param_type="body"),
            {},
        )

        self.assertTrue(isinstance(result, BodyParam))

    def test_build_explicit_param_for_current_user(self):
        def example_function(q: str = CurrentUser()):
            return

        result = build_explicit_param(
            self.get_params(example_function)[0],
            self.fake_request(),
            ParamSettings(param_type="current_user"),
            {},
        )

        self.assertTrue(isinstance(result, CurrentUserParam))
