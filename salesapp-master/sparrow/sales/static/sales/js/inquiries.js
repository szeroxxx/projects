function inquiriesInit() {
    sparrow.registerCtrl('inquiriesCtrl',function($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService){
        var partner_type = $routeParams.type;
        var config = {
            pageTitle: "Inquiries",
            topActionbar: {
               add: {
                    url: "/#/accounts/user/"
               },
               edit: {
                    url: "/#/accounts/user/"
               },
               delete: {
                    url: "/accounts/inquiries_del/"
               },
               extra: [
                // {
                //     id:"btnUserHistory",
                //     multiselect : false,
                //     function: showLog
                // },
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
                    function: exportInquriesData
                }]
            },
            listing: [{
                index : 1,
                search: {
                    params: [
                        { key: "inquiry_no", name: "Inquiry nr", placeholder: "" },
                        { key: "order_Ref", name: "Order ref", placeholder: "" },
                        { key: "customer_name", name: "Customer name", placeholder: "" },
                        { key: "inquiry_date__date",name: "Inquiry date",type: "datePicker"},
                        { key: 'country', name: 'Country'},

                    ]
                },
                url: "/sales/inquiries_search/",
                crud: true,
                scrollBody: true,
                columns: [
                    { name: 'data__inquiry_no', title: 'Inquiry Nr', sort: false},
                    { name: 'data__inquiry_date', title: 'Inquiry date', sort: false},
                    { name: 'data__status', title: 'Status', sort: false},
                    { name: 'data__pcbqty', title: 'PCB qty', sort: false},
                    { name: 'data__order_Ref', title: 'Order ref', sort: false},
                    { name: 'data__service', title: 'Service', sort: false},
                    { name: 'data__delivery_term', title: 'Delivery term', sort: false},
                    { name: 'data__customer_name', title: 'Customer name', sort: false, renderWith: function(data, type, full, meta) {
                        return '<span>\
                                   <a class="link-iframe-item" ng-click="onEditLink(\'/b/iframe_index/#/sales/customer/inq/'+full.customer_id+'/true/true'+'/\',\'Customer profile - ' + data +'\','+null+', '+false+', '+1+','+true+')">'+data+'</a>\
                               </span>';
                    }},
                    { name: 'data__remark', title: 'Remark', sort: false},
                    { name: 'country', title: 'Country'},
                ]
            }]
        }


        function getInquiryNumber(){
            var selectedId = $scope.getSelectedIds(1)[0];
            var rowData = $.grep($scope['dtInstance1'].DataTable.data() , function( n, i ) {
                return n.id == selectedId;
            });
            return rowData[0].data__inquiry_no;
        }
        function onbtnPCBVis(scope){
            var inquiry_number = getInquiryNumber();
            window.open("/sales/pcbvis/"+inquiry_number+"/");
        }
        function onbtnPCBAVis(scope){
            var inquiry_number = getInquiryNumber();
            window.open("/sales/pcbavis/"+inquiry_number+"/");
        }


        // function showLog(){
        //     var selectedId = $scope.getSelectedIds(1)[0];
        //     var rowData = $.grep($scope['dtInstance1'].DataTable.data() , function( n, i ) {
        //         return n.id == selectedId;
        //     });
        //     window.location.hash = "#/auditlog/logs/userprofile/"+selectedId+"?title="+rowData[0].first_name;
        // }

        function exportInquriesData(){
            var postParam = Object.assign({}, $scope['searchParams1'], config.listing[0].postData);
            sparrow.downloadData("/sales/export_inquiries/", postParam)
        }
        // function selectedRowLength(){
        //     if($scope.getSelectedIds(1).length==0 || $scope.getSelectedIds(1).length > 1 ){
        //         sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select one invoice', 10);
        //         return false
        //     }
        //     if ($route.current.controller != 'inquiriesCtrl'){
        //         return false;
        //     }
        //     return true
        // }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
}

inquiriesInit();