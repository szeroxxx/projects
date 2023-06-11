function compare_ordersInit(data) {
  sparrow.registerCtrl(
    "compare_ordersCtrl",
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
      var type = data.type;
      $scope.allPageTitles = {
        ec_pending: "Compare orders (EC Pending)",
        ec_inq_pending: "Compare orders (EC Inquiry Pending)",
        power_pending: "Compare orders (Power Pending)",
        imported: "Compare orders (Imported)",
        power_inq_pending: "Compare orders (Power Inquiry Pending)",
        ec_compare: "Compare orders (EC Compare)",
        power_compare: "Compare orders (Power Compare)",
      }
      var pageTitle = $scope.allPageTitles[type];
      $scope.allIndex = {
        ec_pending: 1,
        ec_inq_pending:2,
        power_pending: 3,
        power_inq_pending:4,
        imported: 5,
        ec_compare: 6,
        power_compare: 7,

      };
      $scope.tabIndex = $scope.allIndex[type];
      $scope.requestStatus = {
        ec_pending: false,
        ec_inq_pending:false,
        ec_compare: false,
        power_pending: false,
        imported: false,
        power_inq_pending: false,
        power_compare: false,


      };
      $scope.requestStatus[type] = true;
      var searchObj = {
          params: [
            { key: "customer", name: "Customer" },
            { key: "service", name: "Service" },
            { key: "customer_order_nr", name: "Order no" },
            { key: "ecc_status", name: "PWS status" },
            { key: "layer", name: "Layer" },
            { key: "pcb_name", name: "PCB name" },
            { key: "pre_due_date", name: "Preparation due date", type: "datePicker"},
            { key: "order_date", name: "Order date", type: "datePicker"},
          ],
      };
      var searchObjByOrderNr = {
          params: [
            { key: "customer_order_nr", name: "Order no" },
          ],
      };
      var columnObj =[
              {
                name: "order_date",
                title: "Order date",
                sort: false,
              },
              {
                name: "customer",
                title: "Customer",
                sort: false,
              },
              {
                name: "service",
                title: "Service",
                sort: false,
              },
              {
                name: "cus_order_no",
                title: "Number",
                sort: false,
              },
              {
                name: "ecc_status",
                title: "EC Status",
                sort: false,
              },
              {
                name: "layer",
                title: "Layer",
                sort: false,
              },
              {
                name: "pcb_name",
                title: "PCB name",
                sort: false,
              },
              {
                name: "pre_due_date",
                title: "Preparation due date",
                sort: false,
              },
          ];
      var columnObjPower =[
              {
                name: "order_date",
                title: "Order date",
                sort: false,
              },
              {
                name: "customer",
                title: "Customer",
                sort: false,
              },
              {
                name: "service",
                title: "Service",
                sort: false,
              },
              {
                name: "cus_order_no",
                title: "Number",
                sort: false,
              },
              {
                name: "ecc_status",
                title: "Power status",
                sort: false,
              },
              {
                name: "layer",
                title: "Layer",
                sort: false,
              },
              {
                name: "pcb_name",
                title: "PCB name",
                sort: false,
              },
              {
                name: "pre_due_date",
                title: "Preparation due date",
                sort: false,
              },
          ];
      var columnObjPWS =[
              {
                name: "import_order_date",
                title: "Imported on",
              },
              {
                name: "order_date",
                title: "Order date",
              },
              {
                name: "company",
                title: "Customer",
              },
              {
                name: "service",
                title: "Service",
              },
              {
                name: "customer_order_nr",
                title: "Number",
              },
              {
                name: "order_status",
                title: "PWS status",
              },
              {
                name: "layer",
                title: "Layer",
              },
              {
                name: "pcb_name",
                title: "PCB name",
              },
              {
                name: "preparation_due_date",
                title: "Preparation due date",
              },

          ];
        var columnObjCompareOrder = [
          {
            name:"cus_order_no",
            title:"Number",
          },
          {
            name:"order_status",
            title:"EC Status",
          },
          {
            name:"pws_status",
            title:"PWS status",
          },
          {
            name:"compared_on",
            title:"Compared on",
          }
        ]
        var columnObjPwCompareOrder = [
          {
            name:"cus_order_no",
            title:"Number",
          },
          {
            name:"order_status",
            title:"Power status",
          },
          {
            name:"pws_status",
            title:"PWS status",
          },
          {
            name:"compared_on",
            title:"Compared on",
          },
        ]
      var config = {
        pageTitle:pageTitle,
        topActionbar: {
          extra: [
             {
              id: "btnImportOrder",
              multiselect: true,
              function: importOrder,
            },
          ],
        },
        listing: [
          {
            index: 1,
            search:searchObjByOrderNr,
            url: "/pws/compare_orders_search/ec_pending/0/"+$scope.requestStatus["ec_pending"]+"/",
            crud: true,
            columns:columnObj,
          },
          {
            index: 2,
            search:searchObjByOrderNr,
            url: "/pws/compare_orders_search/ec_inq_pending/0/"+$scope.requestStatus["ec_inq_pending"]+"/",
            crud: true,
            columns:columnObj,
          },
          {
            index: 3,
            search:searchObjByOrderNr,
            url: "/pws/compare_orders_search/power_pending/0/"+$scope.requestStatus["power_pending"]+"/",
            crud: true,
            columns:columnObjPower,
          },
          {
            index: 4,
            search:searchObjByOrderNr,
            url: "/pws/compare_orders_search/power_inq_pending/0/"+$scope.requestStatus["power_inq_pending"]+"/",
            crud: true,
            columns:columnObjPower,
          },
          {
           index: 5,
           search:searchObj,
           url: "/pws/compare_orders_search/imported/0/"+$scope.requestStatus["imported"]+"/",
           crud: true,
           columns:columnObjPWS,
         },
          {
           index: 6,
           search:searchObjByOrderNr,
           url: "/pws/compare_orders_search/ec_compare/0/"+$scope.requestStatus["ec_compare"]+"/",
           crud: true,
           columns:columnObjCompareOrder,
         },
          {
           index: 7,
           search:searchObjByOrderNr,
           url: "/pws/compare_orders_search/power_compare/0/"+$scope.requestStatus["power_compare"]+"/",
           crud: true,
           columns:columnObjPwCompareOrder,
         },
        ],
      };
      $scope.onTabChange = function (status, index) {
        $scope.clearSelection(index);
        $scope.tabIndex = index;
        sparrow.setTitle($scope.allPageTitles[status]);

        history.replaceState(
          undefined,
          undefined,
          "#/compare_orders/?state=" + status
        );
        sparrow.pushLocationHistory(
          $route.current.originalPath,
          "#/compare_orders/?state=" + status
        );
        if ($scope.requestStatus[status] == false) {
          config.listing[index - 1].url =
            "/pws/compare_orders_search/" + status + "/0/true/";
          $scope.reloadData(index, config.listing[index - 1]);
          $scope.requestStatus[status] = true;
        }
        $scope.reloadData(index);
        btnConfiguration(status);
      };

      function btnConfiguration(status) {
        $("#btnImportOrder").show();
        if (status == "imported") {
          $("#btnImportOrder").hide();
        }
        if (status == "power_compare"|| status == "ec_compare"  ){
          $("#paraLastOrder").show();
          sparrow.post(
            "/pws/last_imported_on/",
            {"status":status},
            false,
            function(data){
              if(data.code == 1){
                document.getElementById("importedOn").innerHTML = data.data
                $(".import-btn").css("margin-left", "110px")
              }else{
                document.getElementById("importedOn").innerHTML = "No data imported yet"
                $(".import-btn").css("margin-left", "140px")
              }
            }
          )
        }
        else{
          $("#paraLastOrder").hide();
        }
      }

      function importOrder(){
        if (data.permissions['can_import_order'] == false) {
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
          return;
        }else{
          var selectedIds = $scope.getSelectedIds($scope.tabIndex)
          var rowData = $.grep(
          $scope["dtInstance"+$scope.tabIndex].DataTable.data(),
          function (n, i) {
            return selectedIds.includes(n.id);
            }
          );
          let customer_orders = []
          for (var i in rowData){
            customer_orders.push(rowData[i].cus_order_no)
          }
            if ($scope.tabIndex == 1){
              var postData = {
              order_type: "ecc",
              customer_orders:JSON.stringify(customer_orders),
            };}
            if ($scope.tabIndex == 3){
              var postData = {
              order_type: "power",
              customer_orders:JSON.stringify(customer_orders),
            };}
            if ($scope.tabIndex == 4){
              var postData = {
              order_type: "power_inq",
              customer_orders:JSON.stringify(customer_orders),
            };}
            if ($scope.tabIndex == 2){
              var postData = {
              order_type: "ec_inq_pending",
              customer_orders:JSON.stringify(customer_orders),
            };}
            if ($scope.tabIndex == 6){
              var postData = {
              order_type: "ec_compare",
              customer_orders:JSON.stringify(rowData),
            };}
            if ($scope.tabIndex == 7){
              var postData = {
              order_type: "power_compare",
              customer_orders:JSON.stringify(rowData),
            };}
            if(selectedIds.length != 0){
              sparrow.showConfirmDialog(
                      ModalService,
                      "Are you sure you want to import selected record(s)?",
                      "Confirm import record(s)",
                      function (confirm) {
                        if(confirm) {
                sparrow.post(
                  "/pws/import_order_from_ecc_and_ppm/",
                  postData,
                  false,
                  function (data) {
                    if (data.code == 1) {
                      sparrow.showMessage(
                        "appMsg",
                        sparrow.MsgType.Success,
                        data.msg,
                        10
                      );
                    }else{
                      sparrow.showMessage(
                        "appMsg",
                        sparrow.MsgType.Error,
                        data.msg,
                        10
                      );
                    }
                    $scope.reloadData($scope.tabIndex);
                  }
              )}})
            }else{
              sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
            }
        }
      }
      Mousetrap.bind('shift+i', importOrder)
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
       btnConfiguration(type);
    }
  );
}
compare_ordersInit();
