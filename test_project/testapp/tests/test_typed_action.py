from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from test_project.testapp.models import Movie


class TypedActionTests(APITestCase):
    def setUp(self):
        Movie.objects.all().delete()

    def test_get_reviews_ok(self):
        movie = Movie.objects.create(title="My movie", rating=5.0, genre="comedy")
        url = reverse("movie-reviews", args=[movie.id])

        response = self.client.get(url, {"test_qp": "cats"}, format="json")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data, {"id": 1, "test_qp": "cats", "title": "My default title"}
        )

    def test_get_reviews_error(self):
        movie = Movie.objects.create(title="My movie", rating=5.0, genre="comedy")
        url = reverse("movie-reviews", args=[movie.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"test_qp": ["This field is required."]})

    def test_create_actor_ok(self):
        url = reverse("movie-actors")

        response = self.client.post(
            url, {"id": 123, "name": "Tom Cruze"}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"id": 123, "name": "Tom Cruze", "movies": []})

    def test_create_actor_error(self):
        url = reverse("movie-actors")

        response = self.client.post(url, {"id": 123}, format="json")

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.json(),
            {
                "actor": [
                    {
                        "loc": "('name',)",
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        )
