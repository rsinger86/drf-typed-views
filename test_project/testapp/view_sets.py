from test_project.testapp.serializers import MovieSerializer
from rest_framework import viewsets
from test_project.testapp.models import Movie


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer

    def get_queryset(self):
        return Movie.objects.all()
