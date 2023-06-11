address_types = ((1, ("Invoice address")), (2, ("Shipping address")), (3, ("Visit address")))

product_types = ((1, ("Stockable")), (2, ("Service")), (3, ("Non-stockable")))

product_status = ((1, ("Standard")), (2, ("In Development")), (3, ("Obsolete")), (4, ("Expired")))

pasting_process = (("stencil", "Stencil"), ("jet_printer", "Jet printer"))

lifecycle = (("active", "Active"), ("obsolete", "Obsolete"), ("nrfnd", "NRND"))
inspection_rule_apply_on = (("receipt", "Receipt"), ("shipment", "Shipment"))
order_type = (
    ("draft", "Draft Sales Quotation"),
    ("quotation", "Sales Quotation"),
    ("sale", "Sale Order"),
    ("basket", "Basket"),
    ("purchase", "Purchase order"),
    ("rfqpending", "Request for quotation"),
    ("rfq", "Request for quotation"),
    ("draftrfq", "Draft Request for quotation"),
)

producers = (("eger", "Eger"), ("aachen", "Aachen"))

cost_for = (
    ("machine", "Machine"),
    ("employee", "Employee"),
    ("material", "Material"),
    ("workcenter", "Workcenter"),
)

transfer_type = (
    ("ship", "Shipment"),
    ("receipt", "Purchase receipt"),
    ("so_return", "Sale return"),
    ("purchase_return", "Purchase return"),
    ("customer_supplied", "Customer supplied"),
)

routing_operation_status = (
    ("pending", "Pending"),
    ("started", "Started"),
    ("finished", "Finished"),
    ("paused", "Paused"),
    ("ready_to_start", "Ready to start"),
    ("in_production", "In production pending"),
)

doc_type = (("general", "General"), ("invoice", "Invoice"), ("order", "Order"))

vat_status = (("standard", "Standard"), ("always_tax", "Always tax"), ("exempt", "Tax exempted"))

fin_doc_type = (("cust_inv", "Customer invoice"), ("sup_inv", "Supplier invoice"), ("cred_note", "Credit note"), ("deb_note", "Debit note"))

payment_type = (("in", "Incoming"), ("out", "Outgoing"))

capacitor_type = (("ceramic", "Ceramic"), ("tantalum", "Tantalum"), ("film", "Film"), ("electrolytic", "Electrolytic"), ("other", "Other"))

package_type = (
    ("smd", "SMD"),
    ("smd_finepitch", "SMD FinePitch"),
    ("th", "TH"),
    ("bga", "BGA"),
    ("bga_finepitch", "BGA FinePitch"),
    ("qfn", "QFN"),
    ("qfn_finepitch", "QFN FinePitch"),
    ("lga", "LGA"),
    ("lga_finepitch", "LGA FinePitch"),
    ("pressfit", "Pressfit"),
    ("finepitch", "FinePitch"),
    ("mechanical", "Mechanical"),
    ("mixed", "Mixed"),
    ("edge_mount", "Edge-Mount"),
    ("th_cut", "TH_CUT"),
    ("th_r", "TH_R"),
    ("smd_manual", "SMD Manual"),
    ("th_r_manual", "TH_R Manual"),
    ("unknown", "Unknown"),
    ("others", "Others"),
)

pcb_side = (("top", "TOP"), ("bottom", "Bottom"))

user_type = (("1", "Internal"), ("2", "Customer"))

maintenance_type = (("preventive", "Preventive"), ("corrective", "Breakdown"))

maintenance_status = (("running", "Running"), ("finished", "Finished"), ("", ""))

job_status = (
    ("pending", "Pending"),
    ("started", "Started"),
    ("on-hold", "On-hold"),
    ("completed", "Completed"),
    ("finished", "Finished"),
    ("pause", "Pause"),
    ("removed", "Removed"),
)

scheduling_type = (("forward", "Forward"), ("backward", "Backward"))

occurrence = (
    ("once", "Once"),
    ("unit", "Per PCB"),
    ("per_panel", "Per panel"),
    ("per_bom", "Per BOM"),
    ("per_cpl", "Per CPL"),
    ("per_one_pcb", "Per one PCB"),
    ("per_bom_line", "Per BOM Line"),
    ("per_gc_ec_rr_line", "Per GC/EC/RR Line"),
)

