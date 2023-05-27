from decorator_include import decorator_include
from django.urls import include, path
from django.views.decorators.cache import never_cache
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework import routers

from . import views

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
    path("auth/", decorator_include(never_cache, "dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="apiv1:schema"),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="apiv1:schema"),
        name="schema-redoc",
    ),
]

urlpatterns += router.urls
