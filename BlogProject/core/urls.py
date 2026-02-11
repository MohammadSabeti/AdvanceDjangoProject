"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.documentation import include_docs_urls

from core import settings

# -----------------------------
# OpenAPI Infos
# -----------------------------
info_v1 = openapi.Info(
    title="Blog Project API (v1)",
    default_version="v1",
    description="Public API v1 (blog + custom endpoints)",
    contact=openapi.Contact(email="mohammad.sabeti2000@gmail.com"),
    license=openapi.License(name="MIT License"),
)

info_v2 = openapi.Info(
    title="Blog Project API (v2)",
    default_version="v2",
    description="Auth API v2 (Djoser + JWT)",
    contact=openapi.Contact(email="mohammad.sabeti2000@gmail.com"),
    license=openapi.License(name="MIT License"),
)
# -----------------------------
# Swagger schema views (split)
# -----------------------------
schema_view_v1 = get_schema_view(
    info_v1,
    public=True,
    permission_classes=[permissions.AllowAny],
    patterns=[
        path("api/v1/accounts/", include("accounts.urls")),
        path("api/v1/blog/", include("blog.urls")),
    ],
)

schema_view_v2 = get_schema_view(
    info_v2,
    public=True,
    permission_classes=[permissions.AllowAny],
    patterns=[
        path("api/v2/", include("djoser.urls")),
        path("api/v2/", include("djoser.urls.jwt")),
    ],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    # path("api-docs/", include_docs_urls(title="api sample")),

    # -----------------------------
    # API routes (versioned)
    # -----------------------------
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/blog/", include("blog.urls")),
    # v2 auth (djoser)
    path("api/v2/", include("djoser.urls")),
    path("api/v2/", include("djoser.urls.jwt")),
    # -----------------------------
    # Swagger / ReDoc (split by version)
    # -----------------------------
    path(
        "swagger/v1.json",
        schema_view_v1.without_ui(cache_timeout=0),
        name="schema-v1-json",
    ),
    path(
        "swagger/v1/",
        schema_view_v1.with_ui("swagger", cache_timeout=0),
        name="schema-v1-swagger-ui",
    ),
    path(
        "redoc/v1/",
        schema_view_v1.with_ui("redoc", cache_timeout=0),
        name="schema-v1-redoc",
    ),
    path(
        "swagger/v2.json",
        schema_view_v2.without_ui(cache_timeout=0),
        name="schema-v2-json",
    ),
    path(
        "swagger/v2/",
        schema_view_v2.with_ui("swagger", cache_timeout=0),
        name="schema-v2-swagger-ui",
    ),
    path(
        "redoc/v2/",
        schema_view_v2.with_ui("redoc", cache_timeout=0),
        name="schema-v2-redoc",
    ),
]

# serving static and media for development
if settings.DEBUG:
    urlpatterns += (
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        + debug_toolbar_urls()
    )
