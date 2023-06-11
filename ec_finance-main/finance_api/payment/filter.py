import django_filters
from django_filters.filters import OrderingFilter

from payment.models import CodaFile, CodaTransaction, PaymentBrowserUnmatch


class PaymentImportViewFilter(django_filters.FilterSet):
    created_on = django_filters.DateTimeFilter(field_name="created_on")
    file_name = django_filters.CharFilter(lookup_expr="icontains")
    full_name = django_filters.CharFilter(lookup_expr="icontains")

    ordering = OrderingFilter(
        fields=(
            ("created_on", "created_on"),
            ("id", "id"),
            ("file_name", "file_name"),
            ("full_name", "full_name"),
        ),
    )

    class Meta:
        model = CodaFile
        fields = ["id", "created_on", "file_name", "full_name"]


class PaymentBrowserFilter(django_filters.FilterSet):
    invoice_value = django_filters.CharFilter(field_name="invoice__invoice_value", lookup_expr="icontains")
    country = django_filters.CharFilter(field_name="invoice__country__name", lookup_expr="icontains")
    payment_date = django_filters.DateTimeFilter(field_name="invoice__payment_date", lookup_expr="icontains")
    invoice_status = django_filters.CharFilter(field_name="invoice__status__desc", lookup_expr="icontains")
    currency_symbol = django_filters.CharFilter(field_name="invoice__currency__code", lookup_expr="icontains")
    created_on = django_filters.DateTimeFilter(field_name="created_on")
    invoice_no = django_filters.CharFilter(lookup_expr="icontains")
    customer_name = django_filters.CharFilter(lookup_expr="icontains")
    bank_name = django_filters.CharFilter(lookup_expr="icontains")
    bank_account_no = django_filters.CharFilter(lookup_expr="icontains")
    amount = django_filters.CharFilter(lookup_expr="icontains")

    ordering = OrderingFilter(
        fields=(
            ("id", "id"),
            ("invoice_no", "invoice_no"),
            ("customer_name", "customer_name"),
            ("created_on", "created_on"),
            ("bank_name", "bank_name"),
            ("invoice__invoice_value", "invoice_value"),
            ("invoice__country__name", "country"),
            ("invoice__payment_date", "payment_date"),
            ("invoice__status__desc", "invoice_status"),
            ("amount", "amount"),
            ("invoice__currency__code", "currency_symbol"),
            ("bank_account_no", "bank_account_no"),
        ),
    )

    class Meta:
        model = CodaTransaction
        fields = [
            "id",
            "invoice_no",
            "customer_name",
            "created_on",
            "bank_name",
            "invoice_value",
            "country",
            "payment_date",
            "invoice_status",
            "amount",
            "currency_symbol",
            "bank_account_no",
        ]


class PaymentBrowserUnmatchFilter(django_filters.FilterSet):
    bank_name = django_filters.CharFilter(lookup_expr="icontains")
    customer_name = django_filters.CharFilter(lookup_expr="icontains")
    bank_account_nr = django_filters.CharFilter(lookup_expr="icontains")
    amount = django_filters.CharFilter(lookup_expr="icontains")
    message = django_filters.CharFilter(lookup_expr="icontains")
    invoice_nos = django_filters.CharFilter(lookup_expr="icontains")
    remarks = django_filters.CharFilter(lookup_expr="icontains")
    created_on = django_filters.CharFilter(lookup_expr="icontains")
    full_name = django_filters.CharFilter(lookup_expr="icontains")

    ordering = OrderingFilter(
        fields=(
            ("id", "id"),
            ("customer_name", "customer_name"),
            ("bank_account_nr", "bank_account_nr"),
            ("amount", "amount"),
            ("message", "message"),
            ("created_on", "created_on"),
            ("bank_name", "bank_name"),
            ("invoice_nos", "invoice_nos"),
            ("remarks", "remarks"),
            ("created_on", "created_on"),
            ("full_name", "full_name"),
        ),
    )

    class Meta:
        model = PaymentBrowserUnmatch
        fields = ["id", "customer_name", "bank_account_nr", "amount", "message", "created_on", "bank_name", "invoice_nos", "remarks", "full_name"]
