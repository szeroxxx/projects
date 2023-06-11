from django.conf.urls import url

from . import notification_view, views

app_name = "messaging"
urlpatterns = [
    url(r"^messages", views.get_messages, name="messages"),
    url(r"^message", views.create_message, name="message"),
    url(r"^sendmessage", views.sendmessage, name="message"),
    url(r"^notifications/$", views.notifications, name="notifications"),
    url(r"^mark_as_read/$", views.mark_as_read, name="mark_as_read"),
    url(r"^mark_as_all_read/$", views.mark_as_all_read, name="mark_as_all_read"),
    url(r"^get_unread_count/$", notification_view.get_unread_count, name="get_unread_count"),
    url(r"^update_push_notify/$", notification_view.update_push_notify, name="update_push_notify"),
]
