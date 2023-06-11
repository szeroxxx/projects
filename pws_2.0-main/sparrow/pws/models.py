
from attachment.models import Attachment
from base.choices import (
    bottom_heat_sink_paste,
    bottom_legend,
    bottom_solder_mask,
    carbon_contacts,
    delivery_format,
    delivery_term,
    due_time,
    edge_connector_bevelling,
    engineer_1,
    engineer_2,
    exception_status,
    fai,
    hole_plugging,
    inner_layer_copper_foil,
    inner_layer_core_thickness,
    material_tg,
    nc_type,
    operator_group,
    operator_type,
    order_allocation,
    order_status,
    outer_layer_copper_foil,
    pcb_separation_method,
    peelable_mask,
    permanent_shift,
    prod_panel_size,
    removal_nfp_allowed,
    shift,
    surface_finish,
    top_heat_sink_paste,
    top_legend,
    top_solder_mask,
    u_via_filling,
    venting_pattern,
    via_filling_hole_plugging,
    tech_help_status,
    years_of_experience,
)
from django.contrib.auth.models import User
from django.db import models
from jsonfield import JSONField

class Company(models.Model):
    name = models.CharField(max_length=200)
    initials = models.CharField(max_length=200)
    company_img = models.TextField(default="")
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CompanyParameter(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="%(class)s_company")
    gen_mail = models.CharField(max_length=200, null=True)
    ord_rec_mail = models.CharField(max_length=200, null=True)
    ord_exc_gen_mail = models.CharField(max_length=200, null=True)
    ord_exc_rem_mail = models.CharField(max_length=200, null=True)
    ord_comp_mail = models.CharField(max_length=200, null=True)
    mail_from = models.CharField(max_length=100, null=True)
    is_req_multi_operator = models.BooleanField(default=True)
    is_req_files = models.BooleanField(default=True)
    is_send_attachment = models.BooleanField(default=True)
    no_of_jobs = models.IntegerField(null=True)
    is_smart_plate = models.BooleanField(default=True)
    is_checklist_req = models.BooleanField(default=True)
    is_exp_file_attachment = models.BooleanField(default=True)
    is_checklist_pdf = models.BooleanField(default=True)
    int_exc_from = models.CharField(max_length=200, null=True, blank=True)
    int_exc_to = models.CharField(max_length=200, null=True, blank=True)
    int_exc_cc = models.CharField(max_length=200, null=True, blank=True)


class OrderScreenParameter(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    sequence = models.IntegerField(null=True, blank=True)
    parent_id = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.code


class OrderScreen(models.Model):
    order_screen_parameter = models.ForeignKey(OrderScreenParameter, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="%(class)s_company")
    default_value = models.CharField(max_length=400, null=True)
    display_ids = models.CharField(max_length=400, null=True, blank=True)
    is_compulsory = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.order_screen_parameter.name + "   " + self.company.name)


