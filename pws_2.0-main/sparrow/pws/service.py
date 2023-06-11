import datetime
import decimal
import json
import logging
import requests
from auditlog import views as log_views
from auditlog.models import AuditAction
from base import views as base_views
from base.choice_mapping import (
    bottom_heat_sink_paste, bottom_legend,
    bottom_solder_mask, carbon_contacts,
    delivery_format, delivery_term,
    edge_connector_bevelling,
    inner_layer_copper_foil,
    inner_layer_core_thickness, material_tg,
    outer_layer_copper_foil,
    pcb_separation_method, peelable_mask,
    surface_finish, top_heat_sink_paste,
    top_legend, top_solder_mask,
    via_filling_hole_plugging
    )
from base.models import AppResponse, DocNumber
from base.util import Util
from django.conf import settings
from django.http import HttpResponse
from exception_log import manager
from pws.models import (CompanyParameter, Layer, Order, OrderFlowMapping,
                        OrderProcess, OrderScreenParameter, OrderTechParameter,
                        Service, OrderException, Order_Attachment)

from . import views
from mails.views import send_mail
from datetime import timedelta
from django.db.models import Q

class PWSEcPyService(object):
    def get_ecc(self, post_data, ec_py_end_point):
        response = Util.get_ec_py_token(token=None)
        headers = {"accept": "application/json", "Authorization": "Bearer " + response["access_token"]}
        url = str(settings.EC_PY_URL) + ec_py_end_point
        response = requests.post(url, data=json.dumps(post_data), headers=headers ,timeout=5).json()
        if "data" in response and len(response["data"]) > 0 and isinstance(response["data"], list):
            return response["data"]
        elif len(response["data"]) == 0:
            return response["data"]
        else:
            return ValueError("Error")


    def post_ecc(self, post_data, ec_py_end_point):
        response = Util.get_ec_py_token(token=None)
        headers = {"accept": "application/json", "Authorization": "Bearer " + response["access_token"]}
        url = str(settings.EC_PY_URL) + ec_py_end_point
        response = requests.post(url, data=json.dumps(post_data), headers=headers).json()
        return response


