from django.urls import path, include


app_name = 'api-v1'
urlpatterns = [
    path("auth/",include('accounts.api.v1.urls.auth')),
    path("profile/",include('accounts.api.v1.urls.profiles')),
]
