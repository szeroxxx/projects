from django.contrib import admin
from qualityapp.models import (ActiveOperators, BoardThickness, Company,
                        CompanyParameter, CompanyUser, Efficiency, Layer,
                        NcCategory, NonConformity, NonConformityDetail,
                        Operator, OperatorLogs, Order, Order_Attachment,
                        OrderAllocationFlow, OrderException, OrderFlowMapping,
                        OrderProcess, OrderScreen, OrderScreenParameter,
                        OrderTechParameter, PreDefineExceptionProblem,
                        PreDefineExceptionSolution, Service, SkillMatrix,
                        UserEfficiencyLog, ManageAutoAllocation, TechnicalHelp,
                        SubGroupOfOperator, CompareData, PerformanceIndex)

admin.site.register(Order_Attachment)
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["is_deleted", "is_active", "initials", "name"][::-1]


@admin.register(CompanyParameter)
class CompanyParameterAdmin(admin.ModelAdmin):
    list_display = ["is_checklist_pdf", "is_exp_file_attachment", "is_checklist_req", "is_smart_plate", "no_of_jobs", "is_send_attachment", "is_req_files", "is_req_multi_operator", "mail_from", "ord_comp_mail", "ord_exc_rem_mail", "ord_exc_gen_mail", "ord_rec_mail", "gen_mail", "company"][::-1]


@admin.register(OrderScreenParameter)
class OrderScreenParameterAdmin(admin.ModelAdmin):
    list_display = ["is_deleted", "parent_id", "sequence", "code", "name"][::-1]


@admin.register(OrderScreen)
class OrderScreenAdmin(admin.ModelAdmin):
    list_display = ["is_deleted", "is_compulsory", "display_ids", "default_value", "company", "order_screen_parameter"][::-1]


@admin.register(OrderProcess)
class OrderProcessAdmin(admin.ModelAdmin):
    list_display = ["sequence", "code", "name"][::-1]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["code", "name"][::-1]


@admin.register(BoardThickness)
class BoardThicknessAdmin(admin.ModelAdmin):
    list_display = ["code", "name"][::-1]


@admin.register(Layer)
class LayerAdmin(admin.ModelAdmin):
    list_display = ["code", "name"][::-1]


@admin.register(OrderFlowMapping)
class OrderFlowMappingAdmin(admin.ModelAdmin):
    list_display = ["is_deleted", "process_ids", "service", "company"][::-1]


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ["remark", "dor", "doc", "doj", "show_own_records_only", "is_deleted", "created_on", "operator_type", "operator_group", "permanent_shift", "shift", "is_active", "ec_user", "company_ids", "user"][::-1]


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ["is_deleted", "company", "user"][::-1]


@admin.register(OrderAllocationFlow)
class OrderAllocationFlowAdmin(admin.ModelAdmin):
    list_display = ["is_deleted", "created_on", "active_date", "allocation", "allocation_by", "company"][::-1]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["panel_qty", "panel_no", "in_time", "is_repeat", "is_modify", "remarks", "customer_type", "preparation_due_date", "order_previous_status", "order_next_status", "order_status", "finished_on", "act_delivery_date", "delivery_date", "import_order_date", "order_date", "operator", "user", "pcb_name", "delivery_term", "delivery_format", "layer", "service", "company", "customer_order_nr", "order_number"][::-1]



@admin.register(OrderTechParameter)
class OrderTechParameterAdmin(admin.ModelAdmin):
    list_display = ["engineer_2", "engineer_1", "venting_pattern", "cam_remark", "fai", "u_via_filling", "hole_plugging", "extra_coupon", "removal_nfp_allowed", "logistics_spec", "tool_spec", "due_time", "is_qta", "is_nda", "prod_panel_size", "tool_nr", "via_filling_hole_plugging", "bottom_heat_sink_paste", "top_heat_sink_paste", "edge_connector_bevelling", "edge_connector_gold_surface", "depth_routing", "chamfered_holes", "press_fit_holes", "copper_upto_board_edge", "round_edge_plating", "pth_on_the_board_edge", "specific_marking", "ul_marking", "carbon_contacts", "peelable_mask", "is_bare_board_testing", "surface_finish", "bottom_legend", "top_legend", "bottom_solder_mask", "top_solder_mask", "is_defined_impedance", "blind_buried_via_runs", "inner_layer_core_thickness", "is_special_buildup", "inner_layer_copper_foil", "outer_layer_copper_foil", "buildup_code", "material_tg", "board_thickness", "pcb_separation_method", "is_bottom_stencil", "is_top_stencil", "is_include_assembly", "order"][::-1]


