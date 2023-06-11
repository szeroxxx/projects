from typing_extensions import ParamSpecArgs

from sqlalchemy import false
import core
from fastapi import APIRouter, Request

pws = APIRouter()


@pws.post("/order_from_ecc/")
async def order_from_ecc(request: Request):
    try:
        order_nr = await request.json()
        order_nrs = ""
        for order in order_nr:
            order_nrs += str(order["order_nr"])
            order_nrs += ","
        order_nrs = order_nrs[:-1]
        query = f"ExportOrdersToPWS '{order_nrs}'"
        data = core.execute_query(query, "Export order", "0", "PWS User")
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@pws.post("/inquiry_from_ecc/")
def inquiry_from_ecc():
    try:
        query = "ExportInquiryToPWS"
        data = core.execute_query(query, "Export inquiry", "0", "PWS User")
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@pws.post("/import_pending_orders_from_ec/")
async def import_pending_orders_from_ec(request: Request):
    try:
        order_nr = await request.json()
        if len(order_nr) == 0 :
            query = "ECImportPendingINPWS"
        else:
            cust_order_nr = order_nr["customer_order_nr"]
            query = f"[ECImportPendingINPWS] '{cust_order_nr}'"
        data = core.execute_query(query, "Compare orders", "0", "PWS User")
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@pws.post("/remove_pws_queue_data/")
async def remove_pws_queue_data(request: Request):
    try:
        data = await request.json()
        order_id = ""
        for i in data:
            order_id += str(i["order_id"])
            order_id += ","
        order_id = order_id[:-1]
        # its pending to empliment all orders import.
        if order_id!="":
            remove_order = f"exec removeOrderFromPWSQueue'{order_id}'"
            core.execute_nonquery(remove_order, "Compare orders", "0", "PWS User")
            return {"code": 1, "msg": ""}
        return {"code": 0, "msg": ""}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@pws.post("/import_inq_from_ecc/")
async def import_inq_from_ecc(request: Request):
    try:
        order_nr = await request.json()
        if len(order_nr) == 0 :
            query = "ECImportInqPendingINPWS"
        else:
            cust_order_nr = order_nr["customer_order_nr"]
            query = f"ECImportInqPendingINPWS '{cust_order_nr}'"
        
        data = core.execute_query(query, "Compare orders", "0", "PWS User")
        
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@pws.post("/export_inq_from_ecc/")
async def export_inq_from_ecc(request: Request):
    try:
        data = await request.json()
        customer_order_no = []
        for cust_orde_nr in data:
            customer_order_no.append(cust_orde_nr["customer_order_nr"])
        customer_order_no = str(customer_order_no).replace("[", "")
        customer_order_no = str(customer_order_no).replace("]", "")
        customer_order_no = str(customer_order_no).replace("'", "")
        customer_order_no = str(customer_order_no).replace(" ", "")
        query = f"ExportInquiryToPWS '{customer_order_no}'"
        data = core.execute_query(query, "Compare orders", "0", "PWS User")
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@pws.post("/remove_ec_inq_queue_data/")
async def remove_ec_inq_queue_data(request: Request):
    try:
        data = await request.json()
        order_ids = ""
        for order_id in data:
            order_ids += str(order_id["order_id"])
            order_ids += ","
        order_ids = order_ids[:-1]
        remove_inq = f"exec removeOrderFromPWSQueue'{order_ids}'"
        data = core.execute_nonquery(remove_inq, "Compare orders", "0", "PWS User")
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@pws.post("/orders_and_inquiries_export/")
async def order_inq_export_to_pws(request: Request):
    try:
        order_type = await request.json()
        query ="ExportOrderINQToPWS"
        if order_type[0]["order_type"] == "ECORD":
            query ="ExportOrderINQToPWS 'ECORD'"
        if order_type[0]["order_type"] == "ECINQ":
            query ="ExportOrderINQToPWS 'ECINQ'"
        data = core.execute_query(query, "Export orders and Inquiry to PWS", "0", "PWS User")
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}

@pws.post("/get_orders_for_pws_compare/")
def get_orders_for_pws_compare():
    try:
        query = "getOrdersForPWSCompare"
        data = core.execute_query(query, "Get orders for PWS compare", "0", "PWS User")
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}

@pws.post("/get_inq_for_pws_compare/")
def get_inq_for_pws_compare():
    try:
        query = "getinqForPWSCompare"
        data = core.execute_query(query, "Get inq for pws compare", "0", "PWS User")
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}