from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from . import views
from .sitemap import index, sitemap, sitemaps_context

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path(
        "robots.txt",
        cache_page(86400)(
            TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        ),
        name="robotstxt",
    ),
    path(
        "sitemap.xml",
        cache_page(86400)(index),
        {"sitemaps": sitemaps_context, "sitemap_url_name": "rcoi:sitemap_section"},
        name="sitemap",
    ),
    path(
        "sitemap-<section>.xml",
        cache_page(86400)(sitemap),
        {"sitemaps": sitemaps_context},
        name="sitemap_section",
    ),
    path("admin/update_db/", views.update_db_view, name="update_db"),
    path("admin/clear_caches/", views.clear_caches_view, name="clear_caches"),
    # urls for Date
    path("date/", views.DateListView.as_view(), name="date_list"),
    path(
        "date/detail/<int:pk>/",
        views.DateDetailView.as_view(),
        name="date_detail",
    ),
    # urls for Level
    path("level/", views.LevelListView.as_view(), name="level_list"),
    path(
        "level/detail/<int:pk>/",
        views.LevelDetailView.as_view(),
        name="level_detail",
    ),
    # urls for Organisation
    path(
        "organisation/",
        views.OrganisationTableView.as_view(),
        name="organisation",
    ),
    path(
        "organisation/detail/<int:pk>/",
        views.OrganisationDetailView.as_view(),
        name="organisation_detail",
    ),
    # urls for Position
    path("position/", views.PositionListView.as_view(), name="position_list"),
    path(
        "position/detail/<int:pk>/",
        views.PositionDetailView.as_view(),
        name="position_detail",
    ),
    # urls for Employee
    path("employee/", views.EmployeeTableView.as_view(), name="employee"),
    path(
        "employee/detail/<int:pk>/",
        views.EmployeeDetailView.as_view(),
        name="employee_detail",
    ),
    # urls for Place
    path("place/", views.PlaceTableView.as_view(), name="place"),
    path(
        "place/detail/<int:pk>/",
        views.PlaceDetailView.as_view(),
        name="place_detail",
    ),
    # urls for Exam
    path("exam/", views.ExamTableView.as_view(), name="exam"),
    path(
        "exam/detail/<int:pk>/",
        views.ExamDetailView.as_view(),
        name="exam_detail",
    ),
]
