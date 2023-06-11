function waitingComponentsInit() {
    var waitingComponents = {};
    sparrow.registerCtrl('waitingComponentsInit', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        config = {
            pageTitle: 'Report - Waiting for components',
            listing: [
                {
                    index: 1,
                    url: '/base/waiting_component_search/',
                    paging: true,
                    scrollBody: true,
                    // footerClass : 'status-info',
                    search: {
                        params: [
                            { key: 'mfg_order_num__icontains', name: 'Number' },
                            { key: 'sales_order__ship_date', name: 'Ship date', type: 'datePicker' },
                            { key: 'status', name: 'Status' },
                        ],
                    },
                    columns: [
                        { name: 'mfg_order_num', title: 'Mfg number', renderWith: mfgOrdersLink },
                        { name: 'sales_order__ship_date', title: 'Ship date' },
                        { name: 'status', title: 'Status' },
                        { name: 'receipt', title: 'Receipt', sort: false, renderWith: receiptLink },
                        {
                            name: '',
                            title: 'Sourcing',
                            sort: false,
                            renderWith: function (data, type, full, meta) {
                                return '<a id="id_sourcing_status" title="View sourcing" ng-click="onSourcingStatus(' + full.mfg_order_id + ')">View</a>';
                            },
                        },
                    ],
                    index: 1,
                },
            ],
        };

        $scope.onSourcingStatus = function (id) {
            $scope.mfg_order_id = id;
            sparrow.post(
                '/production/mfg_order_sourcing/' + id + '/',
                {},
                false,
                function (data) {
                    $('#sourcing_form').html(data);
                    $('#SourcingModel').modal('show');
                    $('#sourcingLable').text('Sourcing');
                    $('#sourcing_model_body').css('height', parent.document.body.clientHeight - 120 + 'px');
                },
                'html'
            );
        };

        $scope.exportSyncData = function (event) {
            event.preventDefault();
            window.open('/production/export_sourcing_data/' + $scope.mfg_order_id + '/', '_blank');
        };

        function mfgOrdersLink(data, type, full, meta) {
            return '<span><a ng-click="mfgOrderEdit(' + full.mfg_order_id + ",'" + full.mfg_order_num + '\')">' + data + '</a></span>';
        }

        function receiptLink(data, type, full, meta) {
            var keys = Object.keys(full.receipt_data);
            if (keys.length > 1) {
                console.log(full);
            }
            var mainDiv = '<span style="display: -webkit-inline-box;">';
            if (keys.length == 0) {
                return '';
            }

            // eslint-disable-next-line guard-for-in
            for (var key in full.receipt_data) {
                receiptData = full.receipt_data[key];
                if (keys[keys.length - 1] != key) {
                    receiptData = receiptData + ',';
                }
                if (full.receipt_status_data[key] == 'partial_received') {
                    mainDiv += '<div class="circle circle_orange"></div>';
                }
                mainDiv += '<a ng-click="receiptEdit(' + key + ",'" + full.receipt_data[key] + '\')" style="margin-left: 5px;">' + receiptData + '</a>';
            }
            return mainDiv + '</span>';
        }

        $scope.mfgOrderEdit = function (id, ordernum) {
            $scope.onEditLink('/b/iframe_index/#/production/mfg_order/' + id, 'Mfg order - ' + ordernum, closeIframeCallback, '', '', true);
            // parent.globalIndex.iframeCloseCallback.push(openIframeDialog);
        };

        $scope.receiptEdit = function (id, ordernum) {
            $scope.onEditLink('/b/iframe_index/#/logistics/receipt/' + id + '?transfer_type=receipt', 'Receipt - ' + ordernum, closeIframeCallback, '', '', true);
            // parent.globalIndex.iframeCloseCallback.push(openIframeDialog);
        };

        function closeIframeCallback() {
            $scope.reloadData(1);
        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });

    return waitingComponents;
}

waitingComponentsInit();
