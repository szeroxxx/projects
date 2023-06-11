# -*- coding: utf-8 -*-
import json
import time

import pandas as pd
import requests
from base.models import CodeTable
from django.core.management.base import BaseCommand


# from base.util import Util
class Command(BaseCommand):
    help = ""
    def handle(self, *args, **options):
        countries_file = pd.read_csv("D:/TnuTaral/country.csv")
        countries_file = json.loads(countries_file.to_json(orient='records',date_format = 'iso'))
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        start = 0
        length = 50
        while True:
            countries = countries_file[start:(start + length)]
            if len(countries) == 0:
                    break
            countries_data  = []
            for country in countries:
                countries_data.append({
                    'name': country['Name'] if country['Name'] else "",
                    'code': country['Initial'] if country['Initial'] else "",
                    })

            # #--------------call API ------------------------
            start += length
            time.sleep(1)
            url = 'http://192.168.1.247:8004/dt/customer/country/'
            response = requests.post(url, data=json.dumps(countries_data), headers=headers)
