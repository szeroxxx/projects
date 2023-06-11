function invoicesInit(data) {
  var invoices = {};
  sparrow.registerCtrl(
    "invoicesCtrl",
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
      $location,
      ModalService
    ) {
      var customerSearch = { key: "customer", name: "Customer" };
      var statusSearch = { key: "invoice_status", name: "Invoice status" };
      if (sparrow.inIframe()) {
        if (data.customer_name != "") {
          customerSearch = {
            key: "customer",
            name: "Customer",
            default_val: data.customer_name,
          };
          statusSearch = {
            key: "invoice_status",
            name: "Invoice status",
            default_val: "Pending",
          };
        }
        $("#top_action_bar").hide();
      }
      $scope.modalopened = false;

      var config = {
        pageTitle: "Invoices",
        topActionbar: {
          extra: [
            {
              id: "btnGrantDays",
              multiselect: false,
              function: grantDays,
            },
            {
              id: "btnCreditLimit",
              multiselect: false,
              function: creditLimit,
            },
            {
              id: "btnEditProfile",
              multiselect: false,
              function: onbtnEditProfile,
            },
            {
              id: "btnCustomerLogin",
              multiselect: false,
              function: onCustomerLogin,
            },
            {
              id: "btnCustomerFinReport",
              multiselect: false,
              function: onCustomerFinReport,
            },
            {
              id: "btnChangeSecondaryStatus",
              multiselect: false,
              function: onChangeSecodaryStatus,
            },
            {
              id: "btnDeliveryNote",
              multiselect: false,
              function: onbtnDeliveryNote,
            },
            {
              id: "btnInvoice",
              multiselect: false,
              function: onbtnInvoice,
            },
            {
              id: "btnProformaInvoice",
              multiselect: false,
              function: onbtnProformaInvoice,
            },
            {
              id: "btnCreditStatus",
              multiselect: false,
              function: onbtnCreditStatus,
            },
            {
              id: "btnInvoiceHistory",
              multiselect: false,
              function: onbtnInvoiceHistory,
            },
            {
              id: "btncreditReport",
              multiselect: false,
              function: onbtnCreditReport,
            },
            {
              id: "btnCreateTask",
              multiselect: false,
              function: onbtnCreateTask,
            },
          ],
        },
        listing: [
          {
            index: 1,
            search: {
              params: [
                { key: "invoice_number", name: "Invoice number" },
                {
                  key: "invoice_date__date",
                  name: "Invoice from date till date",
                  type: "datePicker",
                },
                {
                  key: "invoice_dueDate__date",
                  name: "Invoice due date",
                  type: "datePicker",
                },
                { key: "invoice_value", name: "Invoice value" },
                // { key: 'order_number', name: 'Order number'},
                // { key: 'invoice_status', name: 'Invoice status'},
                {
                  key: "invoice_secondary_status",
                  name: "Invoice secondary status",
                },
                { key: "country", name: "Country" },
                customerSearch,
                statusSearch,
                { key: "handling_company", name: "Handling company" },
                { key: "root_company", name: "Root company" },
                { key: "postal_code", name: "Postal code" },
                { key: "city", name: "City" },
                { key: "phone", name: "Phone" },
                { key: "vat_nr", name: "VAT nr" },
                { key: "payment_tracking_id", name: "Payment tracking id" },
                // { key: 'invoice_dueDate', name: 'Invoice due date'},
                { key: "phone", name: "Phone" },
                // { key: 'pcb_name', name: 'PCB name'},
                // { key: 'username', name: 'Username'},
              ],
            },
            url: "/finance/invoices_search/",
            crud: true,
            paging: true,
            columns: [
              { name: "invoice_number", title: "Invoice number" },
              { name: "invoice_date", title: "Invoice date" },
              { name: "last_rem_date", title: "Last Rem date" },
              { name: "exchange_rate", title: "Exchange rate" },
              { name: "currency_symbol", title: "Currency symbol" },
              { name: "outstanding", title: "Outstanding" },
              { name: "cust_outstanding", title: "Cust outstanding" },
              { name: "invoice_dueDate", title: "Invoice due date" },
              { name: "financial_blocked", title: "Financial blocked" },
              { name: "credit_limit", title: "Credit limit" },
              { name: "cust_credit_limit", title: "Cust credit limit" },
              {
                name: "customer",
                title: "Customer",
                renderWith: function (data, type, full, meta) {
                  return (
                    '<span>\
                                   <a class="link-iframe-item" ng-click="onEditLink(\'/b/iframe_index/#/sales/customer/inv/' +
                    full.customer_id +
                    "/true/true" +
                    "/','Customer profile - " +
                    data +
                    "'," +
                    null +
                    ", " +
                    false +
                    ", " +
                    1 +
                    "," +
                    true +
                    ')">' +
                    data +
                    "</a>\
                               </span>"
                  );
                },
              },
              { name: "customer_type", title: "Customer type" },
              { name: "root_company", title: "Root company" },
              { name: "invoice_value", title: "Invoice value" },
              { name: "cust_invoice_value", title: "Cust invoice value" },
              { name: "invoice_status", title: "Invoice status" },
              { name: "recent", title: "Recent" },
              { name: "communication", title: "Communication" },
              { name: "amount_paid", title: "Amount paid" },
              { name: "cust_amountPaid", title: "Cust amountPaid" },
              { name: "payment_date", title: "Payment date" },
              { name: "delivery_nr", title: "Delivery nr" },
              { name: "vat_nr", title: "VAT nr" },
              { name: "country", title: "Country" },
              { name: "address_line1", title: "Address line1" },
              { name: "accounting_no", title: "Accounting no" },
              { name: "address_line2", title: "Address line2" },
              { name: "postal_code", title: "Postal code" },
              { name: "city", title: "City" },
              { name: "email", title: "Email" },
              { name: "phone", title: "Phone" },
              { name: "fax", title: "Fax" },
              { name: "match", title: "Match" },
              { name: "handling_company", title: "Handling company" },
              // { name: 'order_number', title: 'Order number'},
              { name: "payment_status", title: "Payment status" },
              {
                name: "deliver_invoice_by_post",
                title: "Deliver invoice by post",
              },
              { name: "isInvoice_deliver", title: "Is invoice deliver" },
              {
                name: "invoice_secondary_status",
                title: "Invoice secondary status",
              },
              { name: "invoice_delivery", title: "Invoice delivery" },
              { name: "payment_tracking_id", title: "Payment tracking id " },
              // { name: 'pcb_name', title: 'PCB name'},
              // { name: 'username', title: 'Username'},
            ],
          },
        ],
      };
      config.listing[0].columns.forEach(columnSort);
      function columnSort(obj) {
        obj.sort = false;
      }

      function selectedRowLength() {
        if ($route.current.controller != "invoicesCtrl") {
          return false;
        }
        if (
          $scope.getSelectedIds(1).length == 0 ||
          $scope.getSelectedIds(1).length > 1
        ) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "Please select one invoice",
            10
          );
          return false;
        }

        return true;
      }

      Mousetrap.bind("i", function () {
        if (selectedRowLength() == true) {
          onbtnInvoice();
        }
      });

      Mousetrap.bind("p i", function () {
        if (selectedRowLength() == true) {
          onbtnProformaInvoice();
        }
      });

      Mousetrap.bind("l", function () {
        if (selectedRowLength() == true) {
          onCustomerLogin();
        }
      });

      Mousetrap.bind("e p", function () {
        if (selectedRowLength() == true) {
          onbtnEditProfile();
        }
      });

      Mousetrap.bind("f r", function () {
        if (selectedRowLength() == true) {
          onCustomerFinReport();
        }
      });
      Mousetrap.bind("g d", function () {
        if (selectedRowLength() == true) {
          grantDays();
        }
      });
      Mousetrap.bind("c l", function () {
        if (selectedRowLength() == true) {
          creditLimit();
        }
      });
      Mousetrap.bind("c r", function () {
        if (selectedRowLength() == true) {
          onbtnCreditReport();
        }
      });
      Mousetrap.bind("c s", function () {
        if (selectedRowLength() == true) {
          onbtnCreditStatus();
        }
      });
      Mousetrap.bind("d n", function () {
        if (selectedRowLength() == true) {
          onbtnDeliveryNote();
        }
      });
      Mousetrap.bind("s s", function () {
        if (selectedRowLength() == true) {
          onChangeSecodaryStatus();
        }
      });
      Mousetrap.bind("h", function () {
        if (selectedRowLength() == true) {
          onbtnInvoiceHistory();
        }
      });

      function onbtnCreateTask() {
        // if (data.permissions["can_grant_days"]) {
        var title = "Create task - " + getRowData().invoice_number;
        $("#createTaskTitle").text(title);
        $("#id_task_title").val(getRowData().invoice_number + " - ");
        console.log("id_task_title");
        console.log($("#id_task_title").val());
        $("#createTaskModal").modal("show");

        // $("#id_grantdays").val("");
        // } else {
        //   sparrow.showMessage(
        //     "appMsg",
        //     sparrow.MsgType.Error,
        //     "You do not have permission to perform this action",
        //     10
        //   );
        // }
      }
      $scope.oncreateTask = function () {
        console.log($("#id_task_title").val());
        console.log($("#id_task_desc").val());
        var postData = {
          task_title: $("#id_task_title").val(),
          desc: $("#id_task_desc").val(),
        };
        sparrow.postForm(
          postData,
          $("#frmCreateTask"),
          $scope,
          function (data) {
            console.log(data.code, typeof data.code);
            if (data.code == 1) {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Success,
                "Task created",
                10
              );
              $("#id_task_title").val("");
              $("#id_task_desc").val("");
              $("#createTaskModal").modal("hide");
            } else {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                "Something went wrong.",
                10
              );
            }
          }
        );
      };

      function grantDays() {
        if (data.permissions["can_grant_days"]) {
          var title = "Enter grant days - " + getRowData().invoice_number;
          $("#grantDaysTitle").text(title);
          $("#grantDaysModal").modal("show");
          $("#id_grantdays").val("");
        } else {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            10
          );
        }
      }

      function creditLimit() {
        if (data.permissions["can_update_invoice_credit_limit"]) {
          var templateUrl =
            "/finance/credit_limit/" + getRowData().customer_id + "/";
          function openmodal() {
            if ($scope.modalopened) return;
            var creditLimitModal = $uibModal.open({
              templateUrl: templateUrl,
              controller: "creditLimitModalCtrl",
              scope: $scope,
              size: "md",
              backdrop: false,
            });
            $scope.modalopened = true;
            $scope.creditLimitModalTitle =
              "Credit limit - " + getRowData().customer;
            creditLimitModal.closed.then(function () {
              $scope.modalopened = false;
              $templateCache.remove(templateUrl);
            });
          }
          openmodal();
        } else {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            10
          );
        }
      }

      $scope.saveGrantDays = function (event) {
        if (
          $("#id_grantdays").val() == "" ||
          $("#id_grantdays").val() == undefined
        ) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "Please enter value",
            10
          );
          return;
        }
        sparrow.post(
          "/finance/save_grant_days/",
          {
            invoice_id: $scope.getSelectedIds(1)[0],
            days: $("#id_grantdays").val(),
          },
          true,
          function (data) {
            if (data.code == 1) {
              $scope.reloadData(1);
              $("#grantDaysModal").modal("hide");
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Success,
                "Days are granted",
                10
              );
            } else {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                data.msg,
                10
              );
              return;
            }
          }
        );
      };

      function onbtnEditProfile(scope) {
        var customerId = getRowData().customer_id;
        if ($scope.modalopened) return;
        $scope.onEditLink(
          "/b/iframe_index/#/sales/customer/inv/" + customerId + "/true/true/",
          "Customer profile - " + getRowData().customer,
          dialogCloseCallback,
          false,
          "+1+",
          true
        );
        $scope.modalopened = true;
      }
      function dialogCloseCallback() {
        $scope.modalopened = false;
      }

      function onCustomerLogin() {
        if (data.permissions["can_customer_login_invoices"]) {
          var customer_id = getRowData().customer_id;
          var inv_nr = getRowData().invoice_number.split("/").join("-");
          sparrow.post(
            "/sales/validate_customer_login/",
            { customer_id: customer_id, from: "INVOICE" },
            false,
            function (data) {
              if (data.code == "1") {
                if (data.msg == "") {
                  var ec_user_id = data.ec_user_id;
                  var from = "INVOICE";
                  window.open(
                    "/sales/customer_login/" +
                      inv_nr +
                      "/" +
                      from +
                      "/" +
                      ec_user_id +
                      "/" +
                      customer_id +
                      "/"
                  );
                } else {
                  function openmodal() {
                    if ($scope.modalopened) return;
                    var templateUrl = "/sales/validate_customer_login_modal/";
                    var customerLoginValidateModal = $uibModal.open({
                      templateUrl: templateUrl,
                      controller: "customerLoginValidateModalCtrl",
                      scope: $scope,
                      size: "md",
                      backdrop: false,
                      resolve: {
                        dataModal: function () {
                          return {
                            entity_nr: inv_nr,
                            msg: data.msg,
                            customer_id: customer_id,
                            from: "INVOICE",
                            ec_user_id: data.ec_user_id,
                          };
                        },
                      },
                    });
                    $scope.modalopened = true;
                    // $scope.customerLoginModalTitle = "Credit report - "+rowDta.customer;
                    $scope.ConfirmMessage = data.msg;
                    customerLoginValidateModal.closed.then(function () {
                      $scope.modalopened = false;
                      $templateCache.remove(templateUrl);
                    });
                  }
                  openmodal();
                }
              }
            }
          );

          // window.open("/sales/customer_login/" + customerId + "/");
        } else {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            10
          );
        }
      }
      function getCustomerId() {
        var selectedId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        return rowData[0].customer_id;
      }
      function onCustomerFinReport() {
        var customerId = getCustomerId();
        sparrow.post(
          "/finance/customer_finance_report/",
          { customer_id: customerId, is_refresh: "false" },
          false,
          function (data) {
            $("#idCustomerInvGrids").html(data);
            var title =
              "Customer financial report - " + $("#idCompanyName").text();
            $("#idCustomerFinReportTitle").text(title);
            $("#customerFinReportModal").modal("show");
          },
          "html"
        );
      }

      function getRowData() {
        var selectedId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        return rowData[0];
      }

      function onbtnCreditReport() {
        var rowDta = getRowData();
        function openmodal() {
          if ($scope.modalopened) return;
          var templateUrl =
            "/finance/credit_report/" + rowDta.customer_id + "/";
          // var templateUrl = "/finance/credit_report/404392/";
          // var templateUrl = "/finance/credit_report/1435130/";
          var creditReportModal = $uibModal.open({
            templateUrl: templateUrl,
            controller: "creditReportModalCtrl",
            scope: $scope,
            size: "lg",
            backdrop: false,
          });
          $scope.modalopened = true;
          $scope.creditReportModalTitle = "Credit report - " + rowDta.customer;
          creditReportModal.closed.then(function () {
            $scope.modalopened = false;
            $templateCache.remove(templateUrl);
          });
        }
        openmodal();
      }
      function onChangeSecodaryStatus() {
        $scope.defaultSecondaryStatus = getRowData().invoice_secondary_status;
        if (data.permissions["can_update_secondary_status"]) {
          sparrow.post(
            "/finance/get_secondary_status_list/",
            {
              invoice_id: $scope.getSelectedIds(1)[0],
              days: $("#id_grantdays").val(),
            },
            false,
            function (data) {
              setAutoLookup("id_secondary_status", data);
              if ($scope.defaultSecondaryStatus != null && data != undefined) {
                for (i in data) {
                  if (data[i].name == $scope.defaultSecondaryStatus) {
                    var secondaryStatus_ms = $(
                      "#id_secondary_status"
                    ).magicSuggest();
                    secondaryStatus_ms.setSelection([
                      { codeid: data[i].codeid, name: data[i].name },
                    ]);
                  }
                }
              }
              var title =
                "Change secondary status - " + getRowData().invoice_number;
              $("#secondaryStatusTitle").text(title);
              $("#secondaryStatusModal").modal("show");
            }
          );
        } else {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            10
          );
        }
      }

      $scope.saveSecondaryStatus = function (e) {
        var selectedId = $scope.getSelectedIds(1)[0];

        var secondaryStatus_ms = $("#id_secondary_status").magicSuggest();
        if (secondaryStatus_ms.getSelection()[0] != undefined) {
          statusCodeId = secondaryStatus_ms.getSelection()[0].codeid;
        } else {
          // statusCodeId = ''
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "Please select a valid entry.",
            10
          );
          return;
        }
        if (
          $scope.defaultSecondaryStatus == null &&
          secondaryStatus_ms.getSelection()[0] == undefined
        ) {
          $("#secondaryStatusModal").modal("hide");
          return;
        }
        sparrow.post(
          "/finance/save_secondary_status/",
          {
            statusId: statusCodeId,
            invoiceId: selectedId,
            customerId: getRowData().customer_id,
          },
          false,
          function (data) {
            sparrow.showMessage(
              "appMsg",
              sparrow.MsgType.Success,
              "Status saved",
              10
            );
            $scope.reloadData(1);
            $("#secondaryStatusModal").modal("hide");
          }
        );
      };

      function onbtnDeliveryNote() {
        var invoice_num = getRowData().invoice_number;
        var doc_type = "deliverynote";
        window.open(
          "/sales/get_ec_customer_inv_doc/" + invoice_num + "/" + doc_type + "/"
        );
      }

      function onbtnInvoice() {
        var invoice_num = getRowData().invoice_number;
        var doc_type = "invoice";
        window.open(
          "/sales/get_ec_customer_inv_doc/" + invoice_num + "/" + doc_type + "/"
        );
      }
      function onbtnProformaInvoice() {
        var invoice_num = getRowData().invoice_number;
        var doc_type = "performa";
        window.open(
          "/sales/get_ec_customer_inv_doc/" + invoice_num + "/" + doc_type + "/"
        );
      }
      $scope.refreshcustomerFinReport = function () {
        var customerId = getCustomerId();
        sparrow.post(
          "/finance/customer_finance_report/",
          { customer_id: customerId, is_refresh: "true" },
          false,
          function (data) {
            $("#idCustomerInvGrids").html(data);
            var title =
              "Customer financial report - " + $("#idCompanyName").text();
            $("#idCustomerFinReportTitle").text(title);
          },
          "html"
        );
      };

      function onbtnCreditStatus() {
        var rowDta = getRowData();

        sparrow.post(
          "/finance/get_credit_status/",
          {
            custUserId: rowDta.custUserId,
            customerId: rowDta.customer_id,
          },
          false,
          function (data) {
            $("#id_creditStatusGrid").html(data);
            $("#creditStatusModal").modal("show");
          },
          "html"
        );
      }
      function onbtnInvoiceHistory() {
        var templateUrl =
          "/finance/get_invoice_history/" + getRowData().id + "/";
        function openmodal() {
          if ($scope.modalopened) return;
          var invoiceHistoryModal = $uibModal.open({
            templateUrl: templateUrl,
            controller: "invoiceHistoryModalCtrl",
            scope: $scope,
            size: "lg",
            backdrop: true,
          });
          $scope.modalopened = true;
          invoiceHistoryModal.closed.then(function () {
            $scope.modalopened = false;
          });
        }
        openmodal();
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

  return invoices;
}

var invoices = invoicesInit();
