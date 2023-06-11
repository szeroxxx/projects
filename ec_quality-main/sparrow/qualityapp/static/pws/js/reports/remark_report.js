function remark_reportInit(data) {
  sparrow.registerCtrl(
    "remark_reportCtrl",
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
        pageTitle: "Remarks report",
        topActionbar: {},
        listing: [
          {
            index: 1,
            pagging: true,
            url: "/qualityapp/search_remark_report/",
            crud: false,
            scrollBody: true,
            postData: {
              start_date__date: "",
              end_date__date: "",
              company_id: "",
              remark_id: "",
            },
            columns: [
              {
                name: "id",
                title: "ID",
                class: "hide-items",
              },
              {
                name: "order_number",
                title: "qualityapp ID",
              },
              {
                name: "customer_order_nr",
                title: "Order number",
              },
              {
                name: "company__name",
                title: "Customer",
              },
              {
                name: "layer",
                title: "Layer",
                sort: false,
              },
              {
                name: "service__name",
                title: "Service",
              },
              {
                name: "remarks_type",
                title: "Remark type",
              },
              {
                name: "remark",
                title: "Remarks",
                class: "remarks",
              },
              {
                name: "remark_by",
                title: "Remark by",
              },
              {
                name: "remarks_date",
                title: "Remark added on",
              },
              {
                name: "prep_by",
                title: "prep by",
              },
              {
                name: "prep_on",
                title: "prep on",
              },
              {
                name: "prep_section",
                title: "prep section",
              },
            ],
          },
        ],
      };
      setAutoLookup("id_company", "/b/lookups/companies/", "", true);
      setAutoLookup("id_remark", "/b/lookups/remark_type/", "", false, false, false, null, 100);
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
        var remark_id_ = $("#id_remark").magicSuggest();
        var remark_id = remark_id_.getSelection();
        var remarks_list = []
        if (remark_id.length != 0){
          for (let i = 0; i < remark_id.length; i++) {
            remarks_list.push(remark_id[i]["id"]);
          }
        }
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
          start_date__date: from_date,
          end_date__date: to_date,
          company_id: company_id,
          remark_id: remarks_list,
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
        if (data.permissions["can_export_remarks_report"] == false) {
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
        sparrow.downloadData("/qualityapp/exports_remark_report/", {
          start: $rootScope.start,
          length: $rootScope.length,
          company_id: postData["company_id"],
          remark_id: postData["remark_id"],
          from: postData["start_date__date"],
          to: postData["end_date__date"],
          order_by: order_by_,
        });
      };

      $scope.onAllDataExport = function () {
        if (data.permissions["can_export_remarks_report"] == false) {
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
        sparrow.downloadData("/qualityapp/exports_remark_report/", {
          start: 0,
          length: display_data[0].recordsTotal,
          company_id: postData["company_id"],
          remark_id: postData["remark_id"],
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
remark_reportInit();
