from django.conf.urls import url

from exception_log import views

app_name = "exception_log"

urlpatterns = [
    url(r"^dashboard/$", views.dashboard, name="dashboard"),
    url(r"^logs/([^/]+)/$", views.logs, name="logs"),
    url(r"^exception_log_search/$", views.exception_log_search, name="exception_log_search"),
    url(r"^delete_exception_log/$", views.delete_exception_log, name="delete_exception_log"),
    url(r"^exception_log_remove/([^/]+)/$", views.exception_log_remove, name="exception_log_remove"),
]
