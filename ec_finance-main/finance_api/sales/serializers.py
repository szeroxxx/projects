from numpy import source
from base.choices import action_status, action_types
from finance_api.rest_config import LocalDateTime
from rest_framework import serializers

from sales.models import CollectionAction, CustomInvoice, HutaxInvoice, Invoice, InvoiceDiscount, InvoiceOrder, PeppolInvoice, Scheduler


class SchedulerSerializer(serializers.ModelSerializer):
    scheduler_name = serializers.CharField(source="name")
    customer_name = serializers.CharField()
    created_on = LocalDateTime()
    total_invoice = serializers.IntegerField(source="total_invoices")
    customer_id = serializers.IntegerField()

    class Meta:
        model = Scheduler
        fields = ["id", "customer_id", "scheduler_name", "customer_name", "total_invoice", "created_on"]


class ActionSerializer(serializers.ModelSerializer):
    attachment = serializers.FileField(required=False)
    action_by_id = serializers.IntegerField(write_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    action_date = LocalDateTime()
    invoice_id = serializers.IntegerField(required=False)
    is_legal = serializers.BooleanField(write_only=True, required=False)
    invoices = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True, required=False)
    invoice_nr = serializers.CharField( read_only=True, required=False)

    class Meta:
        model = CollectionAction
        fields = [
            "id",
            "full_name",
            "invoice_id",
            "invoices",
            "is_legal",
            "action_by_id",
            "customer_id",
            "action_type",
            "action_status",
            "action_date",
            "summary",
            "attachment",
            "invoice_nr",
            "is_cust_base"
        ]

    def create(self, validate_data):
        validate_data.pop("invoice_id")
        if validate_data.get("attachment"):
            validate_data.pop("attachment")
        return super().create(validate_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance:
            representation["action_type"] = dict(action_types)[representation["action_type"]]
            if representation["action_status"] == "due":
                representation["action_status"] = "Pending"
            if representation["action_status"] == "done":
                representation["action_status"] = "Completed"
            return representation


class CustomerDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer__name", read_only=True, required=False)
    total_reminder = serializers.IntegerField(read_only=True, required=False)
    invoice_amount = serializers.DecimalField(max_digits=12, decimal_places=3, source="total_invoice_amount", read_only=True, required=False)
    paid_amount = serializers.DecimalField(max_digits=12, decimal_places=3, source="total_paid_amount", read_only=True, required=False)
    outstanding_amount = serializers.DecimalField(max_digits=12, decimal_places=3, source="total_outstanding_amount", read_only=True, required=False)

    last_reminder = LocalDateTime(read_only=True, source="last_reminder_date")
    email = serializers.CharField(read_only=True, required=False)
    contact = serializers.CharField(read_only=True)
    country = serializers.CharField(read_only=True, required=False, source="country__name")
    total_invoice = serializers.IntegerField(source="total_invoices", required=False)
    fax = serializers.CharField(read_only=True, required=False)
    address = serializers.CharField(read_only=True, required=False)
    hand_com_name = serializers.CharField(read_only=True, required=False)
    scheduler_id = serializers.IntegerField(required=False)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "customer_name",
            "hand_com_name",
            "email",
            "contact",
            "fax",
            "address",
            "outstanding_amount",
            "country",
            "total_invoice",
            "total_reminder",
            "invoice_amount",
            "paid_amount",
            "last_reminder",
            "scheduler_id",
        ]


class UpdateListSerializer(serializers.ListSerializer):
    def update(self, instances, validated_data):
        instance_hash = {index: instance for index, instance in enumerate(instances)}

        result = [self.child.update(instance_hash[index], attrs) for index, attrs in enumerate(validated_data)]
        return result


class InvoiceOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceOrder
        fields = "__all__"

    def create(self, validated_data):
        instance = InvoiceOrder(**validated_data)
        # if isinstance(self._kwargs["data"], dict):
        #     instance.save()
        return instance

    def update(self, instance, validated_data):
        [setattr(instance, k, v) for k, v in validated_data.items()]
        instance.save()
        # if isinstance(self._kwargs["data"], dict):
        #     instance.save()
        return instance


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"


class UpdateInvoiceSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        [setattr(instance, k, v) for k, v in validated_data.items()]
        instance.save()
        if validated_data.get("last_rem_date"):
            instance.last_rem_date = validated_data["last_rem_date"]
        # if isinstance(self._kwargs["data"], dict):
        #     instance.save()
        return instance

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ("id",)
        # list_serializer_class = BulkListSerializer


class InvoiceListSerializer(serializers.ModelSerializer):
    last_reminder_date = LocalDateTime(read_only=True)
    customer_name = serializers.CharField(read_only=True)
    country = serializers.CharField(read_only=True)
    invoice_amount = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=3)
    total_reminder = serializers.IntegerField(read_only=True)
    invoice_created_on = LocalDateTime(read_only=True)
    status = serializers.CharField(read_only=True)
    secondary_status = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    contact = serializers.CharField(read_only=True)
    action_status = serializers.CharField(read_only=True)
    action_date = LocalDateTime(read_only=True)
    is_finished = serializers.BooleanField()
    # is_collection_legal = serializers.BooleanField(source="collectioninvoice_invoice__action__is_legal", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "payment_tracking_number",
            "invoice_created_on",
            "is_legal",
            "status",
            "last_reminder_date",
            "amount_paid",
            "invoice_amount",
            "customer_id",
            "customer_name",
            "total_reminder",
            "is_finished",
            "email",
            "contact",
            "country",
            "action_status",
            "action_date",
            "secondary_status",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance:
            if "action_status" in representation and representation["action_status"]:
                representation["action_status"] = dict(action_status)[representation["action_status"]]
            return representation


class SchedulePaymentReminderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer__name", read_only=True)
    company_name = serializers.CharField(source="hand_company__name", read_only=True)
    currency_symbol = serializers.CharField(source="currency__code", read_only=True)
    created_on = LocalDateTime()
    invoice_due_date = LocalDateTime()
    last_rem_date = LocalDateTime()
    reminder_status = serializers.IntegerField()
    outstanding_days = serializers.IntegerField()
    customer__id = serializers.IntegerField()
    outstanding = serializers.DecimalField(max_digits=11, decimal_places=3, read_only=True)
    customer_outstanding = serializers.DecimalField(max_digits=11, decimal_places=3, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "created_on",
            "company_name",
            "customer_name",
            "customer__id",
            "invoice_due_date",
            "invoice_value",
            "currency_invoice_value",
            "amount_paid",
            "currency_ots_vat_value",
            "currency_symbol",
            "reminder_status",
            "last_rem_date",
            "outstanding_days",
            "cust_amount_paid",
            "outstanding",
            "customer_outstanding",
        ]


class SearchInvoiceSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(source="customer__account_number", read_only=True)
    ec_customer_id = serializers.CharField(source="customer__ec_customer_id", read_only=True)
    currency_symbol = serializers.CharField(source="currency__code", read_only=True)
    # outstanding_amount = serializers.CharField(source="outstanding_amount",read_only=True)
    handling_company = serializers.CharField(source="hand_company__name", read_only=True)
    status = serializers.CharField(source="status__desc", read_only=True)
    secondry_status = serializers.CharField(source="secondry_status__desc", read_only=True)
    customer_name = serializers.CharField(source="customer__name", read_only=True)
    is_deliver_invoice_by_post = serializers.CharField(read_only=True)
    is_invoice_deliver = serializers.CharField(read_only=True)
    invo_delivery = serializers.CharField(source="customer__invo_delivery", read_only=True)
    customer_type = serializers.CharField(source="customer__customer_type__name", read_only=True)
    vat_no = serializers.CharField(source="customer__vat_no", read_only=True)
    account_number = serializers.CharField(source="customer__account_number", read_only=True)
    country = serializers.CharField(source="country__name", read_only=True)
    address_line_1 = serializers.CharField(source="street_address1", read_only=True)
    address_line_2 = serializers.CharField(source="street_address2", read_only=True)
    postal_code = serializers.CharField(read_only=True)
    city = serializers.CharField(source="invoice_city", read_only=True)
    email = serializers.CharField(source="invoice_email", read_only=True)
    phone = serializers.CharField(source="invoice_phone", read_only=True)
    fax = serializers.CharField(source="invoice_fax", read_only=True)
    invoice_created_on = LocalDateTime()
    invoice_due_date = LocalDateTime()
    payment_date = LocalDateTime()
    last_reminder_date = LocalDateTime(source="last_rem_date", required=False)
    delivery_no = serializers.CharField(read_only=True)
    outstanding = serializers.DecimalField(max_digits=11, decimal_places=3, read_only=True)
    customer_outstanding = serializers.DecimalField(max_digits=11, decimal_places=3, read_only=True)
    credit_limit = serializers.DecimalField(max_digits=11, decimal_places=3, read_only=True, source="customer__credit_limit")
    customer_credit_limit = serializers.DecimalField(max_digits=11, decimal_places=3, read_only=True, source="customer__customer_credit_limit")
    customer_id = serializers.IntegerField(source="customer__id", read_only=True)
    is_root = serializers.CharField(source="customer__is_root__name", read_only=True, required=False)
    financial_block = serializers.CharField(read_only=True, required=False)
    is_finished = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "status",
            "invoice_created_on",
            "customer_name",
            "invoice_value",
            "last_reminder_date",
            "curr_rate",
            "currency_symbol",
            "outstanding_amount",
            "currency_outstanding_amount",
            "invoice_due_date",
            "payment_date",
            "is_invoice_deliver",
            "amount_paid",
            "cust_amount_paid",
            "delivery_condition",
            "secondry_status",
            "phone",
            "fax",
            "email",
            "city",
            "address_line_1",
            "address_line_2",
            "postal_code",
            "country",
            "vat_no",
            "handling_company",
            "customer_type",
            "is_deliver_invoice_by_post",
            "account_number",
            "customer_credit_limit",
            "credit_limit",
            "delivery_no",
            "outstanding",
            "customer_outstanding",
            "currency_invoice_value",
            "invo_delivery",
            "payment_date",
            "customer_id",
            "ec_customer_id",
            "financial_block",
            "is_root",
            "packing",
            "is_finished"
        ]


