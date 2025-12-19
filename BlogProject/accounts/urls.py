from django.urls import path, include
from .views import *

app_name='accounts'
urlpatterns = [
path("", include("django.contrib.auth.urls")),
path("", include("accounts.api.v1.urls")),
]