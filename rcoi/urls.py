from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ExamTableView.as_view(), name='index'),
    url(r'^employee/$', views.EmployeeTableView.as_view(), name='employee'),
    url(r'^place/$', views.PlaceTableView.as_view(), name='place'),
    url(r'^list/$', views.ListView.as_view(), name='list'),
    # url(r'^update$', views.IndexView.as_view(), name='index'),
]
