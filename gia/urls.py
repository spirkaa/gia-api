from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^', include('rcoi.urls', namespace="rcoi")),
    url(r'^api/v1/', include('api.v1.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
