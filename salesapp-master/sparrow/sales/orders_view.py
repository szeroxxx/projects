import json
import logging
from datetime import datetime, time

import requests
from auditlog.models import AuditAction, Auditlog
from base.models import AppResponse
from base.util import Util
from django.conf import settings
from django.db.models import CharField, Q
from django.http import HttpResponse, response
from django.shortcuts import redirect, render
from exception_log import manager
from sparrow.decorators import check_view_permission

from sales.models import Orders
from sales.service import SalesEcPyService, SalesService


@check_view_permission([{"sales": "sales_order"}])
def orders(request):
    perms = ["view", "can_customer_login_orders"]
    permissions = Util.get_permission_role(request.user, perms)
    return render(request, "sales/orders.html", {"permissions": json.dumps(permissions)})


def orders_search(request):
    try:
        ec_py_service = SalesEcPyService()
        request.POST = Util.get_post_data(request)
        post_data = {
            "RowLimit": str(request.POST["length"]),
        }

        search_request = False
        if request.POST.get("order_number") != None:
            post_data["OrderNumber"] = request.POST["order_number"].strip()
            search_request = True

        if request.POST.get("pcb_name") != None:
            post_data["PCBName"] = request.POST["pcb_name"].strip()
            search_request = True

        if request.POST.get("customer_name") != None:
            post_data["so.CustomerName"] = request.POST["customer_name"].strip()
            search_request = True

        if request.POST.get("delivery_date__date") != None:
            if "delivery_date__date_from_date" in request.POST:
                post_data["FromDeliveryDate"] = request.POST["delivery_date__date_from_date"].strip()
                post_data["TillDeliveryDate"] = request.POST["delivery_date__date_to_date"].strip()
                search_request = True

        if request.POST.get("order_date__date") != None:
            if "order_date__date_from_date" in request.POST:
                post_data["OrderStartDate"] = request.POST["order_date__date_from_date"].strip()
                post_data["OrderEndDate"] = request.POST["order_date__date_to_date"].strip()
                search_request = True

        if request.POST.get("country") is not None:
            post_data["sc.VisitCountry"] = request.POST["country"].strip()
            search_request = True
        ec_py_response = []
        if search_request:
            ec_py_end_point = "/ecpy/sales/search_orderv2"
            ec_py_response = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)

        recordsTotal = len(ec_py_response)
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        count = 0
        for order in ec_py_response:
            count += 1
            response["data"].append(
                {
                    "id": count,
                    "data__order_number": order["order_number"],
                    "data__order_status": order["order_status"],
                    "data__order_date": order["order_date"],
                    "data__order_value": order["order_value"],
                    "data__delivery_term": order["delivery_term"],
                    "data__pcb_qty": order["pcb_qty"],
                    "data__panel_qty": order["panel_qty"],
                    "data__service": order["service"],
                    "data__pcb_name": order["pcb_name"],
                    "data__layers": order["layers"],
                    "data__first_orderdate": order["first_orderdate"],
                    "data__customer_id": order["customerid"],
                    "data__customer_name": order["customer_name"],
                    "data__contact_firstname": order["contact_firstname"],
                    "data__contact_lastname": order["contact_lastname"],
                    "data__contact_email": order["contact_email"],
                    "data__contact_phone": order["contact_phone"],
                    "data__company_phone": order["company_phone"],
                    "data__company_city": order["company_city"],
                    "data__company_country": order["company_country"],
                    "delivery_date": order["DeliveryDate"],
                }
            )

        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# def orders_search(request):
#     try:
#         sales_service = SalesService()
#         sales_service.rebuild_table(Orders(), "search-orders")

#         request.POST = Util.get_post_data(request)
#         start = int(request.POST['start'])
#         length = int(request.POST['length'])
#         sort_col = Util.get_sort_column(request.POST)
#         recordsTotal = 0
#         query = OrderService().get_orders_list_query_object(request.POST)

#         if sort_col in ["id", "-id"]:
#             sort_col = sort_col.replace("id", "data__orderid")

#         recordsTotal = Orders.objects.filter(query).count()
#         orders = Orders.objects.filter(query).order_by(sort_col)[start: (start+length)]

#         response = {
#             'draw': request.POST['draw'],
#             'recordsTotal': recordsTotal,
#             'recordsFiltered': recordsTotal,
#             'data': [],
#         }

#         for order in orders:
#             response['data'].append({
#                 'id': order.data['orderid'],
#                 'data__order_number': order.data['order_number'],
#                 'data__order_status': order.data['order_status'],
#                 'data__order_date': Util.get_display_date(order.data['order_date']),
#                 'data__order_value': order.data['order_value'],
#                 'data__delivery_term': order.data['delivery_term'],
#                 'data__pcb_qty': order.data['pcb_qty'],
#                 'data__panel_qty': order.data['panel_qty'],
#                 'data__service': order.data['service'],
#                 'data__pcb_name': order.data['pcb_name'],
#                 'data__layers': order.data['layers'],
#                 'data__first_orderdate': Util.get_display_date(order.data['first_orderdate']),
#                 'data__customer_id': order.data['customerid'],
#                 'data__customer_name': order.data['customer_name'],
#                 'data__contact_firstname': order.data['contact_firstname'],
#                 'data__contact_lastname': order.data['contact_lastname'],
#                 'data__contact_email': order.data['contact_email'],
#                 'data__contact_phone': order.data['contact_phone'],
#                 'data__company_phone': order.data['company_phone'],
#                 'data__company_city': order.data['company_city'],
#                 'data__company_country': order.data['company_country'],
#             })

#         return HttpResponse(AppResponse.get(response), content_type='json')
#     except Exception as e:
#         manager.create_from_exception(e)
#         logging.exception('Something went wrong.')
#         return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')


def export_orders(request):
    query = OrderService().get_orders_list_query_object(request.POST)

    orders = (
        Orders.objects.filter(query)
        .values(
            "data__order_number",
            "data__order_status",
            "data__order_date",
            "data__order_value",
            "data__delivery_term",
            "data__pcb_qty",
            "data__panel_qty",
            "data__service",
            "data__pcb_name",
            "data__layers",
            "data__first_orderdate",
            "data__customer_name",
            "data__contact_firstname",
            "data__contact_email",
            "data__contact_phone",
            "data__company_phone",
            "data__company_city",
            "data__company_country",
        )
        .order_by("-data__orderid")[0:2000]
    )

    headers = [
        {"title": "Order"},
        {"title": "Status"},
        {"title": "Order Date", "type": "date"},
        {"title": "Order Value"},
        {"title": "Delivery Term"},
        {"title": "PCB Qty"},
        {"title": "Panel Qty"},
        {"title": "Service"},
        {"title": "PCB Name"},
        {"title": "Layers"},
        {"title": "First Order Date", "type": "date"},
        {"title": "Customer Name"},
        {"title": "Contact First Name"},
        {"title": "Contact Email"},
        {"title": "Contact Phone"},
        {"title": "Company Phone"},
        {"title": "Company City"},
        {"title": "Company Country"},
    ]
    return Util.export_to_xls(headers, orders, "orders.xls")
