from dataclasses import fields
import django
import django_filters
from django_filters.filters import OrderingFilter
from sales.models import CollectionAction, Invoice, Scheduler, PeppolInvoice, HutaxInvoice
from django_filters.widgets import RangeWidget


class SchedulerFilter(django_filters.FilterSet):
    scheduler_name = django_filters.CharFilter(field_name="scheduler__name", lookup_expr="icontains")
    created_on = django_filters.DateFilter(field_name="scheduler__created_on")
    customer_name = django_filters.CharFilter(field_name="customer__name", lookup_expr="icontains")
    ordering = OrderingFilter(
        fields=(
            ("created_on", "created_on"),
            ("id", "id"),
            ("name", "scheduler_name"),
            ("customer__name", "customer_name"),
            ("total_invoice", "total_invoice"),
        ),
    )

    class Meta:
        model = Scheduler
        fields = ["id", "scheduler_name", "created_on", "customer_name"]


class SearchInvoiceFilter(django_filters.FilterSet):
    invoice_number = django_filters.CharFilter(lookup_expr="icontains")
    invoice_value = django_filters.CharFilter(lookup_expr="icontains")
    address_line_1 = django_filters.CharFilter(lookup_expr="icontains", field_name="street_address1")
    address_line_2 = django_filters.CharFilter(lookup_expr="icontains", field_name="street_address2")
    secondry_status = django_filters.CharFilter(lookup_expr="icontains", field_name="secondry_status__desc")
    last_reminder_date = django_filters.DateTimeFilter(field_name="last_rem_date")
    last_reminder_date_gte = django_filters.DateTimeFilter(field_name="last_rem_date")
    last_reminder_date_lte = django_filters.DateTimeFilter(field_name="last_rem_date")
    customer_name = django_filters.CharFilter(field_name="customer__name", lookup_expr="icontains")
    country = django_filters.CharFilter(lookup_expr="icontains", field_name="country__name")
    contact = django_filters.CharFilter(lookup_expr="icontains")
    city = django_filters.CharFilter(lookup_expr="icontains", field_name="invoice_city")
    phone = django_filters.CharFilter(lookup_expr="icontains", field_name="invoice_phone")
    fax = django_filters.CharFilter(lookup_expr="icontains", field_name="invoice_fax")
    vat_no = django_filters.CharFilter(lookup_expr="icontains", field_name="customer__vat_no")
    account_number = django_filters.CharFilter(lookup_expr="icontains", field_name="customer__account_number")
    postal_code = django_filters.CharFilter(lookup_expr="icontains")
    order_nrs = django_filters.CharFilter(lookup_expr="icontains")
    email = django_filters.CharFilter(lookup_expr="icontains")
    invoice_created_on_gte = django_filters.DateTimeFilter(field_name="invoice_created_on", lookup_expr="gte")
    invoice_created_on_lte = django_filters.DateTimeFilter(field_name="invoice_created_on", lookup_expr="lte")
    invoice_due_date_gte = django_filters.DateTimeFilter(field_name="invoice_due_date", lookup_expr="gte")
    invoice_due_date_lte = django_filters.DateTimeFilter(field_name="invoice_due_date", lookup_expr="lte")
    invoice_created_on = django_filters.DateTimeFromToRangeFilter()
    invoice_due_date = django_filters.DateTimeFilter(lookup_expr="icontains")
    hand_company = django_filters.CharFilter(lookup_expr="icontains", field_name="hand_company__name")
    root_company = django_filters.CharFilter(lookup_expr="icontains", field_name="customer__is_root__name")

    action_date = django_filters.DateTimeFromToRangeFilter(
        lookup_expr=("icontains"),
    )
    delivery_no = django_filters.CharFilter(lookup_expr="icontains")
    packing = django_filters.CharFilter(lookup_expr="icontains")
    invo_delivery = django_filters.CharFilter(lookup_expr="icontains", field_name="customer__invo_delivery")
    ordering = OrderingFilter(
        fields=(
            ("id", "id"),
            ("invoice_due_date", "invoice_due_date"),
            ("status__name", "status"),
            ("customer__name", "customer_name"),
            ("hand_company__name", "handling_company"),
            ("contact", "contact"),
            ("email", "email"),
            ("invoice_city", "city"),
            ("street_address1", "address_line_1"),
            ("street_address2", "address_line_2"),
            ("invoice_fax", "fax"),
            ("invoice_email", "email"),
            ("invoice_phone", "phone"),
            ("invoice_number", "invoice_number"),
            ("country__name", "country"),
            ("invoice_created_on", "invoice_created_on"),
            ("action_status", "action_status"),
            ("action_date", "action_date"),
            ("last_rem_date", "last_reminder_date"),
            ("curr_rate", "curr_rate"),
            ("currency__code", "currency_symbol"),
            ("invoice_amount", "invoice_amount"),
            ("amount_paid", "amount_paid"),
            ("invoice_value", "invoice_value"),
            ("total_reminder", "total_reminder"),
            ("outstanding_amount", "outstanding"),
            ("currency_outstanding_amount", "customer_outstanding"),
            ("payment_date", "payment_date"),
            ("total_reminder", "total_reminder"),
            ("is_deliver_invoice_by_post", "is_deliver_invoice_by_post"),
            ("is_invoice_deliver", "is_invoice_deliver"),
            ("secondry_status__name", "secondry_status"),
            ("customer__credit_limit", "credit_limit"),
            ("customer__customer_credit_limit", "customer_credit_limit"),
            ("customer__customer_type__name", "customer_type"),
            ("cust_amount_paid", "cust_amount_paid"),
            ("delivery_no", "delivery_no"),
            ("customer__is_root__name", "is_root"),
            ("financial_block", "financial_block"),
            ("secondry_status__desc", "secondry_status__desc"),
            ("customer__vat_no", "vat_no"),
            ("postal_code", "postal_code"),
            ("customer__invo_delivery", "invo_delivery"),
            ("customer__account_number", "account_number"),
            ("packing", "packing"),
            ("is_finished", "is_finished"),
        ),
    )

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "country",
            "contact",
            "email",
            "invoice_created_on",
            "is_legal",
            "last_reminder_date",
            "amount_paid",
            "customer_id",
            "customer_name",
            "hand_company",
            "city",
            "invoice_due_date",
            "invoice_value",
            "street_address1",
            "street_address2",
            "address_line_1",
            "address_line_2",
            "postal_code",
            "phone",
            "fax",
            "vat_no",
            "account_number",
            "order_nrs",
            "secondry_status",
            "root_company",
            "delivery_no",
            "packing",
            "invoice_created_on_gte",
            "invoice_created_on_lte",
            "curr_rate",
            "invo_delivery",
            "is_finished",
        ]


