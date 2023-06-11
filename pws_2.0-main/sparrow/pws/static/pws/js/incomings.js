function incomingsInit(data) {
  sparrow.registerCtrl(
    "incomingsCtrl",
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
      var type = data.type;
      $scope.allPageTitles = {
        in_coming: "Exception (In coming)",
        put_to_customer: "Exception (Put to customer)",
      };
      var pageTitle = $scope.allPageTitles[type];
      $scope.allIndex = {
        in_coming: 1,
        put_to_customer: 2,
      };
      $scope.tabIndex = $scope.allIndex[type];
      $scope.requestStatus = {
        in_coming: false,
        put_to_customer: false,
      };
      $scope.requestStatus[type] = true;
      var searchObj = {
        params: [
          { key: "customer_order_nr", name: "Order number" },
          { key: "layer", name: "Layer" },
          { key: "company", name: "Customer name" },
          { key: "service", name: "Service" },
          { key: "exception_nr", name: "Exception number" },
          { key: "order_number", name: "PWS ID" },
          { key: "pcb_name", name: "PCB name" },
          { key: "pre_define_problem", name: "Prob statement" },
          { key: "created_on", name: "Exception date", type: "datePicker" },
        ],
      };
      var in_coming_col = [
        {
          name: "exception_nr",
          title: "Exception number",
          renderWith: viewExceptionLink,
        },
        {
          name: "order__order_number",
          title: "PWS ID",
          renderWith: viewOrderLink,
        },
        {
          name: "order__customer_order_nr",
          title: "Order number",
        },
        {
          name: "order__company",
          title: "Customer name",
        },
        {
          name: "created_on",
          title: "Exception date",
        },
        {
          name: "order__service",
          title: "Service",
        },
        {
          name: "created_by",
          title: "Created by",
        },
        {
          name: "order__layer",
          title: "Layers",
        },
        {
          name: "include_assembly",
          title: "Include assembly",
          sort: false,
        },
        {
          name: "order__pcb_name",
          title: "PCB name",
        },
        {
          name: "order__delivery_term",
          title: "Delivery term",
        },
        {
          name: "order__delivery_date",
          title: "Delivery date",
        },
        {
          name: "pre_define_problem",
          title: "Prob statement",
        },
        {
          name: "order__remarks",
          title: "Remark",
          class: "remarks",
          sort: false,
        },
        {
          name: "order_status",
          title: "Origin of problem",
        },
      ];
      var put_to_customer_col = [
        {
          name: "exception_nr",
          title: "Exception number",
          renderWith: viewExceptionLink,
        },
        {
          name: "order__order_number",
          title: "PWS ID",
          renderWith: viewOrderLink,
        },
        {
          name: "order__customer_order_nr",
          title: "Order number",
        },
        {
          name: "order__company",
          title: "Customer name",
        },
        {
          name: "created_on",
          title: "Exception date",
        },
        {
          name: "order__service",
          title: "Service",
        },
        {
          name: "created_by",
          title: "Created by",
        },
        {
          name: "order__layer",
          title: "Layers",
        },
        {
          name: "include_assembly",
          title: "Include assembly",
          sort: false,
        },
        {
          name: "order__pcb_name",
          title: "PCB name",
        },
        {
          name: "order__delivery_term",
          title: "Delivery term",
        },
        {
          name: "order__delivery_date",
          title: "Delivery date",
        },
        {
          name: "pre_define_problem",
          title: "Prob statement",
        },
        {
          name: "order__remarks",
          title: "Remark",
          class: "remarks",
          sort: false,
        },
        {
          name: "order_status",
          title: "Origin of problem",
        },
        {
          name: "total_reminder",
          title: "Total reminder",
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
              id: "btnModifyException",
              multiselect: false,
              function: showModifyException,
            },
            {
              id: "btnViewDetails",
              multiselect: true,
              noselect: true,
            },
            {
              id: "btnPutToCustomer",
              multiselect: false,
              function: onPutToCustomer,
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
              id: "btnSendback",
              multiselect: false,
              function: showSendBack,
            },
            {
              id: "btnBackToInComing",
              multiselect: false,
              function: onBackToInComing,
            },
            {
              id: "btnSendReminder",
              multiselect: false,
              function: onSendReminder,
            },
            {
              id: "btnSendReminderIncoming",
              multiselect: false,
              function: onSendReminderIncoming,
            },
            {
              id: "btnCancel",
              multiselect: false,
              function: onCancel,
            },
          ],
        },
        listing: [
          {
            index: 1,
            search: searchObj,
            url:
              "/pws/exceptions_search/in_coming/0/" +
              $scope.requestStatus["in_coming"] +
              "/",
            crud: true,
            scrollBody: true,
            columns: in_coming_col,
          },
          {
            index: 2,
            search: searchObj,
            url:
              "/pws/exceptions_search/put_to_customer/0/" +
              $scope.requestStatus["put_to_customer"] +
              "/",
            crud: true,
            scrollBody: true,
            columns: put_to_customer_col,
          },
        ],
      };
      $scope.status = type;
      $scope.onTabChange = function (status, index) {
        $scope.clearSelection(index);
        $scope.tabIndex = index;
        $scope.status = status;
        sparrow.setTitle($scope.allPageTitles[status]);

        history.replaceState(
          undefined,
          undefined,
          "#/exceptions/incoming/?state=" + status
        );
        sparrow.pushLocationHistory(
          $route.current.originalPath,
          "#/exceptions/incoming/?state=" + status
        );
        if ($scope.requestStatus[status] == false) {
          config.listing[index - 1].url =
            "/pws/exceptions_search/" + status + "/0/true/";
          $scope.requestStatus[status] = true;
        }
        btnConfiguration(status);
        $route.reload()
      };

      function btnConfiguration(status) {
        $("#btnFiles").show();
        $("#btnModifyException").show();
        $("#btnViewDetails").show();
        $("#btnPutToCustomer").show();
        $("#btnHistory").show();
        $("#btnExport").show();
        $("#btnSendback").show();
        $("#btnCancel").show();
        $("#btnSendReminderIncoming").show();
        $("#btnSendReminder").hide();
        $("#btnBackToInComing").hide();
        // for shortcut key
        Mousetrap.bind('shift+m', function() {
           if(status == "in_coming"){
            	showModifyException();
            }
        });
        Mousetrap.bind('shift+u', function() {
           if(status == "in_coming"){
            	onPutToCustomer();
            }
        });
        Mousetrap.bind('shift+b', function() {
            if(status == "in_coming"){
              showSendBack();
            }
         });
        Mousetrap.bind('shift+v',function(){
            var order_exception_id = $scope.getSelectedIds($scope.tabIndex)[0];
            var rowData = $.grep(
                $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
                function (n, i) {
                  return n.id == order_exception_id;
                }
            );
            if(order_exception_id){
                $scope.viewOrderDetails(rowData[0].order__id,  rowData[0].order__order_number)
            }
            else{
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
            }
        })

        if (status == "put_to_customer") {
          $("#btnFiles").show();
          $("#btnViewDetails").show();
          $("#btnHistory").show();
          $("#btnSendReminder").show();
          $("#btnExport").show();
          $("#btnSendback").hide();
          $("#btnBackToInComing").show();
          $("#btnModifyException").hide();
          $("#btnPutToCustomer").hide();
          $("#btnSendReminderIncoming").hide();
          $("#btnCancel").hide();

        }
      }
       $('#sendBackToProcess').on('shown.bs.modal', function () {
          $('#id_remarks_back').focus();
      })
      function onPutToCustomer(){
          if (data.permissions['can_put_to_customer'] == false) {
              sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
              return;
          }
          else{
              var order_exception_id = $scope.getSelectedIds($scope.tabIndex)[0];
              var rowData = $.grep(
                    $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
                    function (n, i) {
                      return n.id == order_exception_id;
                    }
                  );
              if(order_exception_id){
                  if(rowData[0].mail_to_customer || rowData[0].pre_define_problem == "Internal Exception"){
                    sparrow.post(
                        "/pws/mail_screen_file/",
                        {
                          order_exception_id:order_exception_id,
                          order_id:rowData[0].order__id,
                          order_number:rowData[0].order__customer_order_nr,
                          company_name:rowData[0].order__company,
                        },
                        false,
                        function(data){
                          if(data.code == 1){
                                var to_emails = data.mail_to_customer;
                                var cc_mails = data.mail_to_cc;
                                if(data.upload_image){
                                  var upload_image =data.upload_image
                                }else{
                                    var upload_image = ""
                                }
                                if(data.si_file){
                                  var si_file = data.si_file
                                }else{
                                    var si_file = ""
                                }
                                var emailTeplate = {
                                    subject:data.subject,
                                    template:data.message,
                                };
                                attachments =[
                                        {
                                          upload_image : upload_image.name,
                                          upload_image_uid :upload_image.uid,
                                        },
                                        {
                                          si_file : si_file.name,
                                          si_file_uid :si_file.uid,
                                        },
                                    ]

                                sparrow.showMailScreen(ModalService,
                                  'Exception put to customer',
                                  "",
                                  "",
                                  attachments,
                                  rowData[0].order__id,
                                  "/pws/send_exception_mail/",
                                  to_emails,
                                  cc_mails,
                                  emailTeplate,
                                  "",
                                  "",
                                  function (result) {
                                    if (result) {
                                      sparrow.post(
                                          '/pws/put_to_customer/',
                                          {
                                              order_exception_id: order_exception_id,
                                              order_id:rowData[0].order__id,
                                              company_name:rowData[0].order__company,
                                          },
                                          false,
                                          function(data){
                                              if(data.code == 1){
                                                  $scope.reloadData($scope.tabIndex);
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
                    );
                  }
                  else{
                     sparrow.showConfirmDialog(
                      ModalService,
                      "Are you sure you want send this exception to customer?",
                      "Put to customer",
                      function (confirm) {
                          if (confirm) {
                            sparrow.post(
                                '/pws/put_to_customer/',
                                {
                                    order_exception_id: order_exception_id,
                                    order_id:rowData[0].order__id,
                                    company_name:rowData[0].order__company,
                                },
                                false,
                                function(data){
                                    if(data.code == 1){
                                        $scope.reloadData($scope.tabIndex);
                                        sparrow.showMessage(
                                            "appMsg",
                                            sparrow.MsgType.Success,
                                            data.msg,
                                            3
                                        );
                                    }
                                }
                            )
                      }})
                  }
               }
              else{
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
              }
          }
      }


      function onBackToInComing(){
          if (data.permissions['can_back_to_incoming'] == false) {
              sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
              return;
          }
          else{
              var order_exception_id = $scope.getSelectedIds($scope.tabIndex)[0];
              var rowData = $.grep(
                  $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
                  function (n, i) {
                    return n.id == order_exception_id;
                  }
                );
              sparrow.showConfirmDialog(
                  ModalService,
                  "Are you sure you want send exception back to In coming stage?",
                  "Back to In coming",
                  function (confirm) {
                      if (confirm) {
                          sparrow.post(
                              '/pws/back_to_in_coming/',
                              {
                                  order_exception_id: order_exception_id,
                                  order_id:rowData[0].order__id,
                              },
                              false,
                              function(data){
                                  if(data.code == 1){
                                      $scope.reloadData($scope.tabIndex);
                                      sparrow.showMessage(
                                          "appMsg",
                                          sparrow.MsgType.Success,
                                          data.msg,
                                          3
                                      );
                                  }
                              }
                          );
                      }
                  }
              )
          }
      }

      function onSendReminderIncoming() {
        if (data.permissions["can_send_reminder"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        var order_exception_id = $scope.getSelectedIds($scope.tabIndex)[0];
        var rowData = $.grep(
          $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
          function (n, i) {
            return n.id == order_exception_id;
          }
        );
        if (rowData[0].pre_define_problem != "Internal Exception") {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "Reminder can not be sent from this stage other than Internal exceptions.",
            3
          );
          return;
        }
        if (order_exception_id) {
          sparrow.post(
            "/pws/incoming_reminder_mail_screen/",
            {
              order_exception_id: order_exception_id,
              order_id: rowData[0].order__id,
              order_number: rowData[0].order__customer_order_nr,
              company_name: rowData[0].order__company,
            },
            false,
            function (data) {
              if (data.code == 1) {
                var to_emails = data.mail_to_customer;
                var cc_mails = data.mail_to_cc;
                if (data.upload_image) {
                  var upload_image = data.upload_image;
                } else {
                  var upload_image = "";
                }
                if (data.si_file) {
                  var si_file = data.si_file;
                } else {
                  var si_file = "";
                }
                var emailTeplate = {
                  subject: data.subject,
                  template: data.message,
                };
                attachments = [
                  {
                    upload_image: upload_image.name,
                    upload_image_uid: upload_image.uid,
                  },
                  {
                    si_file: si_file.name,
                    si_file_uid: si_file.uid,
                  },
                ];

                sparrow.showMailScreen(
                  ModalService,
                  "Reminder for internal exception",
                  "",
                  "",
                  attachments,
                  rowData[0].order__id,
                  "/pws/send_exception_mail/",
                  to_emails,
                  cc_mails,
                  emailTeplate,
                  "",
                  "",
                  function (result) {
                    if (result) {
                      sparrow.post(
                        "/pws/incoming_send_reminder/",
                        {
                          order_exception_id: order_exception_id,
                          order_id: rowData[0].order__id,
                          cc_mail: rowData[0].mail_to_cc,
                        },
                        false,
                        function (data) {
                          if (data.code == 1) {
                            $scope.reloadData($scope.tabIndex);
                            sparrow.showMessage(
                              "appMsg",
                              sparrow.MsgType.Success,
                              data.msg,
                              3
                            );
                          } else {
                            sparrow.showMessage(
                              "appMsg",
                              sparrow.MsgType.Error,
                              data.msg,
                              3
                            );
                          }
                        }
                      );
                    }
                  }
                );
              }
            }
          );
        } else {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "Please select record",
            2
          );
        }
      };

      function onSendReminder(){
          if (data.permissions['can_send_reminder'] == false) {
              sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
              return;
          }
          else{
              var order_exception_id = $scope.getSelectedIds($scope.tabIndex)[0];
              var rowData = $.grep(
                    $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
                    function (n, i) {
                      return n.id == order_exception_id;
                    }
                  );
              sparrow.showConfirmDialog(
                  ModalService,
                  "Are you sure you want send exception reminder to customer?",
                  "Send reminder",
                  function (confirm) {
                      if(confirm) {
                        sparrow.post(
                          '/pws/send_reminder/',
                          {
                            order_exception_id: order_exception_id,
                            total_reminder:rowData[0].total_reminder,
                            order_id:rowData[0].order__id,
                            cc_mail:rowData[0].mail_to_cc,
                          },
                          false,
                          function(data){
                            if(data.code == 1){
                                $scope.reloadData($scope.tabIndex)
                                sparrow.showMessage("appMsg", sparrow.MsgType.Success, data.msg, 3);
                            }
                            else{
                                sparrow.showMessage("appMsg", sparrow.MsgType.Error, data.msg, 3);
                            }
                          }
                          );
                      }
                  }
              )
          }
      }


      function showSendBack(){
          if (data.permissions['can_send_back'] == false) {
              sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
              return;
          }
          else{
               var order_exception_id = $scope.getSelectedIds($scope.tabIndex)[0];
               if(order_exception_id){
                  $("#sendBackToProcess").modal("show");
                  setAutoLookup("id_remarks_type_back", "/lookups/remark_type/", "", true, "", "", "", 1,);
                  var remarks_type_back = $('#id_remarks_type_back').magicSuggest()
                  remarks_type_back.setSelection([ { name: "Exception Reply Remarks", id: 14 }, ])
               }
               else{
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
               }
          }
      }



      function showHistory(scope){
          var selectedId = $scope.getSelectedIds($scope.tabIndex)[0];
          var rowData = $.grep(
          $scope["dtInstance"+$scope.tabIndex].DataTable.data(),
                  function (n, i) {
                      return n.id == selectedId;
                  }
              );
          if(selectedId){
              window.location.hash =
              "#/auditlog/logs/order/" + rowData[0].order__id + "?title=" + rowData[0].order__customer_order_nr;
          }else{
             sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 3);
          }
      }

      function onExport() {
        if (data.permissions["can_export_exception"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
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
        var customer_order_nr = "";
        var exception_nr = "";
        var order_number = "";
        var company = "";
        var service = "";
        var layer = "";
        var created_on = "";
        var pcb_name = "";
        var pre_define_problem = "";

        if (search_parameter) {
          if ("Order number" in search_parameter) {
            var customer_order_nr = search_parameter["Order number"];
          }
          if ("Exception number" in search_parameter) {
            var exception_nr = search_parameter["Exception number"];
          }
          if ("PWS ID" in search_parameter) {
            var order_number = search_parameter["PWS ID"];
          }
          if ("Customer name" in search_parameter) {
            var company = search_parameter["Customer name"];
          }
          if ("Service" in search_parameter) {
            var service = search_parameter["Service"];
          }
          if ("Layer" in search_parameter) {
            var layer = search_parameter["Layer"];
          }
          if ("Exception date" in search_parameter) {
            var created_on = search_parameter["Exception date"];
          }
          if ("PCB name" in search_parameter) {
            var pcb_name = search_parameter["PCB name"];
          }
          if ("Prob statement" in search_parameter) {
            var pre_define_problem = search_parameter["Prob statement"];
          }
        }
        if (!selectedIds) {
          selectedIds = "";
        }
        if(display_data != ""){
          order_by_ = display_data[0].sort_col
          exception_status = display_data[0].exception_status
        }
        else{
          order_by_ = "-id"
          exception_status =  " "
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        sparrow.downloadData("/pws/exports_exception/", {
          start: $rootScope.start,
          length: $rootScope.length,
          status: exception_status,
          customer_order_nr: customer_order_nr,
          exception_nr: exception_nr,
          order_number: order_number,
          company: company,
          service: service,
          layer: layer,
          created_on: created_on,
          pcb_name: pcb_name,
          pre_define_problem: pre_define_problem,
          ids: selectedIds,
          order_by: order_by_,
        });
      };

      function onAllDataExport() {
        if (data.permissions["can_export_exception"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
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
        var customer_order_nr = "";
        var exception_nr = "";
        var order_number = "";
        var company = "";
        var service = "";
        var layer = "";
        var created_on = "";
        var pcb_name = "";
        var pre_define_problem = "";

        if (search_parameter) {
          if ("Order number" in search_parameter) {
            var customer_order_nr = search_parameter["Order number"];
          }
          if ("Exception number" in search_parameter) {
            var exception_nr = search_parameter["Exception number"];
          }
          if ("PWS ID" in search_parameter) {
            var order_number = search_parameter["PWS ID"];
          }
          if ("Customer name" in search_parameter) {
            var company = search_parameter["Customer name"];
          }
          if ("Service" in search_parameter) {
            var service = search_parameter["Service"];
          }
          if ("Layer" in search_parameter) {
            var layer = search_parameter["Layer"];
          }
          if ("Exception date" in search_parameter) {
            var created_on = search_parameter["Exception date"];
          }
          if ("PCB name" in search_parameter) {
            var pcb_name = search_parameter["PCB name"];
          }
          if ("Prob statement" in search_parameter) {
            var pre_define_problem = search_parameter["Prob statement"];
          }
        }
        if (!selectedIds) {
          selectedIds = "";
        }
        if(display_data != ""){
          order_by_ = display_data[0].sort_col
          exception_status = display_data[0].exception_status
          length = display_data[0].recordsTotal
        }
        else{
          order_by_ = "-id"
          exception_status = " "
          length = 1
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        sparrow.downloadData("/pws/exports_exception/", {
          start: 0,
          length: length,
          status: exception_status,
          customer_order_nr: customer_order_nr,
          exception_nr: exception_nr,
          order_number: order_number,
          company: company,
          service: service,
          layer: layer,
          created_on: created_on,
          pcb_name: pcb_name,
          pre_define_problem: pre_define_problem,
          ids: selectedIds,
          order_by: order_by_,
        });
      };

      function viewExceptionLink(data, type, full, meta) {
        return (
          '<span><a ng-click="showExceptionDetails(' +
          full.id +
          ",'" +
          full.exception_nr +
          "')\">" +
          data +
          "</a></span>"
        );
      }

      $scope.showExceptionDetails = function(orderExceptionId, exception_nr) {
        sparrow.post(
          "/pws/exception_details/",
          {
            orderExceptionId: orderExceptionId,
          },
          false,
          function (data) {
            $("#exceptionDetails").html(data);
            $("#viewExceptionTitle").text("Exception Details: " + exception_nr);
            $("#detailsException").modal("show");
            $("#id_order_exception").val(orderExceptionId);
          },
          "html"
        );
      }


      function showModifyException(scope) {
          if (data.permissions['can_modify_exception'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
                return;
          }
          else{
              var orderExceptionId = $scope.getSelectedIds($scope.tabIndex)[0];
              var rowData = $.grep(
                $scope["dtInstance1"].DataTable.data(),
                    function (n, i) {
                      return n.id == orderExceptionId;
                    }
                  );
              if(orderExceptionId){
                sparrow.post(
                  "/pws/modify_exception/",
                  {
                    orderExceptionId: orderExceptionId,
                  },
                  false,
                  function (data) {
                    $("#exceptionModify").html(data);
                    $("#modifyException").modal("show");
                    $("#viewModifyExceptionTitle").text("Modify Exception: "+rowData[0].exception_nr);
                    $("#id_order_exception").val(orderExceptionId);
                    setAutoLookup(
                      "id_pre_defined_problem",
                      "/lookups/pre_define_problem/",
                      "",
                      true,
                      true
                    );
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
                  },
                  "html"
                );
              }else{
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
              }
          }
        }


      $scope.SavePreDefineProblem = function () {
        var pre_def_prob = $("#hid_pre_defined_problem").val()
        if (!pre_def_prob){
          $("#id_message_pre_defined_problem").show();
          $('#id_pre_defined_problem').css('border-color', '#a94442');
          return;
        }
        var id_si_file = $("#id_si_file").val();
        if(id_si_file){
          var status_id_si_file = id_si_file.toLowerCase().endsWith('.zip')
          if(status_id_si_file == false){
              sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please upload file(SI file) having extension .zip only.", 3);
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
                $("#modifyException").modal("hide");
                $('#frmSaveExceptionProblem').trigger("reset");
                $(".modal-backdrop").remove();
              }
              $route.reload();
            }
          );
        }
      };

      $scope.SaveRemarks = function () {
        var order_exception_id = $scope.getSelectedIds($scope.tabIndex)[0];
        var rowData = $.grep(
          $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
          function (n, i) {
            return n.id == order_exception_id;
          }
        );
        if ((order_exception_id == undefined) & (rowData.length < 0)) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Success,
            "Something wrong",
            3
          );
          return;
        }
        var postData = {
          order_exception_id: order_exception_id,
          order_id: rowData[0].order__id,
          order_status: rowData[0].order_status_code,
        };
        sparrow.postForm(
          postData,
          $("#frmSaveRemarks"),
          $scope,
          function (data) {
            if (data.code == 1) {
              $("#sendBackToProcess").modal("hide");
              $(".modal-backdrop").remove();
              $("#frmSaveRemarks").trigger("reset");
            }
            $scope.reloadData($scope.tabIndex);
          }
        );
      };

      function viewOrderLink(data, type, full, meta) {
        return (
          '<span><a ng-click="viewOrderDetails(' +
          full.order__id +
          ",'" +
          full.order__customer_order_nr +
          "')\">" +
          data +
          "</a></span>"
        );
      }

      $scope.viewOrderDetails = function (order__id, order__customer_order_nr) {
        remarks_ = false
        $scope.onEditLink(
          "/b/iframe_index/#/pws/order/" + order__id  + remarks_,
          "Order - " + order__customer_order_nr,
          closeIframeCallback,
          "",
          "",
          true
        );
      };

      function closeIframeCallback() {
        $scope.reloadData($scope.tabIndex);
        return;
      }

      function onFileSearch() {
          if (data.permissions['can_view_exception_files'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
                return;
            }
          else{
              var selectedId = $scope.getSelectedIds($scope.tabIndex)[0];
              var rowData = $.grep(
                $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
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
                  $scope.permission = data;
                  $scope.is_incomings_section = true
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
      }

      function onCancel() {
          if (data.permissions['cancel_order_exception'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 3);
                return;
            }
          else{
              var selectedId = $scope.getSelectedIds($scope.tabIndex)[0];
              var rowData = $.grep(
                $scope["dtInstance" + $scope.tabIndex].DataTable.data(),
                function (n, i) {
                  return n.id == selectedId;
                }
              );
              sparrow.showConfirmDialog(
                ModalService,
                "Are you sure you want to cancel order?",
                "Cancel order",
                function (confirm) {
                  if (confirm) {
                    sparrow.post(
                      "/pws/exception_order_cancel/" + rowData[0].order__id + "/",
                      {
                        exception_id:rowData[0].id
                      },
                      false,
                      function (data) {
                        if (data.code == 1) {
                          sparrow.showMessage(
                            "appMsg",
                            sparrow.MsgType.Success,
                            data.msg,
                            3
                          );
                          $scope.reloadData($scope.tabIndex);
                          return;
                        }
                      }
                    );
                  }
                }
              );
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
      btnConfiguration(type);
    }
  );
}
incomingsInit();
