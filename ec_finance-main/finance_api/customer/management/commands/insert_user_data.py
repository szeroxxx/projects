# -*- coding: utf-8 -*-
# from base.models import *
# from products.models import *
import json
import time

import pandas as pd
import requests
from django.core.management.base import BaseCommand


# from base.util import Util
class Command(BaseCommand):
    help = ""
    def handle(self, *args, **options):
        user_file = pd.read_excel("D:/TnuTaral/ECdata/users.xlsx")
        user_file = json.loads(user_file.to_json(orient='records'))
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        start = 0
        length = 25
        while True:
            users_data = user_file[start:(start + length)]
            if len(users_data) == 0:
                    break
            start += length
            time.sleep(1)
            url = 'http://192.168.1.247:8004/dt/customer/user/'
            response = requests.post(url, data=json.dumps(users_data), headers=headers)