occurrence_type = (
    ("total", "Total"),
    ("smd_bga_qfn_finepitch", "SMD total"),
    ("smd", "SMD"),
    ("bga", "BGA"),
    ("qfn", "QFN"),
    ("finepitch", "Finepitch"),
    ("mixed", "Mixed"),
    ("mechanical", "Mechanical"),
    ("th", "TH"),
    ("edge_mount", "Edge-mount"),
    ("smd_manual", "SMD Manual"),
    ("th_r_manual", "TH_R Manual"),
)

occurrence_side = (
    ("both_side", "Total"),
    ("top", "TOP"),
    ("bottom", "BOT"),
)

field_type = (("text", "Text"), ("choices", "Choices"), ("bool", "Boolean"))
pricelist_type = (("general", "General"), ("customer", "Customer specific"))

pricelist_line_type = (("general", "General"), ("product_category", "Product category"), ("product", "Product"))

price_calc = (("fix_price", "Fix price"), ("percentage", "Percentage"))

purchase_status = ((1, "Sourcing"), (2, "Ordered"), (3, "Arrived"), (4, "Closed"))

mfg_order_status = (
    ("pending", "Pending"),
    ("scheduled", "Scheduled"),
    ("ready_for_prod", "Ready for production"),
    ("started", "Started"),
    ("finished", "Finished"),
    ("rework", "Rework"),
    ("cancel", "Cancel"),
    ("forwarded", "Forwarded"),
    ("on_hold", "On Hold"),
)

aachen_compatible = (("yes", "Yes"), ("no", "No"), ("not_checked", "Not checked"))

to_order_status = (("draft", "Draft"), ("partial_received", "Partial Received"), ("confirmed", "confirmed"), ("cancel", "Cancel"))

task_status = (("not_started", "Not started"), ("in_progress", "In progress"), ("completed", "Completed"))

task_priority = (("low", "Normal"), ("medium", "Warning"), ("high", "Critical"), ("urgent", "Urgent"))

deal_priority = (
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
)

deal_entity_type = (
    ("customer", "Customer"),
    ("contact", "Contact"),
)

requistion_type = (("internal", "Internal Requisition"), ("purchase", "Purchase Requisition"))

purchase_plan_type = (("offer", "Offer"), ("order", "Order"))

requisition_status = (
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("to_be_approved", "Waiting for approval"),
    ("rejected", "Rejected"),
    ("cancel", "Cancelled"),
    ("finished", "Finished"),
)

remark_type = (("normal", "Normal"), ("rejection", "Rejection"), ("customer", "Customer"), ("Cus_rema", "Customer Remarks"), ("Cum_rema", "Customer CAM Remarks"))

notification_type = (
    ("so_ship_delay", "SO shipment due"),
    ("po_ship_delay", "PO shipment due"),
    ("mo_delay", "MO due"),
    ("maintenance_delay", "Maintenance due"),
    ("comment_mension", "Mension in comment"),
    ("product_reorder", "Product reorder level"),
    ("product_review", "Product review"),
)

event_group = (
    ("sales", "Sales"),
    ("purchasing", "Purchasing"),
    # ("production", "Production"),
    ("inventory", "Inventory"),
    # ("hrm", "HRM"),
    # ("maintenances", "Maintenances"),
    # ("others", "Others"),
)

