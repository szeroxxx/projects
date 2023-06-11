function ordersInit() {
  sparrow.registerCtrl(
    "ordersCtrl",
    function (
      $scope,
      $rootScope,
      $route,
      $routeParams,
      $compile,
      $uibModal,
      DTOptionsBuilder,
      DTColumnBuilder,
      $templateCache,
      ModalService
    ) {
      var customer = { key: "company", name: "Customer" };
      company_search = sparrow.getStorage("company_search");
      if (company_search) {
        customer = { key: "company", name: "Customer", default_val: company_search };
        sparrow.removeStorage("company_search");
      }

      var process = { key: "order_status", name: "Process" };
      process_search = sparrow.getStorage("process_search");
      if (process_search) {
        process ={ key: "order_status", name: "Process" , default_val: process_search };
        sparrow.removeStorage("process_search");
      }
      var config = {
        pageTitle: "Orders",
        topActionbar: {
          extra: [
            {
              id: "btnFiles",
              multiselect: false,
              function: onFileSearch,
            },
            {
              id: "btnChangeStatus",
              multiselect: false,
              function: ChangeStatus,
            },
            {
              id: "btnNCreport",
              multiselect: false,
              function: NCreport,
            },
            {
              id: "btnHistory",
              multiselect: false,
              function: showLog,
            },
            {
              id: "btnRemark",
              multiselect: false,
              function: showRemark,
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
              id: 'btnReserveMultiple',
              function: onReserveMultiple,
            },
            {
              id: "btnSendtonext",
              multiselect: false,
              function: onSendToNext,
            },
            {
              id: "btnBackToprevious",
              multiselect: false,
              function: onBackToPrevious,
            },
            {
              id: "btnGenerateException",
              multiselect: false,
              function: showGenerateException,
            },
            {
              id: "btnSendToFQC",
              multiselect: false,
              function: onSendToFQC,
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
            search: {
              params: [
                { key: "customer_order_nr", name: "Order number" },
                { key: "operator", name: "Engineer" },
                { key: "layer", name: "Layer" },
                customer,
                { key: "service", name: "Service" },
                process,
                { key: "order_number", name: "qualityapp ID" },
                { key: "pcb_name", name: "PCB name" },
                { key: "order_date", name: "Order date", type: "datePicker" },
              ],
            },
            url: "/qualityapp/search_orders/",
            crud: true,
            scrollBody: true,
            columns: [
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
                name: "pcb_name",
                title: "PCB name",
              },
              {
                name: "layer",
                title: "Layers",
              },
              {
                name: "service__name",
                title: "Service",
              },
              {
                name: "board_thickness",
                title: "Board thickness",
              },
              {
                name: "user__user__username",
                title: "Username",
              },
              {
                name: "company__name",
                title: "Customer",
              },
              {
                name: "order_date",
                title: "Order date",
              },
              {
                name: "preparation_due_date",
                title: "Preparation due date",
              },
              {
                name: "delivery_date",
                title: "Delivery date",
              },
              {
                name: "operator__user__username",
                title: "Engineer",
              },
              {
                name: "order_status",
                title: "Process",
              },
              {
                name: "in_time",
                title: "In time",
              },
              {
                name: "finished_on",
                title: "Order finish date",
              },
              {
                name: "remarks",
                title: "Remark",
                renderWith: viewRemarkLink,
                class: "remarks",
                sort: false,
              },
              {
                name: "order_next_status",
                title: "Next stage",
              },
              {
                name: "order_previous_status",
                title: "Previous stage",
              },
            ],
          },
        ],
      };
      function ChangeStatus(scope) {
        if (data.permissions['can_change_status'] == false) {
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
          return;
        }
        var id = $scope.getSelectedIds(1)[0];
        if(id == undefined ){
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
            return;
        }
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == id;
          }
        );
        if (rowData[0].order_status_code == "exception") {
          sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "Exception stage record(s) can not be change the status.", 3);
          return;
        }
        if(rowData[0].service__name == null){
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Job process flow is not selected for this service or customer.", 3);
          return;
        }
        id = id ? id : 0;
        $("#title").text("Change status");
        sparrow.post(
          "/qualityapp/change_order_status/",
          {
            id: id,
          },
          false,
          function (data) {
            $("#status").html(data);
            $("#ChangeStatus").modal("show");
          },
          "html"
        );
      };

      $scope.saveOrderStatus = function () {
        var status = $("#hid_status").val()
        var id = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == id;
          }
        );
        if (rowData[0].order_status_code == status) {
          sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "Order is already in this stage.", 3);
          return;
        }
        if (status == "finished") {
          sparrow.showConfirmDialog(ModalService, "Are you sure you want to finish order?", "Order finish",
            function (confirm) {
                if (confirm) {
                  sparrow.postForm(
                  {
                    id: $routeParams.id,
                  },
                  $("#frmSaveStatus"),
                  $scope,
                  function (data) {
                    if (data.code == 1) {
                      $("#ChangeStatus").modal("hide");
                      $scope.reloadData(1);
                    }
                  }
                );
                }
            }
          )
          return;
        }
        if (status == "cancel") {
          sparrow.showConfirmDialog(ModalService, "Are you sure you want to cancel order?", "Order cancel",
            function (confirm) {
                if (confirm) {
                  sparrow.postForm(
                  {
                    id: $routeParams.id,
                  },
                  $("#frmSaveStatus"),
                  $scope,
                  function (data) {
                    if (data.code == 1) {
                      $("#ChangeStatus").modal("hide");
                      $scope.reloadData(1);
                    }
                  }
                );
                }
            }
          )
          return;
        }
        sparrow.postForm(
          {
            id: $routeParams.id,
          },
          $("#frmSaveStatus"),
          $scope,
          function (data) {
            if (data.code == 1) {
              $("#ChangeStatus").modal("hide");
              $scope.reloadData(1);
            }
          }
        );
      };

      function NCreport(scope) {
        if (data.permissions['can_add_nc'] == false) {
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
            return;
        }
        var id = $scope.getSelectedIds(1)[0];
        if(id == undefined ){
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
          return;
        }
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {return n.id == id;}
        );
        if(rowData[0].order_previous_status == "finished") {
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "You can not be create NC for this stage.", 3);
          return;
        };
        id = id ? id : 0;
        $("#label").text("Add NC Report");
        sparrow.post(
          "/qualityapp/nc_report/",
          {
            id: id,
          },
          false,
          function (data) {
            $("#addNC").html(data);
            var count = $("#id_nc_not").val().length;
            if (count == 2) {
              sparrow.showMessage("appMsg", sparrow.MsgType.Error, "You can not be create NC for this stage.", 3);
              return;
            }
            $("#AddNCReport").modal("show");
          },
          "html"
        );
      };

      $scope.saveNCReport = function () {
        var $checkboxes = $('.table tr td input[type="checkbox"]');
        var countCheckedCheckboxes = $checkboxes.filter(":checked").length;
        if (countCheckedCheckboxes == 0) {
          sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "Please select atleast one record.", 3);
          return;
        }
        if($("#id_file").val() != ""){
          var id_file = $("#id_file").val();
          files_ = id_file.split("\\")
          if(files_.slice(-1)[0].length > 170){
            sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "File name is too long.", 3);
            return;
          }
        }
        if ($("#frmSaveNCReport").valid() == false) {
          $("#hid_main_category").val() == undefined
            ? $("#id_main_category_message").show()
            : $("#id_main_category_message").hide();

          if ($("#hid_sub_category").val() == undefined) {
            $("#id_sub_category_message").show();
            $("#id_select_message").hide();
          }

          $("#hid_nc_create_by").val() == undefined
            ? $("#id_nc_create_by_message").show()
            : $("#id_nc_create_by_message").hide();

          $("#hid_nc_type").val() == undefined
            ? $("#id_nc_type_message").show()
            : $("#id_nc_type_message").hide();
          return;
        }

        $("#hid_main_category").val() == undefined
          ? $("#id_main_category_message").show()
          : $("#id_main_category_message").hide();

        if ($("#hid_sub_category").val() == undefined) {
          $("#id_sub_category_message").show();
          $("#id_select_message").hide();
        }

        $("#hid_nc_create_by").val() == undefined
          ? $("#id_nc_create_by_message").show()
          : $("#id_nc_create_by_message").hide();

        $("#hid_nc_type").val() == undefined
          ? $("#id_nc_type_message").show()
          : $("#id_nc_type_message").hide();

        if (
          $("#hid_nc_type").val() == undefined ||
          $("#hid_main_category").val() == undefined ||
          $("#hid_sub_category").val() == undefined ||
          $("#hid_nc_create_by").val() == undefined
        ) {
          return;
        };
        var id = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == id;
          }
        );
        sparrow.postForm(
          {
            id: $routeParams.id,
            order_number:rowData[0].customer_order_nr
          },
          $("#frmSaveNCReport"),
          $scope,
          function (data) {
            if (data.code == 1) {
              $("#AddNCReport").modal("hide");
              $(".navbar-nav").load(window.location.href + " .navbar-nav");
              $scope.reloadData(1);
            }
          }
        );
      };

      function showLog(scope) {
        var selectedId = $scope.getSelectedIds(1)[0];
        if(selectedId == undefined ){
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
          return;
        }
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        window.location.hash = "#/auditlog/logs/order/" + selectedId + "?title=" + rowData[0].customer_order_nr;
      }

      function onFileSearch() {
        if (data.permissions['can_view_files'] == false) {
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
          return;
        }
        var selectedId = $scope.getSelectedIds(1)[0];
        if(selectedId == undefined ){
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
          return;
        }
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
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
        $scope.is_reserve = rowData[0].operator__user__username == null ? false :true
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
          $scope.reloadData(1);
          return;
        };

      function showRemark() {
        if(data.permissions['can_add_remark'] == false){
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
          return;
        }
        var selectedId = $scope.getSelectedIds(1)[0];
        if(selectedId == undefined ){
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
          return;
        }
        $("#addRemark").modal("show");
        setAutoLookup("id_remarks_type_add", "/lookups/remark_type/", "", true, "", "", "", 1,);
      };

      $scope.SaveRemarks = function () {
        var selectedId = $scope.getSelectedIds(1)[0];
        sparrow.postForm(
          {
            id: selectedId,
          },
          $("#frmSaveRemarks"),
          $scope,
          function (data) {
            if (data.code == 1) {
              $("#addRemark").modal("hide");
              remark_type_add = $("#id_remarks_type_add").magicSuggest();
              remark_type_add.clear();
              $("#id_remarks_add").val("");
              $scope.reloadData(1);
            }
          }
        );
      };

      setAutoLookup("id_operator", "/lookups/operators/", "", true, false, false, null, 1);

      $scope.ReserveorderList = [];
      function OnReserve() {
        $scope.ReserveorderList = [];
        if (data.permissions['can_reserve'] == false) {
              sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
              return;
        }
        var selectedId = $scope.getSelectedIds(1);
        if(selectedId.length == 0){
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
          return;
        }
        if (selectedId.length == 1){
          var rowData = $.grep(
            $scope["dtInstance1"].DataTable.data(),
            function (n, i) {
              return n.id == selectedId[0];
            }
          );
          if(rowData[0].order_status_code == "exception"){
            sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "Exception stage record(s) can not be reserve operator.", 3);
            return;
          }
          if(rowData[0].operator__user__username != null){
            sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "Order has already operator reserved.", 3);
            return;
          }
        }
        for (let index = 0; index < selectedId.length; index++) {
          var rowData = $.grep(
            $scope["dtInstance1"].DataTable.data(),
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
      }

      $scope.saveReserve = function () {
        var order_id = $scope.getSelectedIds(1);
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
              $scope.reloadData(1);
              if (order_id.length == 1){
                setTimeout(function () {
                  $("#chk_" + 1 + "_" + order_id[0]).trigger("click").prop("checked", true);
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

      function onReserveMultiple() {
        if (data.permissions['reserve_multiple_report_orders'] == false) {
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
            return;
        }
        $("#viewReserveMultipleTitle").text( "Reserve multiple records");
        $("#viewReserveMultipleModel").modal("show");
        var operator_ids = $("#id_operator_resrve_multiple").magicSuggest();
        $(operator_ids).on("selectionchange", function (e, m) {
        var operator_ids_id = $("#hid_operator_resrve_multiple").val()
        if (operator_ids_id) {
            $("#id_message_oper_resrve_multiple").hide();
            $('#id_operator_resrve_multiple').css('border-color', '#ccc');
        }
        });
      };

      $scope.saveReserveMultiple = function () {
      var operator_ids = $("#id_operator_resrve_multiple").magicSuggest();
      var operator_id = operator_ids.getSelection();
      if($("#frmSaveReserveMultiple").valid() == false){
          if(operator_id.length ==0){
              $("#id_message_oper_resrve_multiple").show()
              $('#id_operator_resrve_multiple').css('border-color', '#a94442');
              return;
          }
      }
      if(operator_id.length ==0){
          $("#id_message_oper_resrve_multiple").show()
          $('#id_operator_resrve_multiple').css('border-color', '#a94442');
          return;
      }
      if($("#id_order_resrve_multiple").val() == ""){
          return;
      }
      var operator_list = operator_id[0]["id"]
      var ReserveOrderList = $("#id_order_resrve_multiple").val()
      var confirm_dialog = "Are you sure you want to reserve operator for these selected jobs? " + ReserveOrderList + "</br></br> On 'Yes' click, already reserved operator(s) will be replaced with new one, click 'No' to abort.";
      sparrow.showConfirmDialog(ModalService, confirm_dialog, "Reserve multiple records",
        function (confirm) {
          if (confirm) {
            sparrow.postForm(
                {
                    operator_list: operator_list
                },
                $("#frmSaveReserveMultiple"),
                $scope,
                function (data) {
                    if (data.code == 1) {
                        sparrow.showMessage('appMsg', sparrow.MsgType.Success, data.msg, 3);
                        $('.modal-backdrop').remove();
                        $("#id_order_resrve_multiple").val("");
                        $("#viewReserveMultipleModel").modal("hide");
                        operator_ids.clear()
                        $scope.reloadData(1);
                        return;
                    } else {
                        sparrow.showMessage('appMsg', sparrow.MsgType.Error, data.msg, 3);
                        $scope.reloadData(1);
                        return;
                    }
                }
            );
          }
        }
      );
    };
    $scope.closeReserveMultipleModel = function(){
      var operator_ids = $("#id_operator_resrve_multiple").magicSuggest();
      operator_ids.clear()
      $(".form-group").removeClass("has-error");
      $("#id_order_resrve_multiple").val("");
      $("#id_order_resrve_multiple-error").hide()
      $("#id_message_oper_resrve_multiple").hide();
      $('#id_operator_resrve_multiple').css('border-color', '#ccc');
      $('.modal-backdrop').remove();
    };

      function OnRelease() {
          if (data.permissions['can_release'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
                return;
          }
          var selectedId = $scope.getSelectedIds(1);
          if(selectedId.length == 0){
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
            return;
          }
          if (selectedId.length == 1){
            var rowData = $.grep(
              $scope["dtInstance1"].DataTable.data(),
              function (n, i) {
                return n.id == selectedId[0];
              }
            );
            if(rowData[0].order_status_code == "exception"){
              sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Exception stage record(s) can not be release operator.", 3);
              return;
            }
            if (rowData[0].operator__user__username == null){
              sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Order has no operator reserved.", 3);
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
                     sparrow.showMessage("appMsg", sparrow.MsgType.Success, data.msg, 3);
                      $scope.reloadData(1);
                      return;
                    }
                  }
                );
              }
            }
          );
        }

      function onSendToNext() {
          if (data.permissions['can_send_to_next'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
                return;
          };
          var orderId = $scope.getSelectedIds(1)[0];
          if(orderId == undefined ){
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
            return;
          }
          var rowData = $.grep(
            $scope["dtInstance1"].DataTable.data(),
            function (n, i) {return n.id == orderId;}
          );
          if(rowData[0].order_status_code == "exception"){
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Exception stage record(s) can not be sent to Next stage.", 3);
            return;
          };
          if(rowData[0].order_status_code == "cancel"){
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Cancel stage record(s) can not be sent to Next stage.", 3);
            return;
          };
          if(rowData[0].order_status_code == "finished"){
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Finished stage record(s) can not be sent to Next stage.", 3);
            return;
          };
          if(rowData[0].order_status == ""){
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Job process flow is not selected for this service or customer.", 3);
            return;
          }
          if(rowData[0].operator__user__username == null){
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
        var orderId = $scope.getSelectedIds(1)[0];
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
                  $scope.reloadData(1);
                  return;
              } else {
                  sparrow.showMessage('appMsg', sparrow.MsgType.Error, data.msg, 3);
                  $scope.reloadData(1);
                  return;
              }
            }
          );
        };

      function onBackToPrevious() {
        if (data.permissions['can_back_to_previous'] == false) {
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
          return;
        };
        var orderId = $scope.getSelectedIds(1)[0];
        if(orderId == undefined ){
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 3);
          return;
        }
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {return n.id == orderId;}
        );
        if(rowData[0].order_status_code == "exception"){
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Exception stage record(s) can not be sent to Previous stage.", 3);
          return;
        }
        if(rowData[0].order_status_code == "cancel"){
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Cancel stage record(s) can not be sent to Previous stage.", 3);
          return;
        }
        if(rowData[0].order_status_code == "finished"){
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Finished stage record(s) can not be sent to Previous stage.", 3);
          return;
        }
        if (rowData[0].order_previous_status == "") {
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Order has no previous stage.", 3);
          return;
        }
        if (rowData[0].operator__user__username == null) {
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please first reserve the operator.", 3);
          return;
        };
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
        var orderId = $scope.getSelectedIds(1)[0];
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
              $scope.reloadData(1);
              return;
            } else {
              sparrow.showMessage("appMsg", sparrow.MsgType.Error, data.msg, 3);
              $scope.reloadData(1);
              return;
            }
          }
        );
      };

      setAutoLookup("id_pre_defined_problem", "/lookups/pre_define_problem/", "", true, true);

      function showGenerateException(scope) {
         $('#btnSavePreDefineProblem').prop('disabled', false);
         if (data.permissions['can_register_exception'] == false) {
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
            return;
          }
          var order_id = $scope.getSelectedIds(1)[0];
          var rowData = $.grep(
            $scope["dtInstance1"].DataTable.data(),
            function (n, i) {
              return n.id == order_id;
            }
          );
          if(order_id){
              if (rowData[0].order_status_code == "upload_panel") {
                sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "Operator can not register exception in upload panel stage. ", 3);
                return;
              }
              if (rowData[0].order_status_code == "exception") {
                sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "Already exception registered for this order. ", 3);
                return;
              }
              if (rowData[0].order_status_code == "cancel") {
                sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "Cancel stage record(s) can not be sent to Exception stage.", 3);
                return;
              }
              if (rowData[0].order_status_code == "finished") {
                sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "Finished stage record(s) can not be sent to Exception stage.", 3);
                return;
              }
              if(rowData[0].order_status == ""){
                sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Job process flow is not selected for this service or customer.", 3);
                return;
              }
              if (rowData[0].operator__user__username == null) {
                sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please first reserve the operator.", 3);
                return;
              };
              $("#generateException").modal("show");
              $("#id_order_id").val(order_id);
              $("#id_order_number").val(rowData[0].customer_order_nr);
              $("#id_problem_department").val(rowData[0].order_status);
              var pre_defined_problem = $('#id_pre_defined_problem').magicSuggest()
              pre_defined_problem.clear();
              pre_defined_problem.setSelection([ {name: "See attached document.", id: data.exception_problems_id}, ])
        }
        else{
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
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


      function onSendToFQC() {
        if (data.permissions['can_send_to_fqc'] == false) {
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
          return;
        }
        var orderId = $scope.getSelectedIds(1)[0];
        if(orderId == undefined ){
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
          return;
        }
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == orderId;
          }
        );
        if(rowData[0].order_status_code == "exception"){
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Exception stage record(s) can not be sent to FQC stage.", 3);
          return;
        }
        if(rowData[0].order_status_code == "cancel"){
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Cancel stage record(s) can not be sent to FQC stage.", 3);
          return;
        }
        if( rowData[0].order_status_code == "finished" ){
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Finished stage record(s) can not be sent to FQC stage.", 3);
          return;
        }
        if(rowData[0].order_status == ""){
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Job process flow is not selected for this service or customer.", 3);
            return;
          }
        if(rowData[0].operator__user__username == null){
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please first reserve the operator.", 3);
          return;
        }
        if(rowData[0].order_status_code == "FQC"){
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Order is already in FQC.", 3);
          return;
        }
        sparrow.post(
          "/qualityapp/chaeck_fqc_in_process/",
          {
            orderId: orderId,
          },
          false,
          function (data) {
            if (data.code == 1) {
              sparrow.showConfirmDialog(ModalService, "Are you sure you want to send this order to FQC?", "Send to FQC",
                function (confirm) {
                  if (confirm) {
                    sparrow.post(
                      "/qualityapp/send_to_fqc/",
                      {
                        orderId: orderId,
                      },
                      false,
                      function (data) {
                        if (data.code == 1) {
                          sparrow.showMessage("appMsg", sparrow.MsgType.Success, data.msg, 3);
                          $scope.reloadData(1);
                          return;
                        } else {
                          sparrow.showMessage("appMsg", sparrow.MsgType.Error, data.msg, 3);
                          return;
                        }
                      }
                    );
                  }
                }
              )
              return;
            } else {
              sparrow.showMessage("appMsg", sparrow.MsgType.Error, "In job process flow FQC is not selected for this service or customer.", 3);
              return;
            }
          }
        );

      };

      var exports_cus = Array();
      var exports_process = Array();
      function onAllDataExport() {
        if (data.permissions['can_export_orders'] == false) {
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
        var pcb_name = "";
        var qualityapp_id = "";
        var customer_order_nr = "";
        var company = "";
        var service = "";
        var layer = "";
        var order_status = "";
        var operator = "";
        var order_date = "";
        if (search_parameter) {
          exports_cus = [];
          exports_process = [];
          if ("Order number" in search_parameter) {
            var customer_order_nr = search_parameter["Order number"];
          }
          if ("qualityapp ID" in search_parameter) {
            var qualityapp_id = search_parameter["qualityapp ID"];
          }
          if ("Customer" in search_parameter) {
            var company = search_parameter["Customer"];
          } else {
            if (exports_cus.length == 1 || exports_cus.length == 0) {
              company = company_search;
              sparrow.removeStorage("company_search");
            }
          }
          if ("Service" in search_parameter) {
            var service = search_parameter["Service"];
          }
          if (" PCB name" in search_parameter) {
            var pcb_name = search_parameter[" PCB name"];
          }
          if ("Layer" in search_parameter) {
            var layer = search_parameter["Layer"];
          }
          if ("Process" in search_parameter) {
            var order_status = search_parameter["Process"];
          } else {
            if (exports_process.length == 1 || exports_process.length == 0) {
              order_status = process_search;
              sparrow.removeStorage("process_search");
            }
          }
          if ("Engineer" in search_parameter) {
            var operator = search_parameter["Engineer"];
          }
          if ("Order date" in search_parameter) {
            var order_date = search_parameter["Order date"];
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
          company = company_search;
          sparrow.removeStorage("company_search");
        }

        if (process_search && !search_parameter) {
          exports_process.push(process_search);
          sparrow.removeStorage("process_search");
        }
        if (exports_process.length == 1 && !search_parameter) {
          order_status = process_search;
          sparrow.removeStorage("process_search");
        }
        if(display_data != ""){
          order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }

        sparrow.downloadData("/qualityapp/exports_orders/", {
          start: 0,
          length: display_data[0].recordsTotal,
          pcb_name: pcb_name,
          qualityapp_id: qualityapp_id,
          customer_order_nr: customer_order_nr,
          company: company,
          service: service,
          layer: layer,
          order_status: order_status,
          operator: operator,
          order_date: order_date,
          ids: selectedIds,
          order_by: order_by_,
        });
      };

      var exports_cus = Array();
      var exports_process = Array();
      function onExport() {
        if (data.permissions['can_export_orders'] == false) {
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
        var pcb_name = "";
        var qualityapp_id = "";
        var customer_order_nr = "";
        var company = "";
        var service = "";
        var layer = "";
        var order_status = "";
        var operator = "";
        var order_date = "";
        if (search_parameter) {
          exports_cus = [];
          exports_process = [];
          if ("Order number" in search_parameter) {
            var customer_order_nr = search_parameter["Order number"];
          }
          if ("qualityapp ID" in search_parameter) {
            var qualityapp_id = search_parameter["qualityapp ID"];
          }
          if ("Customer" in search_parameter) {
            var company = search_parameter["Customer"];
          } else {
            if (exports_cus.length == 1 || exports_cus.length == 0) {
              company = company_search;
              sparrow.removeStorage("company_search");
            }
          }
          if ("Service" in search_parameter) {
            var service = search_parameter["Service"];
          }
          if (" PCB name" in search_parameter) {
            var pcb_name = search_parameter[" PCB name"];
          }
          if ("Layer" in search_parameter) {
            var layer = search_parameter["Layer"];
          }
          if ("Process" in search_parameter) {
            var order_status = search_parameter["Process"];
          } else {
            if (exports_process.length == 1 || exports_process.length == 0) {
              order_status = process_search;
              sparrow.removeStorage("process_search");
            }
          }
          if ("Engineer" in search_parameter) {
            var operator = search_parameter["Engineer"];
          }
          if ("Order date" in search_parameter) {
            var order_date = search_parameter["Order date"];
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
          company = company_search;
          sparrow.removeStorage("company_search");
        }

        if (process_search && !search_parameter) {
          exports_process.push(process_search);
          sparrow.removeStorage("process_search");
        }
        if (exports_process.length == 1 && !search_parameter) {
          order_status = process_search;
          sparrow.removeStorage("process_search");
        }
        if(display_data != ""){
          order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }

        sparrow.downloadData("/qualityapp/exports_orders/", {
          start: $rootScope.start,
          length: $rootScope.length,
          pcb_name: pcb_name,
          qualityapp_id: qualityapp_id,
          customer_order_nr: customer_order_nr,
          company: company,
          service: service,
          layer: layer,
          order_status: order_status,
          operator: operator,
          order_date: order_date,
          ids: selectedIds,
          order_by: order_by_,
        });
      }

      Mousetrap.bind("shift+r", OnReserve);
      Mousetrap.bind("shift+l", OnRelease);
      Mousetrap.bind('shift+c', NCreport);
      Mousetrap.bind("shift+n", onSendToNext);
      Mousetrap.bind("shift+p", onBackToPrevious);
      Mousetrap.bind("shift+q", onSendToFQC);
      Mousetrap.bind("shift+t", ChangeStatus);
      Mousetrap.bind("shift+k", showRemark);
      Mousetrap.bind("shift+g", showGenerateException);
      Mousetrap.bind('shift+v',function(){
        var orderId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
            $scope["dtInstance1"].DataTable.data(),
            function (n, i) {
              return n.id == orderId;
            }
          );
        if(orderId){
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
    }
  );
}
ordersInit();
