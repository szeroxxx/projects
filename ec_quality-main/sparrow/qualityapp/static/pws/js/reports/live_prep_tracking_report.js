function live_prep_tracking_reportInit(data) {
  sparrow.registerCtrl(
    "live_prep_tracking_reportCtrl",
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
        pageTitle: "Live prep tracking report",
        topActionbar: {
          extra: [
            {
              id: "btnHistory",
              multiselect: false,
            },
            {
              id: "load_btn",
            },
          ],
        },
        listing: [
          {
            index: 1,
            search: {
              params: [
                { key: "customer_order_nr", name: "Order number" },
                { key: "order_number", name: "qualityapp id" },
                { key: "operator", name: "Operator name" },
                { key: "customer", name: "Customer" },
                { key: "service", name: "Service" },
              ],
            },
            pagging: true,
            url: "/qualityapp/search_live_prep_tracking_report/",
            crud: true,
            on_load: false,
            postData: {},
            scrollBody: true,
            columns: [
              {
                name: "order_number",
                title: "qualityapp ID",
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
                name: "resreve_time",
                title: "Reserved on",
                sort: false,
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
                name: "prep_time",
                title: "Minutes till now",
                sort: false,
              },
              {
                name: "ontime",
                title: "Ontime",
                sort: false,
              },
              {
                name: "operator",
                title: "Operator name",
              },
              {
                name: "order_status",
                title: "Order status",
              },
            ],
          },
        ],
      };
      $('#load_btn').on('click', function (event) {
            $("#btnExport").prop('disabled', false);
            $("#btnAllDataExport").prop('disabled', false);
            sparrow.global.set('SEARCH_EVENT', true);
            dtBindFunction();
            config.listing[0].postData = $scope.postData;
            $scope.reloadData(1, config.listing[0]);
        });
        function dtBindFunction() {
            var postData = {
              load_data: true,
            };
            $scope.postData = postData;
        };

      $scope.onhistory = function() {
        var selectedId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        if (selectedId) {
          $scope.onEditLink(
            "/b/iframe_index/#/auditlog/logs/order/" + rowData[0].order_id,
            "Order - " + rowData[0].customer_order_nr,
            closeIframeCallback,
            "",
            "",
            true
          );
        } else {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "please select record",
            2
          );
        }
      }
      function closeIframeCallback() {
        $scope.reloadData(1);
        return;
      }

      $scope.onExport = function(){
        if (data.permissions["can_export_live_prep_tracking_report"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        var selectedIds = $scope.getSelectedIds(1).join([(separator = ",")]);
        var search_parameter = $rootScope.searchParts;
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
        var customer_order_nr = "";
        var order_number = "";
        var operator = "";
        var customer = "";
        var service = "";


        if (search_parameter) {
          if ("Order number" in search_parameter) {
            var customer_order_nr = search_parameter["Order number"];
          }
          if ("qualityapp id" in search_parameter) {
            var order_number = search_parameter["qualityapp id"];
          }
          if ("Operator name" in search_parameter) {
            var operator = search_parameter["Operator name"];
          }
          if ("Customer" in search_parameter) {
            var customer = search_parameter["Customer"];
          }
          if ("Service" in search_parameter) {
            var service = search_parameter["Service"];
          }
        }
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

        sparrow.downloadData("/qualityapp/export_live_prep_tracking_report/", {
          start: $rootScope.start,
          length: $rootScope.length,
          order_by: order_by_,
          customer_order_nr: customer_order_nr,
          order_number: order_number,
          operator: operator,
          customer: customer,
          service: service,
          ids: selectedIds,
          display_data_list: display_data_list,
        });
      };

      $scope.onAllDataExport = function(){
        if (data.permissions["can_export_live_prep_tracking_report"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        var selectedIds = $scope.getSelectedIds(1).join([(separator = ",")]);
        var search_parameter = $rootScope.searchParts;
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id;
          }
        );
        var customer_order_nr = "";
        var order_number = "";
        var operator = "";
        var customer = "";
        var service = "";


        if (search_parameter) {
          if ("Order number" in search_parameter) {
            var customer_order_nr = search_parameter["Order number"];
          }
          if ("qualityapp id" in search_parameter) {
            var order_number = search_parameter["qualityapp id"];
          }
          if ("Operator name" in search_parameter) {
            var operator = search_parameter["Operator name"];
          }
          if ("Customer" in search_parameter) {
            var customer = search_parameter["Customer"];
          }
          if ("Service" in search_parameter) {
            var service = search_parameter["Service"];
          }
        }
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

        sparrow.downloadData("/qualityapp/export_live_prep_tracking_report/", {
          start: 0,
          length: display_data[0].recordsTotal,
          order_by: order_by_,
          customer_order_nr: customer_order_nr,
          order_number: order_number,
          operator: operator,
          customer: customer,
          service: service,
          ids: selectedIds,
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
live_prep_tracking_reportInit();
