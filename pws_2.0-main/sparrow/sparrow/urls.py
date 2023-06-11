"""sparrow URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
# from base import SubmissionLogFormMixin

# from decorator_include import decorator_include
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
    # url(r"^", include("website.urls")),
    url(r"^mails/", include("mails.urls")),
    # url(r"^filemgmt/", include("filemgmt.urls")),
    url(r"^", include("base.urls")),
    url(r"^b/", include("base.urls")),
    url(r"^base/", include("base.urls")),
    url(r"^accounts/", include("accounts.urls")),
    url(r"^attachment/", include("attachment.urls")),
    # url(r'^admin/filebrowser/', include(site.urls)),
    url(r"^admin/filebrowser/", site.urls),
    url(r"^grappelli/", include("grappelli.urls")),  # grappelli URLS
    url(r"^admin/", admin.site.urls),
    url(r"^comments/", include("django_comments.urls")),
    # url(r"^baseimport/", include("baseimport.urls")),
    # url(r"^hrm/", include("hrm.urls")),
    # url(r"^robots\.txt$", base_views.robots, name="robots"),
    # url(r"^clear_cache/", base_views.clear_cache, name="clear_cache"),
    url(r"^pws/", include("pws.urls")),
    url(r"^auditlog/", include("auditlog.urls")),
    url(r"^pws_portal/", include("pws_portal.urls")),
    url(r"^messaging/", include("messaging.urls")),
    url(r"^task/", include("task.urls")),
]

if settings.DEBUG:  # will be 'True' in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.RESOURCES_URL, document_root=settings.RESOURCES_ROOT)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.RESOURCES_URL, document_root=settings.RESOURCES_ROOT)
