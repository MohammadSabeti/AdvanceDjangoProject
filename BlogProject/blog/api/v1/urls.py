from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('post',PostViewSet, basename='Posts')
router.register('category',CategoryViewSet, basename='Categories')
app_name = 'api-v1'
urlpatterns = [
    path("", include(router.urls)),
    path("post_fbv/", post_list, name="post_list_fbv"),
    path("post_fbv/<int:id>/", post_detail, name="post_detail_fbv"),
    path("post_api_view/", PostListAPIView.as_view(), name="post_list_api_view"),
    path("post_api_view/<int:id>/", PostDetailAPIView.as_view(), name="post_detail_api_view"),
    path("post_gen_api_view/", PostListGenericAPIView.as_view(), name="post_list_gen_api_view"),
    path("post_gen_api_view/<int:id>/", PostDetailGenericAPIView.as_view(), name="post_detail_gen_api_view"),


]

# urlpatterns=router.urls