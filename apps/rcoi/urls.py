from django.conf.urls import url
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='rcoi:exam')),
    url(r'^update$', views.UpdateView.as_view(), name='update'),
    # urls for Date
    url(r'^date/$', views.DateListView.as_view(), name='date_list'),
    url(r'^date/detail/(?P<pk>\S+)/$', views.DateDetailView.as_view(), name='date_detail'),
    # urls for Level
    url(r'^level/$', views.LevelListView.as_view(), name='level_list'),
    url(r'^level/detail/(?P<pk>\S+)/$', views.LevelDetailView.as_view(), name='level_detail'),
    # urls for Organisation
    url(r'^organisation/$', views.OrganisationListView.as_view(), name='organisation_list'),
    url(r'^organisation/detail/(?P<pk>\S+)/$', views.OrganisationDetailView.as_view(), name='organisation_detail'),
    # urls for Position
    url(r'^position/$', views.PositionListView.as_view(), name='position_list'),
    url(r'^position/detail/(?P<pk>\S+)/$', views.PositionDetailView.as_view(), name='position_detail'),
    # urls for Employee
    url(r'^employee/$', views.EmployeeTableView.as_view(), name='employee'),
    url(r'^employee/detail/(?P<pk>\S+)/$', views.EmployeeDetailView.as_view(), name='employee_detail'),
    # urls for Territory
    url(r'^territory/$', views.TerritoryListView.as_view(), name='territory_list'),
    url(r'^territory/detail/(?P<pk>\S+)/$', views.TerritoryDetailView.as_view(), name='territory_detail'),
    # urls for Place
    url(r'^place/$', views.PlaceTableView.as_view(), name='place'),
    url(r'^place/detail/(?P<pk>\S+)/$', views.PlaceDetailView.as_view(), name='place_detail'),
    # urls for Exam
    url(r'^exam/$', views.ExamTableView.as_view(), name='exam'),
    url(r'^exam/detail/(?P<pk>\S+)/$', views.ExamDetailView.as_view(), name='exam_detail'),
]