@admin.register(Efficiency)
class EfficiencyAdmin(admin.ModelAdmin):
    list_display = ["is_deleted", "multi_layer", "layer", "process", "service", "company"][::-1]


@admin.register(NcCategory)
class NcCategoryAdmin(admin.ModelAdmin):
    list_display = ["is_deleted", "created_on", "created_by", "parent_id", "name"][::-1]


@admin.register(PreDefineExceptionProblem)
class PreDefineExceptionProblemAdmin(admin.ModelAdmin):
    list_display = ["is_problem", "is_deleted", "description", "code"][::-1]


@admin.register(PreDefineExceptionSolution)
class PreDefineExceptionSolutionAdmin(admin.ModelAdmin):
    list_display = ["is_deleted", "description", "code"][::-1]


@admin.register(OrderException)
class OrderExceptionAdmin(admin.ModelAdmin):
    list_display = ["is_si_file", "order_in_exception", "is_remark_used", "is_cancel_used", "is_modify_used", "is_confirm_used", "last_reminder_date", "total_reminder", "exp_resolve_date", "send_back_by", "send_back_date", "put_to_customer_by", "put_to_customer_date", "created_on", "created_by", "pre_define_solution", "problem_description", "pre_define_problem", "order_status", "exception_status", "order", "exception_nr"][::-1]


@admin.register(NonConformity)
class NonConformityAdmin(admin.ModelAdmin):
    list_display = ["created_by", "nc_from", "nc_date", "created_on", "solution", "problem", "root_cause", "nc_type", "order", "sub_category", "category", "company", "nc_number"][::-1]


@admin.register(NonConformityDetail)
class NonConformityDetailAdmin(admin.ModelAdmin):
    list_display = ["nc_detail_date", "process", "operator", "non_conformity"][::-1]


@admin.register(UserEfficiencyLog)
class UserEfficiencyLogAdmin(admin.ModelAdmin):
    list_display = ["target_efficiency", "minimum_efficiency", "operator_shift", "preparation", "knowledge_leaders", "service", "created_on", "total_work_efficiency", "extra_point", "order_layer", "company", "prep_time", "order_to_status", "order_from_status", "layer_point", "layer", "action_code", "order", "operator"][::-1]


@admin.register(ActiveOperators)
class ActiveOperatorsAdmin(admin.ModelAdmin):
    list_display = ["shift_id", "reserved_order_id", "logged_in_time", "operator_id"][::-1]


@admin.register(OperatorLogs)
class OperatorLogsAdmin(admin.ModelAdmin):
    list_display = ["shift_id", "logged_out_time", "logged_in_time", "operator_id"][::-1]


@admin.register(SkillMatrix)
class SkillMatrixAdmin(admin.ModelAdmin):
    list_display = ["is_deleted", "operator_ids", "process", "company"][::-1]


@admin.register(ManageAutoAllocation)
class ManageAutoAllocationAdmin(admin.ModelAdmin):
    list_display = ["stop_end_time", "stop_start_time"][::-1]


@admin.register(TechnicalHelp)
class TechnicalHelpAdmin(admin.ModelAdmin):
    list_display = ["attended_on", "attended_by", "status", "created_on", "created_by"][::-1]


@admin.register(SubGroupOfOperator)
class SubGroupOfOperatorAdmin(admin.ModelAdmin):
    list_display = ["is_deleted", "sub_group_name"][::-1]


@admin.register(CompareData)
class CompareDataAdmin(admin.ModelAdmin):
    list_display = ["compared_on", "import_from", "order_status", "number"][::-1]


@admin.register(PerformanceIndex)
class PerformanceIndexAdmin(admin.ModelAdmin):
    list_display = ["is_deleted", "minimum_efficiency", "target_efficiency", "years_of_experience"][::-1]
