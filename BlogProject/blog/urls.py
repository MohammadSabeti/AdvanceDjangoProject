from django.urls import path, include
from . import views

app_name='blog'
urlpatterns = [

    # API
    # TODO: for running tests in this version, comment api path
    path("", include("blog.api.v1.urls")),

    # Template Views
    path("home", views.IndexView.as_view(), name="index"),
    # path('go-to-maktabkhooneh', views.RedirectToMaktab.as_view(), name='redirect-to-maktabkhooneh'),
    path("post/", views.PostListView.as_view(), name="post-list-tmp"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post-detail-tmp"),
    path("post/create/", views.PostCreateView.as_view(), name="post-create-tmp"),
    path("post/<int:pk>/edit/", views.PostEditView.as_view(), name="post-edit-tmp"),
    path("post/<int:pk>/delete/",views.PostDeleteView.as_view(),name="post-delete-tmp",)

]