class InvoiceFilter(django_filters.FilterSet):
    invoice_number = django_filters.CharFilter(lookup_expr="icontains")
    last_reminder_date = django_filters.DateTimeFilter(field_name="last_rem_date")
    customer_name = django_filters.CharFilter(field_name="customer__name", lookup_expr="icontains")
    currency_symbol = django_filters.CharFilter(field_name="currency__code", lookup_expr="icontains")
    financial_block = django_filters.CharFilter(field_name="financial_block", lookup_expr="icontains")
    country = django_filters.CharFilter(lookup_expr="icontains")
    contact = django_filters.CharFilter(lookup_expr="icontains")
    email = django_filters.CharFilter(lookup_expr="icontains")
    invoice_created_on = django_filters.DateTimeFilter()
    company_name = django_filters.CharFilter(lookup_expr="icontains", field_name="hand_company__name")
    action_status = django_filters.CharFilter(lookup_expr="exact")
    action_date = django_filters.DateTimeFromToRangeFilter()
    invoice_created_on_gte = django_filters.DateTimeFilter(field_name="invoice_created_on", lookup_expr="gte")
    invoice_created_on_lte = django_filters.DateTimeFilter(field_name="invoice_created_on", lookup_expr="lte")
    action_date_gte = django_filters.DateTimeFilter(field_name="action_date", lookup_expr="gte")
    action_date_lte = django_filters.DateTimeFilter(field_name="action_date", lookup_expr="lte")
    ordering = OrderingFilter(
        fields=(
            ("id", "id"),
            ("invoice_due_date", "invoice_due_date"),
            ("status__name", "status"),
            ("customer__name", "customer_name"),
            ("hand_company__name", "company_name"),
            ("outstanding", "outstanding"),
            ("customer_outstanding", "customer_outstanding"),
            ("outstanding_days", "outstanding_days"),
            ("invoice_due_date", "invoice_due_date"),
            ("invoice_value", "invoice_value"),
            ("currency_invoice_value", "currency_invoice_value"),
            ("amount_paid", "amount_paid"),
            ("cust_amount_paid", "cust_amount_paid"),
            ("reminder_status", "reminder_status"),
            ("currency__code", "currency_symbol"),
            ("created_on", "created_on"),
            ("contact", "contact"),
            ("email", "email"),
            ("invoice_number", "invoice_number"),
            ("country", "country"),
            ("invoice_created_on", "invoice_created_on"),
            ("action_status", "action_status"),
            ("action_date", "action_date"),
            ("last_rem_date", "last_reminder_date"),
            ("invoice_amount", "invoice_amount"),
            ("amount_paid", "amount_paid"),
            ("total_reminder", "total_reminder"),
            ("secondry_status__desc", "secondary_status"),
            ("currency_symbol", "currency_symbol"),
        ),
    )

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "country",
            "contact",
            "email",
            "invoice_created_on",
            "is_legal",
            "last_rem_date",
            "amount_paid",
            "customer_id",
            "customer_name",
            "company_name",
            "currency_symbol",
            "invoice_created_on_gte",
            "invoice_created_on_lte",
            "action_date_gte",
            "action_date_lte",
            "financial_block",
        ]


