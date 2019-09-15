from django.conf.urls import include, url
from rest_framework import routers
from test_project.testapp.views import get_logs


urlpatterns = [
    url(r"^get-logs/", get_logs, name="get-logs"),
]
