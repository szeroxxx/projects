from django.conf.urls import url

from . import views

app_name = "finance"
urlpatterns = [
    url(r"^invoices/$", views.invoices, name="invoices"),
    url(r"^invoices/([^/]+)/$", views.invoices, name="invoices"),
    url(r"^invoices_search/$", views.invoices_search, name="invoices_search"),
    url(r"^proforma_invoices/$", views.proforma_invoices, name="proforma_invoices"),
    url(r"^proforma_invoices/([^/]+)/$", views.proforma_invoices, name="proforma_invoices"),
    url(r"^proforma_invoices_search/$", views.proforma_invoices_search, name="proforma_invoices_search"),
    url(r"^payment_browser/$", views.payment_browser, name="payment_browser"),
    url(r"^payment_browser_search/$", views.payment_browser_search, name="payment_browser_search"),
    url(r"^payment_browser_unmatched/$", views.payment_browser_unmatched, name="payment_browser_unmatched"),
    url(r"^payment_browser_unmatched_search/$", views.payment_browser_unmatched_search, name="payment_browser_unmatched_search"),
    url(r"^credit_limit/(\d+)/$", views.credit_limit, name="credit_limit"),
    url(r"^save_credit_limit/$", views.save_credit_limit, name="save_credit_limit"),
    url(r"^save_grant_days/$", views.save_grant_days, name="save_grant_days"),
    url(r"^customer_finance_report/$", views.customer_finance_report, name="customer_finance_report"),
    url(r"^get_secondary_status_list/$", views.get_secondary_status_list, name="get_secondary_status_list"),
    url(r"^save_secondary_status/$", views.save_secondary_status, name="save_secondary_status"),
    url(r"^get_credit_status/$", views.get_credit_status, name="get_credit_status"),
    url(r"^invoice_proforma_search/$", views.invoice_proforma_search, name="invoice_proforma_search"),
    url(r"^credit_report/(\d+)/$", views.credit_report, name="credit_report"),
    url(r"^get_invoice_history/(\d+)/$", views.get_invoice_history, name="get_invoice_history"),
]
