from django.urls import path
from ..views import *

urlpatterns = [
    path("", ProfileApiView.as_view(), name="profile"),
]
