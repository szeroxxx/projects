# -*- coding: utf-8 -*-
# from base.models import *
# from products.models import *
import datetime
import json
import time
from datetime import date, datetime

import pandas as pd
import requests
from django.core.management.base import BaseCommand


# from base.util import Util
class Command(BaseCommand):
    help = ""
    def handle(self, *args, **options):
        address_file = pd.read_excel("D:/TnuTaral/ECdata/address.xlsx")
        address_file = json.loads(address_file.to_json(orient='records', date_format = 'iso'))
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        start = 0
        length = 25
        while True:
            addresses_data = address_file[start:(start + length)]
            if len(addresses_data) == 0:
                    break
            start += length
            time.sleep(1)
            url = 'http://192.168.1.247:8004/dt/customer/address/'
            response = requests.post(url, data=json.dumps(addresses_data), headers=headers)

