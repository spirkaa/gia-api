from decorator_include import decorator_include
from django.conf.urls import include, url
from django.views.decorators.cache import never_cache
from rest_framework import routers
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token
from rest_framework_swagger.views import get_swagger_view

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
    url(r"^auth/", decorator_include(never_cache, "rest_auth.urls")),
    url(r"^auth/registration/", include("rest_auth.registration.urls")),
    url(r"^auth/token-refresh/$", refresh_jwt_token),
    url(r"^auth/token-verify/$", verify_jwt_token),
    url(r"^docs/$", get_swagger_view(title="API Docs"), name="api_docs"),
    url(r"^api-auth/", include("rest_framework.urls")),
]

urlpatterns += router.urls
