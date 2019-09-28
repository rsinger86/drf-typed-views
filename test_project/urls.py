from django.conf.urls import include, url
from rest_framework import routers

from test_project.testapp.views import (
    create_booking,
    create_user,
    get_logs,
    create_band_member,
)
from test_project.testapp.view_sets import MovieViewSet

router = routers.SimpleRouter()

router.register(r"movies", MovieViewSet, basename="movie")

urlpatterns = [
    url(r"^logs/(?P<id>[0-9])/", get_logs, name="logs"),
    url(r"^users/", create_user, name="create-user"),
    url(r"^bookings/", create_booking, name="create-booking"),
    url(r"^band-members/", create_band_member, name="create-band-member"),
    url(r"^", include(router.urls)),
]
