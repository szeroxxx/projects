function productionsInit(data) {
  sparrow.registerCtrl(
    "productionsCtrl",
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
      var customer = { key: "customer", name: "Customer" };
      company_search = sparrow.getStorage("company_search");
      if (company_search) {
        customer = { key: "customer", name: "Customer", default_val: company_search };
        sparrow.removeStorage("company_search");
      }
      var type = data.type;
      $scope.allPageTitles = {
            panel: 'Panel Preparation (Panel)',
            upload_panel: 'Panel Preparation (Upload panel)',

        };
      var pageTitle = $scope.allPageTitles[type];
      $scope.allIndex = {
            panel: 1,
            upload_panel: 2,
        };
        $scope.tabIndex = $scope.allIndex[type];
        $scope.requestStatus = {
            panel: false,
            upload_panel: false,
        };
        $scope.requestStatus[type] = true;
        var searchObj = {
            params: [
              { key: "customer_order_nr", name: "Order number" },
              { key: "operator", name: "Engineer" },
              { key: "layer", name: "PCB type" },
              customer,
              { key: "service", name: "Service" },
              { key: "order_number", name: "qualityapp ID" },
              { key: "pcb_name", name: "PCB name" },
              { key: "order_date", name: "Order in date", type:"datePicker"},
            ],
        };
        var columnObjUploadPanel = [
          {
            name: "order_number",
            title: "qualityapp ID",
            renderWith: viewOrderLink,
          },
          {
            name: "customer_order_nr",
            title: "Order number",
          },
          {
            name: "order_date",
            title: "Order date",
          },
          {
            name: "in_time",
            title: "In time",
          },
          {
            name: "pcb_name",
            title: "PCB name",
          },
          {
            name: "tool_nr",
            title: "Tool nr",
          },
          {
            name: "panel_no",
            title: "Panel number",
          },
          {
            name: "panel_qty",
            title: "Panel quantity",
          },
          {
            name: "layer",
            title: "PCB type",
          },
          {
            name: "customer",
            title: "Customer",
          },
          {
            name: "remarks",
            title: "Remarks",
            renderWith: viewRemarkLink,
            class: "remarks",
            sort: false,
          },
          {
            name: "board_thickness",
            title: "Board thickness",
          },
          {
            name: "material_tg",
            title: "Material tg",
          },
          {
            name: "service",
            title: "Service",
          },
          {
            name: "operator",
            title: "Engineer",
          },
          {
            name: "bottom_solder_mask",
            title: "Soldermask bottom",
          },
          {
            name: "top_solder_mask",
            title: "Soldermask top",
          },
          {
            name: "top_legend",
            title: "Legend top",
          },
          {
            name: "bottom_legend",
            title: "Legend bottom",
          },
          {
            name: "surface_finish",
            title: "Surface finish",
          },
          {
            name: "order_next_status",
            title: "Next stage",
          },
          {
            name: "order_previous_status",
            title: "Previous stage",
          },
        ];
        var columnObjPanel = [
          {
            name: "order_number",
            title: "qualityapp ID",
            renderWith: viewOrderLink,
          },
          {
            name: "customer_order_nr",
            title: "Order number",
          },
          {
            name: "order_date",
            title: "Order date",
          },
          {
            name: "in_time",
            title: "In time",
          },
          {
            name: "pcb_name",
            title: "PCB name",
          },
          {
            name: "tool_nr",
            title: "Tool nr",
          },
          {
            name: "layer",
            title: "PCB type",
          },
          {
            name: "customer",
            title: "Customer",
          },
          {
            name: "remarks",
            title: "Remarks",
            renderWith: viewRemarkLink,
            class: "remarks",
            sort: false,
          },
          {
            name: "board_thickness",
            title: "Board thickness",
          },
          {
            name: "material_tg",
            title: "Material tg",
          },
          {
            name: "service",
            title: "Service",
          },
          {
            name: "operator",
            title: "Engineer",
          },
          {
            name: "bottom_solder_mask",
            title: "Soldermask bottom",
          },
          {
            name: "top_solder_mask",
            title: "Soldermask top",
          },
          {
            name: "top_legend",
            title: "Legend top",
          },
          {
            name: "bottom_legend",
            title: "Legend bottom",
          },
          {
            name: "surface_finish",
            title: "Surface finish",
          },
          {
            name: "order_next_status",
            title: "Next stage",
          },
          {
            name: "order_previous_status",
            title: "Previous stage",
          },
        ];
        var config = {
          pageTitle: pageTitle,
          topActionbar: {
            extra: [
              {
                id: "btnFiles",
                multiselect: false,
                function: onFileSearch,
              },
              {
                id: "btnReserve",
                multiselect: true,
                function: OnReserve,
              },
              {
                id: "btnRelease",
                multiselect: true,
                function: OnRelease,
              },
              {
                id: "btnReserveSendtonextPanel",
                function: onReserveSendtonextPanel,
              },
              {
                id: "btnSendtonext",
                function: onSendtonext,
              },
              {
                id: "btnBackToprevious",
                function: onBackToprevious,
              },
              {
                id: "btnGenerateException",
                multiselect: false,
                function: showGenerateException,
              },
              {
                id: "btnHistory",
                multiselect: false,
                function: showLog,
              },
              {
                id: "btnExport",
                function: onExport,
              },
              {
                id: "btnAllDataExport",
                function: onAllDataExport,
              },
            ],
          },
          listing: [
            {
              index: 1,
              search: searchObj,
              url:
                "/qualityapp/workspace_search/panel/0/" +
                $scope.requestStatus["panel"] +
                "/",
              crud: true,
              scrollBody: true,
              columns: columnObjPanel,
            },
            {
              index: 2,
              search: searchObj,
              url:
                "/qualityapp/workspace_search/upload_panel/0/" +
                $scope.requestStatus["upload_panel"] +
                "/",
              crud: true,
              scrollBody: true,
              columns: columnObjUploadPanel,
            },
          ],
        };

        var exports_cus = Array()
        function onExport() {
          if (data.permissions["can_export_job_processing_panel_preparation"] == false) {
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "You do not have permission to perform this action", 3);
            return;
          }
          var selectedIds = $scope.getSelectedIds($scope.tabIndex).join([(separator = ",")]);
          var search_parameter = $rootScope.searchParts;
          var display_data = $.grep(
            $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
            function (n, i) {
              return n.id;
            }
          );
          var order_number = "";
          var customer_order_nr = "";
          var operator = "";
          var pcb_name = "";
          var layer = "";
          var customer = "";
          var service = "";
          var order_date = "";
          if (search_parameter) {
            exports_cus = [];
            if ("qualityapp ID" in search_parameter) {
              var order_number = search_parameter["qualityapp ID"];
            }
            if ("Order number" in search_parameter) {
              var customer_order_nr = search_parameter["Order number"];
            }
            if ("Engineer" in search_parameter) {
              var operator = search_parameter["Engineer"];
            }
            if (" PCB name" in search_parameter) {
              var pcb_name = search_parameter[" PCB name"];
            }
            if ("PCB type" in search_parameter) {
              var layer = search_parameter["PCB type"];
            }
            if ("Customer" in search_parameter) {
              var customer = search_parameter["Customer"];
            } else {
              if (exports_cus.length == 1 || exports_cus.length == 0) {
                customer = company_search;
                sparrow.removeStorage("company_search");
              }
            }
            if ("Service" in search_parameter) {
              var service = search_parameter["Service"];
            }
            if ("Order in date" in search_parameter) {
              var order_date = search_parameter["Order in date"];
            }
          }
          if (!selectedIds) {
            selectedIds = "";
          }
          if (company_search && !search_parameter) {
            exports_cus.push(company_search);
            sparrow.removeStorage("company_search");
          }
          if (exports_cus.length == 1 && !search_parameter) {
            customer = company_search;
            sparrow.removeStorage("company_search");
          }
          if(display_data != ""){
            order_by_ = display_data[0].sort_col
            order_status = display_data[0].order_status
          }
          else{
            order_by_ = "-id"
            order_status = " "
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
            return
          }

          sparrow.downloadData("/qualityapp/exports_job_processing_/", {
            start: $rootScope.start,
            length: $rootScope.length,
            status: order_status,
            order_number: order_number,
            customer_order_nr: customer_order_nr,
            operator: operator,
            pcb_name: pcb_name,
            layer: layer,
            customer: customer,
            service: service,
            order_date: order_date,
            ids: selectedIds,
            order_by: order_by_,
          });
        };

        var exports_cus = Array()
        function onAllDataExport() {
          if (data.permissions["can_export_job_processing_panel_preparation"] == false) {
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "You do not have permission to perform this action", 3);
            return;
          }
          var selectedIds = $scope.getSelectedIds($scope.tabIndex).join([(separator = ",")]);
          var search_parameter = $rootScope.searchParts;
          var display_data = $.grep(
            $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
            function (n, i) {
              return n.id;
            }
          );
          var order_number = "";
          var customer_order_nr = "";
          var operator = "";
          var pcb_name = "";
          var layer = "";
          var customer = "";
          var service = "";
          var order_date = "";
          if (search_parameter) {
            exports_cus = [];
            if ("qualityapp ID" in search_parameter) {
              var order_number = search_parameter["qualityapp ID"];
            }
            if ("Order number" in search_parameter) {
              var customer_order_nr = search_parameter["Order number"];
            }
            if ("Engineer" in search_parameter) {
              var operator = search_parameter["Engineer"];
            }
            if (" PCB name" in search_parameter) {
              var pcb_name = search_parameter[" PCB name"];
            }
            if ("PCB type" in search_parameter) {
              var layer = search_parameter["PCB type"];
            }
            if ("Customer" in search_parameter) {
              var customer = search_parameter["Customer"];
            } else {
              if (exports_cus.length == 1 || exports_cus.length == 0) {
                customer = company_search;
                sparrow.removeStorage("company_search");
              }
            }
            if ("Service" in search_parameter) {
              var service = search_parameter["Service"];
            }
            if ("Order in date" in search_parameter) {
              var order_date = search_parameter["Order in date"];
            }
          }
          if (!selectedIds) {
            selectedIds = "";
          }
          if (company_search && !search_parameter) {
            exports_cus.push(company_search);
            sparrow.removeStorage("company_search");
          }
          if (exports_cus.length == 1 && !search_parameter) {
            customer = company_search;
            sparrow.removeStorage("company_search");
          }
          if(display_data != ""){
            order_by_ = display_data[0].sort_col
            order_status = display_data[0].order_status
            length = display_data[0].recordsTotal
          }
          else{
            order_by_ = "-id"
            order_status = " "
            length = 1
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
            return
          }

          sparrow.downloadData("/qualityapp/exports_job_processing_/", {
            start: 0,
            length: length,
            status: order_status,
            order_number: order_number,
            customer_order_nr: customer_order_nr,
            operator: operator,
            pcb_name: pcb_name,
            layer: layer,
            customer: customer,
            service: service,
            order_date: order_date,
            ids: selectedIds,
            order_by: order_by_,
          });
        };

        $scope.status = type;
        $scope.onTabChange = function (status, index) {
            $scope.clearSelection(index);
            $scope.tabIndex = index;
            $scope.status = status;
            sparrow.setTitle($scope.allPageTitles[status]);
            history.replaceState(undefined, undefined, '#/job_processing/panel_preparation/?state=' + status);
            sparrow.pushLocationHistory($route.current.originalPath, '#/job_processing/panel_preparation/?state=' + status);
            if ($scope.requestStatus[status] == false) {
              config.listing[index - 1].url = '/qualityapp/workspace_search/' + status + '/0/true/';
              $scope.reloadData(index, config.listing[index - 1]);
              $scope.requestStatus[status] = true;
            }
            $scope.reloadData(index);
            btnConfiguration(status);

        };

        function btnConfiguration(status) {
            if (status == 'upload_panel') {
                $('#btnCreateException').hide();
                $('#btnGenerateException').hide();
                $('#btnReserveSendtonextPanel').hide();
                $('#btnReserve').hide();
                $('#btnRelease').hide();
            }
            else if (status == 'panel') {
                $('#btnCreateException').show();
                $('#btnGenerateException').show();
                $('#btnReserveSendtonextPanel').show();
                $('#btnReserve').show();
                $('#btnRelease').show();
            }
        }

        function viewOrderLink(data, type, full, meta) {
          return '<span><a ng-click="viewOrderDetails(' + full.id + "," + false + ",'" + full.customer_order_nr + '\')">' + data + '</a></span>';
        };
        function viewRemarkLink(data, type, full, meta) {
          return '<span><a ng-click="viewOrderDetails(' + full.id + "," + true + ",'" + full.customer_order_nr + '\')">' + data + '</a></span>';
        };
        $scope.viewOrderDetails = function (id, remarks_, customer_order_nr) {
          $scope.onEditLink('/b/iframe_index/#/qualityapp/order/' + id  + remarks_ , 'Order - ' + customer_order_nr, closeIframeCallback, '', '', true);
        };
        function closeIframeCallback() {
          $scope.reloadData($scope.tabIndex);
          return;
        };

        $scope.ReserveorderList = [];
        function OnReserve() {
          $scope.ReserveorderList = [];
            if (data.permissions['reserve_order_production'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
                return;
            }
            var selectedId = $scope.getSelectedIds($scope.tabIndex);
            if(selectedId.length == 0){
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
                return;
            }
            if (selectedId.length == 1){
              var rowData = $.grep(
                $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
                function (n, i) {
                  return n.id == selectedId[0];
                }
              );
              if(rowData[0].operator != null){
                sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "Order has already operator reserved.", 3);
                return;
              }
            }
            for (let index = 0; index < selectedId.length; index++) {
              var rowData = $.grep(
                $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
                function (n, i) {
                  return n.id == selectedId[index];
                }
              );
              $scope.ReserveorderList.push("&nbsp;" + rowData[0].customer_order_nr);
            }
            if ($scope.ReserveorderList.length != 1){
              var confirm_dialog = "Are you sure you want to reserve operator for these selected jobs? " + $scope.ReserveorderList + "</br></br> On 'Yes' click, already reserved operator(s) will be replaced with new one, click 'No' to abort."
              sparrow.showConfirmDialog(ModalService, confirm_dialog, "Reserve operator",
                function (confirm) {
                  if (confirm) {
                    $("#viewReserveTitle").text("Reserve operator");
                    $("#viewReserveModel").modal("show");
                  }
                }
              );
            }
            else{
              $("#viewReserveTitle").text("Reserve operator");
              $("#viewReserveModel").modal("show");
            }

        };

        $scope.saveReserve = function () {
        var order_id = $scope.getSelectedIds($scope.tabIndex);
        var operator_ids = $("#id_operator").magicSuggest();
        sparrow.postForm(
            {
            order_id: order_id,
            },
            $("#frmSaveReserve"),
            $scope,
            function (data) {
            if (data.code == 1) {
                operator_ids.clear()
                $("#viewReserveModel").modal("hide");
                $scope.reloadData($scope.tabIndex);
                if (order_id.length == 1){
                  setTimeout(function () {
                    $("#chk_" + $scope.tabIndex + "_" + order_id[0]).trigger("click").prop("checked", true);
                  }, 100);
                }
                return;
            }
            }
            );
        };

        $scope.closeReserveModel = function(){
            var operator_ids = $("#id_operator").magicSuggest();
            operator_ids.clear()
            $("#viewReserveModel").modal("hide");
            $('.modal-backdrop').remove();
        };

        function OnRelease() {
            if (data.permissions['release_order_production'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
                return;
            }
            var selectedId = $scope.getSelectedIds($scope.tabIndex);
            if(selectedId.length == 0){
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 3);
                return;
            }
            if (selectedId.length == 1){
              var rowData = $.grep(
              $scope["dtInstance"+$scope.tabIndex].DataTable.data(),
              function (n, i) {
                  return n.id == selectedId[0];
              }
              );
              if (rowData[0].operator == null){
                  sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please first reserve the operator.', 3);
                  return;
              }
            }
            sparrow.showConfirmDialog(ModalService, "Are you sure you want to release operator?", "Release operator",
                function (confirm) {
                    if (confirm) {
                        sparrow.post(
                        "/qualityapp/release_operator/" + selectedId + "/",
                        {},
                        false,
                        function (data) {
                            if (data.code == 1) {
                                sparrow.showMessage('appMsg', sparrow.MsgType.Success, data.msg, 3);
                                $scope.reloadData($scope.tabIndex);
                                return;
                            }
                            },
                        );
                    }
                }
            );
        };

        function onReserveSendtonextPanel() {
            if (data.permissions['reserve_and_send_next_multiple_production'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
                return;
            }
            $("#viewReserveandSendToNextTitle").text( "Orders reserve and send to next");
            $("#viewReserveandSendToNextModel").modal("show");
            var operator_ids = $("#id_operator_resrve_send_to_next").magicSuggest();
            $(operator_ids).on("selectionchange", function (e, m) {
            var operator_ids_id = $("#hid_operator_resrve_send_to_next").val()
            if (operator_ids_id) {
                $("#id_message_oper_resrve_send_to_next").hide();
                $('#id_operator_resrve_send_to_next').css('border-color', '#ccc');
            }
            });
        };

        $scope.saveReserveandSendToNext = function () {
            var operator_ids = $("#id_operator_resrve_send_to_next").magicSuggest();
            var operator_id = operator_ids.getSelection();
            if($("#frmSaveReserveandSendToNext").valid() == false){
                if(operator_id.length ==0){
                    $("#id_message_oper_resrve_send_to_next").show()
                    $('#id_operator_resrve_send_to_next').css('border-color', '#a94442');
                    return;
                }
            }
            if(operator_id.length ==0){
                $("#id_message_oper_resrve_send_to_next").show()
                $('#id_operator_resrve_send_to_next').css('border-color', '#a94442');
                return;
            }
            var operator_list = operator_id[0]["id"]
            sparrow.postForm(
                {
                    operator_list: operator_list
                },
                $("#frmSaveReserveandSendToNext"),
                $scope,
                function (data) {
                    if (data.code == 1) {
                        $("#viewReserveandSendToNextModel").modal("hide");
                        operator_ids.clear()
                        $("#id_panel_no").val("")
                        $("#id_panel_qty").val("")
                        $("#id_order_resrve_send_to_next").val("")
                        $scope.reloadData($scope.tabIndex);
                        return;
                    }
                }
            );
        };

        $scope.closeReserveandSendToNextModel = function(){
            $("#id_message_oper_resrve_send_to_next").hide();
            $('#id_operator_resrve_send_to_next').css('border-color', '#ccc');
            $("#id_panel_no-error").hide()
            $("#id_panel_qty-error").hide()
            $("#id_panel_no").val("")
            $("#id_panel_qty").val("")
            $("#id_order_resrve_send_to_next").val("")
            $(".form-group").removeClass("has-error");
            var operator_ids = $("#id_operator_resrve_send_to_next").magicSuggest();
            operator_ids.clear()
            $('.modal-backdrop').remove();
        }

        function onSendtonext() {
            if (data.permissions['send_to_next_production'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
                return;
            }
            var orderId = $scope.getSelectedIds($scope.tabIndex)[0];
            if(orderId == undefined ){
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
                return;
            }
            var rowData = $.grep(
                $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
                function (n, i) {return n.id == orderId;}
            );
            if (rowData[0].operator == null) {
                sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please first reserve the operator.", 3);
                return;
            };
            sparrow.post(
                '/qualityapp/send_to_next_details/' + orderId + '/',
                {},
                false,
                function (data) {
                  $("#send_to_next_form_").html(data);
                  $("#viewSendToNextTitle").text( "Send to next - " + rowData[0].customer_order_nr);
                  $("#viewSendToNextModel").modal("show");
                  var remark = $('#id_remarks_type').magicSuggest()
                  $(remark).on("selectionchange", function (e, m) {
                      var remark_id = $("#hid_remarks_type").val()
                      if (remark_id) {
                          $("#id_message_remarks").hide();
                          $("#id_remarks_type").css('border-color', '#ccc');
                          $("#id_message_lable_remarks_").css('color', 'black');
                      }
                  });
                  var file_type = $('#id_file_type_').magicSuggest()
                  $(file_type).on("selectionchange", function (e, m) {
                      var file_type_id = $("#hid_file_type_send_next").val()
                      if (file_type_id) {
                      $("#id_message").hide();
                      $('#id_file_type_').css('border-color', '#ccc');
                      }
                  });
                },
                "html"
            );
      };

      $scope.saveSendToNext = function () {
        var orderId = $scope.getSelectedIds($scope.tabIndex)[0];
        if ($('#id_file_not_req').is(":checked"))
        {
          $("#id_file_send_next").removeAttr("required");
          $("#id_message").hide();
          $('#id_file_type_').css('border-color', '#ccc');
        }
        if ($('#id_file_not_req').is(":unchecked"))
        {
          if($("#hid_file_type_send_next").val() == undefined){
            $("#id_message").show();
            $("#id_message_lable").css('color', '#a94442');
            $('#id_file_type_').css('border-color', '#a94442');
          }
          $("#id_file_send_next").removeAttr("disabled", true);
          var id_file = $("#id_file_send_next").val();
          if (id_file.trim() != "") {
            var type_file = id_file.toLowerCase().endsWith('.zip')
            var files_ = id_file.split("\\")
            if(type_file == false){
                sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please file having extension .zip only.", 3);
                return;
            }
            if(files_.slice(-1)[0].length > 170){
              sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "File name is too long.", 3);
              return;
            }
            if($("#hid_file_type_send_next").val() == undefined){
              $("#id_message").show();
              $("#id_message_lable").css('color', '#a94442');
              $('#id_file_type_').css('border-color', '#a94442');
              return;
            }
          }
          if (id_file.trim() == "") {
            if($("#hid_file_type_send_next").val() == undefined){
              $("#id_message").show();
              $("#id_message_lable").css('color', '#a94442');
              $('#id_file_type_').css('border-color', '#a94442');
              $("#id_message_").show();
              $("#id_file_send_next-error").hide();
              $("#id_file_send_next").attr("required", true);
              $(".select-file").css('color', '#a94442');
              $('#id_file_send_next').css('border-color', '#a94442');
              return;
            }
            $("#id_message_").hide();
            $("#id_file_send_next").attr("required", true);
            $(".select-file").css('color', '#a94442');
            $('#id_file_send_next').css('border-color', '#a94442');
          }
        }
        if($("#hid_file_type_send_next").val() != undefined){
          $("#id_message").hide();
        }
        if($("#id_remarks").val() != ""){
          $("#id_message_remarks").hide();
          $("#id_message_lable_remarks_").css('color', 'black');
          if($("#hid_remarks_type").val() == undefined){
            $("#id_message_remarks").show();
            $('#id_remarks_type').css('border-color', '#a94442');
            $("#id_message_lable_remarks_").css('color', '#a94442');
            return;
          }
        }
        if($("#id_attachment").val() != ""){
          var id_attachment = $("#id_attachment").val();
          files_ = id_attachment.split("\\")
          if(files_.slice(-1)[0].length > 170){
            sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "File name is too long.", 3);
            return;
          }
          if($("#hid_remarks_type").val() == undefined){
            $("#id_message_remarks").show();
            $('#id_remarks_type').css('border-color', '#a94442');
            $("#id_message_lable_remarks_").css('color', '#a94442');
          }
          if($("#id_remarks").val() == ""){
            $("#id_message_remarks_textarea").show();
            $("id_remarks").css('border-bottom-color', 'red');
            $("#id_remarks_lable").css('color', '#a94442');
          }
          if($("#hid_remarks_type").val() == undefined || $("#id_remarks").val() == ""){
              return;
          }
        }
        if($("#hid_remarks_type").val() != undefined){
          $("#id_message_remarks").hide();
          $("#id_message_lable_remarks_").removeClass("required", true);
        }
        sparrow.postForm(
            {
            order_id: orderId,
            },
            $("#frmSaveSendToNext"),
            $scope,
            function (data) {
              if (data.code == 1) {
                  $("#viewSendToNextModel").modal("hide");
                  $(".modal-backdrop").remove();
                  sparrow.showMessage('appMsg', sparrow.MsgType.Success, data.msg, 3);
                  $scope.reloadData($scope.tabIndex);
                  $scope.reloadData($scope.allIndex[data.status]);
                  return;
              } else {
                  sparrow.showMessage('appMsg', sparrow.MsgType.Error, data.msg, 3);
                  $scope.reloadData($scope.tabIndex);
                  return;
              }
            }
          );
        };

        function onBackToprevious() {
        if (data.permissions['back_to_previous_design'] == false) {
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
          return;
        };
        var orderId = $scope.getSelectedIds($scope.tabIndex)[0];
        if(orderId == undefined ){
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 3);
          return;
        }
        var rowData = $.grep(
          $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
          function (n, i) {return n.id == orderId;}
        );
        if (rowData[0].order_previous_status == " ") {
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Order has no previous stage.", 3);
          return;
        }
        if (rowData[0].operator == null) {
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please first reserve the operator.", 3);
          return;
        };
        var stage_type = data.type;
        sparrow.post(
          '/qualityapp/back_to_previous_details/' + orderId + '/',
          {},
          false,
          function (data) {
            $("#back_to_previous_form").html(data);
            $("#viewBackToPreviousTitle").text( "Back to previous - " + rowData[0].customer_order_nr);
            $("#viewBackToPreviousModel").modal("show");
            var remark = $('#id_remarks_type_back_to_previous').magicSuggest()
            $(remark).on("selectionchange", function (e, m) {
              var remark_id = $("#hid_remarks_type_back_to_previous").val();
              if (remark_id) {
                  $("#id_message_remarks_back_to_previous").hide();
                  $("#id_remarks_type_back_to_previous").css('border-color', '#ccc');
                  $("#id_message_lable_remarks_back_to_previous").css('color', 'black');
              }
            });
            var file_type = $('#id_file_type_back_to_previous').magicSuggest()
            $(file_type).on("selectionchange", function (e, m) {
              var file_type_id = $("#hid_file_type_back_to_previous").val();
              if (file_type_id) {
                $("#id_message_back_to_previous").hide();
                $("#id_message_lable_back_to_previous").css('color', 'black');
                $("#id_file_type_back_to_previous").css("border-color", "#ccc");
              }
            });
          },
          "html"
        );
      };

      $scope.saveBackToPrevious = function () {
        var orderId = $scope.getSelectedIds($scope.tabIndex)[0];
        if ($("#id_file_not_req_back_to_previous").is(":checked")) {
          $("#id_file_back_to_previous").removeAttr("required");
          $("#id_message_back_to_previous").hide();
          $("#id_message_lable_back_to_previous").css("color", "black");
          $(".select-file-back-previous").css("color", "black");
          $("#id_file_type_back_to_previous").css("border-color", "#ccc");
        }
        if ($("#id_file_not_req_back_to_previous").is(":unchecked")) {
          if ($("#hid_file_type_back_to_previous").val() == undefined) {
            $("#id_message_back_to_previous").show();
            $("#id_message_lable_back_to_previous").css("color", "#a94442");
            $("#id_file_type_back_to_previous").css("border-color", "#a94442");
          }
          $("#id_file_back_to_previous").removeAttr("disabled", true);
          var id_file = $("#id_file_back_to_previous").val();
          if (id_file.trim() != "") {
            var type_file = id_file.toLowerCase().endsWith(".zip");
            var files_ = id_file.split("\\");
            if (type_file == false) {
              sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please file having extension .zip only.", 3);
              return;
            }
            if (files_.slice(-1)[0].length > 170) {
              sparrow.showMessage("appMsg", sparrow.MsgType.Error, "File name is too long.", 3);
              return;
            }
            if ($("#hid_file_type_back_to_previous").val() == undefined) {
              $("#id_message_back_to_previous").show();
              $("#id_message_lable_back_to_previous").css("color", "#a94442");
              $("#id_file_type_back_to_previous").css("border-color", "#a94442");
              return;
            }
          }
          if (id_file.trim() == "") {
            if ($("#hid_file_type_back_to_previous").val() == undefined) {
              $("#id_message_back_to_previous").show();
              $("#id_message_lable_back_to_previous").css("color", "#a94442");
              $("#id_file_type_back_to_previous").css("border-color", "#a94442");
              $("#id_message_back_to_previous_").show();
              $("#id_file_back_to_previous-error").hide();
              $("#id_file_back_to_previous").attr("required", true);
              $(".select-file-back-previous").css("color", "#a94442");
              $("#id_file_back_to_previous").css("border-color", "#a94442");
              return;
            }
            $("#id_message_back_to_previous_").hide();
            $("#id_file_back_to_previous").attr("required", true);
            $(".select-file-back-previous").css("color", "#a94442");
            $("#id_file_back_to_previous").css("border-color", "#a94442");
          }
        }
        if ($("#hid_file_type_back_to_previous").val() != undefined) {
          $("#id_message_back_to_previous").hide();
          $("#id_message_lable_back_to_previous").removeClass("required", true);
        }
        if ($("#id_remarks_back_to_previous").val() != "") {
          $("#id_message_remarks_back_to_previous").hide();
          $("#id_message_lable_remarks_back_to_previous").css("color", "black");
          if ($("#hid_remarks_type_back_to_previous").val() == undefined) {
            $("#id_message_remarks_back_to_previous").show();
            $("#id_remarks_type_back_to_previous").css("border-color", "#a94442");
            $("#id_message_lable_remarks_back_to_previous").css("color", "#a94442");
            return;
          }
        }
        if ($("#id_attachment_back_to_previous").val() != "") {
          var id_attachment = $("#id_attachment_back_to_previous").val();
          files_ = id_attachment.split("\\");
          if (files_.slice(-1)[0].length > 170) {
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "File name is too long.", 3);
            return;
          }
          if ($("#hid_remarks_type_back_to_previous").val() == undefined) {
            $("#id_message_remarks_back_to_previous").show();
            $("#id_remarks_type_back_to_previous").css("border-color", "#a94442");
            $("#id_message_lable_remarks_back_to_previous").css("color", "#a94442");
          }
          if ($("#id_remarks_type_back_to_previous").val() == "") {
            $("#id_message_remarks_textarea_back_to_previous").show();
            $("#id_remarks_type_back_to_previous").css("border-bottom-color", "red");
            $("#id_remarks_lable_back_to_previous").css("color", "#a94442");
          }
          if (
            $("#hid_remarks_type_back_to_previous").val() == undefined ||
            $("#id_remarks_back_to_previous").val() == ""
          ) {
            return;
          }
        }
        if ($("#hid_remarks_type_back_to_previous").val() != undefined) {
          $("#id_message_remarks_back_to_previous").hide();
          $("#id_message_lable_remarks_back_to_previous").removeClass("required", true);
        }
        sparrow.postForm(
          {
            order_id: orderId,
          },
          $("#frmSaveBackToPrevious"),
          $scope,
          function (data) {
            if (data.code == 1) {
              $("#viewBackToPreviousModel").modal("hide");
              $(".modal-backdrop").remove();
              sparrow.showMessage("appMsg", sparrow.MsgType.Success, data.msg, 3);
              $scope.reloadData($scope.tabIndex);
              return;
            } else {
              sparrow.showMessage("appMsg", sparrow.MsgType.Error, data.msg, 3);
              $scope.reloadData($scope.tabIndex);
              return;
            }
          }
        );
      };

        setAutoLookup("id_pre_defined_problem", "/lookups/pre_define_problem/", "", true, true);
        function showGenerateException(scope){
            $('#btnSavePreDefineProblem').prop('disabled', false);
            if (data.permissions['generate_exception_production'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
                return;
            }
            else{
                var order_id = $scope.getSelectedIds($scope.tabIndex)[0];
                var rowData = $.grep(
                    $scope["dtInstance"+$scope.tabIndex].DataTable.data(),
                    function (n, i) {
                        return n.id == order_id;
                    }
                    );
                if(order_id){
                    if (rowData[0].operator == null){
                        sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please first reserve the operator.', 3);
                        return;
                    }
                    $("#generateException").modal("show");
                    $("#id_order_id").val(order_id);
                    $("#id_order_number").val(rowData[0].customer_order_nr);
                    $("#id_problem_department").val(rowData[0].order_status_name)
                    var pre_defined_problem = $('#id_pre_defined_problem').magicSuggest()
                    pre_defined_problem.clear();
                    pre_defined_problem.setSelection([ {name: "See attached document.", id: data.exception_problems_id}, ])
                }
                else{
                    sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
                }
            }
        }

          var problem = $("#id_pre_defined_problem").magicSuggest();
        $(problem).on("selectionchange", function (e, m) {
          var pre_def_prob_id = $("#hid_pre_defined_problem").val()
          if (pre_def_prob_id) {
              $("#id_message_pre_defined_problem").hide();
              $("#id_pre_defined_problem").css('border-color', '#ccc');
          }
          var problem_id = problem.getSelection();
          if(problem_id.length != 0 ){
            if (problem_id[0].name == "See attached document." ||
                problem_id[0].name == "Cancel on customer request." ||
                problem_id[0].name == "Internal Exception" ||
                problem_id[0].name == "Exception on customer request.") {
              $("#si_file_label").removeClass("required");
              $("#id_si_file").removeAttr("required");
              $("#si_file").removeClass("has-error");
              $("#id_si_file-error").hide();
            } else if (problem_id[0].name == "Pre-production approval") {
              $("#si_file_label").addClass("required");
              $("#id_si_file").attr("required", true);
            }
            if(problem_id[0].name == "Internal Exception"){
                $(".internal_remark").show();
            }
            else{
                  $(".internal_remark").hide();
            }
          }
         else{
              $("#si_file").removeClass("has-error");
              $("#si_file_label").removeClass("required");
              $("#upload_image").removeClass("has-error");
              $("#id_upload_image-error").hide();
              $("#id_si_file-error").hide();
           }
          });


        $scope.SavePreDefineProblem = function () {
          var pre_def_prob = $("#hid_pre_defined_problem").val()
          if (!pre_def_prob){
            $("#id_message_pre_defined_problem").show();
            $('#id_pre_defined_problem').css('border-color', '#a94442');
            return;
          }
          var id_upload_image = $("#id_upload_image").val();
          if(id_upload_image){
              var files_ = id_upload_image.split("\\")
              if(files_.slice(-1)[0].length > 170){
                  sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "Exception File name is too long.", 3);
                  return;
              }
          }
          var id_si_file = $("#id_si_file").val();
          if(id_si_file){
              var status_id_si_file = id_si_file.toLowerCase().endsWith('.zip')
              var files_ = id_si_file.split("\\")
              if(status_id_si_file == false){
                  sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please upload file(SI file) having extension .zip only.", 3);
                  return;
              }
              if(files_.slice(-1)[0].length > 170){
                  sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "SI File name is too long.", 3);
                  return;
              }
          }
          if($("#frmSaveExceptionProblem").valid()){
            $('#btnSavePreDefineProblem').prop('disabled', true);
            sparrow.postForm(
                {},
                $("#frmSaveExceptionProblem"),
                $scope,
                function (data) {
                  if (data.code == 1) {
                      $("#generateException").modal("hide");
                      $('#frmSaveExceptionProblem').trigger("reset");
                      $(".modal-backdrop").remove();
                      problem = $("#id_pre_defined_problem").magicSuggest();
                      problem.removeFromSelection(problem.getSelection(), true);

                  }
                  $route.reload()
                }
                );
          }
        };

        function onFileSearch() {
            if (data.permissions['view_file_production'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
                return;
            }
            var selectedId = $scope.getSelectedIds($scope.tabIndex)[0];
            if(selectedId == undefined ){
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
                return;
            }
            var rowData = $.grep(
            $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
            function (n, i) {
                return n.id == selectedId;
            }
            );
            $scope.filesModelTitle = "File - " + rowData[0].customer_order_nr;
            $scope.order_number = rowData[0].customer_order_nr;
            $scope.object_id = rowData[0].id;
            $scope.app_name = "qualityapp";
            $scope.model_name = "order_attachment";
            $scope.permission = data;
            $scope.is_reserve = rowData[0].operator == null ? false :true
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
        };

        function showLog(scope) {
            var selectedId = $scope.getSelectedIds($scope.tabIndex)[0];
            if(selectedId == undefined ){
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
                return;
            }
            var rowData = $.grep(
            $scope["dtInstance"+$scope.tabIndex].DataTable.data(),
            function (n, i) {
                return n.id == selectedId;
            }
            );
            window.location.hash = "#/auditlog/logs/order/" + selectedId + "?title=" + rowData[0].customer_order_nr;
        };

      Mousetrap.bind("shift+n", onSendtonext);
      Mousetrap.bind("shift+p", onBackToprevious);
      if($scope.status == "panel"){
          Mousetrap.bind("shift+g", showGenerateException);
          // Mousetrap.bind("shift+e", onReserveSendtonextPanel);
          Mousetrap.bind("shift+r", OnReserve);
          Mousetrap.bind("shift+l", OnRelease);
      }
     Mousetrap.bind('shift+v',function(){
            var selectedId = $scope.getSelectedIds($scope.tabIndex)[0];
            var rowData = $.grep(
              $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
              function (n, i) {
                return n.id == selectedId;
              }
            );
            if(selectedId){
                $scope.viewOrderDetails(rowData[0].id, false, rowData[0].order_number)
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
        btnConfiguration(type);
    }
  );
}
productionsInit();