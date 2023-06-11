# -*- coding: utf-8 -*-
# from base.models import *
# from products.models import *
import datetime
import json
import time
from datetime import date, datetime

import pandas as pd
import requests
from dateutil import parser
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ""
    def handle(self, *args, **options):
        customer_file = pd.read_excel("D:/TnuTaral/ECdata/Customers2.xlsx")
        customer_file = json.loads(customer_file.to_json(orient='records',date_format = 'iso'))
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        start = 0
        length = 25
        while True:
            customer_data = customer_file[start:(start + length)]
            if len(customer_data) == 0:
                break
            start += length
            time.sleep(1)
            url = 'http://192.168.1.247:8004/dt/customer/customer/'
            response = requests.post(url, data=json.dumps(customer_data,cls=DateEncoder), headers=headers)


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)
