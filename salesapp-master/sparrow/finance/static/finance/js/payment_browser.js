function paymentBrowserInit(data) {
    var paymentBrowser = {};
    sparrow.registerCtrl('paymentBrowserCtrl',function($scope, $rootScope, $route, $routeParams, $compile, $uibModal,DTOptionsBuilder, DTColumnBuilder, $templateCache, $location, ModalService){
        $scope.modalopened = false;
        var config = {
            pageTitle: 'Payment browser',
            topActionbar: {
                extra: [
                {
                    id: 'btnEditProfile',
                    multiselect: false,
                    function: onbtnEditProfile,
                },
                {
                    id:"btnCustomerLogin",
                    multiselect : false,
                    function: onCustomerLogin
                },
                {
                    id:"btnCustInvoice",
                    multiselect : false,
                    function: onCustInvoice
                },
                {
                    id:"btnProformaInvoice",
                    multiselect : false,
                    function: onbtnProformaInvoice
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
                    { key: "payment_date__date",name: "Payment from date till date",type: "datePicker"},
                    { key: "invoice_dueDate__date",name: "Invoice due date",type: "datePicker"},
                    // { key: 'invoice_value', name: 'Invoice value'},
                    // { key: 'order_number', name: 'Order number'},
                    // { key: 'pcb_name', name: 'PCB-name'},
                    { key: 'payment_mode', name: 'Payment mode'},
                    { key: 'payment_id', name: 'Payment id'},
                    { key: 'customer', name: 'Customer'},
                    // { key: 'username', name: 'Username'},
                    { key: 'country', name: 'Country'},
                    // { key: 'handling_company', name: 'Handling company'},
                    // { key: 'root_company', name: 'Root company'},
                    // { key: 'Postal_code', name: 'Postal code'},
                    // { key: 'city', name: 'City'},
                    // { key: 'phone', name: 'Phone'},
                    // { key: 'vat_nr', name: 'VAT nr '},

                ]},
                url: "/finance/payment_browser_search/",
                crud: true,
                columns: [

                    { name: 'invoice_number', title: 'Invoice number'},
                    { name: 'customer', title: 'Customer name', renderWith: function(data, type, full, meta) {
                        return '<span>\
                                   <a class="link-iframe-item" ng-click="onEditLink(\'/b/iframe_index/#/sales/customer/payment_browser/'+full.customer_id+'/true/true'+'/\',\'Customer profile - ' + data +'\','+null+', '+false+', '+1+','+true+')">'+data+'</a>\
                               </span>';
                    }},
                    { name: 'payment_date', title: 'Payment date'},
                    { name: "invoice_dueDate",title: "Invoice due date"},
                    { name: 'payment_mode', title: 'Payment mode'},
                    { name: 'Invoice_status', title: 'Invoice status'},
                    { name: 'Closed_by', title: 'Closed by'},
                    { name: 'Closed_on', title: 'Closed on'},
                    { name: 'Invoice_amount', title: 'Invoice amount'},
                    { name: 'Payment_amount', title: 'Payment amount'},
                    { name: 'Currency_symbol', title: 'Currency symbol'},
                    { name: 'Bank_AccountNo', title: 'Bank account no'},
                    { name: 'Bank_name', title: 'Bank name'},
                    { name: 'country', title: 'Country'},
                    { name: 'payment_id', title: 'Payment id'},


                ]
            }]
        }

        config.listing[0].columns.forEach(columnSort)
        function columnSort(obj){
            obj.sort=false
        }

        function selectedRowLength(){
            if ($route.current.controller != 'paymentBrowserCtrl'){
                return false;
            }
            if($scope.getSelectedIds(1).length==0 || $scope.getSelectedIds(1).length > 1 ){
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select one invoice', 10);
                return false
            }

            return true
        }

        Mousetrap.bind('i', function() {
            if (selectedRowLength() == true){
                onCustInvoice()
            }
        });

        Mousetrap.bind('p i', function() {
            if (selectedRowLength() == true){
                onbtnProformaInvoice()
            }
        });

        Mousetrap.bind('l', function() {
            if (selectedRowLength() == true){
                onCustomerLogin()
            }
        });

        Mousetrap.bind('e p', function() {
            if (selectedRowLength() == true){
                onbtnEditProfile()
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

        function onbtnEditProfile(scope){
            rowDta = getRowData()
            var customerId = rowDta.customer_id;
            if ($scope.modalopened) return;
            $scope.onEditLink("/b/iframe_index/#/sales/customer/payment_browser/"+customerId+"/true/true/", 'Customer profile - '+rowDta.customer, dialogCloseCallback,false,'+1+',true);
            $scope.modalopened = true;
        }
        function dialogCloseCallback(){
            $scope.modalopened = false;
        }

        function onCustomerLogin(){
            if (data.permissions["can_customer_login_payment_browser"]) {
                rowDta = getRowData();
                var customer_id = rowDta.customer_id;
                var inv_nr =  getRowData().invoice_number.split("/").join("-");
                var from = "INVOICE";
                sparrow.post("/sales/validate_customer_login/", {customer_id:customer_id,from: from}, false, function(data) {
                    if(data.code == '1'){
                        if (data.msg == ''){
                            var ec_user_id = data.ec_user_id;

                            window.open("/sales/customer_login/" + inv_nr + "/" + from + "/" + ec_user_id + "/" + customer_id + "/");
                        }
                        else{
                            function openmodal(){
                                if ($scope.modalopened) return;
                                var templateUrl = "/sales/validate_customer_login_modal/";
                                var customerLoginValidateModal = $uibModal.open({
                                    templateUrl: templateUrl,
                                    controller: "customerLoginValidateModalCtrl",
                                    scope: $scope,
                                    size: "md",
                                    backdrop: false,
                                    resolve: {
                                        dataModal : function() {
                                            return {entity_nr : inv_nr, msg : data.msg, customer_id : customer_id, from : from, ec_user_id : data.ec_user_id} ;
                                        }
                                    }

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

                });
            }else{
                sparrow.showMessage(
                  "appMsg",
                  sparrow.MsgType.Error,
                  "You do not have permission to perform this action",
                  10
                );
            }
        }

        function onCustInvoice() {
            rowDta = getRowData()
            invoicenum = rowDta.invoice_number
            var doc_type = "invoice";
            window.open("/sales/get_ec_customer_inv_doc/"+ invoicenum + "/" + doc_type + "/");

        }
        function onbtnProformaInvoice() {
            rowDta = getRowData()
            invoicenum = rowDta.invoice_number
            var doc_type = "performa";
            window.open("/sales/get_ec_customer_inv_doc/"+ invoicenum + "/" + doc_type + "/");

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

    return paymentBrowser;
}

var paymentBrowser = paymentBrowserInit();


