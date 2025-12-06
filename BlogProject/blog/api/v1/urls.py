from django.urls import path, include
from .views import *

app_name = 'api-1'
urlpatterns = [
    # path("post/", post_list, name="post_list"),
    # path("post/<int:id>/", post_detail, name="post_detail"),
    path("post/", PostList.as_view(), name="post_list"),
    path("post/<int:id>/", PostDetail.as_view(), name="post_detail"),

]
