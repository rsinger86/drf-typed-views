from rest_framework.response import Response
from rest_framework.views import APIView
from typed_views import typed_method


class MovieView(APIView):
    @typed_method
    def get(self, request, number: int):
        """
        Return a list of all users.
        """

        return Response({"1": number})
