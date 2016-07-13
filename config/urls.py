from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^', include('apps.rcoi.urls', namespace="rcoi")),
    url(r'^api/v1/', include('apps.api.v1.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