class OrderProcess(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    sequence = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BoardThickness(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Layer(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class OrderFlowMapping(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="%(class)s_company")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="%(class)s_service", null=True, blank=True)
    process_ids = models.CharField(max_length=200, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)


class SubGroupOfOperator(models.Model):
    sub_group_name = models.CharField(max_length=200)
    is_deleted = models.BooleanField(default=False)


class Operator(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    company_ids = models.CharField(max_length=4000, null=True, blank=True)
    ec_user = models.CharField(max_length=250, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    shift = models.CharField(choices=shift, max_length=50, null=True, blank=True)
    permanent_shift = models.CharField(choices=permanent_shift, max_length=50, null=True, blank=True)
    operator_group = models.CharField(choices=operator_group, max_length=50, null=True, blank=True)
    operator_type = models.CharField(choices=operator_type, max_length=50, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    show_own_records_only = models.BooleanField(default=False)
    doj = models.DateTimeField(null=True, blank=True)
    doc = models.DateTimeField(null=True, blank=True)
    dor = models.DateTimeField(null=True, blank=True)
    remark = models.TextField(default="", blank=True)
    emp_code = models.CharField(max_length=200, null=True, blank=True)
    sub_group_of_operator = models.ForeignKey(SubGroupOfOperator, on_delete=models.PROTECT, null=True, blank=True)


class CompanyUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)


class OrderAllocationFlow(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="%(class)s_company")
    allocation_by = models.ForeignKey(CompanyUser, on_delete=models.PROTECT, null=True, blank=True)
    allocation = models.CharField(choices=order_allocation, max_length=50, null=True, blank=True)  # not clear
    active_date = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)


class Order(models.Model):
    order_number = models.CharField(max_length=100, null=True, blank=True)
    customer_order_nr = models.CharField(max_length=100, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, null=True, blank=True)
    layer = models.CharField(max_length=50, null=True, blank=True)
    delivery_format = models.CharField(choices=delivery_format, max_length=50, null=True, blank=True)
    delivery_term = models.CharField(choices=delivery_term, max_length=50, null=True, blank=True)
    pcb_name = models.CharField(max_length=350, null=True, blank=True)
    user = models.ForeignKey(CompanyUser, on_delete=models.PROTECT, null=True, blank=True)
    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)
    order_date = models.DateTimeField(null=True, blank=True)
    import_order_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    act_delivery_date = models.DateTimeField(null=True, blank=True)
    finished_on = models.DateTimeField(null=True, blank=True)
    order_status = models.CharField(choices=order_status, max_length=50, null=True, blank=True)
    order_next_status = models.CharField(max_length=50, null=True, blank=True)
    order_previous_status = models.CharField(max_length=50, null=True, blank=True)
    preparation_due_date = models.DateTimeField(null=True, blank=True)
    customer_type = models.CharField(max_length=500, null=True, blank=True)
    remarks = models.TextField(default="", blank=True)
    is_modify = models.BooleanField(default=False)
    is_repeat = models.BooleanField(default=False)
    in_time = models.DateTimeField(null=True, blank=True)
    panel_no = models.CharField(max_length=200, null=True, blank=True)
    panel_qty = models.IntegerField(null=True, blank=True)
    mail_messages = JSONField(null=True, blank=True)

    def __str__(self):
        return str(self.order_number)


class OrderTechParameter(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    is_include_assembly = models.BooleanField(default=False)
    is_top_stencil = models.BooleanField(default=False)
    is_bottom_stencil = models.BooleanField(default=False)
    pcb_separation_method = models.CharField(choices=pcb_separation_method, max_length=100, null=True, blank=True)
    board_thickness = models.CharField(max_length=100, null=True, blank=True)
    material_tg = models.CharField(choices=material_tg, max_length=100, null=True, blank=True)
    buildup_code = models.CharField(max_length=100, null=True, blank=True)
    outer_layer_copper_foil = models.CharField(choices=outer_layer_copper_foil, max_length=100, null=True, blank=True)
    inner_layer_copper_foil = models.CharField(choices=inner_layer_copper_foil, max_length=100, null=True, blank=True)
    is_special_buildup = models.BooleanField(default=False)
    inner_layer_core_thickness = models.CharField(choices=inner_layer_core_thickness, max_length=100, null=True, blank=True)
    blind_buried_via_runs = models.CharField(max_length=100, null=True, blank=True)
    is_defined_impedance = models.BooleanField(default=False)
    top_solder_mask = models.CharField(choices=top_solder_mask, max_length=100, null=True, blank=True)
    bottom_solder_mask = models.CharField(choices=bottom_solder_mask, max_length=100, null=True, blank=True)
    top_legend = models.CharField(choices=top_legend, max_length=100, null=True, blank=True)
    bottom_legend = models.CharField(choices=bottom_legend, max_length=100, null=True, blank=True)
    surface_finish = models.CharField(choices=surface_finish, max_length=100, null=True, blank=True)
    is_bare_board_testing = models.BooleanField(default=False)
    peelable_mask = models.CharField(choices=peelable_mask, max_length=100, null=True, blank=True)
    carbon_contacts = models.CharField(choices=carbon_contacts, max_length=100, null=True, blank=True)
    ul_marking = models.BooleanField(default=False)
    specific_marking = models.BooleanField(default=False)
    pth_on_the_board_edge = models.BooleanField(default=False)
    round_edge_plating = models.BooleanField(default=False)
    copper_upto_board_edge = models.BooleanField(default=False)
    press_fit_holes = models.BooleanField(default=False)
    chamfered_holes = models.BooleanField(default=False)
    depth_routing = models.BooleanField(default=False)
    edge_connector_gold_surface = models.CharField(max_length=100, null=True, blank=True)
    edge_connector_bevelling = models.CharField(choices=edge_connector_bevelling, max_length=100, null=True, blank=True)
    top_heat_sink_paste = models.CharField(choices=top_heat_sink_paste, max_length=100, null=True, blank=True)
    bottom_heat_sink_paste = models.CharField(choices=bottom_heat_sink_paste, max_length=100, null=True, blank=True)
    via_filling_hole_plugging = models.CharField(choices=via_filling_hole_plugging, max_length=100, null=True, blank=True)
    tool_nr = models.CharField(max_length=100, null=True, blank=True)
    prod_panel_size = models.CharField(choices=prod_panel_size, max_length=100, null=True, blank=True)
    is_nda = models.BooleanField(default=False)
    is_qta = models.BooleanField(default=False)
    due_time = models.CharField(choices=due_time, max_length=100, null=True, blank=True)
    tool_spec = models.CharField(max_length=100, null=True, blank=True)
    logistics_spec = models.CharField(max_length=100, null=True, blank=True)
    removal_nfp_allowed = models.CharField(choices=removal_nfp_allowed, max_length=100, null=True, blank=True)
    extra_coupon = models.CharField(max_length=100, null=True, blank=True)
    hole_plugging = models.CharField(choices=hole_plugging, max_length=100, null=True, blank=True)
    u_via_filling = models.CharField(choices=u_via_filling, max_length=100, null=True, blank=True)
    fai = models.CharField(choices=fai, max_length=100, null=True, blank=True)
    cam_remark = models.CharField(max_length=100, null=True, blank=True)
    venting_pattern = models.CharField(choices=venting_pattern, max_length=100, null=True, blank=True)
    engineer_1 = models.CharField(choices=engineer_1, max_length=100, null=True, blank=True)
    engineer_2 = models.CharField(choices=engineer_2, max_length=100, null=True, blank=True)


class Efficiency(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="%(class)s_company")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="%(class)s_service")
    process = models.ForeignKey(OrderProcess, on_delete=models.PROTECT)
    layer = models.IntegerField(null=True, blank=True)
    multi_layer = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)


class NcCategory(models.Model):
    name = models.CharField(max_length=200)
    parent_id = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)


