from django.conf.urls import url

from . import views

app_name = "auditlog"
urlpatterns = [
    url(r"^logs/$", views.logs, name="logs"),
]