event_action = (
    ("new", "New"),
    ("confirmed", "Confirmed"),
    ("started", "Started"),
    ("completed", "Completed"),
    ("remark", "Remark"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
)

supply_type = (
    (0, "Assembler"),
    (1, "Customer"),
    (2, "Not placed"),
    (3, "Delivered/Not placed"),
)

app_label = (
    ("sales", "Sales"),
    ("purchase", "Purchase"),
    ("production", "Production"),
    ("inventory", "Inventory"),
    ("maintenances", "Maintenances"),
    ("hrm", "HRM"),
    ("eda", "EDA"),
)

leave_status = (("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"), ("cancel", "Cancelled"))

mycronic_status = (("pending", "Pending"), ("processed", "Processed"), ("failed", "Failed"))

ipc_doc_type = (
    ("eagle_fprint", "Eagle footprint"),
    ("altium_fprint", "Altium footprint"),
    ("kicad_fprint", "Kicad footprint"),
    ("fpx_fprint", "Fpx footprint"),
    ("eagle_symbol", "Eagle symbol"),
    ("altium_symbol", "Altium symbol"),
    ("kicad_symbol", "Kicad symbol"),
    ("fpx_symbol", "Fpx symbol"),
    ("3d_package", "3D package"),
)

pack_variant_type = (("nominal", "Nominal"), ("minimal", "Minimal"), ("maximal", "Maximal "))

mail_type = (("po_quote_reminder", "Purchase order quotation"),)

so_route_type = (
    ("MTO", "Make to order"),
    ("SNS", "Source and sell"),
)

approval_for_type = (("purchase_order", "Purchase order"), ("purchase_req", "Purchase requisition"), ("internal_supply_req", "Internal supply request"))

salutation = (("mr", "Mr."), ("mrs", "Mrs."), ("ms", "Ms."), ("dr", "Dr."), ("prof", "Prof."))

subscription_status = (
    ("sub", "Subscribed"),
    ("unsub", "Unsubscribed"),
)

campaign_status = (("draft", "Draft"), ("processing", "Processing"), ("sent", "Sent"))

campaign_history_status = (("pending", "Pending"), ("sent", "Sent"), ("error", "Error"))

scheduler_status = (
    ("pending", "Pending"),
    ("processing", "processing"),
)

sales_contract_status = (("pending", "Pending"), ("finish", "Finish"))

sales_contract_line_status = (("pending", "Pending"), ("finish", "Finish"))

mfg_order_type = (("claim", "Claim"), ("restart", "Restart"), ("internal_restart", "Internal restart"), ("service", "Service"))

stock_status_type = (("on_demand", "On demand"), ("ec_stock", "EC stock"), ("special", "Special"))

cost_type = {
    ("actual", "Actual"),
    ("simulate", "Simulate"),
}

customer_receipt_status = (
    ("pending", "Pending"),
    ("recevied", "Recevied"),
)

specs_status_type = (
    ("new", "New"),
    ("pending", "Pending"),
    ("in_progress", "In progress"),
    ("cross_checked", "Cross checked"),
    ("in_verification", "In verification"),
    ("finished", "Finished"),
    ("exception", "Exception"),
)

hawk_monitor_app_status = (
    ("active", "active"),
    ("inactice", "Inactive"),
)

restart_order_source = (
    ("defect_desc", "Defect description"),
    ("rejection_src", "Rejection source"),
)

delivery_format = (("Single PCB", "Single PCB"), ("Panel", "Panel"))

pcb_separation_method = (("Sep_BREAKROUTING", "Breakrouting"), ("Sep_Vcut", "V-cut"), ("No", "Not Available"))

material_tg = (
    ("tg_130-140", "130-140 ºC"),
    ("tg_145-150", "145-150 ºC"),
    ("tg_170-180", "170-180 ºC"),
    ("tg_210", "> 210 C ºC"),
    ("tg_100", "100°C"),
    ("tg_280", "280 ºC")
    )


outer_layer_copper_foil = (
    ("OLCF_12", "12 µm (end +/-30 µm)"),
    ("OLCF_18", "18 µm (end +/-35 µm)"),
    ("OLCF_35", "35 µm (end +/-60 µm)"),
    ("OLCF_70", "70 µm (end +/-95 µm)"),
    ("OLCF_105", "105 µm (end +/-130 µm)"),
    ("OLCF_0", "0"),
)

inner_layer_copper_foil = (
    ("ILCF_12", "12 µm"),
    ("ILCF_18", "18 µm"),
    ("ILCF_35", "35 µm"),
    ("ILCF_70", "70 µm"),
    ("ILCF_105", "105 µm"),
    ("ILCF_0", "0"),
)

inner_layer_core_thickness = (
    ("ILCT_STD", "Standard"),
    ("ILCT_710", "710 µm"),
    ("ILCT_508", "508 µm"),
    ("ILCT_360", "360 µm"),
    ("ILCT_254", "254 µm"),
    ("ILCT_200", "200 µm"),
    ("ILCT_100", "100 µm"),
    ("ILCT_75", "75 µm"),
    ("ILCT_50", "50 µm"),
    ("ILCT_LT_50", "< 50 micron"),
    ("ILCT_GT_100", ">=100 micron"),
    ("ILCT_GT_200", ">=200 micron"),
    ("ILCT_GT_254", ">=254 micron"),
    ("ILCT_GT_360", ">=360 micron"),
    ("ILCT_GT_50", ">=50 micron"),
    ("ILCT_GT_508", ">=508 micron"),
    ("ILCT_GT_710", ">=710 micron"),
    ("ILCT_GT_75", ">=75 micron"),
)

top_solder_mask = (
    ("Top_SM_Green", "Green"),
    ("Top_SM_Black", "Black"),
    ("Top_SM_White", "White"),
    ("Top_SM_None", "None"),
    ("Top_SM_Red", "Red"),
    ("Top_SM_Blue", "Blue"),
    ("Top_SM_Transparent", "Transparent"),
    ("Top_SM_PCBPixture", "PCB PIXture"),
    )

bottom_solder_mask = (
    ("Bot_SM_Green", "Green"),
    ("Bot_SM_Black", "Black"),
    ("Bot_SM_White", "White"),
    ("Bot_SM_None", "None"),
    ("Bot_SM_Red", "Red"),
    ("Bot_SM_Blue", "Blue"),
    ("Bot_SM_Transparent", "Transparent"),
    ("Bot_SM_PCBPixture", "PCB Pixture"),
)

top_legend = (
    ("Top_Legend_White", "White"),
    ("Top_Legend_Black", "Black"),
    ("Top_Legend_None", "None"),
    ("Top_Legend_WHPIL", "WH PIL"),
    ("Top_Legend_Yellow", "Yellow"),
    )

bottom_legend = (
    ("Bot_Legend_White", "White"),
    ("Bot_Legend_Black", "Black"),
    ("Bot_Legend_None", "None"),
    ("Bot_Legend_WHPIL", "WH PIL"),
    ("Bot_Legend_Yellow", "Yellow"),
    )

surface_finish = (
    ("SF_Any_leadfree", "Any lead-free finish"),
    ("SF_HAL", "HAL Lead-free"),
    ("SF_CheNiAu", "Che Ni/Au selective"),
    ("SF_CheNiAu_Sel", "Che Ni/Au sel. - large area"),
    ("SF_CheNiAu_bf_SM", "Che Ni/Au before soldermask"),
    ("SF_CheAg", "Che Ag"),
    ("SF_No", "No"),
    ("SF_HAL_Pb", "HAL Pb"),
    ("SF_Che_Sn", "Che Sn"),
    ("SF_CheNiAu_if", "Che Ni/Au selectif"),
    ("SF_CheNiAu_overall", "Che Ni/Au overall"),
)

peelable_mask = (
    ("Peelable_Not_Available", "Not Available"),
    ("Peelable_No", "No"),
    ("Peelable_Top", "Top"),
    ("Peelable_Bottom", "Bottom"),
    ("Peelable_Top_Bottom", "Top+Bottom"),
)
carbon_contacts = (
    ("Carbon_Not_Available", "Not Available"),
    ("Carbon_No", "No"),
    ("Carbon_Top", "Top"),
    ("Carbon_Bottom", "Bottom"),
    ("Carbon_Both", "Both")
)

edge_connector_bevelling = (
    ("Bevelling_No", "No"),
    ("Bevelling_0", "0"),
    ("Bevelling_Special", "Special"),
    ("Bevelling_STD", "Standard"),
    ("Bevelling_Spl_30", "Special 30 degrees"),
    ("Bevelling_Spl_20", "Special 20 degrees"),
    ("Bevelling_Spl_45", "Special 45 degrees"),
    ("Bevelling_Spl_60", "Special 60 degrees"),
)

top_heat_sink_paste = (("Top_HSP_No", "No"), ("Top_HSP_100", "100 µm"), ("Top_HSP_200", "200 µm"))

bottom_heat_sink_paste = (("Bot_HSP_No", "No"), ("Bot_HSP_100", "100 µm"), ("Bot_HSP_200", "200 µm"))

via_filling_hole_plugging = (
    ("Via_Fill_No", "No"),
    ("Via_Fill_Resin", "Resin"),
    ("Via_Fill_Bottom", "Bottom"),
    ("Via_Fill_Top", "Top"),
    ("Via_Fill_Soldermask", "Soldermask"),
    )

removal_nfp_allowed = (("Removal_NFP_Yes", "Yes"), ("Removal_NFP_No", "No"), ("Removal_NFP_ACP", "ACP"))

hole_plugging = (
    ("HolePlugging_Through", "Through"),
    ("HolePlugging_N/A", "N/A"),
    ("HolePlugging_Blind", "Blind"),
    ("HolePlugging_ThroughBlind", "Through+Blind"),
    ("HolePlugging_ThroughBuried", "Through+Buried"),
)
u_via_filling = (("Uviafilling_1Level", "1 Level"), ("Uviafilling_No", "No"), ("Uviafilling_2Level", "2 Level"), ("Uviafilling_3Level", "3 Level"))

fai = (("FAI_Yes", "Yes"), ("FAI_No", "No"))

venting_pattern = (("Venting_SinglePCB", "Single PCB"), ("Venting_CustPanelwasteborder", "Cust Panel waste border"), ("Venting_No", "No"), ("Venting_Both", "Both"))

engineer_1 = ( ("eng1_JOV", "JOV"), ("eng1_KIB", "KIB"), ("eng1_PHH", "PHH"), ("eng1_STB", "STB"),  ("eng1_VIC", "VIC"), ("eng1_MIS", "MST"))

engineer_2 = ( ("eng2_JOV", "JOV"), ("eng2_KIB", "KIB"), ("eng2_PHH", "PHH"), ("eng2_STB", "STB"), ("eng2_VIC", "VIC"), ("eng2_MIS", "MST"))

delivery_term = (
    ("DEL_0", "0 Working day"),
    ("DEL_1", "1 Working day"),
    ("DEL_2", "2 Working days"),
    ("DEL_3", "3 Working days"),
    ("DEL_4", "4 Working days"),
    ("DEL_5", "5 Working days"),
    ("DEL_6", "6 Working days"),
    ("DEL_7", "7 Working days"),
    ("DEL_8", "8 Working days"),
    ("DEL_9", "9 Working days"),
    ("DEL_10", "10 Working days"),
    ("DEL_12", "12 Working days"),
    ("DEL_15", "15 Working days"),
    ("DEL_20", "20 Working days"),
    ("DEL_25", "25 Working days"),
    ("DEL_30", "30 Working days"),
    ("No", "Not Available"),
)

prod_panel_size = (
    ("prod_panelSize0", "0 x 0"),
    ("prod_panelSize1", "406 x 355"),
    ("prod_panelSize2", "440 x 300"),
    ("prod_panelSize3", "457 x 305"),
    ("prod_panelSize4", "610 x 457"),
    ("prod_panelSize5", "610 x 508"),
    ("prod_panelSize6", "712 x 560"),
    ("prod_panelSize7", "762 x 610"),
    ("prod_panelSize8", "305 x 457"),
    ("prod_panelSize9", "457 x 610"),
    ("prod_panelSize10", "604 x 524"),
    ("prod_panelSize11", "624 x 524"),
    ("prod_panelSize12", "604 x 454"),
    ("prod_panelSize13", "730 x 530"),
)

due_time = (
    ("Due_time_1H", "1 Hour"),
    ("Due_time_2H", "2 Hours"),
    ("Due_time_3H", "3 Hours"),
    ("Due_time_4H", "4 Hours"),
    ("Due_time_5H", "5 Hours"),
    ("Due_time_6H", "6 Hours"),
    ("Due_time_7H", "7 Hours"),
    ("Due_time_8H", "8 Hours"),
    ("Due_time_9H", "9 Hours"),
    ("Due_time_10H", "10 Hours"),
    ("Due_time_12H", "12 Hours"),
    ("Due_time_16H", "16 Hours"),
    ("Due_time_24H", "24 Hours"),
    ("Due_time_36H", "36 Hours"),
    ("Due_time_48H", "48 Hours"),
    ("Due_time_96H", "96 Hours"),
    ("Due_time_120H", "120 Hours"),
)

exception_status = (("in_coming", "In coming"), ("put_to_customer", "Put to customer"), ("resolve", "Resolve"))
tech_help_status = (("open", "Open"), ("attend", "Attend"))

order_status = (
    ("schematic", "Schematic"),
    ("footprint", "Footprint"),
    ("placement", "Placement"),
    ("routing", "Routing"),
    ("gerber_release", "Gerber Release"),
    ("analysis", "Analysis"),
    ("incoming", "Incoming"),
    ("BOM_incoming", "BOM incoming"),
    ("SI", "SI"),
    ("SICC", "SICC"),
    ("BOM_CC", "BOM CC"),
    ("FQC", "FQC"),
    ("panel", "Panel"),
    ("upload_panel", "Upload Panel"),
    ("cancel", "Cancel"),
    ("exception", "Exception"),
    ("ppa_exception", "PPA Exception"),
    ("finished", "Order Finish"),
)


shift = (("first_shift", "First shift"), ("second_shift", "Second shift"), ("third_shift", "Third shift"), ("general_shift", "General shift"))

permanent_shift = (("first_shift", "First shift"), ("second_shift", "Second shift"), ("third_shift", "Third shift"), ("general_shift", "General shift"))

operator_group = (("GROUP_B", "Group B"), ("GROUP_FEE", "Group FEE"), ("CUSTOMER", "Customer"), ("BACKOFFICE_AND_OTH", "Backoffice and others"))

operator_type = (
    ("PLANET_ENG", "Planet engineer"),
    ("KNOWLEDGE_LEA", "Knowledge leaders"),
    ("GROUP_LEA", "Group leaders"),
    ("CUSTOMER", "Customer"),
    ("qualityapp_INCH", "qualityapp incharge"),
    ("NETWORK_ADMI", "Network administrator"),
    ("GROUP_B", "Group B"),
)

order_allocation = (
    ("pre_due_date", "Preparation due date"),
    ("delivery_date", "Delivery date"),
    ("systemin_time", "System intime"),
    ("total_minutes", "Total minutes"),
    ("order_date", "Order date"),
    ("delivery_and_order_date", "Delivery date and Order date"),
)


technical_parameter = [
    "chk_include_assembly",
    "chk_top_stencil",
    "chk_bottom_stencil",
    "cmb_pcb_separation_method",
    "cmb_board_thickness",
    "cmb_material_tg",
    "txt_buildup_code",
    "cmb_outer_layer_copper_foil",
    "cmb_inner_layer_copper_foil",
    "chk_special_buildup",
    "cmb_inner_layer_core_thickness",
    "txt_blind_buried_via_runs",
    "chk_IsImpedence",
    "cmb_top_soldermask",
    "cmb_bottom_soldermask",
    "cmb_top_legend",
    "cmb_bottom_legend",
    "cmb_surface_finish",
    "chk_bare_board_testing",
    "cmb_peelable_mask",
    "cmb_carbon_contacts",
    "chk_ul_marking",
    "chk_specific_marking",
    "chk_pth_on_the_board_edge",
    "chk_round_edge_plating",
    "chk_copper_upto_board_edge",
    "chk_press-fit_holes",
    "chk_chamfered_holes",
    "chk_depth_routing",
    "txt_edge_connector_gold_surface",
    "cmb_edge_connector_bevelling",
    "cmb_top_heatsink_paste",
    "cmb_bottom_heatsink_paste",
    "cmb_via_filling_hole_plugging",
]
customer_specific_parameter = [
    "txt_Toolnr",
    "cmb_prod_panelSize",
    "chk_is_nda",
    "chk_IsQta",
    "cmb_DueTime",
    "txt_remarks",
    "txt_ToolSpec",
    "txt_LogSpec",
    "cmb_RemovalNFPAllowed",
    "txt_ExtraCoupon",
    "cmb_HolePlugging",
    "cmb_Uviafilling",
    "cmb_FAI",
    "txt_cam_remark",
    "cmb_VentingPattern",
    "cmb_engineer1",
    "cmb_engineer2",
]

nc_type = (
    ("rejection", "Rejection"),
    ("remark", "Remark"),
    ("bad_exc", "Bad Exc "),
    ("training", "Training"),
    ("remark_internal", "Remark-internal"),
    ("not_to_count", "Not to count"),
    ("cust_mod", "Cust Mod"),
    ("update", "Update"),
)

years_of_experience = (
    ("6_month", "< 6 months"),
    ("1_year", "more than 6 and < 1 year"),
    ("2_year", "more than a year and < 2 years"),
    ("3_years", "> 2 years"),
)

layer_code_gtn = ["21L", "22L", "23L", "24L", "25L", "26L", "27L", "28L", "29L", "30L", "31L", "32L"]
