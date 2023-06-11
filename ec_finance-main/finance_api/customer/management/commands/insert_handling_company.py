# -*- coding: utf-8 -*-
# from base.models import *
# from products.models import *
import datetime
import json
import time
from datetime import date, datetime
from unicodedata import name
from customer.models import Customer,Address
import pandas as pd
import requests
from dateutil import parser
from django.core.management.base import BaseCommand
from finance_api.util import Util

class Command(BaseCommand):
    help = ""
    def handle(self, *args, **options):
        handling_company = pd.read_csv("D:/TnuTaral/ECdata/Hand.csv")
        handling_company = json.loads(handling_company.to_json(orient='records',date_format = 'iso'))

        address_bulk = []
        countries = Util.get_codes("country")
        ec_root_comp = [x["RootCompanyId"] for x in handling_company]
        root_comp_ids = Customer.objects.filter(ec_customer_id__in=ec_root_comp).values("ec_customer_id","id")
        root_comp_ids = Util.get_dict_from_queryset("ec_customer_id","id",root_comp_ids)
        short_name_ids = Customer.objects.filter(ec_customer_id__in=ec_root_comp).values("ec_customer_id","short_name")
        short_name_ids = Util.get_dict_from_queryset("ec_customer_id","short_name",short_name_ids)
        for company in handling_company :
            root_comp_id = root_comp_ids[company["RootCompanyId"]] if company["RootCompanyId"] in root_comp_ids else None
            short_name = short_name_ids[company["RootCompanyId"]] if company["RootCompanyId"] in short_name_ids else ""
            customer = Customer.objects.create(ec_customer_id=company["CompanyId"],initials=company["Initials"],name=company["Name"],vat_no=company["VATNo"],is_root_id=root_comp_id,short_name=short_name)
            address_bulk.append(Address(
                email = company["Email"],
                phone =company["TelePhone"],
                fax = company["Fax"],
                city = company["City"],
                street_name = company["StreetName"],
                street_no= company["StreetNo"],
                postal_code = company["PostalCode"],
                street_address1 = company["Address1"],
                street_address2 = company["Address2"],
                country = countries[company["CountryCode"]] if company["CountryCode"] in countries else None,
                other_state= company["StateName"],
                customer=customer   
            ))
        Address.objects.bulk_create(address_bulk)
    
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)
