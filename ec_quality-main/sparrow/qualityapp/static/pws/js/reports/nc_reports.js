function nc_reportsInit(data) {
  sparrow.registerCtrl(
    "nc_reportsCtrl",
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
      $scope.uid = [];
      var config = {
        pageTitle: "NC‎ Order Report",
        topActionbar: {
          extra: [
            {
              id: "btnHistory",
              multiselect: false,
            },
          ],
        },
        listing: [
          {
            index: 1,
            pagging: true,
            postData: {
              company_id: "",
              created_on: "",
              service_id: "",
              operator_id: "",
            },
            url: "/qualityapp/search_nc_reports/",
            crud: true,
            scrollBody: true,
            columns: [
              {
                name: "nc_date",
                title: "NC created on",
              },
              {
                name: "nc_number",
                title: "NC number",
                renderWith: viewNCdetail,
              },
              {
                name: "order_number",
                title: "qualityapp ID",
              },
              {
                name: "order__customer_order_nr",
                title: "Order number",
              },
              {
                name: "company__name",
                title: "Customer",
              },
              {
                name: "service_name",
                title: "Service",
              },
              {
                name: "operator",
                title: "Operator",
              },
              {
                name: "category__name",
                title: "Main category",
              },
              {
                name: "sub_category__name",
                title: "Sub category",
              },
              {
                name: "process",
                title: "Process",
              },
              {
                name: "nc_type",
                title: "NC type",
              },
              {
                name: "created_by",
                title: "NC prepared by",
              },
            ],
          },
        ],
      };
      setAutoLookup("id_company", "/b/lookups/companies/", "", false, true);
      setAutoLookup("id_service", "/lookups/services/", "", false, true);
      setAutoLookup("id_operator", "/b/lookups/operators/", "", false, true);

      function viewNCdetail(data, type, full, meta) {
        return (
          '<span><a ng-click="modifyNCDetails_(' +
          full.id +
          ",'" +
          full.nc_number +
          "')\">" +
          data +
          "</a></span>"
        );
      };

      $scope.modifyNCDetails_ = function (nc_id, nc_number) {
        $("#label").text("NC Detail - " + nc_number);
        sparrow.post(
          "/qualityapp/modify_nc/",
          {
            id: nc_id,
          },
          false,
          function (data) {
            $("#modifyNC").html(data);
            $("#modifyNCReport").modal("show");
          },
          "html"
        );
      };

      $scope.saveNCReport = function () {
        if (data.permissions["can_update_nc_report"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            5
          );
          return;
        } else {
          var $checkboxes = $('.table tr td input[type="checkbox"]');
          var countCheckedCheckboxes = $checkboxes.filter(":checked").length;
          if (countCheckedCheckboxes == 0) {
            sparrow.showMessage(
              "appMsg",
              sparrow.MsgType.Error,
              "Please select atleast one record.",
              3
            );
            return;
          }
          var id_car_file = $("#id_car_file").val();
          if (id_car_file) {
            var car_file_pdf = id_car_file.toLowerCase().endsWith(".pdf");
            var car_file_jpg = id_car_file.toLowerCase().endsWith(".jpg");
            var files_ = id_car_file.split("\\");
            if (car_file_pdf == false && car_file_jpg == false) {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                "Please upload CAR document having extension .pdf or .jpg only.",
                3
              );
              return;
            }
          }
          if ($("#id_nc_file").val() != "") {
            var id_nc_file = $("#id_nc_file").val();
            files_ = id_nc_file.split("\\");
            if (files_.slice(-1)[0].length > 170) {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                "NC document name is too long.",
                3
              );
              return;
            }
          }
          if ($("#id_car_file").val() != "") {
            var id_nc_file = $("#id_nc_file").val();
            files_ = id_nc_file.split("\\");
            if (files_.slice(-1)[0].length > 170) {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                "CAR document name is too long.",
                3
              );
              return;
            }
          }
          if ($("#frmSaveNCReport").valid() == false) {
            $("#hid_main_category").val() == undefined
              ? $("#id_main_category_message").show()
              : $("#id_main_category_message").hide();

            if ($("#hid_sub_category").val() == undefined) {
              $("#id_sub_category_message").show();
              $("#id_select_message").hide();
            }

            $("#hid_nc_create_by").val() == undefined
              ? $("#id_nc_create_by_message").show()
              : $("#id_nc_create_by_message").hide();

            $("#hid_nc_type").val() == undefined
              ? $("#id_nc_type_message").show()
              : $("#id_nc_type_message").hide();
            return;
          }

          $("#hid_main_category").val() == undefined
            ? $("#id_main_category_message").show()
            : $("#id_main_category_message").hide();

          if ($("#hid_sub_category").val() == undefined) {
            $("#id_sub_category_message").show();
            $("#id_select_message").hide();
          }

          $("#hid_nc_create_by").val() == undefined
            ? $("#id_nc_create_by_message").show()
            : $("#id_nc_create_by_message").hide();

          $("#hid_nc_type").val() == undefined
            ? $("#id_nc_type_message").show()
            : $("#id_nc_type_message").hide();

          if (
            $("#hid_nc_type").val() == undefined ||
            $("#hid_main_category").val() == undefined ||
            $("#hid_sub_category").val() == undefined ||
            $("#hid_nc_create_by").val() == undefined
          ) {
            return;
          }
          sparrow.postForm(
            {
              id: $routeParams.id,
            },
            $("#frmSaveNCReport"),
            $scope,
            function (data) {
              if (data.code == 1) {
                $("#modifyNCReport").modal("hide");
                $scope.reloadData(1);
              }
            }
          );
        }
      };

      $scope.fileDownload = function () {
        var uid = $scope.uid;
        window.open(
          "/attachment/dwn_attachment/?uid=" +
            uid +
            "&model=" +
            "order_attachment" +
            "&app=" +
            "qualityapp",
          "_blank"
        );
      };
      $("#load_btn").on("click", function () {
        sparrow.global.set("SEARCH_EVENT", true);
        dtBindFunction();
        config.listing[0].postData = $scope.postData;
        $scope.reloadData(1, config.listing[0]);
      });

      function dtBindFunction() {
        var company_id = $("#hid_company").val();
        if (company_id == undefined) {
          company_id = "";
        }
        var created_on = $("#id_date").val();
        if (created_on == undefined) {
          created_on = "";
        }
        var service_id = $("#hid_service").val();
        if (service_id == undefined) {
          service_id = "";
        }
        var operator_id = $("#hid_operator").val();
        if (operator_id == undefined) {
          operator_id = "";
        }
        var postData = {
          company_id: company_id,
          created_on: created_on,
          service_id: service_id,
          operator_id: operator_id,
        };
        $scope.postData = postData;
      }

      $("#btnExport").on("click", function () {
        if (data.permissions["can_export_nc_order_report"] == false) {
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
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id;
          }
        );
        display_data_list = []
        for(i of display_data){
          display_data_list.push(i.id)
        }
        if(display_data != ""){
          order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        sparrow.downloadData("/qualityapp/exports_nc_report/", {
          company_id: postData["company_id"],
          service_id: postData["service_id"],
          operator_id: postData["operator_id"],
          created_on: postData["created_on"],
          display_data_list: display_data_list,
          start: $rootScope.start,
          length: $rootScope.length,
          order_by: order_by_,
        });
      });

      $("#btnAllDataExport").on("click", function () {
        if (data.permissions["can_export_nc_order_report"] == false) {
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
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
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
        sparrow.downloadData("/qualityapp/exports_nc_report/", {
          company_id: postData["company_id"],
          service_id: postData["service_id"],
          operator_id: postData["operator_id"],
          created_on: postData["created_on"],
          start: 0,
          length: display_data[0].recordsTotal,
          order_by: order_by_,
        });
      });

      $scope.onNCHistory = function() {
        var selectedId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        if(selectedId){
           window.location.hash =
          "#/auditlog/logs/nonconformity/" + selectedId + "?title=" + rowData[0].nc_number;
        }
        else{
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, "please select record", 2)
        }
      };
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
nc_reportsInit();
