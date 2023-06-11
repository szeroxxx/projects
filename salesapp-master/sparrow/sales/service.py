import json
import logging

import requests
from base.util import Util
from django.conf import settings
from exception_log import manager


class CustomerService(object):
    def __init__(self, **kwargs):
        self.invalidate_custdetail_cache = False
        if "invalidate_customer_cache" in kwargs:
            self.invalidate_custdetail_cache = kwargs["invalidate_customer_cache"]

    def get_customer(self, customer_id, request):

        customer = Util.get_cache("public", "cust_" + customer_id)
        if self.invalidate_custdetail_cache:
            customer = None

        if customer is None:
            ec_py_service = SalesEcPyService()
            fltr_data = {"customerid": customer_id}
            ec_py_end_point = "/ecpy/sales/get_customer_profile/"
            response = ec_py_service.search_ec_data(fltr_data, ec_py_end_point, request)
            # headers = {"content-type": "application/json", "token":settings.EC_SALES_TOKEN}
            # response = requests.post(url, data=json.dumps(fltr_data), headers=headers).json()
            customer = response
            # if customer["code"] == "0":
            #     raise ValueError("API integration failed")

            Util.set_cache("public", "cust_" + customer_id, customer, 3600)
        return customer

    def get_customer_detail(self, customer_id, request):
        customer = self.get_customer(customer_id, request)
        return customer["Customer"]

    def get_customer_addresses(self, customer_id, request):
        customer = self.get_customer(customer_id, request)
        return customer["Addresses"]

    def get_customer_users(self, customer_id, request):
        customer = self.get_customer(customer_id, request)
        return customer["Users"]

    def get_customer_activities(self, customer_id, request):
        customer = self.get_customer(customer_id, request)
        return customer["UserActivities"]

    def get_customer_master_data(self, customer_id, request):
        customer = self.get_customer(customer_id, request)
        return customer["MasterData"]


class SalesService(object):
    def request_ec_data(self, post_data, end_point_func):
        url = settings.EC_API_ROOT_URL + "/" + end_point_func
        headers = {"content-type": "application/json", "token": settings.EC_SALES_TOKEN}
        data = requests.post(url, data=json.dumps(post_data), headers=headers, timeout=5).json()
        data = json.loads(data)
        if data["code"] == "0":
            # raise ValueError("Failed to fetch records")
            raise ValueError("API integration failed")
        if data["code"] == "2":  # ec team will make this change tomorrow morning.
            raise ValueError("No records found for the search criteria!")

        return data["data"]

    def rebuild_table(self, cls, end_point_func):
        try:
            cache_key = type(cls).__name__
            url = settings.EC_API_ROOT_URL + "/" + end_point_func
            fltr_data = {}
            headers = {"content-type": "application/json", "token": settings.EC_SALES_TOKEN}

            if Util.get_cache("public", cache_key) is not None:
                return

            data = requests.post(url, data=json.dumps(fltr_data), headers=headers, timeout=5).json()
            data = json.loads(data)
            if data["code"] == "0":
                raise ValueError("Failed to fetch latest records")

            cls.rebuild_data(data["data"])

            Util.set_cache("public", cache_key, "exists", 3600)
        except Exception as e:
            manager.create_from_exception(e)
            logging.exception("Something went wrong in rebuild table.")

    def process_ec_data(self, post_data, end_point_func):
        url = settings.EC_ROOT_URL + "/shop/salesappapi/salesapp/" + end_point_func
        headers = {"content-type": "application/json", "token": settings.EC_SALES_TOKEN}
        data = requests.post(url, data=json.dumps(post_data), headers=headers).json()
        data = json.loads(data)
        if data["code"] == "0":
            raise ValueError("API integration failed")
        return data


class SalesEcPyService(object):
    def search_ec_data(self, post_data, ec_py_end_point, request):
        ec_user_id = request.session["ec_user_id"] if "ec_user_id" in request.session else 0
        ec_username = request.session["username"] if "username" in request.session else "SalesApp@demo.com"
        post_data["log_data"] = {"ec_user_id": ec_user_id, "ec_username": ec_username}
        response = Util.get_ec_py_token(token=None)
        headers = {"accept": "application/json", "Authorization": "Bearer " + response["access_token"]}
        url = str(settings.EC_PY_URL) + ec_py_end_point
        response = requests.post(url, data=json.dumps(post_data), headers=headers, timeout=5).json()
        if "data" in response and len(response["data"]) > 0 and isinstance(response["data"], list):
            return response["data"]
        elif "data" in response and isinstance(response["data"], dict):
            return response["data"]
        elif "surveylist" in response:
            return response["data"]
        else:
            raise ValueError("No records found for the search criteria!")

    def process_ec_data(self, post_data, ec_py_end_point, request):
        ec_user_id = request.session["ec_user_id"]
        ec_username = request.session["username"]
        post_data["log_data"] = {"ec_user_id": ec_user_id, "ec_username": ec_username}
        response = Util.get_ec_py_token(token=None)
        headers = {"accept": "application/json", "Authorization": "Bearer " + response["access_token"]}
        url = str(settings.EC_PY_URL) + ec_py_end_point
        response = requests.post(url, data=json.dumps(post_data), headers=headers).json()
        return response