class PaymentReminderSerializer(serializers.ModelSerializer):
    payment_date = LocalDateTime(read_only=True, required=False)
    country_name = serializers.CharField(read_only=True, required=False, source="country__name")
    company_name = serializers.CharField(required=False, source="customer__name")
    email = serializers.CharField(required=False)
    currency_symbol = serializers.CharField(read_only=True, required=False, source="currency__code")
    language_code = serializers.CharField(required=False)
    # type = serializers.CharField(source="customer__customer_type",read_only=True)
    amount_paid = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=3)
    cust_amount_paid = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=3)
    currency_invoice_value = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=3)
    invoice_value = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=3)
    invoice_number = serializers.CharField(read_only=True)
    invoice_created_on = LocalDateTime(required=False)
    invoice_due_date = LocalDateTime(required=False)
    zero_days_amount = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=3)
    zero_days_invoice = serializers.IntegerField(required=False)
    l_ten_days_amount = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=3)
    l_ten_days_invoice = serializers.IntegerField(required=False)
    l_thirty_days_amount = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=3)
    l_thirty_days_invoice = serializers.IntegerField(required=False)
    l_sixty_days_amount = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=3)
    l_sixty_days_invoice = serializers.IntegerField(required=False)
    l_ninety_days_amount = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=3)
    l_ninety_days_invoice = serializers.IntegerField(required=False)
    g_ninety_days_amount = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=3)
    g_ninety_days_invoice = serializers.IntegerField(required=False)
    country_id = serializers.IntegerField(required=False, source="country__id")
    customer_ids = serializers.IntegerField(required=False)
    outstanding_days = serializers.IntegerField(required=False)
    order_nrs = serializers.CharField(required=False, read_only=True)
    last_rem_date = LocalDateTime(required=False)
    status = serializers.CharField(required=False, source="status__code")
    ec_customer_id = serializers.IntegerField(required=False, source="customer__ec_customer_id")
    invoice_id = serializers.IntegerField(required=False, source="id")
    reminder_status = serializers.IntegerField(
        required=False,
    )
    re_created_on = LocalDateTime(required=False, source="scheduler__scheduler__created_on")
    reminder_date = LocalDateTime(required=False, source="scheduleritem_invoice__scheduler__created_on")
    status = serializers.CharField(required=False, read_only=True, source="scheduler__status")
    remarks = serializers.CharField(source="scheduleritem_invoice__remarks", required=False, read_only=True)
    outstanding = serializers.DecimalField(max_digits=11, decimal_places=3, read_only=True)
    customer_outstanding = serializers.DecimalField(max_digits=11, decimal_places=3, read_only=True)
    # full_name = serializers.CharField(source="full_name",required=False,read_only=True)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Invoice
        fields = [
            "payment_date",
            "invoice_id",
            "status",
            "id",
            "country_id",
            "customer_id",
            "ec_customer_id",
            "customer_ids",
            "country_name",
            "company_name",
            "currency_symbol",
            "amount_paid",
            "currency_invoice_value",
            "invoice_value",
            "email",
            "last_rem_date",
            "language_code",
            "order_nrs",
            "invoice_number",
            "invoice_created_on",
            "outstanding_amount",
            "currency_outstanding_amount",
            "invoice_due_date",
            "zero_days_amount",
            "zero_days_invoice",
            "l_ten_days_amount",
            "l_ten_days_invoice",
            "l_thirty_days_amount",
            "l_thirty_days_invoice",
            "l_sixty_days_amount",
            "l_sixty_days_invoice",
            "l_ninety_days_amount",
            "l_ninety_days_invoice",
            "g_ninety_days_amount",
            "g_ninety_days_invoice",
            "outstanding_days",
            "reminder_status",
            "re_created_on",
            "status",
            "remarks",
            "reminder_date",
            "cust_amount_paid",
            "currency_invoice_value",
            "outstanding",
            "customer_outstanding",
        ]


class InvoiceScheduleSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    automatic_invoice = serializers.IntegerField(required=False)
    manual_invoice = serializers.IntegerField(required=False)
    total_invoices = serializers.IntegerField(required=False)
    created_on = LocalDateTime()

    class Meta:
        model = Scheduler
        fields = ["id", "name", "full_name", "created_on", "status", "automatic_invoice", "manual_invoice", "total_invoices"]


class CreditStatusSerializer(serializers.ModelSerializer):
    outstanding = serializers.CharField(required=False)
    customer_outstanding = serializers.CharField(required=False)
    cust_credit_limit = serializers.CharField(required=False, source="customer__customer_credit_limit")
    credit_limit = serializers.CharField(required=False, source="customer__credit_limit")
    invoice_created_on = LocalDateTime()
    invoice_due_date = LocalDateTime()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "invoice_created_on",
            "invoice_due_date",
            "outstanding_amount",
            "currency_invoice_value",
            "invoice_value",
            "amount_paid",
            "cust_amount_paid",
            "customer_outstanding",
            "outstanding",
            "credit_limit",
            "cust_credit_limit",
            "ec_invoice_type_id"
        ]


class CloseInvoiceSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(source="customer__id", read_only=True)
    customer_name = serializers.CharField(source="customer__name", read_only=True)
    currency_name = serializers.CharField(source="currency__name", read_only=True)
    currency_id = serializers.IntegerField(source="currency__id", read_only=True)
    outstanding = serializers.DecimalField(max_digits=11, decimal_places=3, read_only=True)
    new_payment = serializers.DecimalField(max_digits=11, decimal_places=3, read_only=True)
    status = serializers.CharField(source="status__code")
    payment_deference_type = serializers.CharField(required=False)
    difference = serializers.DecimalField(max_digits=11, decimal_places=3, read_only=True)
    ec_customer_id = serializers.IntegerField(source="customer__ec_customer_id", read_only=True)
    invoice_created_on = serializers.DateTimeField(format="%Y-%m-%d")
    invoice_due_date = serializers.DateTimeField(format="%Y-%m-%d")
    # currency_id = serializers.IntegerField(source="currency__id")

    class Meta:
        model = Invoice
        fields = [
            "id",
            "ec_invoice_id",
            "invoice_number",
            "invoice_created_on",
            "invoice_due_date",
            "invoice_value",
            "amount_paid",
            "customer_name",
            "customer_id",
            "currency_name",
            "currency_id",
            "curr_rate",
            "outstanding",
            "status",
            "currency_invoice_value",
            "new_payment",
            "cust_amount_paid",
            "payment_deference_type",
            "difference",
            "ec_customer_id",
        ]


