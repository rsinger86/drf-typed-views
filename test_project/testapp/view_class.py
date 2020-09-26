from typing import List

from pydantic import BaseModel
from rest_framework.response import Response

from rest_typed_views import TypedAPIView, Query, Path


class MusicSchema(BaseModel):
    id: int
    title: str
    rating: int = None
    genre: str


class MusicAPIView(TypedAPIView):

    def get(
        self,
        limit: int = Query(default=5, min_value=1, max_value=10),
        offset: int = 0
    ):
        return Response(data={
            "data": [],
            "limit": limit,
            "offset": offset
        }, status=200)

    def post(self, music: MusicSchema):
        return Response(data={
            "id": music.id,
            "title": music.title,
            "rating": music.rating,
            "genre": music.genre
        }, status=201)
