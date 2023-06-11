import datetime
import time
from datetime import timedelta

from auditlog.models import Auditlog
from base.choices import order_status
from base.models import Remark, DocNumber
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User
from qualityapp.models import (Efficiency, NonConformity, NonConformityDetail,
                        Operator, Order, OrderException,
                        PreDefineExceptionProblem, UserEfficiencyLog, OrderException)


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                def user_efficiency_log_update_preparation():
                    start_time = time.time()
                    UserEfficiencyLog.objects.filter(order_from_status="incoming", order_to_status="panel").update(preparation="Full preparation")
                    UserEfficiencyLog.objects.filter(order_from_status="SI", order_to_status="panel").update(preparation="Full preparation")
                    UserEfficiencyLog.objects.filter(order_from_status="SICC", order_to_status="panel").update(preparation="CC required")
                    UserEfficiencyLog.objects.filter(order_from_status="incoming", order_to_status="SICC").update(preparation="CC required")
                    UserEfficiencyLog.objects.filter(order_from_status="SI", order_to_status="SICC").update(preparation="CC required")
                    elapsed_time_secs = time.time() - start_time
                    print("==> Eser Efficiency Update Preparation Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))

                def user_efficiency_log_update_preparation_incoming_to_exception():
                    start_time = time.time()
                    pre_define_problem = PreDefineExceptionProblem.objects.filter(code="Pre-production approval").values("id").first()
                    incoming_to_exception = UserEfficiencyLog.objects.filter(order_from_status="incoming", order_to_status="exception").values("id", "order__id", "order_from_status", "created_on")
                    for data in incoming_to_exception:
                        data_records_id = data["id"]
                        created_on = data["created_on"]
                        i_to_e_query = Q()
                        i_to_e_query.add(Q(created_on__icontains=datetime.datetime.strptime(str(created_on).strip(), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M")), i_to_e_query.connector)
                        i_to_e_query.add(Q(order=data["order__id"]), i_to_e_query.connector)
                        i_to_e_query.add(Q(order_status=data["order_from_status"]), i_to_e_query.connector)
                        i_to_e_query.add(Q(pre_define_problem=pre_define_problem["id"]), i_to_e_query.connector)
                        order_exception = OrderException.objects.filter(i_to_e_query)
                        if order_exception:
                            UserEfficiencyLog.objects.filter(id=data_records_id).update(preparation="Full preparation", order_to_status="ppa_exception")
                    elapsed_time_secs = time.time() - start_time
                    print("==> Incoming To Exception Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))

                def user_efficiency_log_update_preparation_si_to_exception():
                    start_time = time.time()
                    pre_define_problem = PreDefineExceptionProblem.objects.filter(code="Pre-production approval").values("id").first()
                    si_to_exception = UserEfficiencyLog.objects.filter(order_from_status="SI", order_to_status="exception").values("id", "order__id", "order_from_status", "created_on")
                    for data in si_to_exception:
                        data_records_id = data["id"]
                        created_on = data["created_on"]
                        si_to_e_query = Q()
                        si_to_e_query.add(Q(created_on__icontains=datetime.datetime.strptime(str(created_on).strip(), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M")), si_to_e_query.connector)
                        si_to_e_query.add(Q(order=data["order__id"]), si_to_e_query.connector)
                        si_to_e_query.add(Q(order_status=data["order_from_status"]), si_to_e_query.connector)
                        si_to_e_query.add(Q(pre_define_problem=pre_define_problem["id"]), si_to_e_query.connector)
                        order_exception = OrderException.objects.filter(si_to_e_query)
                        if order_exception:
                            UserEfficiencyLog.objects.filter(id=data_records_id).update(preparation="Full preparation", order_to_status="ppa_exception")

                    elapsed_time_secs = time.time() - start_time
                    print("==> SI To Exception Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))

                def user_efficiency_log_update_preparation_sicc_to_exception():
                    start_time = time.time()
                    pre_define_problem = PreDefineExceptionProblem.objects.filter(code="Pre-production approval").values("id").first()
                    sicc_to_exception = UserEfficiencyLog.objects.filter(order_from_status="SICC", order_to_status="exception").values("id", "order__id", "order_from_status", "created_on")
                    for data in sicc_to_exception:
                        data_records_id = data["id"]
                        created_on = data["created_on"]
                        sicc_to_e_query = Q()
                        sicc_to_e_query.add(Q(created_on__icontains=datetime.datetime.strptime(str(created_on).strip(), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M")), sicc_to_e_query.connector)
                        sicc_to_e_query.add(Q(order=data["order__id"]), sicc_to_e_query.connector)
                        sicc_to_e_query.add(Q(order_status=data["order_from_status"]), sicc_to_e_query.connector)
                        sicc_to_e_query.add(Q(pre_define_problem=pre_define_problem["id"]), sicc_to_e_query.connector)
                        order_exception = OrderException.objects.filter(sicc_to_e_query)
                        if order_exception:
                            UserEfficiencyLog.objects.filter(id=data_records_id).update(preparation="CC required", order_to_status="ppa_exception")
                    elapsed_time_secs = time.time() - start_time
                    print("==> SICC To Exception Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))

                def user_efficiency_log_update_preparation_back_to_previous():
                    start = 0
                    length = 100
                    while True:
                        start_time = time.time()
                        all_records_query = Q()
                        all_records_query.add(~Q(order_from_status__in=["cancel", "exception", "ppa_exception", "finished"]), all_records_query.connector)
                        all_records_query.add(~Q(order_to_status__in=["cancel", "exception", "ppa_exception", "finished"]), all_records_query.connector)
                        all_records = UserEfficiencyLog.objects.filter(all_records_query).values("id", "order_from_status", "order_to_status", "created_on", "order__id",).order_by("id")[start : (start + length)]
                        if len(all_records) == 0:
                            break
                        for data in all_records:
                            data_records_id = data["id"]
                            created_on = data["created_on"]
                            all_records_data_query = Q()
                            all_records_data_query.add(Q(action_on__icontains=datetime.datetime.strptime(str(created_on).strip(), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M")), all_records_data_query.connector)
                            all_records_data_query.add(Q(object_id=data["order__id"]), all_records_data_query.connector)
                            all_records_data_query.add(Q(content_type_id__model="order"), all_records_data_query.connector)
                            all_records_data_query.add(Q(descr__startswith="Order sent back to  <b> " + dict(order_status)[data["order_to_status"]] + " </b>"), all_records_data_query.connector)
                            back_to_previous = Auditlog.objects.filter(all_records_data_query).values("id", "object_id")
                            if back_to_previous:
                                order = Order.objects.filter(id=data["order__id"]).values("id", "service__id", "company__id", "order_status", "operator", "layer").first()
                                layer = order["layer"] if order["layer"] != "" and order["layer"] is not None else ""
                                process__code = "back_to_previous"
                                efficiency = (
                                    Efficiency.objects.filter(company_id=order["company__id"], service_id=order["service__id"], process__code=process__code).values("layer", "multi_layer").first()
                                )
                                layer_point = ""
                                layer_ = ""
                                layer_ = layer[0:2]
                                if efficiency is None:
                                    layer_point = 0
                                else:
                                    if layer != "":
                                        if int(layer_) <= 2:
                                            layer_point = efficiency["layer"] if efficiency["layer"] is not None else 0
                                        else:
                                            layer_point = efficiency["multi_layer"] if efficiency["multi_layer"] is not None else 0
                                    else:
                                        layer_point = 0
                                UserEfficiencyLog.objects.filter(id=data_records_id).update(preparation="Back to previous", layer_point=layer_point)
                        elapsed_time_secs = time.time() - start_time
                        print("==> Back To Previous (" + str(start) + " to " + str(start + length) + ") Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))
                        start += length

                def user_efficiency_log_update_operator_shift():
                    start_time = time.time()
                    all_records = UserEfficiencyLog.objects.values("id", "order__id", "operator")
                    for data in all_records:
                        data_records_id = data["id"]
                        operator_knowledge_list = []
                        operator_shift_id = data["operator"]
                        operator_shift = Operator.objects.filter(id=operator_shift_id).values("shift").first()
                        shift = None
                        if operator_shift:
                            shift = operator_shift["shift"]
                            operator_shift_ = operator_shift["shift"]
                            if operator_shift_ == "first_shift":
                                operator_knowledge_leader = Operator.objects.filter(shift="first_shift", is_deleted=False, operator_type="KNOWLEDGE_LEA").values("id")
                                if operator_knowledge_leader:
                                    for data in operator_knowledge_leader:
                                        operator_knowledge_list.append(data["id"])
                            if operator_shift_ == "second_shift":
                                operator_knowledge_leader = Operator.objects.filter(shift="second_shift", is_deleted=False, operator_type="KNOWLEDGE_LEA").values("id")
                                if operator_knowledge_leader:
                                    for data in operator_knowledge_leader:
                                        operator_knowledge_list.append(data["id"])
                            if operator_shift_ == "third_shift":
                                operator_knowledge_leader = Operator.objects.filter(shift="third_shift", is_deleted=False, operator_type="KNOWLEDGE_LEA").values("id")
                                if operator_knowledge_leader:
                                    for data in operator_knowledge_leader:
                                        operator_knowledge_list.append(data["id"])
                        operator_knowledge_list_ = ",".join(map(str, operator_knowledge_list))
                        if operator_knowledge_list_ == "":
                            operator_knowledge_list_ = None
                        UserEfficiencyLog.objects.filter(id=data_records_id).update(operator_shift=shift, knowledge_leaders=operator_knowledge_list_)
                    elapsed_time_secs = time.time() - start_time
                    print("==> Update operator shift Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))

                def remark_prep_by_update_for_send_next():
                    start = 0
                    length = 100
                    while True:
                        start_time = time.time()
                        query = Q()
                        all_orders = Order.objects.filter().values("id")
                        order_id = [order["id"] for order in all_orders if order["id"]]
                        query.add(Q(entity_id__in=order_id), query.connector)
                        query.add(Q(content_type_id__model="order"), query.connector)
                        query.add(~Q(remark__startswith="<"), query.connector)
                        remarks_type = [
                            "Design_Remarks",
                            "analysis_remarks",
                            "incoming_remarks",
                            "BOM_incoming_remarks",
                            "SI_remarks",
                            "SICC_remarks",
                            "BOM_CC_remarks",
                            "FQC_remarks",
                            "panel_remarks",
                            "upload_panel_remarks",
                            "Efficeiency_Remarks"
                        ]
                        query.add(Q(comment_type__code__in=remarks_type), query.connector)
                        all_remarks = Remark.objects.filter(query).values("id", "entity_id", "created_on__date", "created_on__hour", "created_on__minute", "created_on").order_by("id")[start : (start + length)]
                        if len(all_remarks) == 0:
                            break
                        for data in all_remarks:
                            remark_id = data["id"]
                            order_id = data["entity_id"]
                            date = data["created_on"]
                            created_on = data["created_on__date"]
                            hour = data["created_on__hour"]
                            minute = data["created_on__minute"]
                            query2 = Q()
                            query2.add(~Q(operator=None), query2.connector)
                            query2.add(Q(descr__startswith="Order sent to") | Q(descr__startswith="Order has been  <b> Finished"), query2.connector)
                            query2.add(Q(action_on__gte=date), query2.connector)
                            query2.add(Q(content_type_id__model="order"), query2.connector)
                            query2.add(Q(object_id=order_id), query2.connector)
                            query2.add(Q(action_on__date=created_on), query2.connector)
                            query2.add(Q(action_on__hour=hour), query2.connector)
                            query2.add(Q(action_on__minute=minute), query2.connector)
                            auditlog = Auditlog.objects.filter(query2).values("id", "descr", "operator__user__id").first()
                            if auditlog:
                                order_status_ = (
                                    ("Schematic", "schematic"),
                                    ("Footprint", "footprint"),
                                    ("Placement", "placement"),
                                    ("Routing", "routing"),
                                    ("Gerber Release", "gerber_release"),
                                    ("Analysis", "analysis"),
                                    ("Incoming", "incoming"),
                                    ("BOM incoming", "BOM_incoming"),
                                    ("SI", "SI"),
                                    ("SICC", "SICC"),
                                    ("BOM CC", "BOM_CC"),
                                    ("FQC", "FQC"),
                                    ("Panel", "panel"),
                                    ("Upload Panel", "upload_panel"),
                                    ("Cancel", "cancel"),
                                    ("Exception", "exception"),
                                    ("PPA Exception", "ppa_exception"),
                                    ("Order Finish", "finished"),
                                )
                                query3 = Q()
                                query3.add(Q(descr__endswith="is reserved"), query3.connector)
                                query3.add(Q(content_type_id__model="order"), query3.connector)
                                query3.add(Q(object_id=order_id), query3.connector)
                                query3.add(Q(id__lte=auditlog["id"]), query3.connector)
                                prep_on = Auditlog.objects.filter(query3).values("id", "action_on", "descr").last()
                                descr = auditlog["descr"].split("from <b> ", 1)[1]
                                descr1 = descr.split(" </b>")[0]
                                descr2 = dict(order_status_)[descr1] if descr1 in dict(order_status_) else ""
                                Remark.objects.filter(id=remark_id).update(prep_by_id=auditlog["operator__user__id"], prep_on=prep_on["action_on"], prep_section=descr2)
                        elapsed_time_secs = time.time() - start_time
                        print("==> Remark prep by update for send next(" + str(start) + " to " + str(start + length) + ") Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))
                        start += length

                def remark_prep_section_update_for_customer_remark():
                    start = 0
                    length = 100
                    while True:
                        start_time = time.time()
                        query = Q()
                        all_orders = Order.objects.filter().values("id")
                        order_id = [order["id"] for order in all_orders if order["id"]]
                        query.add(Q(entity_id__in=order_id), query.connector)
                        query.add(Q(content_type_id__model="order"), query.connector)
                        query.add(~Q(remark__startswith="<"), query.connector)
                        remarks_type = [
                            "Customer_Remarks",
                            "Customer_CAM_Remarks"
                        ]
                        query.add(Q(comment_type__code__in=remarks_type), query.connector)
                        all_remarks = Remark.objects.filter(query).values("id", "entity_id").order_by("id")[start : (start + length)]
                        if len(all_remarks) == 0:
                            break
                        for data in all_remarks:
                            remark_id = data["id"]
                            order_id = data["entity_id"]
                            query2 = Q()
                            query2.add(Q(descr__startswith="Order has been crea"), query2.connector)
                            query2.add(Q(content_type_id__model="order"), query2.connector)
                            query2.add(Q(object_id=order_id), query2.connector)
                            auditlog = Auditlog.objects.filter(query2).values("id").first()
                            if auditlog:
                                order_status_ = (
                                    ("Schematic", "schematic"),
                                    ("Footprint", "footprint"),
                                    ("Placement", "placement"),
                                    ("Routing", "routing"),
                                    ("Gerber Release", "gerber_release"),
                                    ("Analysis", "analysis"),
                                    ("Incoming", "incoming"),
                                    ("BOM incoming", "BOM_incoming"),
                                    ("SI", "SI"),
                                    ("SICC", "SICC"),
                                    ("BOM CC", "BOM_CC"),
                                    ("FQC", "FQC"),
                                    ("Panel", "panel"),
                                    ("Upload Panel", "upload_panel"),
                                    ("Cancel", "cancel"),
                                    ("Exception", "exception"),
                                    ("PPA Exception", "ppa_exception"),
                                    ("Order Finish", "finished"),
                                )
                                query3 = Q()
                                query3.add(Q(descr__startswith="Order sent to") | Q(descr__startswith="Order has been  <b> Finished") | Q(descr__startswith="Order status changed"), query3.connector)
                                query3.add(Q(content_type_id__model="order"), query3.connector)
                                query3.add(Q(object_id=order_id), query3.connector)
                                query3.add(Q(id__gte=auditlog["id"]), query3.connector)
                                send_to_next = Auditlog.objects.filter(query3).values("id", "descr").first()
                                if send_to_next:
                                    descr = send_to_next["descr"].split("from <b> ", 1)[1]
                                    descr1 = descr.split(" </b>")[0]
                                    descr2 = dict(order_status_)[descr1] if descr1 in dict(order_status_) else ""
                                    Remark.objects.filter(id=remark_id).update(prep_section=descr2)
                                else:
                                    order = Order.objects.filter(id=order_id).values("order_status").first()
                                    Remark.objects.filter(id=remark_id).update(prep_section=order["order_status"])
                        elapsed_time_secs = time.time() - start_time
                        print("==> Remark prep section update for customer remark(" + str(start) + " to " + str(start + length) + ") Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))
                        start += length

                def remark_prep_section_update_for_exception():
                    start = 0
                    length = 100
                    while True:
                        start_time = time.time()
                        query = Q()
                        all_orders = Order.objects.filter().values("id")
                        order_id = [order["id"] for order in all_orders if order["id"]]
                        query.add(Q(entity_id__in=order_id), query.connector)
                        query.add(Q(content_type_id__model="order"), query.connector)
                        query.add(~Q(remark__startswith="<"), query.connector)
                        query.add(Q(comment_type__code="Exception_Order_Remarks"), query.connector)
                        all_remarks = Remark.objects.filter(query).values("id").order_by("id")[start : (start + length)]
                        if len(all_remarks) == 0:
                            break
                        for data in all_remarks:
                            remark_id = data["id"]
                            Remark.objects.filter(id=remark_id).update(prep_section="exception")
                        elapsed_time_secs = time.time() - start_time
                        print("==> Remark prep section update for exception(" + str(start) + " to " + str(start + length) + ") Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))
                        start += length

                def remark_prep_section_update_for_direct_add():
                    start = 0
                    length = 100
                    while True:
                        start_time = time.time()
                        query = Q()
                        all_orders = Order.objects.filter().values("id")
                        order_id = [order["id"] for order in all_orders if order["id"]]
                        query.add(Q(entity_id__in=order_id), query.connector)
                        query.add(Q(content_type_id__model="order"), query.connector)
                        query.add(Q(prep_section=None) | Q(prep_section="") | Q(prep_section=" "), query.connector)
                        all_remarks = Remark.objects.filter(query).values("id", "entity_id", "created_on", "remark", "created_on", "comment_type__code").order_by("id")[start : (start + length)]
                        if len(all_remarks) == 0:
                            break
                        prep_section_list = []
                        for data in all_remarks:
                            remark_id = data["id"]
                            order_id = data["entity_id"]
                            date = data["created_on"]
                            query2 = Q()
                            query2.add(Q(descr__startswith="Order sent to") | Q(descr__startswith="Order has been  <b> Finished") | Q(descr__startswith="Order status changed"), query2.connector)
                            query2.add(Q(action_on__gte=date), query2.connector)
                            query2.add(Q(content_type_id__model="order"), query2.connector)
                            query2.add(Q(object_id=order_id), query2.connector)
                            auditlog = Auditlog.objects.filter(query2).values("id", "object_id", "descr", "operator__user__id", "action_on").first()
                            if auditlog:
                                order_status_ = (
                                    ("Schematic", "schematic"),
                                    ("Footprint", "footprint"),
                                    ("Placement", "placement"),
                                    ("Routing", "routing"),
                                    ("Gerber Release", "gerber_release"),
                                    ("Analysis", "analysis"),
                                    ("Incoming", "incoming"),
                                    ("BOM incoming", "BOM_incoming"),
                                    ("SI", "SI"),
                                    ("SICC", "SICC"),
                                    ("BOM CC", "BOM_CC"),
                                    ("FQC", "FQC"),
                                    ("Panel", "panel"),
                                    ("Upload Panel", "upload_panel"),
                                    ("Cancel", "cancel"),
                                    ("Exception", "exception"),
                                    ("PPA Exception", "ppa_exception"),
                                    ("Order Finish", "finished"),
                                )
                                descr = auditlog["descr"].split("from <b> ", 1)[1]
                                descr1 = descr.split(" </b>")[0]
                                descr2 = dict(order_status_)[descr1] if descr1 in dict(order_status_) else ""
                                prep_section_list.append(Remark(id=remark_id, prep_section=descr2))
                            else:
                                order = Order.objects.filter(id=order_id).values("order_status").first()
                                prep_section_list.append(Remark(id=remark_id, prep_section=order["order_status"]))
                        Remark.objects.bulk_update(prep_section_list, ["prep_section"])
                        elapsed_time_secs = time.time() - start_time
                        print("==> Remark prep section update for direct add(" + str(start) + " to " + str(start + length) + ") Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))
                        start += length

                def nc_report_created_on_to_nc_date_update():
                    start = 0
                    length = 100
                    while True:
                        start_time = time.time()
                        all_nc_report = NonConformity.objects.values("id", "created_on").order_by("id")[start : (start + length)]
                        if len(all_nc_report) == 0:
                            break
                        for data in all_nc_report:
                            create_date = data["created_on"]
                            nc_id = data["id"]
                            NonConformity.objects.filter(id=nc_id).update(nc_date=create_date)
                            NonConformityDetail.objects.filter(non_conformity_id=nc_id).update(nc_detail_date=create_date)
                        elapsed_time_secs = time.time() - start_time
                        print("==> Nc report created on to nc date update(" + str(start) + " to " + str(start + length) + ") Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))
                        start += length

                def update_order_qualityapp_id():
                    start = 0
                    length = 100
                    while True:
                        start_time = time.time()
                        all_order = Order.objects.values("id").order_by("id")[start : (start + length)]
                        if len(all_order) == 0:
                            break
                        order_update_list = []
                        for data in all_order:
                            order_id = data["id"]
                            docnumber = DocNumber.objects.filter(code="Order_no_for_script").first()
                            order_update_list.append(Order(id=order_id, order_number=docnumber.nextnum))
                            docnumber.increase()
                            docnumber.save()
                        Order.objects.bulk_update(order_update_list, ["order_number"])
                        elapsed_time_secs = time.time() - start_time
                        print("==> Update order qualityapp id(" + str(start) + " to " + str(start + length) + ") Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))
                        start += length

                def update_order_exceptions_details():
                    start = 0
                    length = 100
                    while True:
                        start_time = time.time()
                        all_exception = OrderException.objects.values("id", "created_on", "order__id", "created_by").order_by("id")[start : (start + length)]
                        if len(all_exception) == 0:
                            break
                        exception_update_list = []
                        for data in all_exception:
                            exception_id = data["id"]
                            order_id = data["order__id"]
                            date = data["created_on"]
                            created_by = data["created_by"]
                            put_to_customer_date = None
                            put_to_customer_by = None
                            send_back_date = None
                            send_back_by = None

                            # for put to customer date and put to customer by
                            query = Q()
                            query.add(Q(descr__startswith="Exception sent to Cu"), query.connector)
                            query.add(Q(content_type_id__model="orderexception"), query.connector)
                            query.add(Q(object_id=exception_id), query.connector)
                            auditlog_put_to_custo = Auditlog.objects.filter(query).values("id", "descr", "action_by", "action_on").last()
                            if auditlog_put_to_custo:
                                put_to_customer_date = auditlog_put_to_custo["action_on"]
                                put_to_customer_by = auditlog_put_to_custo["action_by"]

                            # for send to back date and send to back by
                            query1 = Q()
                            query1.add(Q(descr__startswith="Exception order sent b") | Q(descr__startswith="Order has been  <b> Cancel ") | Q(descr__startswith="Exception repli"), query1.connector)
                            query1.add(Q(content_type_id__model="order"), query1.connector)
                            query1.add(Q(action_on__gte=date), query1.connector)
                            query1.add(Q(object_id=order_id), query1.connector)
                            auditlog_is_not_cancel = Auditlog.objects.filter(query1).values("id", "descr", "action_by", "action_on").first()
                            if auditlog_is_not_cancel:
                                descr = auditlog_is_not_cancel["descr"]
                                if descr.startswith("Order has been") or descr.startswith("Exception repli"):
                                    send_back_date = None
                                    send_back_by = None
                                else:
                                    send_back_date = auditlog_is_not_cancel["action_on"]
                                    send_back_by = auditlog_is_not_cancel["action_by"]

                            # for exception created by (operator)
                            query2 = Q()
                            query2.add(Q(descr__endswith=" is reserved"), query2.connector)
                            query2.add(Q(content_type_id__model="order"), query2.connector)
                            query2.add(Q(action_on__lte=date), query2.connector)
                            query2.add(Q(object_id=order_id), query2.connector)
                            auditlog_is_reserve = Auditlog.objects.filter(query2).values("id", "descr", "action_by", "action_on").last()
                            if auditlog_is_reserve:
                                descr = auditlog_is_reserve["descr"].split("<b> ", 1)[1]
                                descr = descr.split(" </b>")[0]
                                created_by = User.objects.filter(username__icontains=descr).values("id").first()
                                created_by = created_by["id"]

                            exception_update_list.append(
                                OrderException(
                                    id=exception_id,
                                    created_by_id=created_by,
                                    put_to_customer_date=put_to_customer_date,
                                    put_to_customer_by_id=put_to_customer_by,
                                    send_back_date=send_back_date,
                                    send_back_by_id=send_back_by
                                )
                            )
                        OrderException.objects.bulk_update(exception_update_list, ["created_by_id", "put_to_customer_date", "put_to_customer_by_id", "send_back_date", "send_back_by_id"])
                        elapsed_time_secs = time.time() - start_time
                        print("==> Update order exception details(" + str(start) + " to " + str(start + length) + ") Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))
                        start += length

                # user_efficiency_log_update_preparation()
                # user_efficiency_log_update_preparation_incoming_to_exception()
                # user_efficiency_log_update_preparation_si_to_exception()
                # user_efficiency_log_update_preparation_sicc_to_exception()
                # user_efficiency_log_update_preparation_back_to_previous()
                # user_efficiency_log_update_operator_shift()
                # remark_prep_by_update_for_send_next()
                # remark_prep_section_update_for_customer_remark()
                # remark_prep_section_update_for_exception()
                # remark_prep_section_update_for_direct_add()
                # nc_report_created_on_to_nc_date_update()
                # update_order_qualityapp_id()
                update_order_exceptions_details()
        except Exception as e:
            print(e)
