from django.conf.urls import include, url
from rest_framework import routers

from test_project.testapp.views import (
    create_booking,
    create_user,
    get_logs,
    create_band_member,
    get_cache_header,
    test_view,
)
from test_project.testapp.view_sets import MovieViewSet

router = routers.SimpleRouter()

router.register(r"movies", MovieViewSet, basename="movie")

urlpatterns = [
    url(r"^logs/(?P<id>[0-9])/", get_logs, name="get-log-entry"),
    url(r"^users/", create_user, name="create-user"),
    url(r"^test/", test_view, name="test-view"),
    url(r"^bookings/", create_booking, name="create-booking"),
    url(r"^test/", test_view, name="test-view"),
    url(r"^band-members/", create_band_member, name="create-band-member"),
    url(r"^get-cache-header/", get_cache_header, name="get-cache-header"),
    url(r"^", include(router.urls)),
]
