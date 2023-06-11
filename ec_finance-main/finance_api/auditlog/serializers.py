
from asyncore import read
from dataclasses import fields
from payment.models import PaymentRegistration

from finance_api.rest_config import LocalDateTime
from numpy import source
from rest_framework import serializers

from auditlog.models import Auditlog,InvoiceHistory


class AuditLogSerializer(serializers.ModelSerializer):
    action_on = LocalDateTime()
    action_by = serializers.CharField(source="full_name",read_only=True)
    class Meta:
        model = Auditlog
        fields = ["action_by","action_on","descr","ip_addr"]


class InvoiceHistorySerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only=True,source="full_name")
    invoice_number = serializers.CharField(read_only=True)
    customer_name = serializers.CharField(read_only=True)
    currency_name = serializers.CharField(read_only=True)
    status_desc = serializers.CharField(read_only=True)
    invoice_due_date = LocalDateTime(read_only = True)
    base_amount = serializers.IntegerField(required=False,source="invoice_value")
    class Meta:
        model = Auditlog
        fields = [
            "id","object_id", "action_by","action_on","descr","ip_addr","created_by","customer_name","invoice_number","currency_name","base_amount","status_desc","invoice_due_date",
            "document_no"
        ]

class paymentHistorySerializer(serializers.ModelSerializer):
    paid_on = LocalDateTime(source="payment__paid_on")
    invoice_date = LocalDateTime(source="invoice__created_on")
    invoice_due_date = LocalDateTime(source="invoice__invoice_due_date")
    # invoice_date = LocalDateTime(source="invoice__created_on")
    total_amount = serializers.DecimalField(max_digits=11, decimal_places=3,read_only=True,source="payment__total_amount")
    invoice_value = serializers.DecimalField(max_digits=11, decimal_places=3,read_only=True,source="invoice__invoice_value")
    currency_invoice_value = serializers.DecimalField(max_digits=11, decimal_places=3,read_only=True,source="invoice__currency_invoice_value")
    currency_total_amount = serializers.DecimalField(max_digits=11,decimal_places=3,read_only=True,source="payment__currency_total_amount")
    payment_mode = serializers.CharField(required=False,source="payment__payment_mode")
    invoice_number = serializers.CharField(required=False,source="invoice__invoice_number")
    currency = serializers.CharField(required=False,source="invoice__currency__code")
    outstanding = serializers.DecimalField(max_digits=11, decimal_places=3,read_only=True)
    customer_outstanding = serializers.DecimalField(max_digits=11, decimal_places=3,read_only=True)
    class Meta:
        model = PaymentRegistration
        fields = ["id","total_amount","paid_on","currency_rate","currency_total_amount","payment_mode","invoice_number",
        "invoice_date","currency","invoice_due_date","invoice_value","currency_invoice_value",
        "outstanding","customer_outstanding"]