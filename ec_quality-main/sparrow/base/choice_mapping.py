pcb_separation_method = {"Breakrouting":"Sep_BREAKROUTING","V-cut":"Sep_Vcut","Not Available":"No","No":"No",}

material_tg = {
    "130-140 C" : "tg_130-140",
    "145-150°C" : "tg_145-150",
    "170-180 C" : "tg_170-180",
    "> 210 C" : "tg_210",
    "100°C" : "tg_100",
    "280" : "tg_280",
}

outer_layer_copper_foil = {
    "0" : "OLCF_0",
    "12 micron" : "OLCF_12",
    "12µm" : "OLCF_12",
    "12µm(End-Cu +/-30µm)" : "OLCF_12",
    "18 micron " : "OLCF_18",
    "18µm" : "OLCF_18",
    "18µm(End-Cu +/-35µm)" : "OLCF_18",
    "35 micron" : "OLCF_35",
    "35µm" : "OLCF_35",
    "35µm (End-Cu +/-60µm)" : "OLCF_35",
    "35µm(End-Cu +/-60µm)" : "OLCF_35",
    "70 micron" : "OLCF_70",
    "70µm" : "OLCF_70",
    "70µm (End-Cu +/-95µm" : "OLCF_70",
    "70µm(End-Cu +/-95µm)" : "OLCF_70",
    "105µm" : "OLCF_105",
    "105µm(End-Cu+/-130µm" : "OLCF_105",
    "105 micron" : "OLCF_105",
}

inner_layer_copper_foil = {
    "0" : "ILCF_0",
    "12 micron" : "ILCF_12",
    "12µm" : "ILCF_12",
    "18 micron " : "ILCF_18",
    "18 micron" : "ILCF_18",
    "18µm" : "ILCF_18",
    "35 micron" : "ILCF_35",
    "35µm" : "ILCF_35",
    "70 micron" : "ILCF_70",
    "70µm" : "ILCF_70",
    "105 micron " : "ILCF_105",
    "105µm" : "ILCF_105",
    "105 micron" : "ILCF_105",
}

top_solder_mask = {
    "Green" : "Top_SM_Green",
    "Black" : "Top_SM_Black",
    "White" : "Top_SM_White",
    "No" : "Top_SM_None",
    "Red" : "Top_SM_Red",
    "Blue" : "Top_SM_Blue",
    "Transparent" : "Top_SM_Transparent",
    "PCB PIXture" : "Top_SM_PCBPixture",
}

bottom_solder_mask = {
    "Green" : "Bot_SM_Green",
    "Black" : "Bot_SM_Black",
    "White" : "Bot_SM_White",
    "No" : "Bot_SM_None",
    "Red" : "Bot_SM_Red",
    "Blue" : "Bot_SM_Blue",
    "Transparent" : "Bot_SM_Transparent",
    "PCB PIXture" : "Bot_SM_PCBPixture",
}

top_legend = {
    "White" : "Top_Legend_White",
    "Black" : "Top_Legend_Black",
    "No" : "Top_Legend_None",
    "WH PIL" : "Top_Legend_WHPIL",
    "Yellow" : "Top_Legend_Yellow",
}

bottom_legend = {
    "White" : "Bot_Legend_White",
    "Black" : "Bot_Legend_Black",
    "No" : "Bot_Legend_None",
    "WH PIL" : "Bot_Legend_WHPIL",
    "Yellow" : "Bot_Legend_Yellow",
}

surface_finish = {
    "Any lead-free finish" : "SF_Any_leadfree",
    "Any lead free finish" : "SF_Any_leadfree",
    "HAL Lead-free" : "SF_HAL",
    "Che Ni/Au selective" : "SF_CheNiAu",
    "Che Ni/Au sel. - large area" : "SF_CheNiAu_Se,l",
    "Che Ni/Au before soldermask" : "SF_CheNiAu_bf_SM",
    "Che Ag" : "SF_CheAg",
    "No" : "SF_No",
    "HAL Pb" : "SF_HAL_Pb",
    "Che Sn" : "SF_Che_Sn",
    "Che Ni/Au selectif" : "SF_CheNiAu_if",
    "Che Ni/Au overall" : "SF_CheNiAu_overall",
}

