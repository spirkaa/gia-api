from decorator_include import decorator_include
from django.urls import include, path, re_path
from django.views.decorators.cache import never_cache
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token

from . import views

schema_view = get_schema_view(
    openapi.Info(title="GIA API", default_version="v1",),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register(r"date", views.DateViewSet)
router.register(r"level", views.LevelViewSet)
router.register(r"organisation", views.OrganisationViewSet)
router.register(r"position", views.PositionViewSet)
router.register(r"employee", views.EmployeeViewSet, basename="employee")
router.register(r"place", views.PlaceViewSet)
router.register(r"exam", views.ExamViewSet)
router.register(r"examflat", views.ExamFlatViewSet, basename="flat")
router.register(r"examfull", views.ExamFullViewSet, basename="full")
router.register(r"datasource", views.DataSourceViewSet)
router.register(r"datafile", views.DataFileViewSet)
router.register(r"subscription", views.SubscriptionViewSet, basename="subscription")

urlpatterns = [
    path("api-auth/", include("rest_framework.urls")),
    path("auth/", decorator_include(never_cache, "rest_auth.urls")),
    path("auth/registration/", include("rest_auth.registration.urls")),
    path("auth/token-refresh/", refresh_jwt_token),
    path("auth/token-verify/", verify_jwt_token),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
]

urlpatterns += router.urls
