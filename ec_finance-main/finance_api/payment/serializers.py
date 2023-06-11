from dataclasses import field, fields
from payment.models import CodaFile, PaymentBrowserUnmatch, CodaTransaction
from rest_framework import serializers
from finance_api.rest_config import LocalDateTime

class CodaFileSerializer(serializers.ModelSerializer):
    created_on = LocalDateTime()
    full_name = serializers.CharField(read_only=True)
    class Meta:
        model = CodaFile
        fields =[
            "id",
            "created_by", 
            "file_name", 
            "compared_xml_string", 
            "is_deleted", 
            "created_on",
            "xml_string",
            "full_name"
        ]
class PaymentBrowserSerializer(serializers.ModelSerializer):
    invoice_status = serializers.CharField(source="invoice__status__desc")
    payment_date = LocalDateTime(source="invoice__payment_date")
    currency_symbol = serializers.CharField(read_only=False,source="invoice__currency__code")
    country = serializers.CharField(source="invoice__country__name")
    invoice_value = serializers.CharField(source="invoice__invoice_value")
    invoice_id = serializers.IntegerField(source="invoice__id")
    created_on = LocalDateTime()

    class Meta:
        model = CodaTransaction
        fields = [
            "id",
            "invoice_id",
            "ec_customer_id",
            "invoice_no",
            "customer_name",
            "created_on",
            "invoice_status",
            "currency_symbol",
            "country",
            "invoice_value",
            "amount",
            "bank_account_no",
            "bank_name",
            "payment_date",
        ]

class PaymentBrowserUnmatchSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    created_on = LocalDateTime()
    class Meta:
        model = PaymentBrowserUnmatch
        fields =[
            "id",
            "customer_name",
            "bank_account_nr",
            "bank_name",
            "amount",
            "message",
            "invoice_nos",
            "remarks",
            "created_on",
            "full_name",
        ]
     