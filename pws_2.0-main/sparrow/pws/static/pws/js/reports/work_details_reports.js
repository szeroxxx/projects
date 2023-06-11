function work_details_reportsInit() {
    var workdetailsReport = {};
  sparrow.registerCtrl(
    "work_details_reportsCtrl",
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
        pageTitle: "Work details report",
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
            url: "/pws/search_work_details_reports/",
            paging: true,
            scrollBody: true,
            on_load: false,
            crud: true,
            postData: {
              start_date__date: "",
              end_date__date: "",
              company_id: "",
              operator_id: "",
            },
            columns: [
              {
                name: "order_number",
                title: "PWS ID",
                renderWith: viewOrderLink,
              },
              {
                name: "customer_order_nr",
                title: "Order number",
              },
              {
                name: "customer",
                title: "Customer",
              },
              {
                name: "order_date",
                title: "Order date",
              },
              {
                name: "service",
                title: "Service",
              },
              {
                name: "layer",
                title: "Layers",
              },
              {
                name: "order_from_status",
                title: "Worked section",
              },
              {
                name: "order_to_status",
                title: "Move to section",
              },
              {
                name: "preparation",
                title: "Preparation",
              },
              {
                name: "operator",
                title: "Operator name",
              },
              {
                name: "sub_group",
                title: "Sub group",
              },
              {
                name: "action_date",
                title: "Action date",
              },
              {
                name: "delivery_date",
                title: "Delivery date",
              },
              {
                name: "remarks",
                title: "Remarks",
                sort: false,
                class: "remarks",
              },
              {
                name: "prep_time",
                title: "Time taken",
              },
              {
                name: "layer_point",
                title: "User Efficiency points",
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
        if (data.permissions["can_export_work_details_report"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        dtBindFunction();
        var selectedIds = $scope.getSelectedIds(1).join([(separator = ",")]);
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id;
          }
        );
        if (!selectedIds) {
          selectedIds = "";
        }
        if(display_data != ""){
          order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        var postData = $scope.postData;
        sparrow.downloadData("/pws/work_details_reports_export/", {
          start: $rootScope.start,
          length: $rootScope.length,
          company_id: postData['company_id'],
          operator_id: postData['operator_id'],
          from: postData['start_date__date'],
          to: postData['end_date__date'],
          ids:selectedIds,
          order_by: order_by_,
        });
      };

      $scope.onAllDataExport = function () {
        if (data.permissions["can_export_work_details_report"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        dtBindFunction();
        var selectedIds = $scope.getSelectedIds(1).join([(separator = ",")]);
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id;
          }
        );
        if (!selectedIds) {
          selectedIds = "";
        }
        if(display_data != ""){
          order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        var postData = $scope.postData;
        sparrow.downloadData("/pws/work_details_reports_export/", {
          start: 0,
          length: display_data[0].recordsTotal,
          company_id: postData['company_id'],
          operator_id: postData['operator_id'],
          from: postData['start_date__date'],
          to: postData['end_date__date'],
          ids:selectedIds,
          order_by: order_by_,
        });
      };

      function viewOrderLink(data, type, full, meta) {
        return '<span><a ng-click="viewOrderDetails(' + full.order_id + ",'" + full.customer_order_nr + '\')">' + data + '</a></span>';
      };
      $scope.viewOrderDetails = function (order_id, customer_order_nr) {
        remarks_ = false
        $scope.onEditLink('/b/iframe_index/#/pws/order/' + order_id  + remarks_, 'Order - ' + customer_order_nr, closeIframeCallback, '', '', true);
      };
      function closeIframeCallback() {
        $scope.reloadData(1);
        return;
      };

      $scope.onRoleHistory = function() {
        var selectedId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        if(selectedId){
            $scope.onEditLink('/b/iframe_index/#/auditlog/logs/order/' + rowData[0].order_id , 'Order - ' + rowData[0].customer_order_nr, closeIframeCallback, '', '', true);
        }
        else{
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, "please select record", 2)
        }
      }

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
  return workdetailsReport;
}
workdetailsReport = work_details_reportsInit();