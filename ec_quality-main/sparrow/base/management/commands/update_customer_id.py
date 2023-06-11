# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch, helpers
from django.conf import settings
from eurocircuits.models import OrderAttributes
from production.models import Mfg_order
import time
from datetime import timedelta
from tenant_schemas.utils import schema_context
from messytables import XLSTableSet
from xlrd import open_workbook
import json
import glob


class Command(BaseCommand):
    help = ''
    def handle(self, *args, **options):
        with schema_context("ec"):
            wb = open_workbook('assembly_orders.xls')
            sheet = wb.sheets()[0]
            
            number_of_rows = sheet.nrows
            number_of_columns = sheet.ncols
            part_header = []
            order_info = []

            for row in range(0, number_of_rows):
                values = {}
                for column in range(0,number_of_columns):
                    if row == 0:
                        part_header.append(sheet.cell(row, column).value)
                    else:   
                        if not column:
                            values['source'] = sheet.cell(row, column).value
                        else:
                            values['customer_id'] = sheet.cell(row, column).value
                if row:
                    order_info.append(values)

            for order in order_info:
                if OrderAttributes.objects.filter(mfg_order__source_doc = order['source']).first():
                    OrderAttributes.objects.filter(mfg_order__source_doc = order['source']).update(customer_id = order['customer_id'])
                    print('update', order)