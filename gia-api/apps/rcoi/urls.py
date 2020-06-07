from django.conf.urls import url
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from . import views
from .sitemap import index, sitemap, sitemaps_context

urlpatterns = [
    url(r"^$", views.HomeView.as_view(), name="home"),
    url(
        r"^robots\.txt$",
        cache_page(86400)(
            TemplateView.as_view(template_name="robots.txt", content_type="text/plain")
        ),
    ),
    url(
        r"^sitemap\.xml$",
        cache_page(86400)(index),
        {"sitemaps": sitemaps_context, "sitemap_url_name": "rcoi:sitemap_section"},
    ),
    url(
        r"^sitemap-(?P<section>.+)\.xml$",
        cache_page(86400)(sitemap),
        {"sitemaps": sitemaps_context},
        name="sitemap_section",
    ),
    url(r"^admin/update_db/$", views.update_db_view, name="update_db"),
    url(r"^admin/clear_caches/$", views.clear_caches_view, name="clear_caches"),
    # urls for Date
    url(r"^date/$", views.DateListView.as_view(), name="date_list"),
    url(
        r"^date/detail/(?P<pk>\S+)/$",
        views.DateDetailView.as_view(),
        name="date_detail",
    ),
    # urls for Level
    url(r"^level/$", views.LevelListView.as_view(), name="level_list"),
    url(
        r"^level/detail/(?P<pk>\S+)/$",
        views.LevelDetailView.as_view(),
        name="level_detail",
    ),
    # urls for Organisation
    url(
        r"^organisation/$",
        views.OrganisationListView.as_view(),
        name="organisation_list",
    ),
    url(
        r"^organisation/detail/(?P<pk>\S+)/$",
        views.OrganisationDetailView.as_view(),
        name="organisation_detail",
    ),
    # urls for Position
    url(r"^position/$", views.PositionListView.as_view(), name="position_list"),
    url(
        r"^position/detail/(?P<pk>\S+)/$",
        views.PositionDetailView.as_view(),
        name="position_detail",
    ),
    # urls for Employee
    url(r"^employee/$", views.EmployeeTableView.as_view(), name="employee"),
    url(
        r"^employee/detail/(?P<pk>\S+)/$",
        views.EmployeeDetailView.as_view(),
        name="employee_detail",
    ),
    # urls for Place
    url(r"^place/$", views.PlaceTableView.as_view(), name="place"),
    url(
        r"^place/detail/(?P<pk>\S+)/$",
        views.PlaceDetailView.as_view(),
        name="place_detail",
    ),
    # urls for Exam
    url(r"^exam/$", views.ExamTableView.as_view(), name="exam"),
    url(
        r"^exam/detail/(?P<pk>\S+)/$",
        views.ExamDetailView.as_view(),
        name="exam_detail",
    ),
]
