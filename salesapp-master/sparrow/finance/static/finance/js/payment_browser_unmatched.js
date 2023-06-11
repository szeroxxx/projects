function paymentBrowserUnmatchedInit(data) {
  var paymentBrowserUnmatched = {};
  sparrow.registerCtrl("paymentBrowserUnmatchedCtrl", function (
    $scope,
    $rootScope,
    $route,
    $routeParams,
    $compile,
    DTOptionsBuilder,
    DTColumnBuilder,
    $templateCache,
    $location,
    ModalService
  ) {
    $scope.modalopened = false;
    var config = {
      pageTitle: "Payment browser unmatched",
      topActionbar: {
        extra: [
          {
            id: "btnProformaInvoice",
            multiselect: false,
            function: onbtnProformaInvoice,
          },
          {
            id: "btnsearchInvoices",
            multiselect: false,
            function: oninvoicesearch,
          },
          {
            id: "btnsearchProformaInvoices",
            multiselect: false,
            function: onproformasearch,
          },
        ],
      },
      listing: [
        {
          index: 1,
          search: {
            params: [
              { key: 'name', name: 'Name'},
              { key: "bank_account_number", name: "Bank account number" },
              { key: "payment_amount", name: "Payment amount" },
              { key: "payment_message", name: "Payment message" },
              // { key: 'create_date', name: 'Create date'},
              { key: "bank_name", name: "Bank name" },
              {
                key: "create_date",
                name: "Created from date till date",
                type: "datePicker",
              },
              { key: 'country', name: 'Country'},

            ],
          },
          url: "/finance/payment_browser_unmatched_search/",
          crud: true,
          columns: [
            { name: 'name', title: 'Name'},
            { name: "bank_account_number", title: "Bank account number" },
            { name: "bank_name", title: "Bank name" },
            { name: "payment_amount", title: "Payment amount" },
            { name: "payment_message", title: "Payment message" },
            { name: "invoice_number", title: "Invoice number" },
            { name: 'country', title: 'Country'},
            { name: "remark", title: "Remark" },
            { name: "create_date", title: "Created date" },
            { name: "Created_by", title: "Created by" },
            { name: "communication", title: "Communication" },
          ],
        },
      ],
    };
    config.listing[0].columns.forEach(columnSort);
    function columnSort(obj) {
      obj.sort = false;
    }

    function selectedRowLength(){
      if ($route.current.controller != 'paymentBrowserUnmatchedCtrl'){
              return false;
          }
            if($scope.getSelectedIds(1).length==0 || $scope.getSelectedIds(1).length > 1 ){
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select one invoice', 10);
                return false
            }

            return true
        }

        Mousetrap.bind('s i', function() {
            if (selectedRowLength() == true){
                oninvoicesearch()
            }
        });

        Mousetrap.bind('s p', function() {
            if (selectedRowLength() == true){
                onproformasearch()
            }
        });



    function getRowData() {
      var selectedId = $scope.getSelectedIds(1)[0];
      var rowData = $.grep($scope["dtInstance1"].DataTable.data(), function (
        n,
        i
      ) {
        return n.id == selectedId;
      });
      return rowData[0];
    }

    function onbtnProformaInvoice() {
      rowDta = getRowData();
      var invoice_num = rowDta.invoice_number;
      var doc_type = "performa";
      window.open(
        "/sales/get_ec_customer_inv_doc/" + invoice_num + "/" + doc_type + "/"
      );
    }
    function onproformasearch(){
      onsearchProforma_or_searchInvoices("SearchUnmatchedProforma")

    }
    function oninvoicesearch(){
      onsearchProforma_or_searchInvoices("SearchUnmatchedInvoice")
    }
    function onsearchProforma_or_searchInvoices(functionName) {
      var row_data = getRowData();
      var postData = {
        funname: functionName,
        Customer_Name: row_data.name,
        Amount: row_data.payment_amount,
        InvoiceNr: row_data.invoice_number,
      };
      sparrow.post(
        "/finance/invoice_proforma_search/",
        postData,
        false,
        function (data) {
          if (data.code == "1") {
            if (data.funname == "SearchInvoice") {
              var customerName = data.searchdata["c.CustomerName"];
              on_inv_search(customerName);
            } else if (data.funname == "SearchProformaInvoice") {
              var customerName = data.searchdata["so.CustomerName"];
              onsearchProformaInvoices(customerName);
            }
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
    }
    function on_inv_search(customerName) {
      if ($scope.modalopened) return;
      $scope.onEditLink(
        "/b/iframe_index/#/finance/invoices/" + customerName + "/",
        "Invoices",dialogCloseCallback
      );
      $scope.modalopened = true;
    }


    function onsearchProformaInvoices(customerName) {
      if ($scope.modalopened) return;
      $scope.onEditLink(
        "/b/iframe_index/#/finance/proforma_invoices/" + customerName + "/",
        "Proforma invoices",dialogCloseCallback
      );
      $scope.modalopened = true;
    }
    function dialogCloseCallback(){
            $scope.modalopened = false;
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
  });

  return paymentBrowserUnmatched;
}

var paymentBrowserUnmatched = paymentBrowserUnmatchedInit();
