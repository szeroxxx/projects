function work_summary_reportsInit() {
    var worksummaryReport = {};
  sparrow.registerCtrl(
    "work_summary_reportsCtrl",
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
      var config = {
        pageTitle: "Work summary report",
        listing: [
          {
            index: 1,
            url: "/qualityapp/search_work_summary_reports/",
            paging: true,
            scrollBody: true,
            postData: {
              start_date__date: "",
              end_date__date: "",
              company_id: "",
              operator_id: "",
            },
            columns: [
              {
                name: "created_on__date",
                title: "Date",
              },
              {
                name: "operator__user__username",
                title: "Operator name",
              },
              {
                name: "company__name",
                title: "Customer",
              },
              {
                name: "layer_point",
                title: "Efficiency point",
              },
              {
                name: "order_count",
                title: "Order counts",
              },
              {
                name: "company__id",
                title: "NC count",
                sort: false,
              },
            ],
          },
        ],
      };
      setAutoLookup('id_company', '/b/lookups/companies/', '', true);
      setAutoLookup("id_operator", "/b/lookups/operators/", "", true);
        $('#load_btn').on('click', function (event) {
          $("#btnExport").prop('disabled', false);
          $("#btnAllDataExport").prop('disabled', false);
            sparrow.global.set('SEARCH_EVENT', true);
            dtBindFunction();
            config.listing[0].postData = $scope.postData;
            $scope.reloadData(1, config.listing[0]);
        });
        function dtBindFunction() {
            var company_id = $('#hid_company').val();
            var operator_id = $('#hid_operator').val()
            if(company_id == undefined){
                company_id = '';
            }
            if (operator_id == undefined) {
                operator_id = '';
            }
            var Dates = $('#dates').text();
            var from_date = '';
            var to_date = '';
            if (Dates != '') {
                var newDates = Dates.split('-');
                from_date = newDates[0].trim();
                to_date = newDates[1].trim();
            }
            var postData = {
                start_date__date: from_date,
                end_date__date: to_date,
                company_id: company_id,
                operator_id:operator_id,
                load_data:true,
            };
            $scope.postData = postData;
            $('.date_range').text('From ' + $scope.postData.start_date__date + ' to ' + $scope.postData.end_date__date);
        };

        $scope.onExport = function () {
          if (data.permissions["can_export_work_summary_report"] == false) {
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
              return n.created_on__date;
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
          var postData = $scope.postData;
          sparrow.downloadData("/qualityapp/work_summary_reports_export/", {
            start: $rootScope.start,
            length: $rootScope.length,
            company_id: postData['company_id'],
            operator_id: postData['operator_id'],
            from: postData['start_date__date'],
            to: postData['end_date__date'],
            order_by: order_by_,
          });
        };

        $scope.onAllDataExport = function () {
          if (data.permissions["can_export_work_summary_report"] == false) {
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
              return n.created_on__date;
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
          var postData = $scope.postData;
          sparrow.downloadData("/qualityapp/work_summary_reports_export/", {
            start: 0,
            length: display_data[0].recordsTotal,
            company_id: postData['company_id'],
            operator_id: postData['operator_id'],
            from: postData['start_date__date'],
            to: postData['end_date__date'],
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
  return worksummaryReport;
}
worksummaryReport = work_summary_reportsInit();