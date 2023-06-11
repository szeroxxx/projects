"""finance_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^dt/accounts/", include('accounts.urls')),
    url(r"^dt/customer/", include('customer.urls')),
    url(r"^dt/sales/", include('sales.urls')),
    url(r"^dt/base/", include('base.urls')),
    url(r"^dt/attachment/", include('attachment.urls')),
    url(r"^dt/auditlog/", include("auditlog.urls")),
    url(r"^dt/payment/", include("payment.urls")),
    



]
urlpatterns += static(settings.RESOURCES_URL, document_root=settings.RESOURCES_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
