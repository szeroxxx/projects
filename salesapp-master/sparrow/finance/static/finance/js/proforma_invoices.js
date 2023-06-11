function proformaInvoicesInit(data) {
    var proformaInvoices = {};
    sparrow.registerCtrl('proformaInvoicesCtrl',function($scope, $rootScope, $route, $routeParams, $compile,$uibModal, DTOptionsBuilder, DTColumnBuilder, $templateCache, $location, ModalService){
        var customerSearch = { key: 'customer', name: 'Customer'};
        if (sparrow.inIframe()) {
            if (data.customer_name !=""){
                customerSearch = { key: 'customer',
                name: 'Customer', default_val:data.customer_name};
            }
            $('#top_action_bar').hide();
        }
        $scope.modalopened = false;
        var config = {
            pageTitle: 'Proforma invoices',
            topActionbar: {
                extra: [
                {
                    id: 'btnCreditLimit',
                    multiselect: false,
                    function: creditLimit,
                },
                {
                    id: 'btnEditProfile',
                    multiselect: false,
                    function: onbtnEditProfile,
                },
                {
                    id:"btnOrderReceipt",
                    multiselect : false,
                    function: onbtnOrderReceipt
                },
                {
                    id:"btnProformInvoice",
                    multiselect : false,
                    function: onbtnProformInvoice
                },
                {
                    id:"btnorderConfirmation",
                    multiselect : false,
                    function: onbtnOrderConf
                },
                {
                    id:"btncreditReport",
                    multiselect : false,
                    function: onbtnCreditReport
                },
                {
                    id:"btnInvoiceHistory",
                    multiselect : false,
                    function: onbtnInvoiceHistory
                },
                ]
            },
            listing: [{
                index : 1,
                search: {
                params:[
                    { key: 'invoice_number', name: 'Invoice number'},
                    { key: "invoice_date__date",name: "Invoice from date till date",type: "datePicker"},
                    { key: 'invoice_value', name: 'Invoice value'},
                    { key: 'order_number', name: 'Order number'},
                    { key: 'pcb_name', name: 'PCB-name'},
                    { key: 'username', name: 'Username'},
                    { key: 'country', name: 'Country'},
                    customerSearch,
                    { key: 'invoice_status', name: 'Invoice status'},
                    // { key: 'invoice_secondary_status', name: 'Invoice secondary status'},
                    { key: 'handling_company', name: 'Handling company'},
                    { key: 'root_company', name: 'Root company'},
                    { key: 'Postal_code', name: 'Postal code'},
                    { key: 'city', name: 'City'},
                    { key: 'phone', name: 'Phone'},
                    { key: 'vat_nr', name: 'VAT nr '},


                ]},
                url: "/finance/proforma_invoices_search/",
                crud: true,
                columns: [
                    { name: 'invoice_number', title: 'Invoice number'},
                    { name: 'DeliveryNo', title: 'Delivery no'},
                    { name: 'order_number', title: 'Order number'},
                    { name: 'invoice_status', title: 'Invoice status'},
                    { name: 'Service', title: 'Service'},
                    { name: 'customer', title: 'Customer', renderWith: function(data, type, full, meta) {
                        return '<span>\
                                   <a class="link-iframe-item" ng-click="onEditLink(\'/b/iframe_index/#/sales/customer/proforma_inv/'+full.customer_id+'/true/true'+'/\',\'Customer profile - ' + data +'\','+null+', '+false+', '+1+','+true+')">'+data+'</a>\
                               </span>';
                    }},
                    { name: 'username', title: 'Username'},
                    { name: 'invoice_value', title: 'Invoice value'},
                    { name: 'Customer1', title: 'Customer 1'},
                    { name: 'CreditLimit', title: 'Credit limit'},
                    { name: 'Currency_Symbol', title: 'Currency symbol'},
                    { name: 'root_company', title: 'Root company'},
                    { name: 'pcb_name', title: 'PCB name'},
                    { name: 'handling_company', title: 'Handling company'},
                    { name: 'CustomerType', title: 'Customer type'},
                    { name: 'Cust_AmountPaid', title: 'Cust amount paid'},
                    { name: 'Cust_Outstanding', title: 'Cust outstanding'},
                    // { name: 'outstanding_only', title: 'Outstanding only'},
                    { name: 'Add1', title: 'Add1'},
                    { name: 'Add2', title: 'Add2'},
                    { name: 'Postal_code', title: 'Postal code'},
                    { name: 'city', title: 'City'},
                    { name: 'phone', title: 'Phone'},
                    { name: 'InvoiceFax', title: 'Fax'},
                    { name: 'vat_nr', title: 'VAT nr '},
                    { name: 'Supplier', title: 'Supplier'},
                    { name: 'country', title: 'Country'},
                    { name: 'OrderStatus', title: 'Order status'},
                    { name: 'LastRemDate', title: 'Last rem date'},
                    { name: 'Exchange_Rate', title: 'Exchange rate'},
                    { name: 'InvoiceDueDate', title: 'Invoice due date'},
                    { name: 'Payment_Date', title: 'Payment date'},
                    { name: 'invoice_secondary_status', title: 'Invoice secondary status'},
                    { name: 'Currency_InvoiceValue', title: 'Currency invoice value'},
                    { name: 'invoice_date', title: 'Invoice date '},
                    { name: 'Comm_InvoiceNr', title: 'Comm invoice nr'},
                ]
            }]
        }
        config.listing[0].columns.forEach(columnSort)
        function columnSort(obj){
            obj.sort=false
        }

        function selectedRowLength(){
            if ($route.current.controller != 'proformaInvoicesCtrl'){
                return false;
            }
            if($scope.getSelectedIds(1).length==0 || $scope.getSelectedIds(1).length > 1 ){
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select one invoice', 10);
                return false
            }

            return true
        }

        Mousetrap.bind('o r', function() {
            if (selectedRowLength() == true){
                onbtnOrderReceipt()
            }
        });

        Mousetrap.bind('p i', function() {
            if (selectedRowLength() == true){
                onbtnProformInvoice()
            }
        });

        Mousetrap.bind('o c', function() {
            if (selectedRowLength() == true){
                onbtnOrderConf()
            }
        });

        Mousetrap.bind('e p', function() {
            if (selectedRowLength() == true){
                onbtnEditProfile()
            }
        });
        Mousetrap.bind('c r', function() {
            if (selectedRowLength() == true){
                onbtnCreditReport()
            }
        });

        Mousetrap.bind('c l', function() {
            if (selectedRowLength() == true){
                creditLimit()
            }
        });

        Mousetrap.bind('h', function() {
            if (selectedRowLength() == true){
                onbtnInvoiceHistory()
            }
        });

        function getRowData(){
            var selectedId = $scope.getSelectedIds(1)[0];
            var rowData = $.grep($scope['dtInstance1'].DataTable.data() , function( n, i ) {
                return n.id == selectedId;
            });
            return rowData[0]
        }

        function creditLimit(){
            if (data.permissions["can_update_proforma_invoice_credit_limit"]) {
              rowDta = getRowData();

                var templateUrl =
                        "/finance/credit_limit/" + rowDta.customer_id + "/";
                function openmodal(){
                    if($scope.modalopened) return ;
                    var creditLimitModal = $uibModal.open({
                        templateUrl: templateUrl,
                        controller: "creditLimitModalCtrl",
                        scope: $scope,
                        size: "md",
                        backdrop: false,
                    });
                    $scope.creditLimitModalTitle =
                        "Credit limit - " + rowDta.customer;
                    $scope.modalopened = true;
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

        function onbtnEditProfile(scope){
            rowDta = getRowData()
            if ($scope.modalopened) return;
            var customerId = rowDta.customer_id;
            $scope.onEditLink("/b/iframe_index/#/sales/customer/proforma_inv/"+customerId+"/true/true/", 'Customer profile - '+rowDta.customer, dialogCloseCallback,false,'+1+',true);
            $scope.modalopened = true
        }
        function dialogCloseCallback(){
            $scope.modalopened = false;
        }
        function onbtnOrderReceipt(){
            rowDta = getRowData()
            var ordernum = rowDta.order_number
            var doc_type = "ord_receipt";
            window.open("/sales/get_ec_doc/" + ordernum +"/"+doc_type + "/");
        }
        function onbtnProformInvoice(scope){
            rowDta = getRowData()
            var order_number = rowDta.order_number
            var doc_type = "performa";
            window.open("/sales/get_ec_doc/"+order_number+"/"+doc_type + "/");
        }
        function onbtnOrderConf(scope){
            rowDta = getRowData()
            var order_number = rowDta.order_number;
            var doc_type = "ord";
            window.open("/sales/get_ec_doc/"+order_number+"/"+doc_type + "/");
        }


        function onbtnCreditReport() {
            var rowDta = getRowData();
            var templateUrl = "/finance/credit_report/"+rowDta.customer_id+"/";
            // var templateUrl = "/finance/credit_report/404392/";
            function openmodal(){
                if ($scope.modalopened) return;
                var creditReportModal = $uibModal.open({
                    templateUrl: templateUrl,
                    controller: "creditReportModalCtrl",
                    scope: $scope,
                    size: "lg",
                    backdrop: false,
                });
                $scope.creditReportModalTitle = "Credit report - "+rowDta.customer;
                $scope.modalopened = true;
                creditReportModal.closed.then(function () {
                    $scope.modalopened = false;
                    $templateCache.remove(templateUrl);
                });
            }
            openmodal();
        }

        function onbtnInvoiceHistory(){
            var templateUrl = "/finance/get_invoice_history/" + getRowData().id + "/";
            function openmodal(){
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
                $scope.modalopened= false;
                });
            }
            openmodal();
        }



        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });

    return proformaInvoices;
}

var proformaInvoices = proformaInvoicesInit();