class FinancialReportSerializer(serializers.ModelSerializer):
    secondry_status = serializers.CharField(source="secondry_status__desc")
    status = serializers.CharField(source="status__code")
    number = serializers.CharField(source="invoice_number")

    outstanding = serializers.DecimalField(max_digits=11, decimal_places=3, read_only=True)
    reminder = serializers.IntegerField(
        required=False,
    )
    outstanding_days = serializers.IntegerField(required=False)
    invoice_created_on = LocalDateTime()
    invoice_due_date = LocalDateTime()
    last_rem_date = LocalDateTime()
    payment_date = LocalDateTime()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "number",
            "invoice_due_date",
            "invoice_value",
            "status",
            "outstanding",
            "reminder",
            "invoice_created_on",
            "secondry_status",
            "outstanding_days",
            "last_rem_date",
            "amount_paid",
            "payment_date",
        ]


class CustomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomInvoice
        fields = "__all__"
        extra_kwargs = {"harm_code": {"required": False, "allow_null": True, "allow_blank": True}, "country_of_origin": {"allow_null": True, "allow_blank": True}}

    def update(self, instance, validated_data):
        print(validated_data, "validated_data")
        [setattr(instance, k, v) for k, v in validated_data.items()]
        instance.save()
        # if isinstance(self._kwargs["data"], dict):
        #     instance.save()
        return instance


class PeppolInvoiceSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source="invoice__invoice_number")
    customer = serializers.CharField(source="invoice__customer__name")
    status = serializers.CharField(source="invoice__status__desc")
    hand_comp = serializers.CharField(source="invoice__hand_company__name")
    vat_no = serializers.CharField(source="invoice__customer__vat_no")
    created_on = LocalDateTime(source="invoice__invoice_created_on")
    peppol_id_verified = serializers.CharField(source="invoice__is_peppol_verified", read_only=True)
    customer_id = serializers.CharField(source="invoice__customer__id")
    ec_customer_id = serializers.CharField(source="invoice__customer__ec_customer_id")

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
            "customer_id",
            "ec_customer_id",
        ]


class HuTaxSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source="invoice__invoice_number", required=False, read_only=True)
    customer = serializers.CharField(source="invoice__customer__name", required=False, read_only=True)
    invoice_date = LocalDateTime(source="invoice__invoice_created_on", required=False, read_only=True)
    hu_status = serializers.CharField(read_only=True)
    transaction_id = serializers.CharField(read_only=True)
    status_time = LocalDateTime(read_only=True)
    created_on = LocalDateTime(read_only=True)

    class Meta:
        model = HutaxInvoice
        fields = [
            "id",
            # "invoice",
            "invoice_number",
            "customer",
            "invoice_date",
            "result",
            "status_time",
            "created_on",
            "hu_status",
            "transaction_id",
        ]


class InvoiceDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceDiscount
        fields = "__all__"

    def update(self, instance, validated_data):
        [setattr(instance, k, v) for k, v in validated_data.items()]
        instance.save()
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance


class PKFBookingSerializer(serializers.ModelSerializer):
    street_name = serializers.CharField(source="invoice_address__street_name", required=False, read_only=True)
    street_no = serializers.CharField(source="invoice_address__street_no", required=False, read_only=True)
    hand_company = serializers.CharField(source="hand_company__name", required=False, read_only=True)
    customer = serializers.CharField(source="customer__name", required=False, read_only=True)
    ec_customer_id = serializers.CharField(source="customer__ec_customer_id", read_only=True)
    customer_name = serializers.CharField(source="customer__name", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "ec_invoice_id",
            "customer",
            "invoice_number",
            "hand_company",
            "invoice_created_on",
            "invoice_due_date",
            "postal_code",
            "street_address1",
            "street_address2",
            "vat_percentage",
            "street_name",
            "street_no",
            "ec_customer_id",
            "customer_name",
        ]


class XeroBookingSerilizer(serializers.ModelSerializer):
    handling_company = serializers.CharField(source="hand_company__name")
    vat_no = serializers.CharField(source="customer__vat_no")
    invoice_created_on = LocalDateTime()
    invoice_due_date = LocalDateTime()
    ec_customer_id = serializers.CharField(source="customer__ec_customer_id", read_only=True)
    customer_name = serializers.CharField(source="customer__name", read_only=True)

    class Meta:
        model = Invoice
        fields = ["id", "invoice_number", "handling_company", "invoice_created_on", "invoice_due_date", "vat_no", "vat_percentage", "ec_customer_id", "customer_name"]
