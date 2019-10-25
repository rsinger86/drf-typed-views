from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from decimal import Decimal
from uuid import UUID
import datetime


class TypedAPIViewTests(APITestCase):
    def test_get_logs__ok(self):
        url = reverse("get-log-entry", args=[7])

        response = self.client.get(
            url,
            {
                "latitude": "63.44",
                "title": "My title",
                "price": 7.5,
                "is_pretty": "yes",
                "email": "homer@hotmail.com",
                "upper_alpha_string": "NBA",
                "identifier": "24adfads",
                "website": "http://bloomgerg.com",
                "identity": "a1e77325-8429-480e-a990-8764f33db2d8",
                "ip": "162.254.168.185",
                "timestamp": "2013-07-16T19:23:00Z",
                "start_date": "2013-07-16",
                "start_time": "10:00",
                "duration": "12 2:23",
                "bag": "paper",
                "numbers": "1,2,3",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data,
            {
                "id": 7,
                "title": "My title",
                "price": 7.5,
                "latitude": Decimal("63.44000000000000000000"),
                "is_pretty": True,
                "email": "homer@hotmail.com",
                "upper_alpha_string": "NBA",
                "identifier": "24adfads",
                "website": "http://bloomgerg.com",
                "identity": UUID("a1e77325-8429-480e-a990-8764f33db2d8"),
                "ip": "162.254.168.185",
                "timestamp": datetime.datetime(
                    2013, 7, 16, 19, 23, tzinfo=datetime.timezone.utc
                ),
                "start_date": datetime.date(2013, 7, 16),
                "start_time": datetime.time(10, 0),
                "duration": datetime.timedelta(12, 143),
                "bag_type": "paper",
                "numbers": [1, 2, 3],
            },
        )

    def test_get_logs_error(self):
        url = reverse("get-log-entry", args=[7])

        response = self.client.get(
            url,
            {
                "is_pretty": "maybe",
                "email": "homerathotmail.com",
                "upper_alpha_string": "mma",
                "identifier": "**()",
                "identity": "a1e77325-8429-480e-a990-8764f33db2d8",
                "ip": "162.254.168.185",
                "timestamp": "700BC-07-16T19:23:00Z",
                "start_date": "i'll get to it",
                "start_time": "when i wake up",
                "duration": "forever",
                "bag": "scrotum",
                "numbers": "fiver",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.json(),
            {
                "latitude": ["This field is required."],
                "title": ["This field is required."],
                "price": ["This field is required."],
                "is_pretty": ["Must be a valid boolean."],
                "email": ["Enter a valid email address."],
                "upper_alpha_string": [
                    "This value does not match the required pattern."
                ],
                "identifier": [
                    'Enter a valid "slug" consisting of letters, numbers, underscores or hyphens.'
                ],
                "website": ["This field is required."],
                "timestamp": [
                    "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."
                ],
                "start_date": [
                    "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
                ],
                "start_time": [
                    "Time has wrong format. Use one of these formats instead: hh:mm[:ss[.uuuuuu]]."
                ],
                "duration": [
                    "Duration has wrong format. Use one of these formats instead: [DD] [HH:[MM:]]ss[.uuuuuu]."
                ],
                "bag": ['"scrotum" is not a valid choice.'],
                "numbers": {"0": ["A valid integer is required."]},
            },
        )

    def test_create_user_ok(self):
        url = reverse("create-user")
        response = self.client.post(
            url,
            {
                "id": 12,
                "name": "Robert",
                "signup_ts": "2013-07-16T19:23:00Z",
                "friends": [3],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data,
            {
                "id": 12,
                "name": "Robert",
                "signup_ts": datetime.datetime(
                    2013, 7, 16, 19, 23, tzinfo=datetime.timezone.utc
                ),
                "friends": [3],
            },
        )

    def test_create_user_error(self):
        url = reverse("create-user")
        response = self.client.post(
            url,
            {"name": "Robert", "signup_ts": "2013-07-16T19:23:00Z", "friends": [3]},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.json(),
            {
                "user": [
                    {
                        "loc": "('id',)",
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        )

    def test_cache_header_ok(self):
        url = reverse("get-cache-header")
        response = self.client.get(
            url, HTTP_CACHE="no"
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data,
            "no",
        )

    def test_cache_header_error(self):
        url = reverse("get-cache-header")
        response = self.client.get(
            url,
        )
        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.json(),
            {'cache': ['This field may not be null.']},
        )

    def test_create_booking_ok(self):
        url = reverse("create-booking")
        response = self.client.post(
            url,
            {
                "_data": {
                    "item": {
                        "start_date": "2019-11-11",
                        "end_date": "2019-11-13",
                        "include_breakfast": True,
                        "room": "twin",
                    }
                }
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "start_date": "2019-11-11",
                "end_date": "2019-11-13",
                "room": "twin",
                "include_breakfast": True,
            },
        )

    def test_create_booking_error(self):
        url = reverse("create-booking")
        response = self.client.post(
            url,
            {
                "_data": {
                    "item": {
                        "start_date": "2019-11-11",
                        "end_date": "2019-11-13",
                        "include_breakfast": True,
                    }
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.json(), {"_data.item": {"room": "This field is required."}}
        )

    def test_create_band_member_ok(self):
        url = reverse("create-band-member")
        response = self.client.post(
            url, {"name": "Homer", "email": "homer@hotmail.com"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"name": "Homer", "email": "homer@hotmail.com"})

    def test_create_band_member_error(self):
        url = reverse("create-band-member")
        response = self.client.post(url, {"email": "homer@hotmail.com"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"band_member": {"name": ["Missing data for required field."]}},
        )
