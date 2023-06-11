from django.conf.urls import url

from . import views

app_name = "pws_portal"

urlpatterns = [
    url(r"^place_order/$", views.place_order, name="place_order"),
    url(r"^order_tracking/([^/]+)/$", views.order_tracking, name="order_tracking"),
    url(r"^exception_tracking/$", views.exception_tracking, name="exception_tracking"),
    url(r"^exports_exception_tracking/$", views.exports_exception_tracking, name="exports_exception_tracking"),
    url(r"^reply_exception_save/$", views.reply_exception_save, name="reply_exception_save"),
    url(r"^dashboard/$", views.dashboard, name="dashboard"),
    url(r"^search_order_tracking/([^/]+)/$", views.search_order_tracking, name="search_order_tracking"),
    url(r"^exports_order_tracking/$", views.exports_order_tracking, name="exports_order_tracking"),
    url(r"^modify_order/([^/]+)/([^/]+)/$", views.modify_order, name="modify_order"),
    url(r"^exception_tracking_order_cancel/$", views.exception_tracking_order_cancel, name="exception_tracking_order_cancel"),
    url(r"^set_order_priority/$", views.set_order_priority, name="set_order_priority"),
    url(r"^accept_preparation/(\d+)/$", views.accept_preparation, name="accept_prep"),
    url(r"^modify_and_place_order/(\d+)/$", views.modify_and_place_order, name="modify_and_place_order"),
    url(r"^exception_tracking_search/$", views.exception_tracking_search, name="exception_tracking_search"),
]
