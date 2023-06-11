function orderTrackingInit(data,page_id) {
  sparrow.registerCtrl(
    "ordertrackingCtrl",
    function (
      $scope,
      $rootScope,
      $route,
      $routeParams,
      $uibModal,
      $compile,
      DTOptionsBuilder,
      DTColumnBuilder,
      $templateCache,
      ModalService
    ) {
      var config = {
        pageTitle: "Order tracking",
        topActionbar: {
          extra: [
            {
              id: "btnFiles",
              multiselect: false,
              function: onFileSearch,
            },
            {
              id: "btnOrderPriority",
              multiselect: false,
              function: showOrderPriority,
            },
            {
              id: "btnHistory",
              multiselect: false,
              function: showHistory,
            },
            {
              id: "btnExport",
              function: onExport,
            },
            {
              id: "btnAllDataExport",
              function: onAllDataExport,
            },
            {
              id: "btnModifyOrder",
              function: modifyOrder,
            },
            {
              id: "btnAcceptPreparation",
              function: acceptPreparation,
            },
          ],
        },
        listing: [
          {
            index: 1,
            search: {
              params: [
                { key: "customer_order_nr", name: "Order number" },
                { key: "layer", name: "Layers" },
                { key: "service__name", name: "Service name" },
                { key: "order_number", name: "PWS ID" },
                { key: "order_status", name: "Order status" },
                { key: "pcb_name", name: "PCB name" },
                { key: "order_date", name: "Order date", type: "datePicker" },
                { key: "finished_on", name: "Finish date", type: "datePicker" },
              ],
            },
            url: "/pws_portal/search_order_tracking/" + page_id.id + "/",
            crud: true,
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
                name: "order_status",
                title: "Order status",
              },
              {
                name: "pcb_name",
                title: "PCB name",
              },
              {
                name: "layer",
                title: "Layers",
              },
              {
                name: "service__name",
                title: "Service name",
              },
              {
                name: "order_date",
                title: "Order date",
              },
              {
                name: "created_by",
                title: "Created by",
              },
              {
                name: "finished_on",
                title: "Finish date",
              },
            ],
          },
        ],
      };


      function modifyOrder(scope) {
           if (data.permissions['can_modify_order'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 5);
                return;
            }
          else{
            var selected_id = $scope.getSelectedIds(1)[0];
            var rowData = $.grep(
              $scope["dtInstance1"].DataTable.data(),
              function (n, i) {
                return n.id == selected_id;
              }
            );
            if(rowData[0].order_status == "Cancel" || rowData[0].order_status == "Order Finish"){
              sparrow.showMessage('appMsg', sparrow.MsgType.Error, ''+ rowData[0].order_status+' stage record(s) can not be modify', 5);
                return;
            }
              var id = $scope.getSelectedIds(1)[0];
              var is_exception = "No"
              window.location.href = "#/pws_portal/modify_order/" + id + "/" + is_exception + "/";
          }
      }

      function onExport() {
        if (data.permissions["can_export_order_tracking"] == false) {
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
        var order_status = "";
        var pcb_name = "";
        var layer = "";
        var service__name = "";
        var order_date = "";
        var finished_on = "";


        if (search_parameter) {
          if ("Order number" in search_parameter) {
            var customer_order_nr = search_parameter["Order number"];
          }
          if ("PWS ID" in search_parameter) {
            var order_number = search_parameter["PWS ID"];
          }
          if ("Order status" in search_parameter) {
            var order_status = search_parameter["Order status"];
          }
          if ("PCB name" in search_parameter) {
            var pcb_name = search_parameter["PCB name"];
          }
          if ("Layers" in search_parameter) {
            var layer = search_parameter["Layers"];
          }
          if ("Service name" in search_parameter) {
            var service__name = search_parameter["Service name"];
          }
          if ("Order date" in search_parameter) {
            var order_date = search_parameter["Order date"];
          }
          if ("Finish date" in search_parameter) {
            var finished_on = search_parameter["Finish date"];
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
        sparrow.downloadData("/pws_portal/exports_order_tracking/", {
          start: $rootScope.start,
          length: $rootScope.length,
          page_id: page_id.id,
          customer_order_nr: customer_order_nr,
          order_number: order_number,
          order_status: order_status,
          pcb_name: pcb_name,
          layer: layer,
          service__name: service__name,
          order_date: order_date,
          finished_on: finished_on,
          ids: selectedIds,
          order_by: order_by_,
        });
      };

      function onAllDataExport() {
        if (data.permissions["can_export_order_tracking"] == false) {
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
        var order_status = "";
        var pcb_name = "";
        var layer = "";
        var service__name = "";
        var order_date = "";
        var finished_on = "";


        if (search_parameter) {
          if ("Order number" in search_parameter) {
            var customer_order_nr = search_parameter["Order number"];
          }
          if ("PWS ID" in search_parameter) {
            var order_number = search_parameter["PWS ID"];
          }
          if ("Order status" in search_parameter) {
            var order_status = search_parameter["Order status"];
          }
          if ("PCB name" in search_parameter) {
            var pcb_name = search_parameter["PCB name"];
          }
          if ("Layers" in search_parameter) {
            var layer = search_parameter["Layers"];
          }
          if ("Service name" in search_parameter) {
            var service__name = search_parameter["Service name"];
          }
          if ("Order date" in search_parameter) {
            var order_date = search_parameter["Order date"];
          }
          if ("Finish date" in search_parameter) {
            var finished_on = search_parameter["Finish date"];
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
        sparrow.downloadData("/pws_portal/exports_order_tracking/", {
          start: 0,
          length: display_data[0].recordsTotal,
          page_id: page_id.id,
          customer_order_nr: customer_order_nr,
          order_number: order_number,
          order_status: order_status,
          pcb_name: pcb_name,
          layer: layer,
          service__name: service__name,
          order_date: order_date,
          finished_on: finished_on,
          ids: selectedIds,
          order_by: order_by_,
        });
      }

      function showHistory(scope) {
        var selected_id = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selected_id;
          }
        );
        if(selected_id){
          window.location.hash =
            "#/auditlog/logs/order/" +
            selected_id +
            "?title=" +
            rowData[0].customer_order_nr;
        }
        else{
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 3);
        }

      }

      $("#confirmation").click(function () {
        alert("Order Completed Successfully");
      });

      function onFileSearch() {
          if (data.permissions['view_file_order_tracking'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 5);
                return;
            }
          else{
            var selectedId = $scope.getSelectedIds(1)[0];
            var rowData = $.grep(
              $scope["dtInstance1"].DataTable.data(),
              function (n, i) {
                return n.id == selectedId;
              }
            );
            if(selectedId){
                $scope.filesModelTitle = "File - " + rowData[0].customer_order_nr;
                $scope.order_number = rowData[0].customer_order_nr;
                $scope.object_id = rowData[0].id;
                $scope.app_name = "pws";
                $scope.model_name = "order_attachment";
                $scope.permission = data;

                var templateUrl = "/attachment/files/"+rowData[0].id+"/";
                var fileSearch = $uibModal.open({
                  templateUrl: templateUrl,
                  controller: "filesCtrl",
                  size: "lg",
                  scope: $scope,
                  backdrop: false,
                });
                fileSearch.closed.then(function () {
                  $templateCache.remove(templateUrl);
                });
            }
            else
            {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 3);
            }
          }
      }

       function showOrderPriority() {
          if (data.permissions['can_set_order_priority'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 5);
                return;
            }
          else{
            var selectedId = $scope.getSelectedIds(1)[0];
            var rowData = $.grep(
              $scope["dtInstance1"].DataTable.data(),
              function (n, i) {
                return n.id == selectedId;
              }
            );
            if(rowData[0]["order_status"] === "Cancel" ){
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                "Order priority cannot be set for the cancelled order.",
                3
              );
            }
            if( rowData[0]["order_status"] === "Order Finish"){
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                "Order priority cannot be set for the completed order",
                3
              );
            }
            if(rowData[0]["order_status"] != "Cancel" && rowData[0]["order_status"] != "Order Finish"){
              $("#viewPriorityTitle").text("Order priority: " + rowData[0].customer_order_nr);
              $("#orderPriority").modal("show");
            }
          }
      }

      var due_time = [
        { id: "Due_time_1H", name: "1 Hour" },
        { id: "Due_time_2H", name: "2 Hours" },
        { id: "Due_time_3H", name: "3 Hours" },
        { id: "Due_time_4H", name: "4 Hours" },
        { id: "Due_time_5H", name: "5 Hours" },
        { id: "Due_time_6H", name: "6 Hours" },
        { id: "Due_time_7H", name: "7 Hours" },
        { id: "Due_time_8H", name: "8 Hours" },
        { id: "Due_time_9H", name: "9 Hours" },
        { id: "Due_time_10H", name: "10 Hours" },
        { id: "Due_time_12H", name: "12 Hours" },
        { id: "Due_time_16H", name: "16 Hours" },
        { id: "Due_time_24H", name: "24 Hours" },
        { id: "Due_time_36H", name: "36 Hours" },
        { id: "Due_time_48H", name: "48 Hours" },
        { id: "Due_time_96H", name: "96 Hours" },
        { id: "Due_time_120H", name: "120 Hours" },
      ];
      setAutoLookup("id_due_time", due_time, "", true, false, false, null, 1);
      $scope.SetOrderPriority = function () {
        var selectedId = $scope.getSelectedIds(1)[0];
        sparrow.postForm(
          {
            id: selectedId,
          },
          $("#frmSetOrderPriority"),
          $scope,
          function(data){
            if(data.code == 1){
              $("#orderPriority").modal("hide");
              problem = $("#id_due_time").magicSuggest();
              problem.clear()

            }
            $scope.reloadData(1);
          }
        );

      };
      function viewOrderLink(data, type, full, meta) {
        return '<span><a ng-click="viewOrderDetails(' + full.id + ",'" + full.customer_order_nr + '\')">' + data + '</a></span>';
      };
      $scope.viewOrderDetails = function (id, customer_order_nr) {
        remarks_ = false
        $scope.onEditLink('/b/iframe_index/#/pws/order/' + id  + remarks_, 'Order - ' + customer_order_nr, closeIframeCallback, '', '', true);
      };
      function closeIframeCallback() {
        $scope.reloadData(1);
        return;
      };
      function acceptPreparation() {
          if (data.permissions['can_accept_preparation'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 5);
                return;
            }
          else{
              var selectedId = $scope.getSelectedIds(1)[0];
              var rowData = $.grep(
                $scope["dtInstance1"].DataTable.data(),
                function (n, i) {
                  return n.id == selectedId;
                }
              );
              document.getElementById("preparationTitle").innerHTML =  "Confirmation  - " + rowData[0]["order_number"];
              if(rowData[0]["order_status"] == "Ready for production"){
                $("#acceptPreparation").modal("show");
              }else{
                sparrow.showMessage(
                  "appMsg",
                  sparrow.MsgType.Error,
                  "Accept Preparation can be set only for Ready for Production Orders.",
                  3
                );
              }
            }
      };
      $scope.approvePreparation = function(){
        var selectedId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        sparrow.post(
          '/pws_portal/accept_preparation/0/',
          {
            id: rowData[0]["id"],
          },
          false,
          function(data){
            if(data.code == 1){
                $scope.reloadData(1);
                sparrow.showMessage(
                  "appMsg",
                  sparrow.MsgType.Success,
                  data.msg,
                  3
                );
            }
          }
      )
      $("#acceptPreparation").modal("hide");
      }
      $scope.declinePreparation = function() {
        var selectedId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
          );
          document.getElementById("declineTitle").innerHTML =  "Confirmation  - " + rowData[0]["order_number"];
          $("#moveToProduction").modal("show");
      }
      $scope.UploadUnaccepted = function() {
        var selectedId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
          );
        sparrow.postForm(
          {
            id: rowData[0]["id"],
            order_number : rowData[0]["order_number"],
          },
          $("#frmDeclinePreparation"),
          $scope,
          function (data) {
            if (data.code == 1) {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Success,
                data.msg,
                5
              );
            }
          },
          "appMsg"
        );
        $("#moveToProduction").modal("hide");
        $("#acceptPreparation").modal("hide");
        $scope.reloadData(1);
      }
      Mousetrap.bind('shift+v',function(){
          var orderId = $scope.getSelectedIds(1)[0];
          var rowData = $.grep(
              $scope["dtInstance1"].DataTable.data(),
              function (n, i) {
                return n.id == orderId;
              }
            );
          if(orderId){
              $scope.viewOrderDetails(rowData[0].id,  rowData[0].order_number)
          }
          else{
              sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
          }
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
orderTrackingInit();
