
from base.models import CodeTable
from finance_api.rest_config import BulkListSerializer, ModelObjectidField
from rest_framework import serializers

from customer.models import Address, Contact, Country, Customer, User


class CustomerSerializer(serializers.ModelSerializer):
    status_id = ModelObjectidField()
    currency_id = ModelObjectidField()
    customer_type_id = ModelObjectidField(allow_null=True)
    tax_number_type_id = ModelObjectidField()
    invoice_lang_id = ModelObjectidField(allow_null=True,required=False)
    # invoice_delivery_id = ModelObjectidField()
    account_manager_id = ModelObjectidField(allow_null=True,required=False)

    class Meta:
        model = Customer
        fields = "__all__"
        list_serializer_class = BulkListSerializer

    def create(self, validated_data):
        instance = Customer(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"
        list_serializer_class = BulkListSerializer

    def create(self, validated_data):
        instance = Contact(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance

class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeTable
        fields = "__all__"
        list_serializer_class = BulkListSerializer

    def create(self, validated_data):
        instance = CodeTable(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        list_serializer_class = BulkListSerializer

    def create(self, validated_data):
        instance = CodeTable(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance

class ECUserSerializer(serializers.ModelSerializer):
    customer_id = ModelObjectidField()
    contact_id = ModelObjectidField()
    language_id = ModelObjectidField(allow_null=True)
    class Meta:
        model = User
        fields = "__all__"
        list_serializer_class = BulkListSerializer

    def create(self, validated_data):
        instance = User(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"
        list_serializer_class = BulkListSerializer

    def create(self, validated_data):
        instance = CodeTable(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance
