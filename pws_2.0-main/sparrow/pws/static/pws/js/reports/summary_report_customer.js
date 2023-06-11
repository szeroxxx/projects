function summaryReportCustomerInit(data) {
  sparrow.registerCtrl(
    "summaryReportCustomerCtrl",
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
        pageTitle: "Customer input/output Summary report",
        topActionbar: {},
        listing: [
          {
            index: 1,
            pagging: true,
            postData: {
              company_id: "",
              start_date__date: "",
              end_date__date: "",
            },
            crud: false,
            scrollBody: true,
            url: "/pws/search_summary_report_customer/",
            columns: [
              {
                name: "action_on__date",
                title: "Date",
              },
              {
                name: "company",
                title: "Customer",
              },
              {
                name: "received",
                title: "Orders received",
              },
              {
                name: "completed",
                title: "Orders completed",
              },
              {
                name: "exception",
                title: "Exception",
              },
              {
                name: "exception_reply",
                title: "Exception Reply",
              },
              {
                name: "operator",
                title: "No of engineers worked",
              },
              {
                name: "total_points",
                title: "Total points",
                sort: false,
              },
              {
                name: "total_time",
                title: "Total time worked on it",
              },
              {
                name: "remark_count",
                title: "Prep remark count",
                sort: false,
              },
              {
                name: "nc_report",
                title: "NC count",
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
        var Dates = $("#dates").text();
        var from_date = "";
        var to_date = "";
        if (Dates != "") {
          var newDates = Dates.split("-");
          from_date = newDates[0].trim();
          to_date = newDates[1].trim();
        }
        var postData = {
          company_id: company_id,
          start_date__date: from_date,
          end_date__date: to_date,
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
        if (data.permissions["can_export_customer_input_output_summary_report"] == false) {
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
        sparrow.downloadData("/pws/exports_summary_report_customer/", {
        start: $rootScope.start,
        length: $rootScope.length,
        company_id: postData["company_id"],
        start_date__date: postData["start_date__date"],
        end_date__date: postData["end_date__date"],
        order_by: order_by_,
        });
      });

      $("#btnAllDataExport").on("click", function () {
        if (data.permissions["can_export_customer_input_output_summary_report"] == false) {
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
        sparrow.downloadData("/pws/exports_summary_report_customer/", {
        start: 0,
        length: display_data[0].recordsTotal,
        company_id: postData["company_id"],
        start_date__date: postData["start_date__date"],
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
summaryReportCustomerInit();
