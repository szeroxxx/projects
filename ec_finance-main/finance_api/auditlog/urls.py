
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from auditlog.views import AuditLog,InvoiceHistoryView,paymentHistoryView


router = DefaultRouter(trailing_slash=True)
router.register(r'invoice_history', InvoiceHistoryView, basename='invoice_history')

urlpatterns = [
    url(r"^logs/", AuditLog.as_view(), name="logs"),
    url(r"^payment_history/", paymentHistoryView.as_view(), name="payment_history"),
]
urlpatterns +=router.urls