class ActionFilter(django_filters.FilterSet):
    customer_name = django_filters.CharFilter(field_name="customer__name", lookup_expr="icontains")
    ordering = OrderingFilter(
        fields=(
            ("action_date", "action_date"),
            ("customer__name", "customer_name"),
            ("action_status", "action_status"),
            ("action_type", "action_type"),
            ("id", "id"),
            ("summary", "summary"),
            ("action_by", "action_by"),
        ),
    )

    class Meta:
        model = CollectionAction
        fields = ["id", "action_date", "customer_name"]


class PeppolInvocieFilter(django_filters.FilterSet):
    invoice_number = django_filters.CharFilter(field_name="invoice__invoice_number", lookup_expr="icontains")
    created_on = django_filters.CharFilter(field_name="invoice__invoice_created_on", lookup_expr="icontains")
    customer = django_filters.CharFilter(field_name="invoice__customer__name", lookup_expr="icontains")
    status = django_filters.CharFilter(field_name="invoice__status__desc", lookup_expr="icontains")
    hand_comp = django_filters.CharFilter(field_name="invoice__hand_company__name", lookup_expr="icontains")
    vat_no = django_filters.CharFilter(field_name="invoice__customer__vat_no", lookup_expr="icontains")
    peppol_id_verified = django_filters.CharFilter(field_name="invoice__is_peppol_verified", lookup_expr="icontains")

    ordering = OrderingFilter(
        fields=(
            ("id", "id"),
            ("invoice__invoice_number", "invoice_number"),
            ("invoice__invoice_created_on", "created_on"),
            ("invoice__customer__name", "customer"),
            ("invoice__status__desc", "status"),
            ("invoice__hand_company__name", "hand_comp"),
            ("invoice__customer__vat_no", "vat_no"),
            ("invoice__is_peppol_verified", "peppol_id_verified"),
            ("result", "result"),
            ("error", "error"),
            ("pe_status", "pe_status"),
        )
    )

    class Meta:
        model = PeppolInvoice
        fields = [
            "id",
            "invoice_number",
            "created_on",
            "customer",
            "status",
            "hand_comp",
            "vat_no",
            "result",
            "error",
            "pe_status",
            "peppol_id_verified",
        ]


class HuTaxInvoiceFilter(django_filters.FilterSet):
    customer = django_filters.CharFilter(field_name="invoice__customer__name", lookup_expr="icontains")
    invoice_date = django_filters.DateTimeFilter(field_name="invoice__invoice_created_on")
    ordering = OrderingFilter(
        fields=(("id", "id"), ("invoice__customer__name", "customer"), ("invoice__invoice_created_on", "invoice_date"), ("result", "result")),
    )

    class Meta:
        model = HutaxInvoice
        fields = ["id", "customer", "hu_status", "result", "invoice_date"]
