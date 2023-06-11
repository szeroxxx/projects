function order_allocationsInit() {
  sparrow.registerCtrl(
    "order_allocationsCtrl",
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
        $scope.ManageAutoAllocation_save = []
        var config = {
          pageTitle: "Order Allocations",
          topActionbar: {
            extra: [
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
                id: "btnReserveMultiple",
                function: onReserveMultiple,
              },
              {
                id: "auto_assignment",
                function: AutoAssignment,
              },
              {
                id: "define_auto_assignment_flow",
                function: defineAutoAssignmentFlow,
              },
              {
                id: "btnSkillMatrix",
                function: onSkillMatrix,
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
                id: "btnManageAutoallocation",
                function: onManageAutoallocation,
              },
            ],
          },
          listing: [
            {
              index: 1,
              url: "/qualityapp/order_allocation/",
              postData: {
                company_id: null,
                process_id: null,
                data_sort: null
              },
              crud: true,
              scrollBody: true,
              pagging: true,
              columns: [
                {
                  name: "order_number",
                  title: "qualityapp ID",
                  renderWith: viewOrderLink,
                  class: "allocation-sort",
                },
                {
                  name: "customer_order_nr",
                  title: "Order number",
                  class: "allocation-sort",
                },
                {
                  name: "preparation_due_date",
                  title: "Preparation due date",
                  class: "allocation-sort",
                },
                {
                  name: "layer",
                  title: "Layers",
                  class: "allocation-sort",
                },
                {
                  name: "order_date",
                  title: "Order date",
                  class: "allocation-sort",
                },
                {
                  name: "delivery_term",
                  title: "Delivery term",
                  class: "allocation-sort",
                },
                {
                  name: "delivery_date",
                  title: "Delivery date",
                  class: "allocation-sort",
                },
                {
                  name: "pcb_name",
                  title: "Pcb name",
                  class: "allocation-sort",
                },
                {
                  name: "in_time",
                  title: "System intime",
                  class: "allocation-sort",
                },
                {
                  name: "company__name",
                  title: "Customer",
                  class: "allocation-sort",
                },
                {
                  name: "operator__user__username",
                  title: "Operator name",
                  class: "allocation-sort",
                },
                {
                  name: "order_status",
                  title: "Order status",
                  class: "allocation-sort",
                },
                {
                  name: "service__name",
                  title: "Service name",
                  class: "allocation-sort",
                },
              ],
            },
          ],
        };

      var order_allocation = [
          { id:'pre_due_date', name:"Preparation due date"},
          { id:'delivery_date', name:"Delivery date"},
          { id:'systemin_time', name:"System intime"},
          { id:'order_date', name:"Order date"},
          { id:'delivery_and_order_date', name:"Delivery date and Order date"},
          { id:'layers', name:"Layers"},
          { id:'delivery_and_layers', name:"Delivery date and Layers"},
      ]
      setAutoLookup("id_order_allocation", order_allocation, "", true);
      setAutoLookup("id_company", "/lookups/companies/", "", false, true);
      setAutoLookup("id_process", "/lookups/processes_allocation/", "", false, true);
      setAutoLookup("id_company_allocation", "/lookups/companies/", "", true, true);


      function viewOrderLink(data, type, full, meta) {
        return '<span><a ng-click="viewOrderDetails(' + full.id + ",'" + full.customer_order_nr + '\')">' + data + '</a></span>';
      };
      $scope.viewOrderDetails = function (id, customer_order_nr) {
        remarks_ = false
        $scope.onEditLink('/b/iframe_index/#/qualityapp/order/' + id  + remarks_, 'Order - ' + customer_order_nr, closeIframeCallback, '', '', true);
      };
      function closeIframeCallback() {
        $scope.reloadData(1);
        return;
      };

      function onSkillMatrix() {
        if (data.permissions['add_skill_matrix_order_allocation'] == false) {
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
            return;
        }
        window.location.hash = "#/qualityapp/skill_matrix/";
      };

      function onManageAutoallocation() {
        if (data.permissions['manage_auto_order_allocation'] == false) {
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
            return;
        }
        $("#viewManageAutoallocationTitle").text("Manage auto allocation");
        $("#viewManageAutoallocationModel").modal("show");
        $(".manage_save_before").removeClass("ng-hide")
        $(".manage_save_after").addClass("ng-hide")
      };

      $scope.removeManageAutoallocation = function (manage_auto_all_id) {
      sparrow.showConfirmDialog(ModalService, "Are you sure you want to remove?", "Remove auto allocation",
          function (confirm) {
            if (confirm) {
              sparrow.post(
                "/qualityapp/remove_manage_auto_allocation_data/",
                {
                    manage_auto_all_id : manage_auto_all_id
                },
                false,
                function (data) {
                  if (data.code == 1) {
                    $("#id_datata").empty();
                    for (var i = 0; i < data.manage_auto_allocation.length; i++) {
                        var html_data = '<div class="col-md-6 col-sm-6"><div class="form-group"><label required class="control-label col-sm-5">Stop start time:</label>\
                          <div class="col-sm-6"><input class="form-control" value="'+ data.manage_auto_allocation[i].stop_start_time +'" readonly/></div></div></div>\
                          <div class="col-md-6 col-sm-6"><div class="form-group"><label required class="control-label col-sm-5">Stop end time : </label>\
                          <div class="col-sm-6"><input class="form-control" value="'+ data.manage_auto_allocation[i].stop_end_time +'" readonly/></div>\
                          <div class="col-sm-1"><i class="fa fa-trash-o remove-auto-allo-dlt"\
                          ng-click="removeManageAutoallocation(' + data.manage_auto_allocation[i].id + ')" title="Remove auto allocation"></i></div></div></div>';
                          var htmldata = $compile(html_data)($scope);
                          $("#id_datata").append(htmldata);
                    }
                      setTimeout(function () {$(".manage_save_after").removeClass("ng-hide")}, 100);
                      setTimeout(function () {$(".manage_save_before").addClass("ng-hide")}, 100);
                      sparrow.showMessage("appMsg", sparrow.MsgType.Success, data.msg, 3);
                      return;
                  } else {
                      sparrow.showMessage("appMsg", sparrow.MsgType.Error, data.msg, 3);
                      $scope.reloadData(1);
                      return;
                  }
                }
              );
            }
          }
        )
      };

      $scope.saveManageAutoallocation = function () {
      sparrow.postForm(
        {},
        $("#frmSaveManageAutoallocation"),
        $scope,
        function (data) {
          if (data.code == 1) {
              $("#id_datata").empty();
              $("#id_stop_start_time").val("");
              $("#id_stop_end_time").val("");
              for (var i = 0; i < data.manage_auto_allocation.length; i++) {
                  var html_data = '<div class="col-md-6 col-sm-6"><div class="form-group"><label required class="control-label col-sm-5">Stop start time:</label>\
                    <div class="col-sm-6"><input class="form-control" value="'+ data.manage_auto_allocation[i].stop_start_time +'" readonly/></div></div></div>\
                    <div class="col-md-6 col-sm-6"><div class="form-group"><label required class="control-label col-sm-5">Stop end time : </label>\
                    <div class="col-sm-6"><input class="form-control" value="'+ data.manage_auto_allocation[i].stop_end_time +'" readonly/></div>\
                    <div class="col-sm-1"><i class="fa fa-trash-o remove-auto-allo-dlt"\
                    ng-click="removeManageAutoallocation(' + data.manage_auto_allocation[i].id + ')" title="Remove auto allocation"></i></div></div></div>';
                  var htmldata = $compile(html_data)($scope);
                  $("#id_datata").append(htmldata);
              }
              setTimeout(function () {$(".manage_save_after").removeClass("ng-hide")}, 10);
              setTimeout(function () {$(".manage_save_before").addClass("ng-hide")}, 10);
              sparrow.showMessage("appMsg", sparrow.MsgType.Success, data.msg, 3);
              return;
          } else {
              sparrow.showMessage("appMsg", sparrow.MsgType.Error, data.msg, 3);
              $scope.reloadData(1);
              return;
          }
        }
      );
      };

      $scope.closeManageAutoallocationModel = function(){
        $("#id_stop_start_time").val("");
        $("#id_stop_end_time").val("");
        $("#id_stop_start_time").removeClass("has-error");
        $(".form-group").removeClass("has-error");
        $("#id_stop_start_time-error").hide();
        $("#id_stop_end_time-error").hide();
        $("#viewManageAutoallocationModel").modal("hide");
        $('.modal-backdrop').remove();
        $route.reload()
      };

      function onReserveMultiple() {
        if (data.permissions['reserve_multiple_order_allocation'] == false) {
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
      var ReserveOrderList = $("#id_order_resrve_multiple").val();
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

      var allocation = []
      function AutoAssignment(scope) {
        if (data.permissions['can_auto_assignment'] == false) {
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
            return;
        }
        var postData = $scope.postData;
        var short = ""
        if (postData == undefined) {
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please select Customer and Process.", 3);
            return;
        }
        if (postData.company_id == "") {
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please select Customer.", 3);
            return;
        }
        if (postData.process_id == "") {
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please select Process.", 3);
            return;
        }
        if(postData.company_id == allocation[1]){
          short = allocation[0]
        }
        data = {"company_id": postData.company_id, "process_id": postData.process_id, short}
        sparrow.post("/qualityapp/auto_assignment/", data, $scope,);
        $scope.reloadData(1);
      }

            function defineAutoAssignmentFlow(scope) {
              if (data.permissions['can_define_auto_assignment'] == false) {
                  sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
                  return;
              }
              $("#allocationFlow").modal("show");
            };

            $(".allo-close").on('click', function (event) {
              $(".modal-backdrop").remove();
              $("#id_message_company_allocation").hide();
              $('#id_company_allocation').css('border-color', '#ccc');
              $("#id_message_order_allocation").hide();
              $('#id_order_allocation').css('border-color', '#ccc');
            });

            $('#load_btn').on('click', function (event) {
                sparrow.global.set('SEARCH_EVENT', true);
                dtBindFunction();
                config.listing[0].postData = $scope.postData;
                $scope.reloadData(1, config.listing[0]);
              });
            function dtBindFunction() {
                var company_id = $('#hid_company').val()
                var process_id = $('#hid_process').val()
                if (company_id == undefined) {
                    $("#company_allocation_for_show").hide()
                    var cus_alloca = $('#id_order_allocation').magicSuggest()
                    cus_alloca.clear();
                    var customer = $('#id_company_allocation').magicSuggest()
                    customer.clear();
                    company_id = '';
                }
                if (process_id == undefined) {
                    process_id = '';
                }
                if (company_id != ""){
                  var company_id = $("#id_company").magicSuggest();
                  var comp_id = company_id.getSelection();
                  var company_id = comp_id[0]["id"]
                  var company_name = comp_id[0]["name"]
                  var customer = $('#id_company_allocation').magicSuggest()
                  customer.clear();
                  customer.setSelection([ { name: company_name, id: company_id }, ])
                  sparrow.post(
                    "/qualityapp/show_auto_define_assignment_flow/",
                  {company_id : company_id},
                  false,
                  function (data) {
                      if(data.order_allocation != null){
                        $("#company_allocation_for_show").show()
                        $("#company_allocation_for_show").text("Allocation flow :" + " " + data.allocation_name)
                        var cus_alloca = $('#id_order_allocation').magicSuggest()
                        cus_alloca.clear();
                        cus_alloca.setSelection([ { name: data.allocation_name, id: data.order_allocation }, ])
                      }
                      if(data.order_allocation == null){
                        $("#company_allocation_for_show").hide()
                        $("#company_allocation_for_show").text("")
                        var cus_alloca = $('#id_order_allocation').magicSuggest()
                        cus_alloca.clear();
                      }
                  }
                );
                }
                var postData = {
                    company_id: company_id,
                    process_id: process_id,
                    data_sort: true,
                };
                $scope.postData = postData;
            };

            $(document).on('click', "th.allocation-sort", function () {
              sparrow.global.set('SEARCH_EVENT', true);
                dtBindFunction1();
                config.listing[0].postData = $scope.postData;
                $scope.reloadData(1, config.listing[0]);
            });
            function dtBindFunction1() {
              var company_id = $('#hid_company').val()
              var process_id = $('#hid_process').val()
              if (company_id == undefined) {
                  company_id = '';
              }
              if (process_id == undefined) {
                  process_id = '';
              }
              var postData = {
                  company_id: company_id,
                  process_id: process_id,
                  data_sort : false,
              };
              $scope.postData = postData;
            };

            $('#id_company_allocation').on('click', function (event) {
              if($('#hid_company_allocation').val() == undefined ){
                var cus_alloca = $('#id_order_allocation').magicSuggest()
                cus_alloca.clear();
              }
              if($('#hid_company_allocation').val() != undefined ){
                var company_id = $("#id_company_allocation").magicSuggest();
                var comp_id = company_id.getSelection();
                var company_id = comp_id[0]["id"]
                var company_name = comp_id[0]["name"]
                if(company_id != ""){
                  sparrow.post(
                      "/qualityapp/show_auto_define_assignment_flow/",
                    {company_id : company_id},
                    false,
                    function (data) {
                        if(data.order_allocation != null){
                          var cus_alloca = $('#id_order_allocation').magicSuggest()
                          cus_alloca.clear();
                          cus_alloca.setSelection([ { name: data.allocation_name, id: data.order_allocation }, ])
                        }
                        if(data.order_allocation == null){
                        var cus_alloca = $('#id_order_allocation').magicSuggest()
                        cus_alloca.clear();
                        }
                    })
                }
              }
            });

            $scope.saveAllocationFlow = function (event) {
              allocation = []
              var customer_alloc = $("#hid_company_allocation").val();
              var alloca_ = $("#hid_order_allocation").val();
              var customer_al = $('#id_company_allocation').magicSuggest()
              $(customer_al).on("selectionchange", function (e, m) {
                var customer_al_id = $("#hid_company_allocation").val()
                if (customer_al_id) {
                  $("#id_message_company_allocation").hide();
                  $('#id_company_allocation').css('border-color', '#ccc');
                }
              });
              var allocaa_ = $('#id_order_allocation').magicSuggest()
              $(allocaa_).on("selectionchange", function (e, m) {
                var allocaa__id = $("#hid_order_allocation").val()
                if (allocaa__id) {
                  $("#id_message_order_allocation").hide();
                  $('#id_order_allocation').css('border-color', '#ccc');
                }
              });
              if (customer_alloc == undefined){
                $('#id_company_allocation').css('border-color', '#a94442');
                $("#id_message_company_allocation").show();
              }
              if (alloca_ == undefined){
                $('#id_order_allocation').css('border-color', '#a94442');
                $("#id_message_order_allocation").show();
              }
              if (alloca_ == undefined || customer_alloc == undefined){
                return;
              }
              var company_id = $("#id_company_allocation").magicSuggest();
              var comp_id = company_id.getSelection();
              var company_id = comp_id[0]["id"]
              var company_name = comp_id[0]["name"]
              var order_allocation = $("#id_order_allocation").magicSuggest();
              var order_allocation_name = order_allocation.getSelection();
              var order_allocation_id = order_allocation_name[0]["id"]
              allocation.push(order_allocation_id, company_id)
              var postData = {
                company_id: company_id,
                order_allocation: order_allocation_id,
              };
              sparrow.post(
                "/qualityapp/auto_define_assignment_flow/",
              postData,
              false,
              function (data) {
                if (data.code == 1) {
                  sparrow.showMessage("appMsg", sparrow.MsgType.Success, data.msg, 3);
                  var process = $('#id_process').magicSuggest()
                  process.clear();
                  $('#load_btn').click()
                }
              }
            );
            $("#allocationFlow").modal('toggle');
            var customer = $('#id_company').magicSuggest()
            customer.clear();
            customer.setSelection([ { name: company_name, id: company_id }, ])
            }

          $scope.ReserveorderList = [];
          function OnReserve() {
            $scope.ReserveorderList = [];
            if (data.permissions['reserve_order_allocation'] == false) {
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

      function OnRelease() {
          if (data.permissions['release_order_allocation'] == false) {
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
            if (rowData[0].operator__user__username == null) {
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
                    }
                  }
                );
              }
            }
          );
      };

      function onExport() {
        if (data.permissions["can_export_order_allocation"] == false) {
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "You do not have permission to perform this action", 3);
          return;
        }
        dtBindFunction();
        var postData = $scope.postData;
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id;
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
        sparrow.downloadData("/qualityapp/exports_order_allocations/", {
          company_id: postData["company_id"],
          process_id: postData["process_id"],
          start: $rootScope.start,
          length: $rootScope.length,
          order_by: order_by_,
        });
      };

      function onAllDataExport() {
        if (data.permissions["can_export_order_allocation"] == false) {
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "You do not have permission to perform this action", 3);
          return;
        }
        dtBindFunction();
        var postData = $scope.postData;
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id;
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
        sparrow.downloadData("/qualityapp/exports_order_allocations/", {
          company_id: postData["company_id"],
          process_id: postData["process_id"],
          start: 0,
          length: display_data[0].recordsTotal,
          order_by: order_by_,
        });
      };


      Mousetrap.bind("shift+r", OnReserve);
      Mousetrap.bind("shift+l", OnRelease);
      Mousetrap.bind("shift+s", function(){
          $("#load_btn").click()
      });
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

order_allocationsInit();