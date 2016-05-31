from django.conf.urls import url, include
from rest_framework import routers
from . import api
from . import views

router = routers.DefaultRouter()
router.register(r'date', api.ExamDateViewSet)
router.register(r'level', api.ExamLevelViewSet)
router.register(r'organisation', api.OrganisationViewSet)
router.register(r'position', api.PositionViewSet)
router.register(r'employee', api.EmployeeViewSet)
router.register(r'territory', api.TerritoryViewSet)
router.register(r'place', api.PlaceViewSet)
router.register(r'exam', api.ExamViewSet)

urlpatterns = [
    url(r'^api/v1/', include(router.urls)),
    # url(r'^$', views.ExamTableView.as_view(), name='index'),
    url(r'^update$', views.IndexView.as_view(), name='index'),
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
