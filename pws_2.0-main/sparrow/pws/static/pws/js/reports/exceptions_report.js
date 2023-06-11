function exceptions_reportInit(data) {
  sparrow.registerCtrl(
    "exceptions_reportCtrl",
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
        pageTitle: "Exceptions report",
        topActionbar: {},
        listing: [
          {
            index: 1,
            pagging: true,
            url: "/pws/search_exceptions_report/",
            crud: false,
            scrollBody: true,
            postData: {
              start_date__date: "",
              end_date__date: "",
              company_id: "",
              exception_type_id: "",
            },
            columns: [
              {
                name: "id",
                title: "ID",
                class: "hide-items",
              },
              {
                name: "pws_id",
                title: "PWS ID",
              },
              {
                name: "order_number",
                title: "Order number",
              },
              {
                name: "operator",
                title: "Engineer",
              },
              {
                name: "put_to_customer_by",
                title: "Put to customer by",
              },
              {
                name: "put_to_customer_date",
                title: "Put to customer on",
              },
              {
                name: "send_back_by",
                title: "Send back by",
              },
              {
                name: "send_back_date",
                title: "Send back on",
              },
              {
                name: "exception_type",
                title: "Exception type",
              },
              {
                name: "customer",
                title: "Customer",
              },
              {
                name: "created_on",
                title: "Created on",
              },
            ],
          },
        ],
      };
      setAutoLookup("id_company", "/b/lookups/companies/", "", true);
      setAutoLookup(
        "id_exception_type",
        "/lookups/pre_define_problem/",
        "",
        true,
        true
      );
      $("#load_btn").on("click", function (event) {
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
        var exception_type_id = $("#hid_exception_type").val();
        if (exception_type_id == undefined) {
          exception_type_id = "";
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
          exception_type_id: exception_type_id,
          load_data: true,
        };
        $scope.postData = postData;
        $(".date_range").text(
          "From " +
            $scope.postData.start_date__date +
            " to " +
            $scope.postData.end_date__date
        );
      };

      $scope.onExport = function () {
        if (data.permissions["can_export_exceptions_report"] == false) {
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
        if (display_data != "") {
          order_by_ = display_data[0].sort_col;
        } else {
          order_by_ = "-id";
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        var postData = $scope.postData;
        sparrow.downloadData("/pws/exports_exceptions_report/", {
          start: $rootScope.start,
          length: $rootScope.length,
          company_id: postData["company_id"],
          exception_type_id: postData["exception_type_id"],
          from: postData["start_date__date"],
          to: postData["end_date__date"],
          order_by: order_by_,
        });
      };

      $scope.onAllDataExport = function () {
        if (data.permissions["can_export_exceptions_report"] == false) {
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
        if (display_data != "") {
          order_by_ = display_data[0].sort_col;
        } else {
          order_by_ = "-id";
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        var postData = $scope.postData;
        sparrow.downloadData("/pws/exports_exceptions_report/", {
          start: 0,
          length: display_data[0].recordsTotal,
          company_id: postData["company_id"],
          exception_type_id: postData["exception_type_id"],
          from: postData["start_date__date"],
          to: postData["end_date__date"],
          order_by: order_by_,
        });
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
exceptions_reportInit();
