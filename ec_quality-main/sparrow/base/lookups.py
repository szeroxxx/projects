from itertools import chain
import json
from accounts.models import RoleGroup, UserGroup
from attachment.models import FileType
from base.models import AppResponse, CommentType
from base.util import Util
from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import HttpResponse
from qualityapp.models import (Company, CompanyUser, Layer,
                        NcCategory, Operator, OrderFlowMapping,
                        OrderProcess, PreDefineExceptionProblem, Service)


class Lookup:
    def __init__(self, model_name, columns=None, query=None, search_value="", length=None, order_by=None):
        self.model_name = model_name
        self.data_order = order_by
        search_value = search_value.strip()
        if length is None:
            length = 10
        if query is None:
            query = Q()
        if search_value != "" and model_name != "UserProfile":
            # query = Q()
            query.add(Q(name__istartswith=search_value), query.connector)
        if search_value != "" and model_name == "UserProfile":
            # query = Q()
            query.add(Q(user__first_name__icontains=search_value) | Q(user__last_name__icontains=search_value), query.connector)
        if columns is None:
            columns = ["id", "name"]
        self.query = query
        self.columns = columns
        self.search_value = search_value
        self.length = length

    def get_data(self):
        model_instance = globals()[self.model_name]
        data = None
        if self.search_value == "":

            data = Util.get_cache("public", "lookup_default_data_" + self.model_name)
            # if data is not None:
            # print("GOT CACHE")

        if data is None and self.search_value == "":
            if self.model_name in ["Routing", "OperationMaster"]:
                if self.data_order is not None:
                    data = model_instance.objects.filter(self.query).order_by(self.data_order).values(*self.columns)
                else:
                    data = model_instance.objects.filter(self.query).values(*self.columns)
            else:
                if self.data_order is not None:
                    data = model_instance.objects.filter(self.query).order_by(self.data_order).values(*self.columns)[: self.length]
                else:
                    data = model_instance.objects.filter(self.query).values(*self.columns)[: self.length]
            Util.set_cache("public", "lookup_default_data_" + self.model_name, data)
            # print("DATABASE")

        if self.query != "" and data is None:
            data = Util.get_cache("public", "lookup_default_data_" + self.model_name)
            comparision_field = "user__first_name" if self.model_name == "UserProfile" else "name"
            if self.search_value in [text[comparision_field] for text in data] and self.search_value != "":
                data = Util.get_cache("public", "lookup_default_data_" + self.model_name)
                # print("SEARCHED FROM CATCH")
            else:
                if self.model_name in ["Routing", "OperationMaster"]:
                    data = model_instance.objects.filter(self.query).values(*self.columns)
                else:
                    data = model_instance.objects.filter(self.query).values(*self.columns)[: self.length]
                # print("SEARCHED IN DB")
        return data

    def get_response(self):
        items = self.get_data()
        response = []
        for item in items:
            response.append(item)
        return response

    def get_seleted_data(self, selectedID):
        response = []
        model_instance = globals()[self.model_name]
        cache_data = Util.get_cache("public", "lookup_default_data_" + self.model_name)
        if cache_data is not None:
            stored_ids = []
            for data_id in cache_data:
                stored_ids.append(data_id["id"])
            if int(selectedID) in stored_ids:
                data = Util.get_cache("public", "lookup_default_data_" + self.model_name)
                # print("CACHE SELECTED ID")
            else:
                if self.model_name in ["Routing", "OperationMaster"]:
                    db_data = model_instance.objects.filter(id=selectedID).values(*self.columns)
                else:
                    db_data = model_instance.objects.filter(id=selectedID).values(*self.columns)[: self.length]
                if len(cache_data) != 0:
                    data = list(chain(db_data, cache_data))
                    if self.model_name in ["Routing", "OperationMaster"]:
                        data = data
                    else:
                        data = data[:10]
                    Util.set_cache("public", "lookup_default_data_" + self.model_name, data)
        else:
            if self.model_name in ["Routing", "OperationMaster"]:
                data = model_instance.objects.filter(id=selectedID).values(*self.columns)
            else:
                data = model_instance.objects.filter(id=selectedID).values(*self.columns)[: self.length]
            # print("DB QUERY FOR SELECTED ID")
        for item in data:
            response.append(item)
        return response