peelable_mask = {
    "No" : "Peelable_No",
    "Not Available" : "Peelable_Not_Available",
    "Top" : "Peelable_Top",
    "Bottom" : "Peelable_Bottom",
    "Top+Bottom" : "Peelable_Top_Bottom",
}

carbon_contacts = {
    "Not Available" : "Carbon_Not_Available",
    "No" : "Carbon_No",
    "Top" : "Carbon_Top",
    "Bottom" : "Carbon_Bottom",
    "Both" : "Carbon_Both",
    "Top+Bottom" : "Carbon_Both",
}

top_heat_sink_paste = {
    "No" : "Top_HSP_No",
    "100 µm" : "Top_HSP_100",
    "100 micron " : "Top_HSP_100",
    "100 micron" : "Top_HSP_100",
    "200 µm" : "Top_HSP_200",
    "200 micron" : "Top_HSP_200",
}

bottom_heat_sink_paste = {
    "No" : "Bot_HSP_No",
    "100 µm" : "Bot_HSP_100",
    "100 micron " : "Bot_HSP_100",
    "100 micron" : "Bot_HSP_100",
    "200 µm" : "Bot_HSP_200",
    "200 micron" : "Bot_HSP_200",
}

via_filling_hole_plugging = {
    "No" : "Via_Fill_No",
    "Resin" : "Via_Fill_Resin",
    "Bottom" : "Via_Fill_Bottom",
    "Top" : "Via_Fill_Top",
    "Soldermask" : "Via_Fill_Soldermask",
}

edge_connector_bevelling = {
    "No" : "Bevelling_No",
    "0" : "Bevelling_0",
    "Special" : "Bevelling_Special",
    "Standard" : "Bevelling_STD",
    "Special 30 degrees" : "Bevelling_Spl_30",
    "Special 20 degrees" : "Bevelling_Spl_20",
    "Special 45 degrees" : "Bevelling_Spl_45",
    "Special 60 degrees" : "Bevelling_Spl_60",
}

delivery_format = {False:"Single PCB",True:"Panel"}

inner_layer_core_thickness = {
    "Standard" : "ILCT_STD",
    ">=710 micron" : "ILCT_GT_710",
    "710 µm" : "ILCT_GT_710",
    ">=508 micron" : "ILCT_GT_508",
    "508 µm" : "ILCT_508",
    "360 µm" : "ILCT_360",
    ">=360 micron" : "ILCT_GT_360",
    "254 µm" : "ILCT_254",
    ">=254 micron" : "ILCT_GT_254",
    "200 µm" : "ILCT_200",
    ">=200 micron" : "ILCT_GT_200",
    "100 µm" : "ILCT_100",
    ">=100 micron" : "ILCT_GT_100",
    "75 µm" : "ILCT_75",
    ">=75 micron" : "ILCT_GT_75",
    "50 µm" : "ILCT_50",
    "< 50 micron" : "ILCT_LT_50",
    ">=50 micron" : "ILCT_GT_50",
}


delivery_term = {
    "0 Working day":"DEL_0",
    "1 Working day":"DEL_1",
    "2 Working days":"DEL_2",
    "3 Working days":"DEL_3",
    "4 Working days":"DEL_4",
    "5 Working days":"DEL_5",
    "6 Working days":"DEL_6",
    "7 Working days":"DEL_7",
    "8 Working days":"DEL_8",
    "9 Working days":"DEL_9",
    "10 Working days":"DEL_10",
    "12 Working days":"DEL_12",
    "15 Working days":"DEL_15",
    "20 Working days":"DEL_20",
    "25 Working days":"DEL_25",
    "30 Working days":"DEL_30",
    "Not Available":"No",
}