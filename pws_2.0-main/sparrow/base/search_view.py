import logging
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from exception_log import manager
from pws.models import Order
from base.models import AppResponse
from base.util import Util


def search(request):
    try:

        if request.method == "GET":
            return render(request, "base/app_search.html", {})
        request.POST = Util.get_post_data(request)

        result = []

        if request.POST.get("order_number") is not None:
            result = search_order(request)

        response = {
            "draw": request.POST["draw"],
            "recordsTotal": 0,
            "recordsFiltered": 0,
            "data": result,
        }

        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_object(id, line1_info1, line1_info2, line1_info3, line2_info1, line3_info1, app_name, model_name, object_id, transfer_order_type):
    return {
        "id": id,
        "line1_info1": line1_info1,
        "line1_info2": line1_info2,
        "line1_info3": line1_info3,
        "line2_info1": line2_info1,
        "line3_info1": line3_info1,
        "object_id": object_id,
        "app_name": app_name,
        "model_name": model_name,
        "type": transfer_order_type,
    }


def search_order(request):
    query = Q()
    if request.POST.get("order_number"):
        query.add(Q(order_number__icontains=request.POST["order_number"]), query.connector)
    orders = (
        Order.objects.filter(query)
        .order_by("-id")
        .values(
            "id",
            "order_number",
        )
    )
    res = []
    for order in orders:
        line1_info1 = order["order_number"] + ","
        line1_info2 = ""
        line1_info3 = "<span class='s-l1'>Created on:</span>"
        line2_info1 = "Order number: " + order["order_number"] + ",<span class='s-l2'> " "</span>"
        line3_info1 = ""

        app_name = "pws"
        model_name = "order"
        object_id = str(order["id"])
        transfer_order_type = ""
        res.append(search_object(order["id"], line1_info1, line1_info2, line1_info3, line2_info1, line3_info1, app_name, model_name, object_id, transfer_order_type))

    return res
