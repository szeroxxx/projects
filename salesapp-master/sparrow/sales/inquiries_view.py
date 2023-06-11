import logging
from base.models import AppResponse
from base.util import Util
from django.http import HttpResponse
from django.shortcuts import render
from exception_log import manager
from sparrow.decorators import check_view_permission

from sales.models import Inquiries
from sales.service import SalesEcPyService


@check_view_permission([{"sales": "sales_inquiries"}])
def inquiries(request):
    return render(request, "sales/inquiries.html")


def inquiries_search(request):
    try:
        ec_py_service = SalesEcPyService()
        request.POST = Util.get_post_data(request)
        post_data = {
            "order_ref": "",
            "customer_name": "",
            "country": "",
            "inquiery_no": "",
            "inq_start_date": "",
            "inq_end_date": "",
            "limit": str(request.POST["length"]),
        }
        search_request = False
        if request.POST.get("inquiry_no") is not None:
            post_data["inquiery_no"] = request.POST["inquiry_no"].strip()
            search_request = True

        if request.POST.get("order_Ref") is not None:
            post_data["order_ref"] = request.POST["order_Ref"].strip()
            search_request = True

        if request.POST.get("customer_name") is not None:
            post_data["customer_name"] = request.POST["customer_name"].strip()
            search_request = True

        if request.POST.get("inquiry_date__date") is not None:
            if "inquiry_date__date_from_date" in request.POST:
                post_data["inq_start_date"] = request.POST["inquiry_date__date_from_date"].strip()
                post_data["inq_end_date"] = request.POST["inquiry_date__date_to_date"].strip()
                search_request = True

        if request.POST.get("country") is not None:
            post_data["country"] = request.POST["country"].strip()
            search_request = True
        ec_py_response = []
        if search_request:
            ec_py_end_point = "/ecpy/sales/get_offers/"
            ec_py_response = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)

        recordsTotal = len(ec_py_response)
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        count = 0
        for resp in ec_py_response:
            count += 1
            response["data"].append(
                {
                    "country": resp["country"],
                    "id": resp["offer_id"],
                    "offer_id": resp["offer_id"],
                    "data__inquiry_no": resp["inquiry_no"],
                    "data__inquiry_date": resp["inquiry_date"],
                    "data__status": resp["status"],
                    "data__pcbqty": resp["pcbqty"],
                    "data__order_Ref": resp["order_Ref"],
                    "data__service": resp["service"],
                    "data__delivery_term": resp["delivery_term"],
                    "data__customer_name": resp["customer_name"],
                    "data__remark": resp["remark"],
                    "customer_id": resp["customer_id"],
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# def inquiries_search(request):
#     try:

#         sales_service = SalesService()
#         sales_service.rebuild_table(Inquiries(), "search-offers")

#         request.POST = Util.get_post_data(request)
#         start = int(request.POST['start'])
#         length = int(request.POST['length'])
#         sort_col = Util.get_sort_column(request.POST)
#         recordsTotal = 0
#         query = OrderService().get_inquiry_list_query_object(request.POST)

#         if sort_col in ["id", "-id"]:
#             sort_col = sort_col.replace("id", "data__offer_id")

#         recordsTotal = Inquiries.objects.filter(query).count()
#         inquiries = Inquiries.objects.filter(query).order_by(sort_col)[start: (start+length)]

#         response = {
#             'draw': request.POST['draw'],
#             'recordsTotal': recordsTotal,
#             'recordsFiltered': recordsTotal,
#             'data': [],
#         }

#         for inquiry in inquiries:

#             response['data'].append({
#                 'id': inquiry.data['offer_id'],
#                 'offer_id': inquiry.data['offer_id'],
#                 'data__inquiry_no': inquiry.data['inquiry_no'],
#                 'data__inquiry_date': Util.get_display_date(inquiry.data['inquiry_date'], True),
#                 'data__status': inquiry.data['status'],
#                 'data__pcbqty': inquiry.data['pcbqty'],
#                 'data__order_Ref': inquiry.data['order_Ref'],
#                 'data__service': inquiry.data['service'],
#                 'data__delivery_term': inquiry.data['delivery_term'],
#                 'data__customer_name': inquiry.data['customer_name'],
#                 'data__remark': inquiry.data['remark'],
#                 'customer_id': inquiry.data['customer_id'],
#             })

#         return HttpResponse(AppResponse.get(response), content_type='json')
#     except Exception as e:
#         manager.create_from_exception(e)
#         logging.exception('Something went wrong.')
#         return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')


def export_inquiries(request):
    query = OrderService().get_inquiry_list_query_object(request.POST)
    inquiries = (
        Inquiries.objects.filter(query)
        .values(
            "data__inquiry_no",
            "data__inquiry_date",
            "data__status",
            "data__pcbqty",
            "data__order_Ref",
            "data__service",
            "data__delivery_term",
            "data__customer_name",
            "data__remark",
        )
        .order_by("-data__offer_id")[0:2000]
    )

    headers = [
        {"title": "Inquiry"},
        {"title": "Inquiry Date", "type": "date"},
        {"title": "Status"},
        {"title": "PCB Qty"},
        {"title": "Order Ref."},
        {"title": "Service"},
        {"title": "Delivery Term"},
        {"title": "Customer"},
        {"title": "Remark"},
    ]
    return Util.export_to_xls(headers, inquiries, "inquiries.xls")
