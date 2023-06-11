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
        code_file = pd.read_excel("D:/TnuTaral/ECdata/codes.xlsx")
        code_file = json.loads(code_file.to_json(orient='records',date_format = 'iso'))
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        start = 0
        length = 25
        while True:
            codes = code_file[start:(start + length)]
            if len(codes) == 0:
                    break
            code_data  = []
            for code in codes:
                code_data.append({
                    'code': code['Code'],
                    'name': code['UsageDescription'],
                    'desc': code['ShortDescription'],
                    })

            # #--------------call API ------------------------
            start += length
            time.sleep(1)
            url = 'http://192.168.1.247:8004/dt/customer/code/'
            response = requests.post(url, data=json.dumps(code_data), headers=headers)