def lookups(request, model):
    response = []
    q = request.POST.get("query")
    bid = request.POST.get("bid")  # base id passed when dropdown is dependent on base field
    onfocus = request.POST.get("onfocus")
    selectedId = request.POST.get("id", False)
    if selectedId == "" and q == "" and not onfocus:
        response.append({"name": "", "id": ""})
        return HttpResponse(AppResponse.get(response), content_type="json")

    selectedIds = []
    if selectedId and selectedId.find(","):
        selectedIds = [int(x) for x in selectedId.split(",")]

    if model == "group":
        user_roles = Group.objects.filter(name__icontains=q).order_by("name")[:10]
        response = []
        for user_role in user_roles:
            response.append({"name": user_role.name, "id": user_role.id})
        if selectedIds:
            selected_records = Group.objects.filter(id__in=selectedIds)
            for selected_record in selected_records:
                response.append({"name": selected_record.name, "id": selected_record.id})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "user_group":
        user_roles = RoleGroup.objects.filter(group__name__icontains=q, user=True, is_deleted=False).order_by("group__name").values("group__name", "group__id")
        response = []
        for user_role in user_roles:
            response.append({"name": user_role["group__name"], "id": user_role["group__id"]})
        if selectedIds:
            selected_records = RoleGroup.objects.filter(id__in=selectedIds).values("group__name", "group__id")
            for selected_record in selected_records:
                response.append({"name": selected_record["group__name"], "id": selected_record["group__id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "operator_group":
        user_roles = RoleGroup.objects.filter(group__name__icontains=q, operator=True, is_deleted=False).order_by("group__name").values("group__name", "group__id")
        response = []
        for user_role in user_roles:
            response.append({"name": user_role["group__name"], "id": user_role["group__id"]})
        if selectedIds:
            selected_records = RoleGroup.objects.filter(id__in=selectedIds).values("group__name", "group__id")
            for selected_record in selected_records:
                response.append({"name": selected_record["group__name"], "id": selected_record["group__id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "companies":
        company_names = Company.objects.filter(name__icontains=q, is_active=True, is_deleted=False).order_by("name").values("name", "id")[:10]
        response = []
        for company_name in company_names:
            response.append({"name": company_name["name"], "id": company_name["id"]})
        if selectedIds and selectedIds != "":
            selected_records = Company.objects.filter(id__in=selectedIds).values("name", "id")
            for selected_record in selected_records:
                response.append({"name": selected_record["name"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "services":
        service_names = Service.objects.filter(name__icontains=q).order_by("name").values("name", "id")
        response = []
        for service_name in service_names:
            response.append({"name": service_name["name"], "id": service_name["id"]})
        if selectedIds and selectedIds != "":
            selected_records = Service.objects.filter(id__in=selectedIds).values("name", "id")
            for selected_record in selected_records:
                response.append({"name": selected_record["name"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "layers":
        layer_names = Layer.objects.filter(name__icontains=q).order_by("name").values("name", "id")
        response = []
        for layer_name in layer_names:
            response.append({"name": layer_name["name"], "id": layer_name["id"]})
        if selectedIds and selectedIds != "":
            selected_records = Layer.objects.filter(id__in=selectedIds).values("name", "id")
            for selected_record in selected_records:
                response.append({"name": selected_record["name"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "processes":
        process_names = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous"]), name__icontains=q).order_by("id").values("name", "id")
        response = []
        for process_name in process_names:
            response.append({"name": process_name["name"], "id": process_name["id"]})
        if selectedIds and selectedIds != "":
            selected_records = OrderProcess.objects.filter(id__in=selectedIds).values("name", "id")
            for selected_record in selected_records:
                response.append({"name": selected_record["name"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "user_efficiency_processes":
        process_names = OrderProcess.objects.filter(name__icontains=q).order_by("id").values("name", "id")
        response = []
        for process_name in process_names:
            response.append({"name": process_name["name"], "id": process_name["id"]})
        if selectedIds and selectedIds != "":
            selected_records = OrderProcess.objects.filter(id__in=selectedIds).values("name", "id")
            for selected_record in selected_records:
                response.append({"name": selected_record["name"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "operators":
        operators = Operator.objects.filter(user__username__icontains=q, is_active=True, is_deleted=False).order_by("user__username").values("user__username", "id")
        response = []
        for operator in operators:
            response.append({"name": operator["user__username"], "id": operator["id"]})
        if selectedIds and selectedIds != "":
            selected_records = Operator.objects.filter(id__in=selectedIds).values("user__username", "id")
            for selected_record in selected_records:
                response.append({"name": selected_record["user__username"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "leaders":
        operators = Operator.objects.filter(user__username__icontains=q, is_active=True, is_deleted=False).order_by("user__username").values("user__username", "id", "user")
        operator_ids = []
        for id in operators:
            operator_ids.append(id["user"])
        Leaders = UserGroup.objects.filter(user__in=operator_ids, group__name__in=["Leader", "Group Leader", "Admin"]).values("user", "group__name", "user__username")
        response = []
        for Leader in Leaders:
            response.append({"name": Leader["user__username"], "id": Leader["user"]})
        if selectedIds and selectedIds != "":
            selected_records = UserGroup.objects.filter(user__in=selectedIds).values("user__username", "user")
            for selected_record in selected_records:
                response.append({"name": selected_record["user__username"], "id": selected_record["user"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "company_user":
        company_id = request.POST.get("filter")
        company_users = CompanyUser.objects.filter(company__is_active=True, company__is_deleted=False, is_deleted=False, company=company_id).order_by("company__name").values("user__username", "id", "user")
        response = []
        for company_user in company_users:
            response.append({"name": company_user["user__username"], "id": company_user["user"]})
        if selectedIds and selectedIds != "":
            selected_records = CompanyUser.objects.filter(id__in=selectedIds).values("user__username", "id", "user")
            for selected_record in selected_records:
                response.append({"name": selected_record["user__username"], "id": selected_record["user"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "select_type":  # for testing purpose

        types = [{"type": "EC09 Order", "id": 1}, {"type": "EC09 Inquiry", "id": 2}, {"type": "Power Order", "id": 3}, {"type": "Power Inquiry", "id": 4}]
        response = []
        for type in types:
            response.append({"name": type["type"], "id": type["id"]})
        if selectedIds and selectedIds != "":
            selected_records = types
            for selected_record in selected_records:
                response.append({"name": selected_record["type"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "order_number":  # for testing purpose
        types = [{"type": "EC09 Order", "id": 1}, {"type": "EC09 Inquiry", "id": 2}, {"type": "Power Order", "id": 3}, {"type": "Power Inquiry", "id": 4}]
        order_numbers = {
            1: [{"name": "Order 1", "id": 1}, {"name": "Order 2", "id": 2}, {"name": "Order 3", "id": 3}],
            2: [{"name": "Order2 1", "id": 1}, {"name": "Order 2", "id": 2}, {"name": "Order3 3", "id": 3}],
        }
        response = []
        for order_number in order_numbers:
            response.append({"name": order_number["order_number"], "id": order_number["id"]})

        if selectedIds and selectedIds != "":
            selected_records = order_numbers
            for selected_record in selected_records:
                response.append({"name": selected_record["order_number"], "id": selected_record["id"]})
        if bid is not None:
            response = order_numbers[bid]
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "order_number":

        order_numbers = [{"order_number": "Order 1", "id": 1}, {"order_number": "Order 2", "id": 2}, {"order_number": "Order 3", "id": 3}]
        response = []
        for order_number in order_numbers:
            response.append({"name": order_number["order_number"], "id": order_number["id"]})
        if selectedIds and selectedIds != "":
            selected_records = order_numbers
            for selected_record in selected_records:
                response.append({"name": selected_record["order_number"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "pre_define_problem":
        exception_problems = PreDefineExceptionProblem.objects.filter(Q(code__icontains=q), Q(is_problem=True)).order_by("id").values("code", "id")
        response = []
        for exception_problem in exception_problems:
            response.append({"name": exception_problem["code"], "id": exception_problem["id"]})
        if selectedIds and selectedIds != "":
            selected_records = PreDefineExceptionProblem.objects.filter(id__in=selectedIds).values("code", "id")
            for selected_record in selected_records:
                response.append({"name": selected_record["code"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "select":
        selects = [{"select": "Company", "id": 1}, {"select": "User", "id": 2}]
        response = []
        for select in selects:
            response.append({"name": select["select"], "id": select["id"]})
        if selectedIds and selectedIds != "":
            selected_records = selects
            for selected_record in selected_records:
                response.append({"name": selected_record["select"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "main_category":
        nc_categories = NcCategory.objects.filter(name__icontains=q, is_deleted=False).order_by("name").values("name", "id")[:5]
        response = []
        for nc_category in nc_categories:
            response.append({"name": nc_category["name"], "id": nc_category["id"]})
        if selectedIds and selectedIds != "":
            selected_records = NcCategory.objects.filter(id__in=selectedIds).values("name", "id")
            for selected_record in selected_records:
                response.append({"name": selected_record["name"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "main_category_nc_report":
        nc_categories = NcCategory.objects.filter(name__icontains=q, parent_id=None, is_deleted=False).order_by("name").values("name", "id")
        response = []
        for nc_category in nc_categories:
            response.append({"name": nc_category["name"], "id": nc_category["id"]})
        if selectedIds and selectedIds != "":
            selected_records = NcCategory.objects.filter(id__in=selectedIds).values("name", "id")
            for selected_record in selected_records:
                response.append({"name": selected_record["name"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "sub_category_nc_report":
        response = []
        nc_categories = NcCategory.objects.filter(id__in=selectedIds, is_deleted=False).values("id", "name")
        for nc_category in nc_categories:
            response.append({"name": nc_category["name"], "id": nc_category["id"]})
        if bid is not None:
            nc_categories = NcCategory.objects.filter(parent_id=int(bid), is_deleted=False).values("id", "name")
            for nc_category in nc_categories:
                response.append({"name": nc_category["name"], "id": nc_category["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "remark_type":
        remark_types = CommentType.objects.filter(~Q(code="monthwise_performance_remark"), name__icontains=q, is_active=True).order_by("name")[:10]
        response = []
        for remark_type in remark_types:
            response.append({"name": remark_type.name, "id": remark_type.id})
        if selectedIds and selectedIds != "":
            selected_record = CommentType.objects.filter(id__in=selectedIds).first()
            if selected_record is not None:
                response.append({"name": selected_record.name, "id": selected_record.id})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "file_type":
        file_types = FileType.objects.filter(Q(is_active=True), ~Q(code__in=["EXCEPTION_IMAGE", "EXCEPTION_SI", "SICC", "ORDER", "MESSAGE", "EXCEPTION", "document", "EXCEPTION_REPLY", "MESSAGE_FILE", "NC_FILE", "CAR_FILE"]), name__icontains=q).order_by("name")
        response = []
        for file_type in file_types:
            response.append({"name": file_type.name, "id": file_type.id})
        if selectedIds and selectedIds != "":
            selected_record = FileType.objects.filter(id__in=selectedIds).first()
            if selected_record is not None:
                response.append({"name": selected_record.name, "id": selected_record.id})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "order_flow_mapping_company":
        order_flow_companies = OrderFlowMapping.objects.filter(company__name__icontains=q, is_deleted=False).order_by("company__name").values("company__name", "company_id").distinct()
        response = []
        for order_flow_company in order_flow_companies:
            response.append({"name": order_flow_company["company__name"], "id": order_flow_company["company_id"]})
        if selectedIds and selectedIds != "":
            selected_records = OrderFlowMapping.objects.filter(id__in=selectedIds).values("company__name", "company_id")
            for selected_record in selected_records:
                response.append({"name": selected_record["company__name"], "id": selected_record["company_id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "order_flow_mapping_service":
        response = []
        order_flow_services = OrderFlowMapping.objects.filter(service_id__in=selectedIds, is_deleted=False).values("service_id", "service__name")
        for order_flow_service in order_flow_services:
            response.append({"name": order_flow_service["service__name"], "id": order_flow_service["service_id"]})
        if bid is not None:
            order_flow_services = OrderFlowMapping.objects.filter(Q(company_id=int(bid)), ~Q(service=None)).values("service_id", "service__name")
            for order_flow_service in order_flow_services:
                response.append({"name": order_flow_service["service__name"], "id": order_flow_service["service_id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "remark_type_send_to_next_back_to_previous":
        remark_list = ["schematic", "footprint", "placement", "routing", "gerber_release"]
        if json.loads(request.POST.get("filter")) in remark_list:
            code = "Design_Remarks"
        else:
            code = json.loads(request.POST.get("filter")) + "_remarks"
        remark_types = CommentType.objects.filter(code=code, is_active=True).order_by("name")[:10]
        response = []
        for remark_type in remark_types:
            response.append({"name": remark_type.name, "id": remark_type.id})
        if selectedIds and selectedIds != "":
            selected_record = CommentType.objects.filter(id__in=selectedIds).first()
            if selected_record is not None:
                response.append({"name": selected_record.name, "id": selected_record.id})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "document_tag":
        from attachment import views
        from attachment.models import Tag

        tags = Tag.objects.get_queryset_ancestors(Tag.objects.filter(name__icontains=q), include_self=True).order_by("name")[:10]
        response = []
        for tag in tags:
            tag_name = views.get_hierarchy_tag(tag, tag.name)
            response.append({"id": tag.id, "name": tag_name})
        if selectedIds and selectedIds != "":
            selected_records = Tag.objects.get_queryset_ancestors(Tag.objects.filter(id__in=selectedIds), include_self=True).values("name", "id")
            for selected_record in selected_records:
                response.append({"name": selected_record["name"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "processes_allocation":
        process_names = OrderProcess.objects.filter(~Q(code__in=["panel", "upload_panel", "exception", "back_to_previous"]), name__icontains=q).order_by("id").values("name", "id")
        response = []
        for process_name in process_names:
            response.append({"name": process_name["name"], "id": process_name["id"]})
        if selectedIds and selectedIds != "":
            selected_records = OrderProcess.objects.filter(id__in=selectedIds).values("name", "id")
            for selected_record in selected_records:
                response.append({"name": selected_record["name"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")

    if model == "select_user_efficiency_report":
        selects = [{"select": "Customer wise", "id": 3}, {"select": "User wise", "id": 2}, {"select": "Shift wise", "id": 1}]
        response = []
        for select in selects:
            response.append({"name": select["select"], "id": select["id"]})
        if selectedIds and selectedIds != "":
            selected_records = selects
            for selected_record in selected_records:
                response.append({"name": selected_record["select"], "id": selected_record["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")


def getAddress(address_obj):
    address_name = address_obj.country.name if address_obj.country is not None else ""
    address_name = address_obj.city + ", " + address_name if address_obj.city != "" else address_name
    address_name = address_obj.street2 + ", " + address_name if address_obj.street2 != "" else address_name
    address_name = address_obj.street + ", " + address_name if address_obj.street != "" else address_name
    return address_name
