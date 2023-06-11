from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from base import lookups as lookups_view
from base.export_views import (
    custom_invoice_export,
    customer_invoice_export,
    e_invoice_export,
    payment_browser_export,
    payment_export,
    payment_unmatch_export,
    peppol_invoice_export,
    pkf_booking_generate,
    proforma_invoice_export,
    search_invoice_export,
)

# router = DefaultRouter(trailing_slash=True)

urlpatterns = [
    url(r"^lookups/([^/]+)/$", lookups_view.lookups, name="lookups"),
    url(r"^choice_lookups/([^/]+)/$", lookups_view.choice_lookups, name="choice_lookups"),
    url(r"payment_export/$", payment_export, name="payment_export"),
    url(r"payment_browser_export/$", payment_browser_export, name="payment_browser_export"),
    url(r"payment_unmatch_export/$", payment_unmatch_export, name="payment_unmatch_export"),
    url(r"e_invoice_export/$", e_invoice_export, name="e_invoice_export"),
    url(r"proforma_invoice_export/$", proforma_invoice_export, name="proforma_invoice_export"),
    url(r"customer_invoice_export/$", customer_invoice_export, name="customer_invoice_export"),
    url(r"custom_invoice_export/$", custom_invoice_export, name="custom_invoice_export"),
    url(r"peppol_invoice_export/$", peppol_invoice_export, name="peppol_invoice_export"),
    url(r"search_invoice_export/$", search_invoice_export, name="search_invoice_export"),
    url(r"pkf_booking_generate/$", pkf_booking_generate, name="pkf_booking_generate"),
]
# urlpatterns += router.urls
