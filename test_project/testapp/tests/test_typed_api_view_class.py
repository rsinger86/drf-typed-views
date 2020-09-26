from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from test_project.testapp.models import Movie


class TypedAPIViewClassTests(APITestCase):
    def test_get_musics_ok(self):
        url = reverse("music-list")
        response = self.client.get(url, {"limit": 5}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data, {"data": [], "limit": 5, "offset": 0}
        )

    def test_get_musics_error(self):
        url = reverse("music-list")
        response = self.client.get(url, {"limit": 20}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {
                "limit": ["Ensure this value is less than or equal to 10."]}
        )

    def test_create_music_ok(self):
        url = reverse("music-list")
        response = self.client.post(
            url, {
                "id": 123,
                "title": "My Music",
                "rating": 5,
                "genre": "jazz"
            }, format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data, {
                "id": 123,
                "title": "My Music",
                "rating": 5,
                "genre": "jazz"
            }
        )

    def test_create_music_error(self):
        url = reverse("music-list")
        response = self.client.post(
            url, {
                "id": 123,
                "title": "My Music"
            }, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "music": [
                    {
                        "loc": "('genre',)",
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        )
