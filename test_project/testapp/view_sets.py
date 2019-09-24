from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from test_project.testapp.models import Movie
from test_project.testapp.serializers import MovieSerializer
from typed_views import typed_action, typed_method


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer

    def get_queryset(self):
        return Movie.objects.all()

    @typed_action(detail=True, methods=["get"])
    def reviews(self, request, pk: int, title: int):
        return Response({"hello": "world"})

    @action(detail=True, methods=["get"])
    def actors(self, request, pk: int):
        return Response({"hello": "world"})

    @typed_method
    def list(self, request):
        return Response({"hello": "world"})

    @typed_method
    def retrieve(self, pk: int, title: str):
        return Response({"hello": "world"})
