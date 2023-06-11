
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from filebrowser.sites import site

# from sparrow import decorators

handler400 = "base.error_views.bad_request"
handler403 = "base.error_views.permission_denied"
handler404 = "base.error_views.page_not_found"
handler500 = "base.error_views.server_error"

urlpatterns = [
    url(r"^", include("base.urls", namespace="^")),
    url(r"^b/", include("base.urls", namespace="b")),
    url(r"^base/", include("base.urls", namespace="base")),
    url(r"^admin/", admin.site.urls),
    url(r"^admin/filebrowser/", site.urls),
    url(r"^accounts/", include("accounts.urls")),
    url(r"^attachment/", include("attachment.urls")),
    url(r"^auditlog/", include("auditlog.urls")),
    url(r"^mails/", include("mails.urls")),
    url(r"^messaging/", include("messaging.urls")),
    url(r"^task/", include("task.urls")),
    url(r"^collection/", include("collection.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.RESOURCES_URL, document_root=settings.RESOURCES_ROOT)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.RESOURCES_URL, document_root=settings.RESOURCES_ROOT)
