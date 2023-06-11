function exception_trackingInit(data) {
  sparrow.registerCtrl(
    "exception_trackingCtrl",
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
        pageTitle: "Exceptions",
        topActionbar: {
            extra: [
                {
                  id: "edit",
                  multiselect: false,
                  function: modifyOrder,
                },
                {
                  id: "btnFiles",
                  multiselect: false,
                  function: onFileSearch,
                },
                {
                  id: "btnHistory",
                  multiselect: false,
                  function: showLog,

                },
                {
                  id: 'btnExport',
                  function: onExport
                },
                {
                  id: "btnAllDataExport",
                  function: onAllDataExport,
                },
                {
                  id: 'btnReplyException',
                  multiselect: false,
                  function: showReplyException,
                },
                 {
                  id: 'btnCancel',
                  multiselect: false,
                  function: onCancel,
                },
            ]
        },
        listing: [
          {
            index: 1,
            search: {
              params: [
                { key: "customer_order_nr", name: "Order number" },
                { key: "layer", name: "Layers" },
                { key: "service", name: "service" },
                { key: "order_number", name: "PWS ID" },
                { key: "order_status", name: "Generate from" },
                { key: "pcb_name", name: "PCB name" },
                { key: "order_date", name: "Order date", type: "datePicker"},
                { key: "created_on", name: "Exception date", type: "datePicker"},
              ],
            },
            pagging: true,
            crud: true,
            url: "/pws_portal/exception_tracking_search/",
            columns: [
              {
                name: "order__order_number",
                title: "PWS ID",
                renderWith: viewOrderLink
              },
              {
                name: "order__customer_order_nr",
                title: "Order number",
              },
              {
                name: "order_status",
                title: "Generate from",
              },
              {
                name: "order__pcb_name",
                title: "PCB name",
              },
              {
                name: "order__layer",
                title: "Layers",
              },
              {
                name: "order__service",
                title: "Service",
              },
              {
                name: "order__order_date",
                title: "Order date",
              },
              {
                name: "created_on",
                title: "Exception date",
              },
            ],
          },
        ],
      };

      function showLog(scope) {
        var selectedId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        if(selectedId){
        window.location.hash =
          "#/auditlog/logs/order/" +
          rowData[0].order__id +
          "?title=" +
          rowData[0].order__customer_order_nr;
        }
        else{
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 3);
        }
      }


      function onExport() {
        if (data.permissions['can_export_exception_tracking'] == false) {
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
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
        var service = "";
        var order_date = "";
        var created_on = "";


        if (search_parameter) {
          if ("Order number" in search_parameter) {
            var customer_order_nr = search_parameter["Order number"];
          }
          if ("PWS ID" in search_parameter) {
            var order_number = search_parameter["PWS ID"];
          }
          if ("Generate from" in search_parameter) {
            var order_status = search_parameter["Generate from"];
          }
          if ("PCB name" in search_parameter) {
            var pcb_name = search_parameter["PCB name"];
          }
          if ("Layers" in search_parameter) {
            var layer = search_parameter["Layers"];
          }
          if ("service" in search_parameter) {
            var service = search_parameter["service"];
          }
          if ("Order date" in search_parameter) {
            var order_date = search_parameter["Order date"];
          }
          if ("Exception date" in search_parameter) {
            var created_on = search_parameter["Exception date"];
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

        sparrow.downloadData("/pws_portal/exports_exception_tracking/", {
          start: $rootScope.start,
          length: $rootScope.length,
          customer_order_nr: customer_order_nr,
          order_number: order_number,
          order_status: order_status,
          pcb_name: pcb_name,
          layer: layer,
          service: service,
          order_date: order_date,
          created_on: created_on,
          ids: selectedIds,
          order_by: order_by_,
        });
      };

      function onAllDataExport() {
        if (data.permissions['can_export_exception_tracking'] == false) {
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
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
        var service = "";
        var order_date = "";
        var created_on = "";


        if (search_parameter) {
          if ("Order number" in search_parameter) {
            var customer_order_nr = search_parameter["Order number"];
          }
          if ("PWS ID" in search_parameter) {
            var order_number = search_parameter["PWS ID"];
          }
          if ("Generate from" in search_parameter) {
            var order_status = search_parameter["Generate from"];
          }
          if ("PCB name" in search_parameter) {
            var pcb_name = search_parameter["PCB name"];
          }
          if ("Layers" in search_parameter) {
            var layer = search_parameter["Layers"];
          }
          if ("service" in search_parameter) {
            var service = search_parameter["service"];
          }
          if ("Order date" in search_parameter) {
            var order_date = search_parameter["Order date"];
          }
          if ("Exception date" in search_parameter) {
            var created_on = search_parameter["Exception date"];
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

        sparrow.downloadData("/pws_portal/exports_exception_tracking/", {
          start: 0,
          length: display_data[0].recordsTotal,
          customer_order_nr: customer_order_nr,
          order_number: order_number,
          order_status: order_status,
          pcb_name: pcb_name,
          layer: layer,
          service: service,
          order_date: order_date,
          created_on: created_on,
          ids: selectedIds,
          order_by: order_by_,
        });
      };


      function onCancel() {
          if (data.permissions['can_cancel'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
                return;
            }
          else{
              var order_exception_id = $scope.getSelectedIds(1);
              var rowData = $.grep(
                  $scope["dtInstance1"].DataTable.data(),
                  function (n, i) {
                    return n.id == order_exception_id;
                  }
              );
              sparrow.showConfirmDialog(
                  ModalService,
                  "Are you sure you want cancel order?",
                  "Cancel order",
                  function (confirm) {
                      if (confirm) {
                          sparrow.post(
                              '/pws_portal/exception_tracking_order_cancel/',
                              {
                                  order_id: rowData[0].order__id,
                                  exception_id: rowData[0].id
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
                      }
                  }
              );
          }
        }


      function showReplyException(scope){
          if (data.permissions['can_replay_exception'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
                return;
            }
          else{
              var orderExceptionId = $scope.getSelectedIds(1)[0];
              var rowData = $.grep(
              $scope["dtInstance1"].DataTable.data(),
                      function (n, i) {
                          return n.id == orderExceptionId;
                      }
                );
                $("#replyException").modal("show");
                $("#id_order_exception_id").val(orderExceptionId);
                $("#viewReplayExceptionTitle").text("Resolve Exception: " + rowData[0].order__customer_order_nr);
                $("#id_order_id").val(rowData[0].order__id);
                $("#id_order_status").val(rowData[0].order_status_code);
                setAutoLookup("id_remarks_type_back", "/lookups/remark_type/", "", true, "", "", "", 1,);
                var remarks_type_back = $('#id_remarks_type_back').magicSuggest()
                remarks_type_back.setSelection([ { name: "Exception Reply Remarks", id: 14 }, ])

          }

      }


      $scope.SaveReplyException =function(){
        var selectedId = $scope.getSelectedIds(1)[0];

         var rowData = $.grep(
            $scope["dtInstance1"].DataTable.data(),
                    function (n, i) {
                        return n.id == selectedId;
                    }
              );
          sparrow.postForm(
              {
                order_number:rowData[0].order__customer_order_nr,
                exception_date:rowData[0].created_on,
                delivery_date:rowData[0].delivery_date,
                delivery_term:rowData[0].delivery_term,
              },
              $('#frmReplyException'),
              $scope,
              function (data) {
                  if (data.code == 1) {
                      $('#replyException').modal('hide');
                      $('.modal-backdrop').remove();
                      $('#frmReplyException').trigger("reset");
                    }
                    $scope.reloadData(1);

              }
          )
        }

      function viewOrderLink(data, type, full, meta) {
        return '<span><a ng-click="viewOrderDetails(' + full.order__id + ",'" + full.order__customer_order_nr + '\')">' + data + '</a></span>';
      };
      $scope.viewOrderDetails = function (order__id, order__customer_order_nr) {
        remarks_ = false
        $scope.onEditLink('/b/iframe_index/#/pws/order/' + order__id  + remarks_, 'Order - ' + order__customer_order_nr, closeIframeCallback, '', '', true);
      };
      function closeIframeCallback() {
        $scope.reloadData(1);
        return;
      };

      function onFileSearch() {
          if (data.permissions['can_exception_tracking_files'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
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
                  $scope.filesModelTitle = "File - " + rowData[0].order__customer_order_nr;
                  $scope.order_number = rowData[0].order__customer_order_nr;
                  $scope.object_id = rowData[0].order__id;
                  $scope.app_name = "pws";
                  $scope.model_name = "order_attachment";
                  $scope.permission = data;  //for add new permission in files.js


                  var templateUrl = "/attachment/files/"+rowData[0].order__id+"/";
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
              else{
                 sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 3);
              }
        }
      };

      function modifyOrder(scope) {
        if (data.permissions['can_modify_exception_order'] == false) {
             sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 5);
             return;
         }
       else{
        var id = $scope.getSelectedIds(1)[0];
        var selectedId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
            $scope["dtInstance1"].DataTable.data(),
                    function (n, i) {
                        return n.id == selectedId;
                    }
              );
        var is_exception = "Yes"
        window.location.href = "#/pws_portal/modify_order/" + rowData[0].order__id + "/" + is_exception + "/";
       }
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
              $scope.viewOrderDetails(rowData[0].order__id,  rowData[0].order__order_number)
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
exception_trackingInit();
