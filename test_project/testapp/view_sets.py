from typing import List

from pydantic import BaseModel
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_typed_views import typed_action
from test_project.testapp.models import Movie
from test_project.testapp.serializers import MovieSerializer


class Actor(BaseModel):
    id: int
    name: str
    movies: List[int] = []


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer

    def get_queryset(self):
        return Movie.objects.all()

    @typed_action(detail=True, methods=["get"])
    def reviews(self, request, pk: int, test_qp: str, title: str = "My default title"):
        obj = self.get_object()
        return Response({"id": obj.id, "test_qp": test_qp, "title": title})

    @typed_action(detail=False, methods=["POST"])
    def actors(self, actor: Actor):
        return Response(dict(actor))
