from pydoc import resolve
from base.models import CodeTable
from base.util import Util
from dateutil import parser
from finance_api.rest_config import APIResponse
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
import requests
import json
from finance_api.settings import EC_API_KEY, EC_API_URL, MEDIA_URL, API_URL, ECC_TOKEN

from customer.models import Address, Contact, Country, Customer, User
from customer.serializers import AddressSerializer, CodeSerializer, ContactSerializer, CountrySerializer, CustomerSerializer, ECUserSerializer

# Create your views here.


class ContactView(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=1, message="data created")


class CodeView(viewsets.ModelViewSet):
    queryset = CodeTable.objects.all()
    serializer_class = CodeSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=1, message="data inserted")


class CountryView(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=1, message="data inserted")


class CustomerView(viewsets.ModelViewSet):
    queryset = Customer.objects.values(
        "id",
        "ec_customer_id",
        "name",
        "account_manager_id",
        "account_number",
        "initials",
        "customer_type_id",
        "tax_number_type_id",
        "vat_no",
        "invoice_prefrence",
        "invoice_postage",
        "is_sales_review",
        "is_vat_verified",
        "sa_company_competence",
        "sa_ec_customer",
        "peppol_address",
        "status_id",
        "last_order_date",
        "is_allow_send_mail",
        "invoice_lang_id",
        "is_deleted",
        "is_duplicate",
        "is_exclude_vat",
        "is_deliver_invoice_by_post",
        "is_student",
        "is_peppol_verfied",
        "is_always_vat",
        "is_teacher",
        "is_student_team",
        "is_call_report_attached",
        "currency_id",
    )
    serializer_class = CustomerSerializer

    def create(self, request):
        code_ids = Util.get_codes("code_table")
        currency_code = Util.get_codes("currency")
        customer_data = []
        ec_contact_ids = [x["account_manager"] for x in request.data]
        contacts = Contact.objects.filter(ec_contact_id__in=ec_contact_ids).values("id", "ec_contact_id")
        contact_ids = Util.get_dict_from_queryset("ec_contact_id", "id", contacts)
        for customer in request.data:
            customer["account_manager_id"] = contact_ids[customer["account_manager"]] if customer["account_manager"] in contact_ids else None
            last_order_date = parser.parse(customer["last_order_date"]) if customer["last_order_date"] else None
            customer["customer_type_id"] = code_ids[customer["customer_type"]] if customer["customer_type"] in code_ids else None
            customer["tax_number_type_id"] = code_ids[customer["tax_number_type"]] if customer["tax_number_type"] in code_ids else None
            customer["status_id"] = code_ids[customer["status"]] if customer["status"] in code_ids else None
            customer["invoice_lang_id"] = code_ids[customer["invoice_lang"]] if customer["invoice_lang"] in code_ids else None
            # customer['invoice_delivery_id'] = code_ids[customer['invoice_delivery']] if customer['invoice_delivery'] in code_ids else None
            customer["currency_id"] = currency_code[customer["currency"]] if customer["currency"] in currency_code else None
            customer.pop("account_manager")
            customer.pop("customer_type")
            customer.pop("tax_number_type")
            customer.pop("status")
            customer.pop("invoice_lang")
            customer.pop("invo_delivery")
            customer.pop("currency")

            if customer["last_order_date"] == "" or customer["last_order_date"] is None:
                customer.pop("last_order_date")

            else:
                customer["last_order_date"] = last_order_date.strftime("%Y-%m-%d %H:%M")
            customer_data.append(customer)
        serializer = self.get_serializer(data=customer_data, many=isinstance(customer_data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=1, message="data inserted")


class AddressView(viewsets.ModelViewSet):
    queryset = Address.objects.values(
        "street_name",
        "ec_address_id",
        "customer",
        "street_no",
        "street_address1",
        "street_address2",
        "postal_code",
        "city",
        "state_id",
        "other_state",
        "address_name",
        "contact_name",
        "country_id",
        "address_type_id",
        "email",
        "phone",
        "fax",
        "box_no",
        "is_primary",
        "is_deleted",
    )
    serializer_class = AddressSerializer

    def create(self, request):
        code_ids = Util.get_codes("code_table")
        country_ids = Util.get_codes("country")
        ec_customer_ids = [x["customer"] for x in request.data]
        customers = Customer.objects.filter(ec_customer_id__in=ec_customer_ids).values("id", "ec_customer_id")
        customer_ids = Util.get_dict_from_queryset("ec_customer_id", "id", customers)
        addresses_data = []
        for address in request.data:
            address["customer_id"] = customer_ids[address["customer"]] if address["customer"] in customer_ids else None
            address["state_id"] = code_ids[address["state"]] if address["state"] in code_ids else None
            address["country_id"] = country_ids[address["country"]] if address["country"] in country_ids else None
            address["address_type_id"] = code_ids[address["address_type"]] if address["address_type"] in code_ids else None
            address.pop("customer")
            address.pop("state")
            address.pop("country")
            address.pop("address_type")
            addresses_data.append(address)
        serializer = self.get_serializer(data=addresses_data, many=isinstance(addresses_data, list))
        serializer.is_valid(raise_exception=True)
        return APIResponse(code=1, message="data inserted")


class ECUserView(viewsets.ModelViewSet):
    queryset = User.objects.values("id", "customer_id", "contact_id", "language_id", "username", "password", "is_power_user", "is_deleted", "is_active", "sa_user_responsibilities")
    serializer_class = ECUserSerializer

    def create(self, request):
        code_ids = Util.get_codes("code_table")
        ec_contact_ids = [x["contact"] for x in request.data]
        contacts = Contact.objects.filter(ec_contact_id__in=ec_contact_ids).values("id", "ec_contact_id")
        contact_ids = Util.get_dict_from_queryset("ec_contact_id", "id", contacts)
        ec_customer_ids = [x["company"] for x in request.data]
        customers = Customer.objects.filter(ec_customer_id__in=ec_customer_ids).values("id", "ec_customer_id")
        customer_ids = Util.get_dict_from_queryset("ec_customer_id", "id", customers)
        users_data = []
        for user in request.data:
            user["customer_id"] = customer_ids[user["company"]] if user["company"] in customer_ids else None
            user["contact_id"] = contact_ids[user["contact"]] if user["contact"] in contact_ids else None
            user["language_id"] = code_ids[user["language"]] if user["language"] in code_ids else None
            user.pop("company")
            user.pop("contact")
            user.pop("language")

            users_data.append(user)
        serializer = self.get_serializer(data=users_data, many=isinstance(users_data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=1, message="data inserted")


@api_view(["POST"])
def edit_profile(request):
    ec_customer_id = request.data.get("ec_customer_id")
    data = {"key": EC_API_KEY, "funname": "GetEDBProfileDetails", "param": {"customer_id": ec_customer_id}}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = requests.request("GET", API_URL + "sparrowapp/api/financeapp", data=json.dumps(data), headers=headers)
    response = json.loads(response.json())
    return APIResponse(response["data"])


@api_view(["POST"])
def customer_login(request):
    ec_customer_id = request.data.get("ec_customer_id")
    data = {"customerid": ec_customer_id, "eccUserId": 0, "from": "Customer", "entityNumber": "", "app": "finapp"}
    headers = {"Content-Type": "application/json", "token": ECC_TOKEN}
    response = requests.request("GET", API_URL + "salesapp/get-customer-login-url", data=json.dumps(data), headers=headers)
    response = json.loads(response.json())
    return APIResponse(response)
