from unittest.mock import MagicMock

from rest_framework.fields import empty
from rest_framework.test import APITestCase

from rest_typed_views import ParamSettings
from rest_typed_views.params import BodyParam


class ParamsTests(APITestCase):
    def fake_request(self, data={}, query_params={}):
        return MagicMock(data=data, query_params=query_params)

    def test_body_raw_value_should_be_request_data_when_not_set(self):
        body_param = BodyParam(
            MagicMock(), self.fake_request(data={"a": "b"}), ParamSettings()
        )

        self.assertEqual(body_param._get_raw_value(), {"a": "b"})

    def test_body_raw_value_should_be_request_data_when_wildcard_set(self):
        body_param = BodyParam(
            MagicMock(), self.fake_request(data={"a": "b"}), ParamSettings(source="*")
        )

        self.assertEqual(body_param._get_raw_value(), {"a": "b"})

    def test_body_raw_value_should_be_empty_when_src_specified_but_not_found(self):
        body_param = BodyParam(
            MagicMock(), self.fake_request(data={"a": "b"}), ParamSettings(source="c")
        )

        self.assertEqual(body_param._get_raw_value(), empty)

    def test_body_raw_value_should_be_found_when_src_specified(self):
        body_param = BodyParam(
            MagicMock(), self.fake_request(data={"a": "b"}), ParamSettings(source="a")
        )

        self.assertEqual(body_param._get_raw_value(), "b")