class PreDefineExceptionProblem(models.Model):
    code = models.CharField(max_length=200)
    description = models.CharField(max_length=600)
    is_deleted = models.BooleanField(default=False)
    is_problem = models.BooleanField(default=False)

    def __str__(self):
        return self.code


class PreDefineExceptionSolution(models.Model):
    code = models.CharField(max_length=200)
    description = models.CharField(max_length=600)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.code


class OrderException(models.Model):
    exception_nr = models.CharField(max_length=100, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    exception_status = models.CharField(choices=exception_status, max_length=100, null=True, default="in_coming")
    order_status = models.CharField(max_length=100, null=True)
    pre_define_problem = models.ForeignKey(PreDefineExceptionProblem, on_delete=models.PROTECT, null=True)
    problem_description = models.CharField(max_length=100, null=True, blank=True)
    pre_define_solution = models.ForeignKey(PreDefineExceptionSolution, on_delete=models.PROTECT, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    put_to_customer_date = models.DateTimeField(null=True, blank=True)
    put_to_customer_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="put_to_customer_by")
    send_back_date = models.DateTimeField(null=True, blank=True)
    send_back_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="send_back_by")
    exp_resolve_date = models.DateTimeField(null=True, blank=True)
    total_reminder = models.IntegerField(null=True, blank=True)
    last_reminder_date = models.DateTimeField(null=True, blank=True)
    is_confirm_used = models.BooleanField(default=False)
    is_modify_used = models.BooleanField(default=False)
    is_cancel_used = models.BooleanField(default=False)
    is_remark_used = models.BooleanField(default=False)
    order_in_exception = models.BooleanField(default=False)
    is_si_file = models.BooleanField(default=False)
    internal_remark = models.TextField(default="", blank=True, null=True)


