function engineers_work_reportInit(data) {
  sparrow.registerCtrl(
    "engineers_work_reportCtrl",
    function (
      $scope,
      $rootScope,
      $route,
      $routeParams,
      $compile,
      DTOptionsBuilder,
      DTColumnBuilder,
      $templateCache,
      ModalService
    ) {
      $scope.addViewButtons("");
      $scope.reload_op = null;

      var config = {
        pageTitle: "Engineers work report",
        listing: [
          {
            index: 1,
            pagging: true,
            postData: {
              select_id: "",
              group_id: "",
              shift_id: "",
              operator_id: "",
              company_id: "",
              date: "",
            },
            crud: false,
            url: "/pws/search_engineers_work_report/",
            columns: [
              {
                name: "company__name",
                title: "Company",
              },
              {
                name: "schematic",
                title: "Schematic",
              },
              {
                name: "footprint",
                title: "Footprint",
              },
              {
                name: "placement",
                title: "Placement",
              },
              {
                name: "routing",
                title: "Routing",
              },
              {
                name: "gerber_release",
                title: "Gerber release",
              },
              {
                name: "analysis",
                title: "Analysis",
              },
              {
                name: "incoming",
                title: "Incoming",
              },
              {
                name: "BOM_incoming",
                title: "BOM incoming",
              },
              {
                name: "SI",
                title: "SI",
              },
              {
                name: "SICC",
                title: "SICC",
              },
              {
                name: "BOM_CC",
                title: "BOM CC",
              },
              {
                name: "FQC",
                title: "FQC",
              },
              {
                name: "panel",
                title: "Panel",
              },
              {
                name: "upload_panel",
                title: "Upload panel",
              },
              {
                name: "exception",
                title: "Exception",
              },
              {
                name: "total",
                title: "Total",
              },
              {
                name: "work_efficiency",
                title: "WorkEfficiency",
              },
            ],
          },
          {
            index: 2,
            pagging: true,
            postData: {
              select_id: "",
              group_id: "",
              shift_id: "",
              operator_id: "",
              company_id: "",
              date: "",
            },
            crud: false,
            url: "/pws/search_engineers_work_report/",
            columns: [
              {
                name: "operator__user__username",
                title: "Username",
              },
              {
                name: "schematic",
                title: "Schematic",
              },
              {
                name: "footprint",
                title: "Footprint",
              },
              {
                name: "placement",
                title: "Placement",
              },
              {
                name: "routing",
                title: "Routing",
              },
              {
                name: "gerber_release",
                title: "Gerber release",
              },
              {
                name: "analysis",
                title: "Analysis",
              },
              {
                name: "incoming",
                title: "Incoming",
              },
              {
                name: "BOM_incoming",
                title: "BOM incoming",
              },
              {
                name: "SI",
                title: "SI",
              },
              {
                name: "SICC",
                title: "SICC",
              },
              {
                name: "BOM_CC",
                title: "BOM CC",
              },
              {
                name: "FQC",
                title: "FQC",
              },
              {
                name: "panel",
                title: "Panel",
              },
              {
                name: "upload_panel",
                title: "Upload panel",
              },
              {
                name: "exception",
                title: "Exception",
              },
              {
                name: "total",
                title: "Total",
              },
              {
                name: "work_efficiency",
                title: "WorkEfficiency",
              },
            ],
          },
        ],
      };
      var shift = [
        { id: "first_shift", name: "First shift" },
        { id: "second_shift", name: "Second shift" },
        { id: "third_shift", name: "Third shift" },
        { id: "general_shift", name: "General shift" },
      ];
      var operator_group = [
        { id: "GROUP_B", name: "Group B" },
        { id: "GROUP_FEE", name: "Group FEE" },
        { id: "CUSTOMER", name: "Customer" },
        { id: "BACKOFFICE_AND_OTH", name: "Backoffice and others" },
      ];
      setAutoLookup("id_group", operator_group, "");
      setAutoLookup("id_shift", shift, "");
      setAutoLookup("id_operator", "/b/lookups/operators/", "", false, true);
      setAutoLookup(
        "id_company",
        "/b/lookups/order_flow_mapping_company/",
        "",
        false,
        true
      );
      setAutoLookup(
        "id_service",
        "/lookups/order_flow_mapping_service/",
        "id_company",
        false,
        true
      );
      setAutoLookup(
        "id_select",
        "/b/lookups/select/",
        "",
        true,
        false,
        false,
        null,
        1
      );
      $scope.messages = function () {
        let company_id = $("#hid_company").val();
        if (company_id == undefined) {
          $("#id_service_select_message").show();
          $("#id_service_message").hide();
          return;
        }
      };
      var company = $("#id_company").magicSuggest();
      $(company).on("selectionchange", function (e, m) {
        $("#id_service_select_message").hide();
        var service = $("#id_service").magicSuggest();
        service.clear();
        let select_id = $("#hid_select").val();
        let company_id = $("#hid_company").val();
        if (company_id == undefined) {
          company_id = "";
          service.clear();
          return;
        }
        if (company_id) {
          $("#id_company_message").hide();
        }
        if (select_id == "1") {
          loadEngineerWorkReport(company_id, select_id, null);
        }
      });

      var service = $("#id_service").magicSuggest();
      $(service).on("selectionchange", function (e, m) {
        let select_id = $("#hid_select").val();
        let service_id = $("#hid_service").val();
        if (service_id == undefined) {
          service_id = "";
        }
        let company_id = $("#hid_company").val();
        if (company_id == undefined) {
          company_id = "";
        }
        if (select_id) {
          $("#id_service_message").hide();
        }
        if (select_id == "1") {
          loadEngineerWorkReport(company_id, select_id, service_id);
        }
      });

      var select_report = $("#id_select").magicSuggest();
      $(select_report).on("selectionchange", function (e, m) {
        let select_id = $("#hid_select").val();
        if (select_id == "1") {
          $(".tabel-body-input :input").prop("disabled", false);
          $("#operator1").hide();
          $("#company1").show();
          $("#service").show();
          $("#id_saveEfficiency").prop("disabled", false);
        } else {
          $(".tabel-body-input :input").prop("disabled", true);
          $(".tabel-body-input :input").css("background-color", "white");
          $("#operator1").show();
          $("#company1").hide();
          $("#service").hide();
          $("#id_saveEfficiency").prop("disabled", true);
        }
        let company_id = $("#hid_company").val();
        if (company_id == undefined) {
          company_id = "";
        }
        let service_id = $("#hid_service").val();
        if (service_id == undefined) {
          service_id = "";
        }
        loadEngineerWorkReport(company_id, select_id, service_id);
      });
      function loadEngineerWorkReport(company_id, select_id, service_id) {
        sparrow.post(
          "/pws/engineers_work_report_process_count/",
          {
            company_id: company_id,
            select_id: select_id,
            service_id: service_id,
          },
          false,
          function (data) {
            if(data.length == 0){
              $(".tabel-body-input :input").val(0);
            }
            else{
              $("#id_schematic").val(data[0].schematic);
              $("#id_footprint").val(data[0].footprint);
              $("#id_placement").val(data[0].placement);
              $("#id_routing").val(data[0].routing);
              $("#id_gerber_release").val(data[0].gerber_release);
              $("#id_analysis").val(data[0].analysis);
              $("#id_incoming").val(data[0].incoming);
              $("#id_BOM_incoming").val(data[0].BOM_incoming);
              $("#id_SI").val(data[0].SI);
              $("#id_SICC").val(data[0].SICC);
              $("#id_BOM_CC").val(data[0].BOM_CC);
              $("#id_FQC").val(data[0].FQC);
              $("#id_panel").val(data[0].panel);
              $("#id_upload_panel").val(data[0].upload_panel);
              $("#id_schematic_ML").val(data[0].schematic_ML);
              $("#id_footprint_ML").val(data[0].footprint_ML);
              $("#id_placement_ML").val(data[0].placement_ML);
              $("#id_routing_ML").val(data[0].routing_ML);
              $("#id_gerber_release_ML").val(data[0].gerber_release_ML);
              $("#id_analysis_ML").val(data[0].analysis_ML);
              $("#id_incoming_ML").val(data[0].incoming_ML);
              $("#id_BOM_incoming_ML").val(data[0].BOM_incoming_ML);
              $("#id_SI_ML").val(data[0].SI_ML);
              $("#id_SICC_ML").val(data[0].SICC_ML);
              $("#id_BOM_CC_ML").val(data[0].BOM_CC_ML);
              $("#id_FQC_ML").val(data[0].FQC_ML);
              $("#id_panel_ML").val(data[0].panel_ML);
              $("#id_upload_panel_ML").val(data[0].upload_panel_ML);
            }
            return;
          }
        );
      }

      $("#generatereport").on("click", function () {
        if (data.permissions["can_generate_report"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            10
          );
          return;
        } else {
          $("#btnExport").prop("disabled", false);
          $("#btnAllDataExport").prop("disabled", false);
          $("#id_service_message").hide();
          $("#id_service_message").hide();
          if ($("#hid_select").val() == undefined) {
            $("#gridCon_company").hide();
            $("#gridCon_user").hide();
            $("#id_select_message").show();
          } else {
            $("#id_select_message").hide();
          }
          if ($("#hid_select").val() == "2") {
            $scope.reload_op = 1;
            $("#gridCon_user").show();
            $("#gridCon_company").hide();
          }
          if ($("#hid_select").val() == "1") {
            $scope.reload_op = 2;
            $("#gridCon_user").hide();
            $("#gridCon_company").show();
          }
          sparrow.global.set("SEARCH_EVENT", true);
          dtBindFunction();
          config.listing[$scope.reload_op - 1].postData = $scope.postData;
          $scope.reloadData(
            $scope.reload_op,
            config.listing[$scope.reload_op - 1]
          );
        }
      });

      function dtBindFunction() {
        var select_id = $("#hid_select").val();
        if (select_id == undefined) {
          select_id = "";
        }
        var shift_id = $("#hid_shift").val();
        if (shift_id == undefined) {
          shift_id = "";
        }
        var group_id = $("#hid_group").val();
        if (group_id == undefined) {
          group_id = "";
        }
        var company_id = $("#hid_company").val();
        if (company_id == undefined) {
          company_id = "";
        }
        var operator_id = $("#hid_operator").val();
        if (operator_id == undefined) {
          operator_id = "";
        }
        var date = $("#id_date").val();
        if (date == undefined) {
          date = "";
        }
        var postData = {
          select_id: select_id,
          group_id: group_id,
          shift_id: shift_id,
          operator_id: operator_id,
          company_id: company_id,
          date: date,
        };
        $scope.postData = postData;
      }

      $("#btnExport").on("click", function () {
        if (data.permissions["can_export_engineers_work_report"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        dtBindFunction();
        var postData = $scope.postData;
        if (postData['select_id'] == 1){
          dtInstance = "dtInstance2"
        }
        if (postData['select_id'] == 2){
          dtInstance = "dtInstance1"
        }
        var display_data = $.grep(
            $scope[dtInstance].DataTable.data(),
            function (n, i) {
              return n.id;
            }
            );
        if(display_data != ""){
           order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        sparrow.downloadData("/pws/exports_engineers_work_report/", {
          start: $rootScope.start,
          length: $rootScope.length,
          company_id: postData['company_id'],
          operator_id: postData['operator_id'],
          group_id: postData['group_id'],
          select_id: postData['select_id'],
          date: postData['date'],
          shift_id: postData['shift_id'],
          order_by: order_by_,
        });
      });

      $("#btnAllDataExport").on("click", function () {
        if (data.permissions["can_export_engineers_work_report"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        dtBindFunction();
        var postData = $scope.postData;
        if (postData['select_id'] == 1){
          dtInstance = "dtInstance2"
        }
        if (postData['select_id'] == 2){
          dtInstance = "dtInstance1"
        }
        var display_data = $.grep(
            $scope[dtInstance].DataTable.data(),
            function (n, i) {
              return n.id;
            }
            );
        if(display_data != ""){
           order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        sparrow.downloadData("/pws/exports_engineers_work_report/", {
          start: 0,
          length: display_data[0].recordsTotal,
          company_id: postData['company_id'],
          operator_id: postData['operator_id'],
          group_id: postData['group_id'],
          select_id: postData['select_id'],
          date: postData['date'],
          shift_id: postData['shift_id'],
          order_by: order_by_,
        });
      });

      $scope.saveEfficiency = function () {
        if (data.permissions["can_save_preptime"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        let company_id = $("#hid_company").val();
        if (company_id == undefined) {
          company_id = "";
          $("#id_company_message").show();
        }
        let service_id = $("#hid_service").val();
        if (service_id == undefined) {
          service_id = "";
          $("#id_service_message").show();
          return;
        }
        if (company_id && service_id) {
          sparrow.postForm(
            {
              company_id: company_id,
              service_id: service_id,
            },
            $("#frmSaveEngineersWorkReport"),
            $scope,
            function (data) {
              if (data.code == 1) {
                $("#mytable").trigger("reset");
              }
            }
          );
        }
      };
      Mousetrap.reset()
      Mousetrap.bind('shift+g', function(){
        document.getElementById("generatereport").click()
      })
      Mousetrap.bind('shift+x', function(){
        document.getElementById("btnExport").click()
      })
      sparrow.setup(
        $scope,
        $rootScope,
        $route,
        $compile,
        DTOptionsBuilder,
        DTColumnBuilder,
        $templateCache,
        config,
        ModalService
      );
    }
  );
}
engineers_work_reportInit();
