from django.conf.urls import url

from . import views, parts_view

app_name = 'auditlog'
urlpatterns = [
    url(r'^logs/$', views.logs, name='logs'),
]