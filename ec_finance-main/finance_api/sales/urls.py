from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from sales.invoice_views import (
    CreditStatus,
    Customs,
    HuTaxService,
    InvoiceDiscountView,
    InvoiceView,
    OrderLines,
    PeppolInvoiceView,
    PKFBooking,
    XeroBooking,
    after_sales,
    change_credit_limit,
    change_status,
    close_coda_invoices,
    credit_limit,
    discount_lookup,
    ec_close_invoice,
    finance_report,
    get_credit_status,
    grant_days,
    order_intake,
    request_report,
    shipment,
    submit_close_invoice,
    update_sec_status,
    generate_e_invoice,
)
from sales.reminder_view import (
    CountryBreakupView,
    CustomerBreakupView,
    InvoiceBreakupView,
    ReminderPreview,
    SchedulePaymentReminderView,
    ScheduleView,
    customer_reminder_preview,
    schedule,
    schedule_update,
    send_reminder,
)
from sales.views import ActionView, CloseInvoiceView, CollectionInvoiceView, LegalInvoiceView, SchedulerView, credit_invoice, edit_invoice

router = DefaultRouter(trailing_slash=True)

router.register(r"invoice", InvoiceView, basename="invoice")
router.register(r"scheduler", SchedulerView, basename="scheduler")
router.register(r"action", ActionView, basename="actions")
router.register(r"collection", CollectionInvoiceView, basename="collection")
router.register(r"hu_service", HuTaxService, basename="hu_service")
collection_actions = CollectionInvoiceView.as_view({"get": "list"})
actions = ActionView.as_view({"get": "list"})
hu_tax_service = HuTaxService.as_view({"get": "list"})
legal_actions = LegalInvoiceView.as_view({"get": "list"})
customer_invoices = CollectionInvoiceView.as_view({"get": "list"})
legal_customer_invoices = LegalInvoiceView.as_view({"get": "list"})
search_invoice = InvoiceView.as_view({"get": "list"})
router.register(r"schedule_payment_reminder", SchedulePaymentReminderView, basename="schedule_payment_reminder")
schedule_payment_reminder = SchedulePaymentReminderView.as_view({"get": "list"})
router.register(r"reminder", ScheduleView, basename="invoice_schedule")
router.register(r"invoice_schedule", ScheduleView, basename="invoice_schedule")
router.register(r"peppol", PeppolInvoiceView, basename="peppol")
peppol_invoice = PeppolInvoiceView.as_view({"get": "list"})

urlpatterns = [
    url(r"search_invoice/$", search_invoice, name="search_invoice"),
    url(r"^legal_actions/$", legal_actions, name="legal-actions"),
    url(r"^actions/$", actions, name="actions"),
    url(r"^collection_actions/$", collection_actions, name="collection-actions"),
    url(r"^customer_invoices/$", customer_invoices, name="customer_invoices"),
    url(r"^legal_customer_invoices/$", legal_customer_invoices, name="legal_customer_invoices"),
    url(r"schedule_payment_reminder/$", schedule_payment_reminder, name="schedule_payment_reminder"),
    url(r"country_breakup/$", CountryBreakupView.as_view(), name="country_breakup"),
    url(r"close_invoice/$", CloseInvoiceView.as_view(), name="close_invoice"),
    url(r"custom/$", Customs.as_view(), name="custom"),
    url(r"order_lines/$", OrderLines.as_view(), name="order_lines"),
    url(r"customer_breakup/$", CustomerBreakupView.as_view(), name="customer_breakup"),
    url(r"invoice_breakup/$", InvoiceBreakupView.as_view(), name="invoice_breakup"),
    url(r"send_reminder/$", send_reminder, name="send_reminder"),
    url(r"reminder_preview/$", ReminderPreview.as_view(), name="reminder_preview"),
    url(r"customer_reminder_preview/$", customer_reminder_preview, name="customer_reminder_preview"),
    url(r"credit_invoice/$", credit_invoice, name="credit_invoice"),
    url(r"edit_invoice/$", edit_invoice, name="edit_invoice"),
    url(r"schedule/$", schedule, name="schedule"),
    url(r"schedule_update/$", schedule_update, name="schedule_update"),
    url(r"submit_close_invoice/$", submit_close_invoice, name="submit_close_invoice"),
    url(r"change_secondary_status/$", update_sec_status, name="change_secondary_status"),
    url(r"change_invoice_status/$", change_status, name="change_invoice_status"),
    url(r"grant_days/$", grant_days, name="grant_days"),
    url(r"^credit_status/", CreditStatus.as_view(), name="credit_status"),
    url(r"^pkf_booking/", PKFBooking.as_view(), name="pkf_booking"),
    url(r"^hu_tax_service/", hu_tax_service, name="hu_tax_service"),
    url(r"peppol_invoice/$", peppol_invoice, name="peppol_invoice"),
    url(r"close_coda_invoices/$", close_coda_invoices, name="close_coda_invoices"),
    url(r"invoice_discount/$", InvoiceDiscountView.as_view(), name="invoice_discount"),
    url(r"change_credit_limit/$", change_credit_limit, name="change_credit_limit"),
    url(r"ec_close_invoice/$", ec_close_invoice, name="ec_close_invoice"),
    url(r"credit_limit/$", credit_limit, name="credit_limit"),
    url(r"discount_lookup/$", discount_lookup, name="discount_lookup"),
    url(r"order_intake/$", order_intake, name="order_intake"),
    url(r"shipment/$", shipment, name="shipment"),
    url(r"request_report/$", request_report, name="request_report"),
    url(r"after_sales/$", after_sales, name="after_sales"),
    url(r"finance_report/$", finance_report, name="finance_report"),
    url(r"get_credit_status/$", get_credit_status, name="get_credit_status"),
    # url(r"get_company_address/$", get_company_address, name="get_company_address"),
    url(r"^xero_booking/", XeroBooking.as_view(), name="xero_booking"),
    url(r"^generate_e_invoice/", generate_e_invoice, name="generate_e_invoice"),
]
urlpatterns += router.urls