class ImportOrder(object):
    def ppm_order(self):
        pass

    def ecc_order(self, customer_orders, request):
        try:
            is_imported = False
            import_order = []
            for order in customer_orders:
                import_order.append(
                    {
                        "order_nr":order
                    }
                )
            if len(import_order)>0:
                pws_service = PWSEcPyService()
                response = pws_service.get_ecc(import_order, "/ecpy/pws/order_from_ecc")
                services = Service.objects.values("id", "name")
                prepared_order_tech_data = []
                import_orders = []
                board_thickness_name = [str(order["MaterialThickness"]) + " MM" for order in response if str(order["MaterialThickness"])]
                board_thickness = OrderScreenParameter.objects.filter(name__in=board_thickness_name).values("name", "code")
                board_thickness_ = Util.get_dict_from_quryset("name", "code", board_thickness)
                for order in response:
                    try:
                        layer_code = None
                        if order["Layers"] is not None:
                            layer_code = str(order["Layers"]) + " L" if order["Layers"] is not None else None
                            if int(order["Layers"]) > 20:
                                layer_code = str(order["Layers"]) + "L"
                        delivery_date = datetime.datetime.strptime(order["DeliveryDate"], "%d %b %Y") if order["DeliveryDate"] else None
                        order_date = datetime.datetime.strptime(order["OrderDate"], "%d %b %Y %H:%M:%S") if order["OrderDate"] else None
                        preparation_due_date = datetime.datetime.strptime(order["PreDueDate"], "%d %b %Y %H:%M:%S") if order["PreDueDate"] else None
                        board_thick_ = "Thickness_NotSpecified"
                        if board_thickness_ and bool(board_thickness_):
                            board_thick_ = board_thickness_[str(order["MaterialThickness"]) + " MM"] if str(order["MaterialThickness"]) + " MM" in board_thickness_ else None
                        is_exist = Order.objects.values("customer_order_nr", "id")
                        is_exist = [x["customer_order_nr"] for x in is_exist]
                        company_id_ = settings.EC_COMPANY
                        if order["RepeatOrderNo"] != "":
                            company_id_ = settings.EC_COMPANY_REPEAT
                        if order["IsRestartorder"] != False:
                            company_id_ = settings.EC_COMPANY_RESTART
                        if order["Include Assembly"] is True:
                            company_id_ = settings.EC_ASSEMBLY
                        service_id = None
                        next_status = None
                        current_status = None
                        previous_status = None
                        for service in services:
                            if order["Service"] == service["name"]:
                                service_id = service["id"]
                        if order["OrderStatus"] == "Order cancelled.":
                            current_status = "cancel"
                        else:
                            order_flow_mapping = OrderFlowMapping.objects.filter(company_id=company_id_, service_id=service_id).values("id", "process_ids").last()
                            if order_flow_mapping and order_flow_mapping["process_ids"]:
                                if len(order_flow_mapping["process_ids"]) >= 1:
                                    current_status_id = order_flow_mapping["process_ids"].split(",")[0]
                                    current_status_ = OrderProcess.objects.filter(id=current_status_id).values("id", "code", "sequence").order_by("sequence")
                                    current_status = current_status_[0]["code"]
                                if len(order_flow_mapping["process_ids"]) >= 2:
                                    next_status_id = order_flow_mapping["process_ids"].split(",")[1]
                                    next_status = OrderProcess.objects.filter(id=next_status_id).values("id", "code", "sequence").order_by("sequence")
                                    next_status = next_status[0]["code"]
                        if order["CurrentStatus"] == "Panelise":
                            current_status = "panel"
                            order_flow_mapping = OrderFlowMapping.objects.filter(company_id=company_id_, service_id=service_id).values("process_ids").first()
                            ids = order_flow_mapping["process_ids"].split(",") if order_flow_mapping and order_flow_mapping["process_ids"] is not None else []
                            processes = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), id__in=ids).values("code", "sequence", "name").order_by("sequence")
                            all_processes_sequence_list = [x["sequence"] for x in processes]
                            cu_sequence = [process["sequence"] if "panel" == process["code"] else None for process in processes]
                            cu_sequence = [sequence for sequence in cu_sequence if sequence]
                            for process in processes:
                                if cu_sequence and cu_sequence[0] < process["sequence"]:
                                    next_status = process["code"]
                                    break
                            orde_prev_list = []
                            for proecess_sequence in all_processes_sequence_list:
                                orde_prev_list.append(proecess_sequence)
                                if cu_sequence and cu_sequence[0] == proecess_sequence:
                                    break
                            if len(orde_prev_list) != 0:
                                if len(orde_prev_list) == 1:
                                    ord_prev = 0
                                else:
                                    ord_prev = orde_prev_list[-2]
                                if ord_prev != 0 and ord_prev in all_processes_sequence_list:
                                    ord_prev_ = OrderProcess.objects.filter(sequence=ord_prev).values("code").first()
                                    previous_status = ord_prev_["code"]
                        if order["CurrentStatus"] == "In production":
                            current_status = "upload_panel"
                            next_status = None
                            order_flow_mapping = OrderFlowMapping.objects.filter(company_id=company_id_, service_id=service_id).values("process_ids").first()
                            ids = order_flow_mapping["process_ids"].split(",") if order_flow_mapping and order_flow_mapping["process_ids"] is not None else []
                            processes = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), id__in=ids).values("code", "sequence", "name").order_by("sequence")
                            all_processes_sequence_list = [x["sequence"] for x in processes]
                            cu_sequence = [process["sequence"] if "upload_panel" == process["code"] else None for process in processes]
                            cu_sequence = [sequence for sequence in cu_sequence if sequence]
                            orde_prev_list = []
                            for proecess_sequence in all_processes_sequence_list:
                                orde_prev_list.append(proecess_sequence)
                                if cu_sequence and cu_sequence[0] == proecess_sequence:
                                    break
                            if len(orde_prev_list) != 0:
                                if len(orde_prev_list) == 1:
                                    ord_prev = 0
                                else:
                                    ord_prev = orde_prev_list[-2]
                                if ord_prev != 0 and ord_prev in all_processes_sequence_list:
                                    ord_prev_ = OrderProcess.objects.filter(sequence=ord_prev).values("code").first()
                                    previous_status = ord_prev_["code"]
                        if order["CurrentStatus"] == "Split Production":
                            current_status = "finished"
                            next_status = None
                            previous_status = None
                        if order["CurrentStatus"] == "Order closed":
                            current_status = "finished"
                            next_status = None
                            previous_status = None
                        if order["CurrentStatus"] == "Restart Order Finished":
                            current_status = "finished"
                            next_status = None
                            previous_status = None
                        act_delivery_date = None
                        if delivery_date:
                            if layer_code :
                                layer_ = layer_code[0:2]
                                list_layer = [4, 6, 8]
                                if int(layer_) not in list_layer:
                                    act_delivery_date = delivery_date
                                if int(layer_) == 4:
                                    act_delivery_date = delivery_date - timedelta(days=1)
                                if int(layer_) == 6:
                                    act_delivery_date = delivery_date - timedelta(days=2)
                                if int(layer_) >= 8:
                                    act_delivery_date = delivery_date - timedelta(days=3)
                            else:
                                act_delivery_date = delivery_date
                        if order["OrderNumber"] in is_exist:
                            exist_order_id = Order.objects.filter(customer_order_nr=order["OrderNumber"]).values("id").first()
                            order_exception = OrderException.objects.filter(order__id=exist_order_id["id"], order_in_exception=False, exception_status="put_to_customer").values("id").last()
                            if order_exception:
                                Order_Attachment.objects.filter(object_id=exist_order_id["id"], file_type__code="EXCEPTION").update(deleted=True)
                                OrderException.objects.filter(id=order_exception["id"]).update(exception_status="resolve", exp_resolve_date=datetime.datetime.now(), order_in_exception=True)
                            Order.objects.filter(customer_order_nr=order["OrderNumber"]).update(
                                customer_order_nr=order["OrderNumber"],
                                service_id=service_id,
                                company_id=company_id_,
                                layer=layer_code,
                                delivery_term=delivery_term[order["DeliveryTerm"]] if order["DeliveryTerm"] in delivery_term else None,
                                pcb_name=order["Board Name"] if order["Board Name"] else None,
                                order_date=order_date,
                                delivery_date=delivery_date,
                                act_delivery_date=act_delivery_date,
                                preparation_due_date=preparation_due_date,
                                remarks=order["Remarks"] if order["Remarks"] else "",
                                is_modify=order["IsModify"] if order["IsModify"] is True else False,
                                import_order_date=datetime.datetime.now(),
                                delivery_format=delivery_format[order["IsPanel"]] if order["IsPanel"] in delivery_format else None,
                                in_time=datetime.datetime.now(),
                                order_status=current_status,
                                order_next_status=next_status,
                                order_previous_status=previous_status,
                            )
                            OrderTechParameter.objects.filter(order__customer_order_nr=order["OrderNumber"]).update(
                                is_include_assembly=order["Include Assembly"] if order["Include Assembly"] is True else False,
                                is_top_stencil=order["Top Stencil"] if order["Top Stencil"] is True else False,
                                is_bottom_stencil=order["Bottom Stencil"] if order["Bottom Stencil"] is True else False,
                                board_thickness=board_thick_,
                                material_tg=material_tg[order["Material Tg"]] if order["Material Tg"] in material_tg else None,
                                buildup_code=order["Buildup code"] if order["Buildup code"] is not None else None,
                                is_special_buildup=True if order["Special buildup"] == 1 else False,
                                is_defined_impedance=order["Defined impedance"] if order["Defined impedance"] else False,
                                top_solder_mask=top_solder_mask[order["SolderMaskTop"]] if order["SolderMaskTop"] in top_solder_mask else None,
                                bottom_solder_mask=bottom_solder_mask[order["SolderMaskBottom"]] if order["SolderMaskBottom"] in bottom_solder_mask else None,
                                top_legend=top_legend[order["Top Legend"]] if order["Top Legend"] in top_legend else None,
                                bottom_legend=bottom_legend[order["Bottom Legend"]] if order["Bottom Legend"] in bottom_legend else None,
                                is_bare_board_testing=True if order["Bare Board Testing"] == "yes" else False,
                                carbon_contacts=carbon_contacts[order["CarbonContacts"]] if order["CarbonContacts"] in carbon_contacts else None,
                                ul_marking=True if order["IsULSign"] == "1" else False,
                                pth_on_the_board_edge=True if order["PTH on the board edge"] == "1" else False,
                                round_edge_plating=True if order["RoundEdgePlatting"] == "1" else False,
                                copper_upto_board_edge=True if order["Copper up to board edge"] == 1 else False,
                                press_fit_holes=order["Press-fit holes"] if order["Press-fit holes"] is True else False,
                                depth_routing=True if order["Depth routing"] == 1 else False,
                                edge_connector_gold_surface=order["Edge connector gold surface mm2"] if order["Edge connector gold surface mm2"] else None,
                                edge_connector_bevelling=edge_connector_bevelling[order["Edge connector bevelling"]] if order["Edge connector bevelling"] in edge_connector_bevelling else None,
                                top_heat_sink_paste=top_heat_sink_paste[order["Top heatsink paste"]] if order["Top heatsink paste"] in top_heat_sink_paste else None,
                                bottom_heat_sink_paste=bottom_heat_sink_paste[order["Bottom heatsink paste"]] if order["Bottom heatsink paste"] in bottom_heat_sink_paste else None,
                                via_filling_hole_plugging=via_filling_hole_plugging[order["Via filling/Hole plugging"]] if order["Via filling/Hole plugging"] in via_filling_hole_plugging else None,
                                pcb_separation_method=pcb_separation_method[order["BoardSeparationX"]] if order["BoardSeparationX"] in pcb_separation_method else None,
                                outer_layer_copper_foil=outer_layer_copper_foil[order["OutStartCu"]] if order["OutStartCu"] in outer_layer_copper_foil else None,
                                surface_finish=surface_finish[order["Platting"]] if order["Platting"] in surface_finish else None,
                                inner_layer_copper_foil=inner_layer_copper_foil[order["InnStartCu"]] if order["InnStartCu"] in inner_layer_copper_foil else None,
                                inner_layer_core_thickness=inner_layer_core_thickness[order["CORE"]] if order["CORE"] in inner_layer_core_thickness else None,
                                blind_buried_via_runs=order["PTH on the board edge"] if order["PTH on the board edge"] else None,
                                peelable_mask=peelable_mask[order["PeelOff"]] if order["PeelOff"] in peelable_mask else None,
                                specific_marking=order["Specific marking"] if order["Specific marking"] is True else False,
                            )
                            import_orders.append(
                                {
                                    "customer_order_nr": order["OrderNumber"],
                                    "order_id": order["OrderId"],
                                }
                            )
                            user_id = None
                            if request.user.id:
                                user_id = request.user.id
                            else:
                                user_id = settings.ADMIN_USER
                            c_ip = base_views.get_client_ip(request)
                            action = AuditAction.UPDATE
                            exist_order_id = exist_order_id["id"]
                            if order_exception:
                                log_views.insert("pws", "order", [exist_order_id], action, user_id, c_ip, "Exception resolved.")
                            log_views.insert("pws", "order", [exist_order_id], action, user_id, c_ip, "Import order has been updated.")
                            is_imported = True
                        else:
                            docnumber = DocNumber.objects.filter(code="Order_place").first()
                            prepared_order_data = {
                                "order_number": docnumber.nextnum,
                                "customer_order_nr": order["OrderNumber"],
                                "service_id": service_id,
                                "company_id": company_id_,
                                "layer": layer_code,
                                "delivery_term": delivery_term[order["DeliveryTerm"]] if order["DeliveryTerm"] in delivery_term else None,
                                "pcb_name": order["Board Name"] if order["Board Name"] else None,
                                "order_date": order_date,
                                "delivery_date": delivery_date,
                                "act_delivery_date": act_delivery_date,
                                "order_status": current_status,
                                "order_next_status": next_status,
                                "order_previous_status": previous_status,
                                "preparation_due_date": preparation_due_date,
                                "remarks": order["Remarks"] if order["Remarks"] else "",
                                "is_modify": order["IsModify"] if order["IsModify"] is True else False,
                                "finished_on": None,
                                "import_order_date": datetime.datetime.now(),
                                "delivery_format": delivery_format[order["IsPanel"]] if order["IsPanel"] in delivery_format else None,
                                "in_time" : datetime.datetime.now()
                            }
                            prepared_ord = {
                                "is_include_assembly": order["Include Assembly"] if order["Include Assembly"] is True else False,
                                "is_top_stencil": order["Top Stencil"] if order["Top Stencil"] is True else False,
                                "is_bottom_stencil": order["Bottom Stencil"] if order["Bottom Stencil"] is True else False,
                                "board_thickness": board_thick_,
                                "material_tg": material_tg[order["Material Tg"]] if order["Material Tg"] in material_tg else None,
                                "buildup_code": order["Buildup code"] if order["Buildup code"] else None,
                                "is_special_buildup": True if order["Special buildup"] == 1 else False,
                                "is_defined_impedance": order["Defined impedance"] if order["Defined impedance"] is True else False,
                                "top_solder_mask": top_solder_mask[order["SolderMaskTop"]] if order["SolderMaskTop"] in top_solder_mask else None,
                                "bottom_solder_mask": bottom_solder_mask[order["SolderMaskBottom"]] if order["SolderMaskBottom"] in bottom_solder_mask else None,
                                "top_legend": top_legend[order["Top Legend"]] if order["Top Legend"] in top_legend else None,
                                "bottom_legend": bottom_legend[order["Bottom Legend"]] if order["Bottom Legend"] in bottom_legend else None,
                                "is_bare_board_testing": True if order["Bare Board Testing"] == "yes" else False,
                                "carbon_contacts": carbon_contacts[order["CarbonContacts"]] if order["CarbonContacts"] in carbon_contacts else None,
                                "ul_marking": True if order["IsULSign"] == "1" else False,
                                "pth_on_the_board_edge": True if order["PTH on the board edge"] == "1" else False,
                                "round_edge_plating": True if order["RoundEdgePlatting"] == "1" else False,
                                "copper_upto_board_edge": True if order["Copper up to board edge"] == 1 else False,
                                "press_fit_holes": order["Press-fit holes"] if order["Press-fit holes"] is True else False,
                                "depth_routing": True if order["Depth routing"] == 1 else False,
                                "edge_connector_gold_surface": order["Edge connector gold surface mm2"] if order["Edge connector gold surface mm2"] else None,
                                "edge_connector_bevelling": edge_connector_bevelling[order["Edge connector bevelling"]] if order["Edge connector bevelling"] in edge_connector_bevelling else None,
                                "top_heat_sink_paste": top_heat_sink_paste[order["Top heatsink paste"]] if order["Top heatsink paste"] in top_heat_sink_paste else None,
                                "bottom_heat_sink_paste": bottom_heat_sink_paste[order["Bottom heatsink paste"]] if order["Bottom heatsink paste"] in bottom_heat_sink_paste else None,
                                "via_filling_hole_plugging": via_filling_hole_plugging[order["Via filling/Hole plugging"]] if order["Via filling/Hole plugging"] in via_filling_hole_plugging else None,
                                "surface_finish": surface_finish[order["Platting"]] if order["Platting"] in surface_finish else None,
                                "pcb_separation_method": pcb_separation_method[order["BoardSeparationX"]] if order["BoardSeparationX"] in pcb_separation_method else None,
                                "outer_layer_copper_foil": outer_layer_copper_foil[order["OutStartCu"]] if order["OutStartCu"] in outer_layer_copper_foil else None,
                                "inner_layer_copper_foil": inner_layer_copper_foil[order["InnStartCu"]] if order["InnStartCu"] in inner_layer_copper_foil else None,
                                "inner_layer_core_thickness": inner_layer_core_thickness[order["CORE"]] if order["CORE"] in inner_layer_core_thickness else None,
                                "blind_buried_via_runs": order["PTH on the board edge"] if order["PTH on the board edge"] else None,
                                "peelable_mask": peelable_mask[order["PeelOff"]] if order["PeelOff"] in peelable_mask else None,
                                "specific_marking": order["Specific marking"] if order["Specific marking"] is True else False,
                            }
                            odr = Order(**prepared_order_data)
                            odr.save()
                            docnumber.increase()
                            docnumber.save()
                            prepared_ord["order_id"] = odr.id
                            import_orders.append(
                                {
                                    "customer_order_nr": order["OrderNumber"],
                                    "order_id": order["OrderId"],
                                }
                            )
                            prepared_order_tech_data.append(OrderTechParameter(**prepared_ord))
                            c_ip = base_views.get_client_ip(request)
                            action = AuditAction.INSERT
                            user_id = None
                            if request.user.id:
                                user_id = request.user.id
                            else:
                                user_id = settings.ADMIN_USER
                            log_views.insert("pws", "order", [odr.id], action, user_id, c_ip, "Order has been created")
                            views.skill_matrix_order(request, odr.id, current_status, user_id)
                            no_of_jobs = CompanyParameter.objects.filter(company_id=company_id_).values("no_of_jobs").first()
                            total_jobs = ""
                            if no_of_jobs["no_of_jobs"] is None:
                                total_jobs = 1
                            else:
                                total_jobs = no_of_jobs["no_of_jobs"] + 1
                            CompanyParameter.objects.filter(company_id=company_id_).update(no_of_jobs=total_jobs)
                            is_imported = True
                    except Exception as e:
                        is_imported = False
                        faild_order_nr = order["OrderNumber"]
                        send_mail(True, "public",[settings.IMPORT_FAILED_EMAIL], "PWS 2.0 Import order(s)", f"{faild_order_nr}- EC order import failed.", "", "")
                        manager.create_from_exception(e)
                OrderTechParameter.objects.bulk_create(prepared_order_tech_data)
                pws_service.post_ecc(import_orders, "/ecpy/pws/remove_pws_queue_data")
                return is_imported
            else:
                return is_imported
        except Exception as e:
            logging.exception("Something went wrong. " + str(e))
            manager.create_from_exception(e)
            return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")

    def power_order(self, customer_orders, request):
        try:
            is_imported = False
            order_numbers = customer_orders
            customer_order_no = str(order_numbers).replace("[", "").replace("]", "").replace("'", "").replace(" ", "")
            url = settings.PPM_URL + f"/pwsAPI/GetOrders?type=order&OrderNr={customer_order_no}"
            post_data = ""
            headers = {"Key": settings.PPM_KEY}
            ec_res = requests.get(url, data=json.dumps(post_data), headers=headers, timeout=5)
            response = None
            try:
                response = ec_res.json()
            except:
                return is_imported
            if response and len(response)>0:
                services = Service.objects.values("id", "name")
                prepared_order_tech_data = []
                board_thickness_name = [
                    str(decimal.Decimal(order["MaterialThickness"]).quantize(decimal.Decimal("0.00"))) + " MM" for order in response if str(order["MaterialThickness"])
                ]
                board_thickness = OrderScreenParameter.objects.filter(name__in=board_thickness_name).values("name", "code")
                board_thickness_ = Util.get_dict_from_quryset("name", "code", board_thickness)
                post_data_ = {}
                for order in response:
                    try:
                        board_thick_ = "Thickness_NotSpecified"
                        if board_thickness_ and bool(board_thickness_):
                            board_thick_ = (
                                board_thickness_[str(decimal.Decimal(order["MaterialThickness"]).quantize(decimal.Decimal("0.00"))) + " MM"] if str(decimal.Decimal(order["MaterialThickness"]).quantize(decimal.Decimal("0.00"))) + " MM" in board_thickness_ else None
                            )
                        layer_code = None
                        if order["Layers"] is not None:
                            layer_code = str(order["Layers"]) + " L" if order["Layers"] is not None else None
                            if int(order["Layers"]) > 20:
                                layer_code = str(order["Layers"]) + "L"
                        delivery_date = datetime.datetime.strptime(order["DeliveryDate"], "%d %b %Y %H:%M:%S") if order["DeliveryDate"] else None
                        order_date = datetime.datetime.strptime(order["OrderDate"], "%d %b %Y %H:%M:%S") if order["OrderDate"] else None
                        preparation_due_date = datetime.datetime.strptime(order["PreDueDate"], "%d %b %Y %H:%M:%S") if order["PreDueDate"] else None
                        deli_term = order["DeliveryTerm"].replace("D", "d")
                        is_exist = Order.objects.values("customer_order_nr", "id")
                        is_exist = [x["customer_order_nr"] for x in is_exist]
                        company_id_ = settings.POWER_COMPANY
                        if order["RepeatOrderNo"] == "1":
                            company_id_ = settings.POWER_COMPANY_REPEAT
                        if order["Include Assembly"] == "Yes":
                            company_id_ = settings.POWER_ASSEMBLY
                        if order["IsRestartorder"] == "Yes":
                            company_id_ = settings.POWER_COMPANY_RESTART
                        if "-L" in order["OrderNumber"]:
                            company_id_ = settings.POWER_LAYOUT
                        service_id = None
                        next_status = None
                        current_status = None
                        for service in services:
                            if order["Service"] == "ON Demand":
                                order["Service"] = "On demand"
                            if order["Service"] == service["name"]:
                                service_id = service["id"]
                        if order["OrderStatus"] == "Order Cancelled":
                            current_status = "cancel"
                        elif order["OrderStatus"] == "Out of Single Image":
                            current_status = "panel"
                            next_status = "upload_panel"
                        else:
                            order_flow_mapping = OrderFlowMapping.objects.filter(company_id=company_id_, service_id=service_id).values("id", "process_ids").last()
                            if order_flow_mapping and order_flow_mapping["process_ids"]:
                                if len(order_flow_mapping["process_ids"]) >= 1:
                                    current_status_id = order_flow_mapping["process_ids"].split(",")[0]
                                    current_status_ = OrderProcess.objects.filter(id=current_status_id).values("id", "code", "sequence").order_by("sequence")
                                    current_status = current_status_[0]["code"]
                                if len(order_flow_mapping["process_ids"]) >= 2:
                                    next_status_id = order_flow_mapping["process_ids"].split(",")[1]
                                    next_status = OrderProcess.objects.filter(id=next_status_id).values("id", "code", "sequence").order_by("sequence")
                                    next_status = next_status[0]["code"]
                        if delivery_date:
                            if layer_code :
                                layer_ = layer_code[0:2]
                                list_layer = [4, 6, 8]
                                if int(layer_) not in list_layer:
                                    act_delivery_date = delivery_date
                                if int(layer_) == 4:
                                    act_delivery_date = delivery_date - timedelta(days=1)
                                if int(layer_) == 6:
                                    act_delivery_date = delivery_date - timedelta(days=2)
                                if int(layer_) >= 8:
                                    act_delivery_date = delivery_date - timedelta(days=3)
                            else:
                                act_delivery_date = delivery_date
                        if order["OrderNumber"] in is_exist:
                            exist_order_id = Order.objects.filter(customer_order_nr=order["OrderNumber"]).values("id").first()
                            order_exception = OrderException.objects.filter(order__id=exist_order_id["id"], order_in_exception=False, exception_status="put_to_customer").values("id").last()
                            if order_exception:
                                Order_Attachment.objects.filter(object_id=exist_order_id["id"], file_type__code="EXCEPTION").update(deleted=True)
                                OrderException.objects.filter(id=order_exception["id"]).update(exception_status="resolve", exp_resolve_date=datetime.datetime.now(), order_in_exception=True)
                            Order.objects.filter(customer_order_nr=order["OrderNumber"]).update(
                                company_id=company_id_,
                                layer=layer_code,
                                delivery_term=delivery_term[deli_term] if deli_term in delivery_term else None,
                                pcb_name=order["Board Name"] if order["Board Name"] else None,
                                order_date=order_date,
                                delivery_date=delivery_date,
                                act_delivery_date=act_delivery_date,
                                preparation_due_date=preparation_due_date,
                                is_modify=order["IsModify"] if order["IsModify"] is True else False,
                                import_order_date=datetime.datetime.now(),
                                delivery_format="Panel" if order["IsPanel"] is True else "Single PCB",
                                in_time=datetime.datetime.now(),
                                order_status=current_status,
                                order_next_status=next_status,
                            )
                            OrderTechParameter.objects.filter(order__customer_order_nr=order["OrderNumber"]).update(
                                is_include_assembly=True if order["Include Assembly"] == "Yes" else False,
                                board_thickness=board_thick_,
                                material_tg=material_tg[order["Material Tg"]] if order["Material Tg"] in material_tg else None,
                                is_special_buildup=order["Special buildup"] if order["Special buildup"] is True else False,
                                is_defined_impedance=True if order["Defined impedance"] == "1" else False,
                                top_solder_mask=top_solder_mask[order["SolderMaskTop"]] if order["SolderMaskTop"] in top_solder_mask else None,
                                bottom_solder_mask=bottom_solder_mask[order["SolderMaskBottom"]] if order["SolderMaskBottom"] in bottom_solder_mask else None,
                                top_legend=top_legend[order["Top Legend"]] if order["Top Legend"] in top_legend else None,
                                bottom_legend=bottom_legend[order["Bottom Legend"]] if order["Bottom Legend"] in bottom_legend else None,
                                carbon_contacts=carbon_contacts[order["CarbonContacts"]] if order["CarbonContacts"] in carbon_contacts else None,
                                ul_marking=order["IsULSign"] if order["IsULSign"] is True else False,
                                pth_on_the_board_edge=True if order["PTH on the board edge"] == "Yes" else False,
                                round_edge_plating=True if order["RoundEdgePlatting"] == "1" else False,
                                copper_upto_board_edge=True if order["PTH on the board edge"] == "Yes" else False,
                                press_fit_holes=order["IsPlattedHole"] if order["IsPlattedHole"] is True else False,
                                depth_routing=True if order["Depth routing"] == "1" else False,
                                edge_connector_gold_surface=order["EdgeConnector"] if order["EdgeConnector"] else None,
                                edge_connector_bevelling="No" if order["Edge connector bevelling"] is False else "Standard",
                                top_heat_sink_paste=top_heat_sink_paste[order["Top heatsink paste"]] if order["Top heatsink paste"] in top_heat_sink_paste else None,
                                bottom_heat_sink_paste=bottom_heat_sink_paste[order["Bottom heatsink paste"]] if order["Bottom heatsink paste"] in bottom_heat_sink_paste else None,
                                via_filling_hole_plugging=via_filling_hole_plugging[order["Via filling/Hole"]] if order["Via filling/Hole"] in via_filling_hole_plugging else None,
                                pcb_separation_method=pcb_separation_method[order["BoardSeparationX"]] if order["BoardSeparationX"] in pcb_separation_method else None,
                                outer_layer_copper_foil=outer_layer_copper_foil[order["OutStartCu"]] if order["OutStartCu"] in outer_layer_copper_foil else None,
                                inner_layer_copper_foil=inner_layer_copper_foil[order["InnStartCu"]] if order["InnStartCu"] in inner_layer_copper_foil else None,
                                blind_buried_via_runs=order["PTH on the board edge"] if order["PTH on the board edge"] else None,
                                peelable_mask=peelable_mask[order["PeelOff"]] if order["PeelOff"] in peelable_mask else None,
                                specific_marking=True if order["BONDINGPADS\tSpecific marking"] == "1" else False,
                            )
                            user_id = None
                            if request.user.id:
                                user_id = request.user.id
                            else:
                                user_id = settings.ADMIN_USER
                            c_ip = base_views.get_client_ip(request)
                            action = AuditAction.UPDATE
                            exist_order_id = exist_order_id["id"]
                            if order_exception:
                                log_views.insert("pws", "order", [exist_order_id], action, user_id, c_ip, "Exception resolved.")
                            log_views.insert("pws", "order", [exist_order_id], action, user_id, c_ip, "Import order has been updated.")
                            is_imported = True
                        else:
                            docnumber = DocNumber.objects.filter(code="Order_place").first()
                            prepared_order_data = {
                                "order_number": docnumber.nextnum,
                                "customer_order_nr": order["OrderNumber"],
                                "service_id": service_id,
                                "company_id": company_id_,
                                "layer": layer_code,
                                "delivery_term": delivery_term[deli_term] if deli_term in delivery_term else None,
                                "pcb_name": order["Board Name"],
                                "order_date": order_date,
                                "delivery_date": delivery_date,
                                "act_delivery_date": act_delivery_date,
                                "order_status": current_status,
                                "order_next_status": next_status,
                                "preparation_due_date": preparation_due_date,
                                "is_modify": order["IsModify"],
                                "finished_on": None,
                                "import_order_date": datetime.datetime.now(),
                                "delivery_format": "Panel" if order["IsPanel"] is True else "Single PCB",
                                "in_time" : datetime.datetime.now()
                            }
                            prepared_ord = {
                                "is_include_assembly": True if order["Include Assembly"] == "Yes" else False,
                                "board_thickness": board_thick_,
                                "material_tg": material_tg[order["Material Tg"]] if order["Material Tg"] in material_tg else None,
                                "is_special_buildup": order["Special buildup"] if order["Special buildup"] is True else False,
                                "is_defined_impedance": True if order["Defined impedance"] == "1" else False,
                                "top_solder_mask": top_solder_mask[order["SolderMaskTop"]] if order["SolderMaskTop"] in top_solder_mask else None,
                                "bottom_solder_mask": bottom_solder_mask[order["SolderMaskBottom"]] if order["SolderMaskBottom"] in bottom_solder_mask else None,
                                "top_legend": top_legend[order["Top Legend"]] if order["Top Legend"] in top_legend else None,
                                "bottom_legend": bottom_legend[order["Bottom Legend"]] if order["Bottom Legend"] in bottom_legend else None,
                                "carbon_contacts": carbon_contacts[order["CarbonContacts"]] if order["CarbonContacts"] in carbon_contacts else None,
                                "ul_marking": order["IsULSign"] if order["IsULSign"] is True else False,
                                "pth_on_the_board_edge": True if order["PTH on the board edge"] == "Yes" else False,
                                "round_edge_plating": True if order["RoundEdgePlatting"] == "1" else False,
                                "copper_upto_board_edge": True if order["PTH on the board edge"] == "Yes" else False,
                                "press_fit_holes": order["IsPlattedHole"] if order["IsPlattedHole"] is True else False,
                                "depth_routing": True if order["Depth routing"] == "1" else False,
                                "edge_connector_gold_surface": order["EdgeConnector"] if order["EdgeConnector"] else None,
                                "edge_connector_bevelling": "No" if order["Edge connector bevelling"] is False else "Standard",
                                "top_heat_sink_paste": top_heat_sink_paste[order["Top heatsink paste"]] if order["Top heatsink paste"] in top_heat_sink_paste else None,
                                "bottom_heat_sink_paste": bottom_heat_sink_paste[order["Bottom heatsink paste"]] if order["Bottom heatsink paste"] in bottom_heat_sink_paste else None,
                                "via_filling_hole_plugging": via_filling_hole_plugging[order["Via filling/Hole"]] if order["Via filling/Hole"] in via_filling_hole_plugging else None,
                                "pcb_separation_method": pcb_separation_method[order["BoardSeparationX"]] if order["BoardSeparationX"] in pcb_separation_method else None,
                                "outer_layer_copper_foil": outer_layer_copper_foil[order["OutStartCu"]] if order["OutStartCu"] in outer_layer_copper_foil else None,
                                "inner_layer_copper_foil": inner_layer_copper_foil[order["InnStartCu"]] if order["InnStartCu"] in inner_layer_copper_foil else None,
                                "blind_buried_via_runs": order["PTH on the board edge"] if order["PTH on the board edge"] else None,
                                "peelable_mask": peelable_mask[order["PeelOff"]] if order["PeelOff"] in peelable_mask else None,
                                "specific_marking": True if order["BONDINGPADS\tSpecific marking"] == "1" else False,
                            }
                            odr = Order(**prepared_order_data)
                            odr.save()
                            docnumber.increase()
                            docnumber.save()
                            prepared_ord["order_id"] = odr.id
                            prepared_order_tech_data.append(OrderTechParameter(**prepared_ord))
                            c_ip = base_views.get_client_ip(request)
                            action = AuditAction.INSERT
                            user_id = None
                            if request.user.id:
                                user_id = request.user.id
                            else:
                                user_id = settings.ADMIN_USER
                            log_views.insert("pws", "order", [odr.id], action, user_id, c_ip, "Order has been created")
                            views.skill_matrix_order(request, odr.id, current_status, user_id)
                            no_of_jobs = CompanyParameter.objects.filter(company_id=company_id_).values("no_of_jobs").first()
                            total_jobs = ""
                            if no_of_jobs["no_of_jobs"] is None:
                                total_jobs = 1
                            else:
                                total_jobs = no_of_jobs["no_of_jobs"] + 1
                            CompanyParameter.objects.filter(company_id=company_id_).update(no_of_jobs=total_jobs)
                        post_data_["id"] = order["OrderId"]
                        is_imported = True
                    except Exception as e:
                        is_imported = False
                        faild_order_nr = order["OrderNumber"]
                        send_mail(True, "public",[settings.IMPORT_FAILED_EMAIL], "PWS 2.0 Import order(s)", f"{faild_order_nr}- Power order import failed.", "", "")
                        manager.create_from_exception(e)
                    url = settings.PPM_URL + "/pwsAPI/DeleteOrder"
                    PPM_KEY = settings.PPM_KEY
                    headers = {"Key": PPM_KEY, "content-type": "application/json"}
                    ec_res = requests.post(url, data=json.dumps(post_data_), headers=headers)
                OrderTechParameter.objects.bulk_create(prepared_order_tech_data)
                return is_imported
            else:
                return is_imported
        except Exception as e:
            logging.exception("Something went wrong. " + str(e))
            manager.create_from_exception(e)
            return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")

    def power_inquery(self, customer_orders, request):
        try:
            is_imported = False
            inquiry_numbers = customer_orders
            customer_inquiry_no = str(inquiry_numbers).replace("[", "").replace("]", "").replace("'", "").replace(" ", "")
            url = settings.PPM_URL + f"/pwsAPI/GetOrders?type=inq&OrderNr={customer_inquiry_no}"
            post_data = ""
            headers = {"Key": settings.PPM_KEY}
            ec_res = requests.get(url, data=json.dumps(post_data), headers=headers, timeout=5)
            response = None
            try:
                response = ec_res.json()
            except:
                return is_imported
            if response and len(response)>0:
                services = Service.objects.values("id", "name")
                prepared_order_tech_data = []
                board_thickness_name = [
                    str(decimal.Decimal(order["MaterialThickness"]).quantize(decimal.Decimal("0.00"))) + " MM" for order in response if str(order["MaterialThickness"])
                ]
                board_thickness = OrderScreenParameter.objects.filter(name__in=board_thickness_name).values("name", "code")
                board_thickness_ = Util.get_dict_from_quryset("name", "code", board_thickness)
                post_data_ = {}
                for order in response:
                    try:
                        delivery_date = datetime.datetime.strptime(order["DeliveryDate"], "%d %b %Y") if order["DeliveryDate"] else None
                        order_date = datetime.datetime.strptime(order["OrderDate"], "%d %b %Y") if order["OrderDate"] else None
                        preparation_due_date = datetime.datetime.strptime(order["PreDueDate"], "%d %b %Y") if order["PreDueDate"] else None
                        board_thick_ = "Thickness_NotSpecified"
                        if board_thickness_ and bool(board_thickness_):
                            board_thick_ = (
                                board_thickness_[str(decimal.Decimal(order["MaterialThickness"]).quantize(decimal.Decimal("0.00"))) + " MM"] if str(decimal.Decimal(order["MaterialThickness"]).quantize(decimal.Decimal("0.00"))) + " MM" in board_thickness_ else None
                            )
                        layer_code = None
                        if order["Layers"] is not None:
                            layer_code = str(order["Layers"]) + " L" if order["Layers"] is not None else None
                            if int(order["Layers"]) > 20:
                                layer_code = str(order["Layers"]) + "L"
                        deli_term = order["DeliveryTerm"].replace("D", "d")
                        is_exist = Order.objects.values("customer_order_nr", "id")
                        is_exist = [x["customer_order_nr"] for x in is_exist]
                        service_id = None
                        next_status = None
                        current_status = None
                        for service in services:
                            if order["Service"] == "ON Demand":
                                order["Service"] = "On demand"
                            if order["Service"] == service["name"]:
                                service_id = service["id"]
                        company_id_ = settings.POWER_COMPANY_INQ
                        if order["Include Assembly"] == "Yes":
                            company_id_ = settings.POWER_ASSEMBLY_INQ
                        order_flow_mapping = OrderFlowMapping.objects.filter(company_id=company_id_, service_id=service_id).values("id", "process_ids").last()
                        if order_flow_mapping and order_flow_mapping["process_ids"]:
                            if len(order_flow_mapping["process_ids"]) >= 1:
                                current_status_id = order_flow_mapping["process_ids"].split(",")[0]
                                current_status_ = OrderProcess.objects.filter(id=current_status_id).values("id", "code", "sequence").order_by("sequence")
                                current_status = current_status_[0]["code"]
                            if len(order_flow_mapping["process_ids"]) >= 2:
                                next_status_id = order_flow_mapping["process_ids"].split(",")[1]
                                next_status = OrderProcess.objects.filter(id=next_status_id).values("id", "code", "sequence").order_by("sequence")
                                next_status = next_status[0]["code"]
                        act_delivery_date = None
                        if delivery_date:
                            if layer_code :
                                layer_ = layer_code[0:2]
                                list_layer = [4, 6, 8]
                                if int(layer_) not in list_layer:
                                    act_delivery_date = delivery_date
                                if int(layer_) == 4:
                                    act_delivery_date = delivery_date - timedelta(days=1)
                                if int(layer_) == 6:
                                    act_delivery_date = delivery_date - timedelta(days=2)
                                if int(layer_) >= 8:
                                    act_delivery_date = delivery_date - timedelta(days=3)
                            else:
                                act_delivery_date = delivery_date
                        if order["OrderNumber"] in is_exist:
                            exist_order_id = Order.objects.filter(customer_order_nr=order["OrderNumber"]).values("id").first()
                            order_exception = OrderException.objects.filter(order__id=exist_order_id["id"], order_in_exception=False, exception_status="put_to_customer").values("id").last()
                            if order_exception:
                                Order_Attachment.objects.filter(object_id=exist_order_id["id"], file_type__code="EXCEPTION").update(deleted=True)
                                OrderException.objects.filter(id=order_exception["id"]).update(exception_status="resolve", exp_resolve_date=datetime.datetime.now(), order_in_exception=True)
                            Order.objects.filter(customer_order_nr=order["OrderNumber"]).update(
                                service_id=service_id,
                                company_id=company_id_,
                                layer=layer_code,
                                delivery_term=delivery_term[deli_term] if deli_term in delivery_term else None,
                                pcb_name=order["Board Name"],
                                order_date=order_date,
                                delivery_date=delivery_date,
                                act_delivery_date=act_delivery_date,
                                preparation_due_date=preparation_due_date,
                                is_modify=order["IsModify"],
                                import_order_date=datetime.datetime.now(),
                                delivery_format="Panel" if order["IsPanel"] is True else "Single PCB",
                                in_time=datetime.datetime.now(),
                                order_status=current_status,
                                order_next_status=next_status,
                            )
                            OrderTechParameter.objects.filter(order__customer_order_nr=order["OrderNumber"]).update(
                                is_include_assembly=True if order["Include Assembly"] != "No" else False,
                                board_thickness=board_thick_,
                                material_tg=material_tg[order["Material Tg"]] if order["Material Tg"] in material_tg else None,
                                is_special_buildup=order["Special buildup"] if order["Special buildup"] is True else False,
                                is_defined_impedance=True if order["Defined impedance"] != "0" else False,
                                top_solder_mask=top_solder_mask[order["SolderMaskTop"]] if order["SolderMaskTop"] in top_solder_mask else None,
                                bottom_solder_mask=bottom_solder_mask[order["SolderMaskBottom"]] if order["SolderMaskBottom"] in bottom_solder_mask else None,
                                top_legend=top_legend[order["Top Legend"]] if order["Top Legend"] in top_legend else None,
                                bottom_legend=bottom_legend[order["Bottom Legend"]] if order["Bottom Legend"] in bottom_legend else None,
                                is_bare_board_testing=order["BBT"] if order["BBT"] else False,
                                carbon_contacts=carbon_contacts[order["CarbonContacts"]] if order["CarbonContacts"] in carbon_contacts else None,
                                ul_marking=order["IsULSign"] if order["IsULSign"] is True else False,
                                pth_on_the_board_edge=True if order["PTH on the board edge"] == "Yes" else False,
                                round_edge_plating=order["RoundEdgePlatting"] if order["RoundEdgePlatting"] is True else False,
                                copper_upto_board_edge=True if order["PTH on the board edge"] == "Yes" else False,
                                depth_routing=True if order["Depth routing"] == "1" else False,
                                edge_connector_gold_surface=order["EdgeConnector"] if order["EdgeConnector"] else None,
                                edge_connector_bevelling="Bevelling_No" if order["Edge connector bevelling"] != True else "Bevelling_STD",
                                top_heat_sink_paste=top_heat_sink_paste[order["Top heatsink paste"]] if order["Top heatsink paste"] in top_heat_sink_paste else None,
                                bottom_heat_sink_paste=bottom_heat_sink_paste[order["Bottom heatsink paste"]] if order["Bottom heatsink paste"] in bottom_heat_sink_paste else None,
                                via_filling_hole_plugging=via_filling_hole_plugging[order["Via filling/Hole"]] if order["Via filling/Hole"] in via_filling_hole_plugging else None,
                                surface_finish=surface_finish[order["Platting"]] if order["Platting"] in surface_finish else "",
                                pcb_separation_method=pcb_separation_method[order["BoardSeparationX"]] if order["BoardSeparationX"] in pcb_separation_method else None,
                                outer_layer_copper_foil=outer_layer_copper_foil[order["OutStartCu"]] if order["OutStartCu"] in outer_layer_copper_foil else None,
                                inner_layer_copper_foil=inner_layer_copper_foil[order["InnStartCu"]] if order["InnStartCu"] in inner_layer_copper_foil else None,
                                blind_buried_via_runs=order["PTH on the board edge"] if order["PTH on the board edge"] else None,
                                peelable_mask=peelable_mask[order["PeelOff"]] if order["PeelOff"] in peelable_mask else None,
                                specific_marking=True if order["BONDINGPADS Specific marking"] != "0" else False,
                            )
                            user_id = None
                            if request.user.id:
                                user_id = request.user.id
                            else:
                                user_id = settings.ADMIN_USER
                            c_ip = base_views.get_client_ip(request)
                            action = AuditAction.UPDATE
                            exist_order_id = exist_order_id["id"]
                            if order_exception:
                                log_views.insert("pws", "order", [exist_order_id], action, user_id, c_ip, "Exception resolved.")
                            log_views.insert("pws", "order", [exist_order_id], action, user_id, c_ip, "Import order has been updated.")
                            is_imported = True
                        else:
                            docnumber = DocNumber.objects.filter(code="Order_place").first()
                            prepared_order_data = {
                                "order_number": docnumber.nextnum,
                                "customer_order_nr": order["OrderNumber"],
                                "service_id": service_id,
                                "company_id": company_id_,
                                "layer": layer_code,
                                "delivery_term":delivery_term[deli_term] if deli_term in delivery_term else None,
                                "pcb_name": order["Board Name"],
                                "order_date": order_date,
                                "delivery_date": delivery_date,
                                "act_delivery_date": act_delivery_date,
                                "order_status": current_status,
                                "order_next_status": next_status,
                                "preparation_due_date": preparation_due_date,
                                "is_modify": order["IsModify"],
                                "import_order_date": datetime.datetime.now(),
                                "delivery_format": "Panel" if order["IsPanel"] is True else "Single PCB",
                                "in_time" : datetime.datetime.now()
                            }
                            prepared_ord = {
                                "is_include_assembly": True if order["Include Assembly"] == "Yes" else False,
                                "board_thickness": board_thick_,
                                "material_tg": material_tg[order["Material Tg"]] if order["Material Tg"] in material_tg else None,
                                "is_special_buildup": order["Special buildup"] if order["Special buildup"] is True else False,
                                "is_defined_impedance": True if order["Defined impedance"] != "0" else False,
                                "top_solder_mask": top_solder_mask[order["SolderMaskTop"]] if order["SolderMaskTop"] in top_solder_mask else None,
                                "bottom_solder_mask": bottom_solder_mask[order["SolderMaskBottom"]] if order["SolderMaskBottom"] in bottom_solder_mask else None,
                                "top_legend": top_legend[order["Top Legend"]] if order["Top Legend"] in top_legend else "",
                                "bottom_legend": bottom_legend[order["Bottom Legend"]] if order["Bottom Legend"] in bottom_legend else None,
                                "is_bare_board_testing": order["BBT"] if order["BBT"] else False,
                                "carbon_contacts": carbon_contacts[order["CarbonContacts"]] if order["CarbonContacts"] in carbon_contacts else None,
                                "ul_marking": order["IsULSign"] if order["IsULSign"] is True else False,
                                "pth_on_the_board_edge": True if order["PTH on the board edge"] == "Yes" else False,
                                "round_edge_plating": order["RoundEdgePlatting"] if order["RoundEdgePlatting"] is True else False,
                                "copper_upto_board_edge": True if order["PTH on the board edge"] == "Yes" else False,
                                "depth_routing": True if order["Depth routing"] == "1" else False,
                                "edge_connector_gold_surface": order["EdgeConnector"] if order["EdgeConnector"] else None,
                                "edge_connector_bevelling": "Bevelling_No" if order["Edge connector bevelling"] != True else "Bevelling_STD",
                                "top_heat_sink_paste": top_heat_sink_paste[order["Top heatsink paste"]] if order["Top heatsink paste"] in top_heat_sink_paste else None,
                                "bottom_heat_sink_paste": bottom_heat_sink_paste[order["Bottom heatsink paste"]] if order["Bottom heatsink paste"] in bottom_heat_sink_paste else None,
                                "via_filling_hole_plugging": via_filling_hole_plugging[order["Via filling/Hole"]] if order["Via filling/Hole"] in via_filling_hole_plugging else None,
                                "surface_finish": surface_finish[order["Platting"]] if order["Platting"] in surface_finish else "",
                                "pcb_separation_method": pcb_separation_method[order["BoardSeparationX"]] if order["BoardSeparationX"] in pcb_separation_method else None,
                                "outer_layer_copper_foil": outer_layer_copper_foil[order["OutStartCu"]] if order["OutStartCu"] in outer_layer_copper_foil else None,
                                "inner_layer_copper_foil": inner_layer_copper_foil[order["InnStartCu"]] if order["InnStartCu"] in inner_layer_copper_foil else None,
                                "blind_buried_via_runs": order["PTH on the board edge"] if order["PTH on the board edge"] else None,
                                "peelable_mask": peelable_mask[order["PeelOff"]] if order["PeelOff"] in peelable_mask else None,
                                "specific_marking": True if order["BONDINGPADS Specific marking"] != "0" else False,
                            }
                            odr = Order(**prepared_order_data)
                            odr.save()
                            docnumber.increase()
                            docnumber.save()
                            prepared_ord["order_id"] = odr.id
                            prepared_order_tech_data.append(OrderTechParameter(**prepared_ord))
                            c_ip = base_views.get_client_ip(request)
                            action = AuditAction.INSERT
                            user_id = None
                            if request.user.id:
                                user_id = request.user.id
                            else:
                                user_id = settings.ADMIN_USER
                            log_views.insert("pws", "order", [odr.id], action, user_id, c_ip, "Order has been created")
                            views.skill_matrix_order(request, odr.id, current_status, user_id)
                            no_of_jobs = CompanyParameter.objects.filter(company_id=company_id_).values("no_of_jobs").first()
                            total_jobs = ""
                            if no_of_jobs["no_of_jobs"] is None:
                                total_jobs = 1
                            else:
                                total_jobs = no_of_jobs["no_of_jobs"] + 1
                            CompanyParameter.objects.filter(company_id=company_id_).update(no_of_jobs=total_jobs)
                        post_data_["id"] = order["OrderId"]
                        is_imported = True
                    except Exception as e:
                        is_imported = False
                        faild_order_nr = order["OrderNumber"]
                        send_mail(True, "public",[settings.IMPORT_FAILED_EMAIL], "PWS 2.0 Import order(s)", f"{faild_order_nr}- Power inquiry import failed.", "", "")
                        manager.create_from_exception(e)
                    url = settings.PPM_URL + "/pwsAPI/DeleteOrder"
                    PPM_KEY = settings.PPM_KEY
                    headers = {"Key": PPM_KEY, "content-type": "application/json"}
                    ec_res = requests.post(url, data=json.dumps(post_data_), headers=headers)
                OrderTechParameter.objects.bulk_create(prepared_order_tech_data)
                return is_imported
            else:
                return is_imported

        except Exception as e:
            logging.exception("Something went wrong. " + str(e))
            manager.create_from_exception(e)
            return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")

    def ec_inquiry(self, customer_orders, request):
        try:
            import_orders = []
            is_imported = False
            for order in customer_orders:
                import_orders.append(
                    {
                        "customer_order_nr": order,
                    }
                )
            if len(import_orders)>0:
                pws_service = PWSEcPyService()
                response = pws_service.post_ecc(import_orders, "/ecpy/pws/export_inq_from_ecc")
                services = Service.objects.values("id", "name")
                prepared_order_tech_data = []
                orders_id = []
                board_thickness_name = [
                    str(decimal.Decimal(order["MaterialThickness"]).quantize(decimal.Decimal("0.00"))) + " MM" for order in response["data"] if str(order["MaterialThickness"])
                ]
                board_thickness = OrderScreenParameter.objects.filter(name__in=board_thickness_name).values("name", "code")
                board_thickness_ = Util.get_dict_from_quryset("name", "code", board_thickness)
                is_exist = Order.objects.values("customer_order_nr", "id")
                is_exist_ = [x["customer_order_nr"] for x in is_exist]
                for order in response["data"]:
                    try:
                        layer_code = None
                        if order["Layers"] is not None:
                            layer_code = str(order["Layers"]) + " L" if order["Layers"] is not None else None
                            if int(order["Layers"]) > 20:
                                layer_code = str(order["Layers"]) + "L"
                        board_thick_ = "Thickness_NotSpecified"
                        if board_thickness_ and bool(board_thickness_):
                            board_thick_ = (
                                board_thickness_[str(decimal.Decimal(order["MaterialThickness"]).quantize(decimal.Decimal("0.00"))) + " MM"] if str(decimal.Decimal(order["MaterialThickness"]).quantize(decimal.Decimal("0.00"))) + " MM" in board_thickness_ else None
                            )
                        company_id_ = settings.EC_COMPANY_INQ
                        if order["Include Assembly"] is True:
                            company_id_ = settings.EC_ASSEMBLY_INQ
                        delivery_date = datetime.datetime.strptime(order["DeliveryDate"], "%d %b %Y") if order["DeliveryDate"] else None
                        order_date = datetime.datetime.strptime(order["OrderDate"], "%d %b %Y %H:%M:%S") if order["OrderDate"] else None
                        preparation_due_date = datetime.datetime.strptime(order["PrepDueDate"], "%d %b %y %H:%M:%S") if order["PrepDueDate"] else None
                        service_id = None
                        next_status = None
                        current_status = None
                        for service in services:
                            if order["Service"] == service["name"]:
                                service_id = service["id"]
                        if order["OrderStatus"] == "Order cancelled.":
                            current_status = "cancel"
                        else:
                            order_flow_mapping = OrderFlowMapping.objects.filter(company_id=company_id_, service_id=service_id).values("id", "process_ids").last()
                            if order_flow_mapping and order_flow_mapping["process_ids"]:
                                if len(order_flow_mapping["process_ids"]) >= 1:
                                    current_status_id = order_flow_mapping["process_ids"].split(",")[0]
                                    current_status_ = OrderProcess.objects.filter(id=current_status_id).values("id", "code", "sequence").order_by("sequence")
                                    current_status = current_status_[0]["code"]
                                if len(order_flow_mapping["process_ids"]) >= 2:
                                    next_status_id = order_flow_mapping["process_ids"].split(",")[1]
                                    next_status = OrderProcess.objects.filter(id=next_status_id).values("id", "code", "sequence").order_by("sequence")
                                    next_status = next_status[0]["code"]
                        act_delivery_date = None
                        if delivery_date:
                            if layer_code :
                                layer_ = layer_code[0:2]
                                list_layer = [4, 6, 8]
                                if int(layer_) not in list_layer:
                                    act_delivery_date = delivery_date
                                if int(layer_) == 4:
                                    act_delivery_date = delivery_date - timedelta(days=1)
                                if int(layer_) == 6:
                                    act_delivery_date = delivery_date - timedelta(days=2)
                                if int(layer_) >= 8:
                                    act_delivery_date = delivery_date - timedelta(days=3)
                            else:
                                act_delivery_date = delivery_date
                        if order["OrderNumber"] in customer_orders:
                            if str(order["OrderNumber"]) in is_exist_:
                                exist_order_id = Order.objects.filter(customer_order_nr=order["OrderNumber"]).values("id").first()
                                order_exception = OrderException.objects.filter(order__id=exist_order_id["id"], order_in_exception=False, exception_status="put_to_customer").values("id").last()
                                if order_exception:
                                    Order_Attachment.objects.filter(object_id=exist_order_id["id"], file_type__code="EXCEPTION").update(deleted=True)
                                    OrderException.objects.filter(id=order_exception["id"]).update(exception_status="resolve", exp_resolve_date=datetime.datetime.now(), order_in_exception=True)
                                Order.objects.filter(customer_order_nr=order["OrderNumber"]).update(
                                    company_id=company_id_,
                                    layer=layer_code,
                                    delivery_term=delivery_term[order["DeliveryTerm"]] if order["DeliveryTerm"] in delivery_term else None,
                                    pcb_name=order["PCBName"],
                                    order_date=order_date,
                                    delivery_date=delivery_date,
                                    act_delivery_date=act_delivery_date,
                                    order_previous_status=preparation_due_date,
                                    remarks=order["Remarks"],
                                    is_modify=order["IsModify"],
                                    import_order_date=datetime.datetime.now(),
                                    finished_on=None,
                                    delivery_format=delivery_format[order["IsPanel"]] if order["IsPanel"] in delivery_format else None,
                                    in_time=datetime.datetime.now(),
                                    order_status=current_status,
                                    order_next_status=next_status,
                                )
                                OrderTechParameter.objects.filter(order__customer_order_nr=order["OrderNumber"]).update(
                                    is_include_assembly=True if order["Include Assembly"] != "No" else False,
                                    board_thickness=board_thick_,
                                    material_tg=material_tg[order["Tg"]] if order["Tg"] in material_tg else None,
                                    buildup_code=order["BUOD"],
                                    top_solder_mask=top_solder_mask[order["SolderMaskTop"]] if order["SolderMaskTop"] in top_solder_mask else None,
                                    bottom_solder_mask=bottom_solder_mask[order["SolderMaskBottom"]] if order["SolderMaskBottom"] in bottom_solder_mask else None,
                                    top_legend=top_legend[order["LegendTop"]] if order["LegendTop"] in top_legend else None,
                                    bottom_legend=bottom_legend[order["LegendBottom"]] if order["LegendBottom"] in bottom_legend else None,
                                    is_bare_board_testing=True if order["BBT"] == "yes" else False,
                                    carbon_contacts=carbon_contacts[order["CarbonContacts"]] if order["CarbonContacts"] in carbon_contacts else None,
                                    ul_marking=True if order["IsULSign"] == 1 else False,
                                    round_edge_plating=True if order["RoundEdgePlatting"] == "1" else False,
                                    copper_upto_board_edge=True if order["IsCopperEdge"] == 1 else False,
                                    press_fit_holes=order["PressFitHoles"],
                                    depth_routing=True if order["DepthRoute"] == 1 else False,
                                    edge_connector_gold_surface=order["EdgeConnectorGoldThick"],
                                    edge_connector_bevelling=edge_connector_bevelling[order["IsBevelling"]] if order["IsBevelling"] in edge_connector_bevelling else None,
                                    top_heat_sink_paste=top_heat_sink_paste[order["HeatSinkTop"]] if order["HeatSinkTop"] in top_heat_sink_paste else "",
                                    bottom_heat_sink_paste=bottom_heat_sink_paste[order["HeatSinkBottom"]] if order["HeatSinkBottom"] in bottom_heat_sink_paste else None,
                                    via_filling_hole_plugging=via_filling_hole_plugging[order["IsViaFill"]] if order["IsViaFill"] in via_filling_hole_plugging else None,
                                    surface_finish=surface_finish[order["Platting"]] if order["Platting"] in surface_finish else None,
                                    pcb_separation_method=pcb_separation_method[order["BoardSeparationX"]] if order["BoardSeparationX"] in pcb_separation_method else None,
                                    outer_layer_copper_foil=outer_layer_copper_foil[order["OutStartCu"]] if order["OutStartCu"] in outer_layer_copper_foil else None,
                                    inner_layer_copper_foil=inner_layer_copper_foil[order["InnStartCu"]] if order["InnStartCu"] in inner_layer_copper_foil else None,
                                    inner_layer_core_thickness=inner_layer_core_thickness[order["CORE"]] if order["CORE"] in inner_layer_core_thickness else None,
                                    peelable_mask=peelable_mask[order["PeelOff"]] if order["PeelOff"] in peelable_mask else None,
                                    specific_marking=order["CustomerSpecificMarking"] if order["CustomerSpecificMarking"] else False,
                                )
                                orders_id.append({"order_id": order["OrderId"]})
                                user_id = None
                                if request.user.id:
                                    user_id = request.user.id
                                else:
                                    user_id = settings.ADMIN_USER
                                c_ip = base_views.get_client_ip(request)
                                action = AuditAction.UPDATE
                                exist_order_id = exist_order_id["id"]
                                if order_exception:
                                    log_views.insert("pws", "order", [exist_order_id], action, user_id, c_ip, "Exception resolved.")
                                log_views.insert("pws", "order", [exist_order_id], action, user_id, c_ip, "Import order has been updated.")
                                is_imported = True
                            else:
                                if order["OrderNumber"] in customer_orders:
                                    docnumber = DocNumber.objects.filter(code="Order_place").first()
                                    prepared_order_data = {
                                        "order_number": docnumber.nextnum,
                                        "customer_order_nr": order["OrderNumber"],
                                        "service_id": service_id,
                                        "company_id": company_id_,
                                        "layer": layer_code,
                                        "delivery_term": delivery_term[order["DeliveryTerm"]] if order["DeliveryTerm"] in delivery_term else None,
                                        "pcb_name": order["PCBName"],
                                        "order_date": order_date,
                                        "delivery_date": delivery_date,
                                        "act_delivery_date": act_delivery_date,
                                        "order_status": current_status,
                                        "order_next_status": next_status,
                                        "order_previous_status": preparation_due_date,
                                        "remarks": order["Remarks"],
                                        "is_modify": order["IsModify"],
                                        "import_order_date": datetime.datetime.now(),
                                        "finished_on": None,
                                        "delivery_format": delivery_format[order["IsPanel"]] if order["IsPanel"] in delivery_format else None,
                                        "in_time" : datetime.datetime.now()
                                    }
                                    prepared_ord = {
                                        "is_include_assembly": True if order["Include Assembly"] == "Yes" else False,
                                        "board_thickness": board_thick_,
                                        "material_tg": material_tg[order["Tg"]] if order["Tg"] in material_tg else None,
                                        "buildup_code": order["BUOD"] if order["BUOD"] else None,
                                        "top_solder_mask": top_solder_mask[order["SolderMaskTop"]] if order["SolderMaskTop"] in top_solder_mask else None,
                                        "bottom_solder_mask": bottom_solder_mask[order["SolderMaskBottom"]] if order["SolderMaskBottom"] in bottom_solder_mask else None,
                                        "top_legend": top_legend[order["LegendTop"]] if order["LegendTop"] in top_legend else None,
                                        "bottom_legend": bottom_legend[order["LegendBottom"]] if order["LegendBottom"] in bottom_legend else None,
                                        "is_bare_board_testing": True if order["BBT"] == "yes" else False,
                                        "carbon_contacts": carbon_contacts[order["CarbonContacts"]] if order["CarbonContacts"] in carbon_contacts else None,
                                        "ul_marking": True if order["IsULSign"] == 1 else False,
                                        "round_edge_plating": True if order["RoundEdgePlatting"] == "1" else False,
                                        "copper_upto_board_edge": True if order["IsCopperEdge"] == 1 else False,
                                        "press_fit_holes": order["PressFitHoles"],
                                        "depth_routing": True if order["DepthRoute"] == 1 else False,
                                        "edge_connector_gold_surface": order["EdgeConnectorGoldThick"] if order["EdgeConnectorGoldThick"] else False,
                                        "edge_connector_bevelling": edge_connector_bevelling[order["IsBevelling"]] if order["IsBevelling"] in edge_connector_bevelling else None,
                                        "top_heat_sink_paste": top_heat_sink_paste[order["HeatSinkTop"]] if order["HeatSinkTop"] in top_heat_sink_paste else None,
                                        "bottom_heat_sink_paste": bottom_heat_sink_paste[order["HeatSinkBottom"]] if order["HeatSinkBottom"] in bottom_heat_sink_paste else None,
                                        "via_filling_hole_plugging": via_filling_hole_plugging[order["IsViaFill"]] if order["IsViaFill"] in via_filling_hole_plugging else None,
                                        "surface_finish": surface_finish[order["Platting"]] if order["Platting"] in surface_finish else None,
                                        "pcb_separation_method": pcb_separation_method[order["BoardSeparationX"]] if order["BoardSeparationX"] in pcb_separation_method else None,
                                        "outer_layer_copper_foil": outer_layer_copper_foil[order["OutStartCu"]] if order["OutStartCu"] in outer_layer_copper_foil else None,
                                        "inner_layer_copper_foil": inner_layer_copper_foil[order["InnStartCu"]] if order["InnStartCu"] in inner_layer_copper_foil else None,
                                        "inner_layer_core_thickness": inner_layer_core_thickness[order["CORE"]] if order["CORE"] in inner_layer_core_thickness else None,
                                        "peelable_mask": peelable_mask[order["PeelOff"]] if order["PeelOff"] in peelable_mask else None,
                                        "specific_marking": order["CustomerSpecificMarking"] if order["CustomerSpecificMarking"] else False,
                                    }
                                    odr = Order(**prepared_order_data)
                                    odr.save()
                                    docnumber.increase()
                                    docnumber.save()
                                    prepared_ord["order_id"] = odr.id
                                    prepared_order_tech_data.append(OrderTechParameter(**prepared_ord))
                                    orders_id.append(
                                        {
                                            "order_id": order["OrderId"],
                                        }
                                    )
                                    c_ip = base_views.get_client_ip(request)
                                    action = AuditAction.INSERT
                                    user_id = None
                                    if request.user.id:
                                        user_id = request.user.id
                                    else:
                                        user_id = settings.ADMIN_USER
                                    log_views.insert("pws", "order", [odr.id], action, user_id, c_ip, "Order has been created")
                                    views.skill_matrix_order(request, odr.id, current_status, user_id)
                                    no_of_jobs = CompanyParameter.objects.filter(company_id=company_id_).values("no_of_jobs").first()
                                    total_jobs = ""
                                    if no_of_jobs["no_of_jobs"] is None:
                                        total_jobs = 1
                                    else:
                                        total_jobs = no_of_jobs["no_of_jobs"] + 1
                                    CompanyParameter.objects.filter(company_id=company_id_).update(no_of_jobs=total_jobs)
                                    is_imported = True
                    except Exception as e:
                        is_imported = False
                        faild_order_nr = order["OrderNumber"]
                        send_mail(True, "public",[settings.IMPORT_FAILED_EMAIL], "PWS 2.0 Import order(s)", f"{faild_order_nr}- EC inquiry import failed.", "", "")
                        manager.create_from_exception(e)
                pws_service.post_ecc(orders_id, "/ecpy/pws/remove_ec_inq_queue_data")
                OrderTechParameter.objects.bulk_create(prepared_order_tech_data)
                return is_imported
            else:
                return is_imported
        except Exception as e:
            logging.exception("Something went wrong. " + str(e))
            manager.create_from_exception(e)
            return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