class Order_Attachment(Attachment):
    pass


class NonConformity(models.Model):
    nc_number = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="%(class)s_company")
    category = models.ForeignKey(NcCategory, on_delete=models.PROTECT, null=True, related_name="nc_category")
    sub_category = models.ForeignKey(NcCategory, on_delete=models.PROTECT, null=True, related_name="nc_sub_category")
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True)
    nc_type = models.CharField(choices=nc_type, max_length=100, null=True)
    root_cause = models.TextField(default="")
    problem = models.TextField(default="")
    solution = models.TextField(default="")
    created_on = models.DateTimeField(auto_now_add=True)
    nc_date = models.DateTimeField(null=True, blank=True)
    nc_from = models.CharField(choices=order_status, max_length=50, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True)


class NonConformityDetail(models.Model):
    non_conformity = models.ForeignKey(NonConformity, on_delete=models.PROTECT, null=True)
    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True)
    process = models.ForeignKey(OrderProcess, on_delete=models.PROTECT, null=True)
    nc_detail_date = models.DateTimeField(null=True, blank=True)
    audit_log = models.ForeignKey("auditlog.Auditlog", on_delete=models.PROTECT, null=True)


class UserEfficiencyLog(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True)
    action_code = models.CharField(max_length=100)
    layer = models.CharField(max_length=100)
    layer_point = models.IntegerField(null=True, blank=True)
    order_from_status = models.CharField(max_length=100)
    order_to_status = models.CharField(max_length=100, null=True, blank=True)
    prep_time = models.IntegerField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    order_layer = models.CharField(max_length=100)
    extra_point = models.IntegerField(null=True, blank=True)
    total_work_efficiency = models.DecimalField(decimal_places=2, max_digits=8)
    created_on = models.DateTimeField(auto_now_add=True)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, null=True, blank=True)
    knowledge_leaders = models.CharField(max_length=4000, null=True, blank=True)
    preparation = models.CharField(max_length=100, null=True, blank=True)
    operator_shift = models.CharField(max_length=200, null=True, blank=True)
    target_efficiency = models.IntegerField(null=True, blank=True)
    minimum_efficiency = models.IntegerField(null=True, blank=True)


class ActiveOperators(models.Model):
    operator_id = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True)
    logged_in_time = models.DateTimeField(null=True, blank=True)
    reserved_order_id = models.ForeignKey(Order, on_delete=models.PROTECT, null=True)
    shift_id = models.CharField(choices=shift, max_length=50, null=True, blank=True)


class OperatorLogs(models.Model):
    operator_id = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True)
    logged_in_time = models.DateTimeField(null=True, blank=True)
    logged_out_time = models.DateTimeField(null=True, blank=True)
    shift_id = models.CharField(choices=shift, max_length=50, null=True, blank=True)


class SkillMatrix(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="%(class)s_company")
    process = models.ForeignKey(OrderProcess, on_delete=models.PROTECT, null=True, blank=True)
    operator_ids = models.CharField(max_length=4000, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)


class ManageAutoAllocation(models.Model):
    stop_start_time = models.TimeField(null=True, blank=True)
    stop_end_time = models.TimeField(null=True, blank=True)


class TechnicalHelp(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=tech_help_status, max_length=100, null=True, default="open")
    attended_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="attended_by")
    attended_on = models.DateTimeField(null=True, blank=True)


class CompareData(models.Model):
    number = models.CharField(max_length=100, null=True, blank=True)
    order_status = models.CharField(max_length=50, null=True, blank=True)
    import_from = models.CharField(max_length=50, null=True, blank=True)
    compared_on  = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.number


class PerformanceIndex(models.Model):
    years_of_experience = models.CharField(choices=years_of_experience, max_length=100, null=True)
    target_efficiency = models.IntegerField(null=True, blank=True)
    minimum_efficiency = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
