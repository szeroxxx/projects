function ordersInit(data) {
    sparrow.registerCtrl('ordersCtrl',function($scope, $rootScope, $route, $routeParams, $compile, $uibModal, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService){
        var partner_type = $routeParams.type;
        $scope.modalopened = false;
        var config = {
            pageTitle: "Orders",
            topActionbar: {
               extra: [
                {
                    id:"btnUserHistory",
                    multiselect : false,
                    function: showLog
                },
                {
                    id:"btnPCBImg",
                    multiselect : false,
                    function: onbtnPCBImg
                },
                {
                    id:"btnLayerImg",
                    multiselect : false,
                    function: onbtnLayerImg
                },
                {
                    id:"btnCustomerLogin",
                    multiselect : false,
                    function: onCustomerLogin
                },
                {
                    id:"btnOrderReceipt",
                    multiselect : false,
                    function: onbtnOrderReceipt
                },
                {
                    id:"btnOrderConf",
                    multiselect : false,
                    function: onbtnOrderConf
                },
                {
                    id:"btnDeliveryNote",
                    multiselect : false,
                    function: onbtnDeliveryNote
                },
                {
                    id:"btnException",
                    multiselect : false,
                    function: onbtnException
                },
                {
                    id:"btnEditProfile",
                    multiselect : false,
                    function: onbtnEditProfile
                },
                {
                    id:"btnPCBVis",
                    multiselect : false,
                    function: onbtnPCBVis
                },
                {
                    id:"btnPCBAVis",
                    multiselect : false,
                    function: onbtnPCBAVis
                },
                {
                    id:"btnExport",
                    function: exportOrdersData
                },
                {
                    id:"CustInvoice",
                    function: onCustInvoice
                },
                {
                    id:"btnProformInvoice",
                    function: onbtnProformInvoice
                }]
            },
            listing: [{
                index : 1,
                search: {
                    params: [
                        { key: "order_number", name: "Order number", placeholder: "" },
                        { key: "pcb_name", name: "PCB name", placeholder: "" },
                        { key: "customer_name", name: "Customer Name", placeholder: "" },
                        { key: "order_date__date",name: "Order date",type: "datePicker"},
                        { key: "delivery_date__date",name: "Delivery from date till date",type: "datePicker"},
                        { key: 'country', name: 'Country'},

                    ]
                },
                url: "/sales/orders_search/",
                crud: true,
                scrollBody: true,
                columns: [
                    { name: 'data__order_number', title: 'Order Nr', 'sort': false},
                    { name: 'data__order_status', title: 'Status', 'sort': false},
                    { name: 'data__order_date', title: 'Order date', 'sort': false},
                    { name: 'delivery_date', title: 'Delivery date', 'sort': false},
                    { name: 'data__order_value', title: 'Order value', 'sort': false},
                    { name: 'data__delivery_term', title: 'Delivery term', 'sort': false},
                    { name: 'data__pcb_qty', title: 'PCB qty', 'sort': false},
                    { name: 'data__panel_qty', title: 'Panel qty', 'sort': false},
                    { name: 'data__service', title: 'Service', 'sort': false},
                    { name: 'data__pcb_name', title: 'PCB name', 'sort': false},
                    { name: 'data__layers', title: 'Layers', 'sort': false},
                    { name: 'data__first_orderdate', title: 'First order date', 'sort': false},
                    { name: 'data__customer_name', title: 'Customer name', 'sort': false, renderWith: function(data, type, full, meta) {
                        return '<span>\
                                   <a class="link-iframe-item" ng-click="onEditLink(\'/b/iframe_index/#/sales/customer/ord/'+full.data__customer_id+'/true/true'+'/\',\'' + data +'\','+null+', '+false+', '+1+','+true+')">'+data+'</a>\
                               </span>';
                    }},
                    { name: 'data__company_city', title: 'City', 'sort': false},
                    { name: 'data__company_country', title: 'Country', 'sort': false},
                ]
            }]
        }

        // $scope.searchOrders = function(event) {
        //     config.listing[0].postData = {}
        //     if ($('#dt_order_date').find('span').html() != "") {
        //         var order_date_ctrl = $('#dt_order_date').data('daterangepicker');
        //         var order_start_date = moment(order_date_ctrl.startDate).format('DD/MM/YYYY h:mm:ss a')
        //         var order_end_date = moment(order_date_ctrl.endDate).format('DD/MM/YYYY h:mm:ss a')
        //         config.listing[0].postData = {
        //             "order_start_date": order_start_date,
        //             "order_end_date": order_end_date
        //         }
        //     }
        //     $scope.reloadData(1, config.listing[0]);
        // }

        function showLog(){
            var selectedId = $scope.getSelectedIds(1)[0];
            var rowData = $.grep($scope['dtInstance1'].DataTable.data() , function( n, i ) {
                return n.id == selectedId;
            });
            window.location.hash = "#/auditlog/logs/userprofile/"+selectedId+"?title="+rowData[0].first_name;
        }

        function getOrderNumer(){
            var selectedId = $scope.getSelectedIds(1)[0];
            var rowData = $.grep($scope['dtInstance1'].DataTable.data() , function( n, i ) {
                return n.id == selectedId;
            });
            return rowData[0].data__order_number;
        }

        function onCustomerLogin(){

            if (data.permissions["can_customer_login_orders"] ==  false) {
                sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                "You do not have permission to perform this action",
                10
              );
              return;
            }

            var selectedId = $scope.getSelectedIds(1)[0];
            var rowData = $.grep($scope['dtInstance1'].DataTable.data() , function( n, i ) {
                return n.id == selectedId;
            });
            var customer_id = rowData[0].data__customer_id;
            var ord_nr = getOrderNumer();

            // window.open("/sales/customer_login/"+customer_id+"/");
            var from = "ORDER";
            sparrow.post("/sales/validate_customer_login/", {customer_id:customer_id,from: from}, false, function(data) {
                if(data.code == '1'){
                    if (data.msg == ''){
                        var ec_user_id = data.ec_user_id;

                        window.open("/sales/customer_login/" + ord_nr + "/" + from + "/" + ec_user_id + "/" + customer_id + "/");
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
                                        return {entity_nr : ord_nr, msg : data.msg, customer_id : customer_id, from : from, ec_user_id : data.ec_user_id} ;
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
        }
        function onbtnPCBImg(scope){
            var order_number = getOrderNumer();
            var doc_type = "pi";
            window.open("/sales/get_ec_doc/"+order_number+"/"+doc_type + "/");
        }
        function onbtnLayerImg(scope){
            var order_number = getOrderNumer();
            var doc_type = "li";
            window.open("/sales/get_ec_doc/"+order_number+"/"+doc_type + "/");
        }

        function onbtnOrderReceipt(){
            var order_number = getOrderNumer();
            var doc_type = "ord_receipt";
            window.open("/sales/get_ec_doc/"+order_number+"/"+doc_type + "/");
        }
        function onbtnOrderConf(){
            var order_number = getOrderNumer();
            var doc_type = "ord";
            window.open("/sales/get_ec_doc/"+order_number+"/"+doc_type + "/");
        }
        function onbtnDeliveryNote(){
            var order_number = getOrderNumer();
            var doc_type = "deliverynote";
            window.open("/sales/get_ec_doc/"+order_number+"/"+doc_type + "/");
        }
        function onCustInvoice(){
            var order_number = getOrderNumer();
            var doc_type = "invoice";
            window.open("/sales/get_ec_doc/"+order_number+"/"+doc_type + "/");
        }
        function onbtnProformInvoice(){
            var order_number = getOrderNumer();
            var doc_type = "performa";
            window.open("/sales/get_ec_doc/"+order_number+"/"+doc_type + "/");
        }
        function onbtnException(scope){
            var order_number = getOrderNumer();
            var doc_type = "exceptions";
            window.open("/sales/get_ec_doc/"+order_number+"/"+doc_type + "/");
        }
        function onbtnEditProfile(){
            if ($scope.modalopened) return;
            var selectedId = $scope.getSelectedIds(1)[0];
            var rowData = $.grep($scope['dtInstance1'].DataTable.data() , function( n, i ) {
                return n.id == selectedId;
            });
            var customer_id = rowData[0].data__customer_id;
            $scope.onEditLink("/b/iframe_index/#/sales/customer/ord/"+customer_id+"/true/true/", 'Customer profile - '+rowData[0].data__customer_name, dialogCloseCallback,false,'+1+',true);
            $scope.modalopened = true;
        }
        function dialogCloseCallback(){
            $scope.modalopened = false;
        }
        function onbtnPCBVis(scope){
            var order_number = getOrderNumer();
            window.open("/sales/pcbvis/"+order_number+"/");
        }
        function onbtnPCBAVis(scope){
            var order_number = getOrderNumer();
            window.open("/sales/pcbavis/"+order_number+"/");
        }

        function exportOrdersData(){
            var postParam = Object.assign({}, $scope['searchParams1'], config.listing[0].postData);
            sparrow.downloadData("/sales/export_orders/", postParam)
        }
        function selectedRowLength(){
            if ($route.current.controller != 'ordersCtrl'){
                return false;
            }
            if($scope.getSelectedIds(1).length==0 || $scope.getSelectedIds(1).length > 1 ){
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select one invoice', 10);
                return false
            }

            return true
        }
        Mousetrap.bind('e p', function() {
            if (selectedRowLength() == true){
                onbtnEditProfile();
            }
        });
        Mousetrap.bind('l', function() {
            if (selectedRowLength() == true){
                onCustomerLogin();
            }
        });
        Mousetrap.bind('o c', function() {
            if (selectedRowLength() == true){
                onbtnOrderConf();
            }
        });
        Mousetrap.bind('i', function() {
            if (selectedRowLength() == true){
                onCustInvoice();
            }
        });
        Mousetrap.bind('p i', function() {
            if (selectedRowLength() == true){
                onbtnProformInvoice();
            }
        });
        Mousetrap.bind('o r', function() {
            if (selectedRowLength() == true){
                onbtnOrderReceipt();
            }
        });
        Mousetrap.bind('d n', function() {
            if (selectedRowLength() == true){
                onbtnDeliveryNote();
            }
        });
        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
}

ordersInit();