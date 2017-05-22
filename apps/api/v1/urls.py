from rest_framework import routersfrom . import viewsrouter = routers.DefaultRouter()router.register(r'date', views.DateViewSet)router.register(r'level', views.LevelViewSet)router.register(r'organisation', views.OrganisationViewSet)router.register(r'position', views.PositionViewSet)router.register(r'employee', views.EmployeeViewSet, base_name='employee')router.register(r'territory', views.TerritoryViewSet)router.register(r'place', views.PlaceViewSet)router.register(r'exam', views.ExamViewSet)router.register(r'examflat', views.ExamFlatViewSet, base_name='flat')router.register(r'examfull', views.ExamFullViewSet, base_name='full')router.register(r'datasource', views.DataSourceViewSet)urlpatterns = router.urls