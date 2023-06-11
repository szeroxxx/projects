from django.conf.urls import url

from . import views

app_name = "auditlog"

urlpatterns = [
    url(r"^logs/([^/]+)/([^/]+)/$", views.logs, name="logs"),
    url(r"^logs_search/([^/]+)/([^/]+)$", views.logs_search, name="logs_search"),
    url(r"^history_unidentified__and_stencil_parts/([^/]+)/([^/]+)$", views.history_unidentified__and_stencil_parts, name="history_unidentified__and_stencil_parts"),
]
