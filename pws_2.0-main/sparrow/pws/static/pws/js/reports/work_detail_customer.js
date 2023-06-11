function workDetailCustomerCtrlInit(data) {
  sparrow.registerCtrl(
    "workDetailCustomerCtrl",
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
      var config = {
        pageTitle: "Customer input/output Detail report",
        topActionbar: {},
        listing: [
          {
            index: 1,
            pagging: true,
            postData: {
              start_date__date: "",
              end_date__date: "",
              company_id: "",
              operator_id: "",
            },
            crud: false,
            scrollBody: true,
            url: "/pws/search_work_detail_customer/",
            columns: [
              {
                name: "order_date",
                title: "Order date",
              },

              {
                name: "company__name",
                title: "Customer",
              },
              {
                name: "order__customer_order_nr",
                title: "Order number",
              },
              {
                name: "order__order_number",
                title: "PWS ID",
              },
              {
                name: "service__name",
                title: "Service",
              },
              {
                name: "layer",
                title: "Layer",
              },
              {
                name: "finished_on",
                title: "Completion date",
              },
              {
                name: "operator",
                title: "No of engineers worked",
              },
              {
                name: "prep_time",
                title: "Total time worked on it",
              },
              {
                name: "si_completed",
                title: "SI completed",
              },
            ],
          },
        ],
      };
      setAutoLookup("id_company", "/b/lookups/companies/", "", false, true);
      setAutoLookup("id_operator", "/b/lookups/operators/", "", false, true);

      $("#load_btn").on("click", function () {
        $("#btnExport").prop("disabled", false);
        $("#btnAllDataExport").prop("disabled", false);
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
        var operator_id = $("#hid_operator").val();
        if (operator_id == undefined) {
          operator_id = "";
        }
        var Dates = $("#dates").text();
        var from_date = "";
        var to_date = "";
        if (Dates != "") {
          var newDates = Dates.split("-");
          from_date = newDates[0].trim();
          to_date = newDates[1].trim();
        }
        var postData = {
          start_date__date: from_date,
          end_date__date: to_date,
          company_id: company_id,
          operator_id: operator_id,
          load_data: true,
        };
        $scope.postData = postData;
        $(".date_range").text(
          "From " +
            $scope.postData.start_date__date +
            " to " +
            $scope.postData.end_date__date
        );
      }

      if ($("#id_datepicker").length != 0) {
        function cb(start, end) {
          if (start != "" && end != "") {
            $("#id_datepicker span").html(
              start.format("DD/MM/YYYY") + " - " + end.format("DD/MM/YYYY")
            );
          }
        }
        var startDate = moment();
        var endDate = moment();
        $("#id_datepicker").daterangepicker(
          {
            startDate: startDate,
            endDate: endDate,
            ranges: {
              Today: [moment(), moment()],
              Yesterday: [
                moment().subtract(1, "days"),
                moment().subtract(1, "days"),
              ],
              "Last 7 Days": [moment().subtract(6, "days"), moment()],
              "Last 30 Days": [moment().subtract(29, "days"), moment()],
              "This Month": [
                moment().startOf("month"),
                moment().endOf("month"),
              ],
              "Last Month": [
                moment().subtract(1, "month").startOf("month"),
                moment().subtract(1, "month").endOf("month"),
              ],
              "This Year": [moment().startOf("year"), moment().endOf("year")],
              "Last Year": [
                moment().subtract(1, "year").startOf("year"),
                moment().subtract(1, "year").endOf("year"),
              ],
            },
          },
          cb
        );
        cb(startDate, endDate);
      }

      $("#btnExport").on("click", function () {
        if (data.permissions["can_export_customer_input_output_detail_report"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        dtBindFunction();
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id;
          }
          );

        var postData = $scope.postData;
        if(display_data != ""){
          order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        sparrow.downloadData("/pws/exports_work_detail_customer/", {
        start: $rootScope.start,
        length: $rootScope.length,
        company_id: postData["company_id"],
        start_date__date: postData["start_date__date"],
        operator_id: postData["operator_id"],
        end_date__date: postData["end_date__date"],
        order_by: order_by_,
        });
      });

      $("#btnAllDataExport").on("click", function () {
        if (data.permissions["can_export_customer_input_output_detail_report"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        dtBindFunction();
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id;
          }
          );

        var postData = $scope.postData;
        if(display_data != ""){
          order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        sparrow.downloadData("/pws/exports_work_detail_customer/", {
        start: 0,
        length: display_data[0].recordsTotal,
        company_id: postData["company_id"],
        start_date__date: postData["start_date__date"],
        operator_id: postData["operator_id"],
        end_date__date: postData["end_date__date"],
        order_by: order_by_,
        });
      });

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
workDetailCustomerCtrlInit();
