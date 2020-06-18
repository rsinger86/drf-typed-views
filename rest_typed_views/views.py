import inspect

from rest_framework.views import APIView
from .decorators import transform_view_params


class TypedAPIView(APIView):
    def dispatch(self, request, *args, **kwargs):
        """
        Override drf's `dispatch` for typing params.
        """
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers  # deprecate?

        try:
            self.initial(request, *args, **kwargs)

            # Get the appropriate handler method
            if request.method.lower() in self.http_method_names:
                handler = getattr(
                    self, request.method.lower(), self.http_method_not_allowed
                )
            else:
                handler = self.http_method_not_allowed

            typed_params = [
                p
                for n, p in inspect.signature(handler).parameters.items()
                if n != "self"
            ]
            transformed = transform_view_params(typed_params, request, kwargs)

            response = handler(*transformed)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response
