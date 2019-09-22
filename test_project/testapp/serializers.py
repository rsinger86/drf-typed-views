from test_project.testapp.models import Movie
from rest_framework.serializers import ModelSerializer


class MovieSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "rating", "genre"]

