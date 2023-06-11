from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from payment.views import (
    PaymentBrowserUnmatchView,
    PaymentBrowserView,
    PaymentImportView,
    change_match_status,
    close_invoice,
    delete_payment_unmatched,
    update_payment_xml,
    upload_payment_file,
)

router = DefaultRouter()
router.register(r"import_payment", PaymentImportView, basename="import_payment")
import_payment = PaymentImportView.as_view({"get": "list"})
# router.register(r'payment_browser', PaymentBrowserView, basename='payment_browser')
# payment_browser = PaymentBrowserView.as_view({"get":"list"})

urlpatterns = [
    url(r"import_payment/$", import_payment, name="import_payment"),
    # url(r"payment_browser/$", payment_browser, name="payment_browser"),
    url(r"payment_browser_unmatch/$", PaymentBrowserUnmatchView.as_view(), name="payment_browser_unmatch"),
    url(r"payment_browser/$", PaymentBrowserView.as_view(), name="payment_browser"),
    url(r"upload_payment_file/$", upload_payment_file, name="upload_payment_file"),
    url(r"delete_payment_unmatched/$", delete_payment_unmatched, name="delete_payment_unmatched"),
    url(r"close_invoice/$", close_invoice, name="close_invoice"),
    url(r"change_match_status/$", change_match_status, name="change_match_status"),
    url(r"update_payment_xml/$", update_payment_xml, name="update_payment_xml"),
]
urlpatterns += router.urls
