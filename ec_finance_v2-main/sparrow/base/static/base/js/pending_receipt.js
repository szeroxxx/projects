function pendingReceiptInit() {
    var pendingReceipt = {};
    sparrow.registerCtrl('pendingReceiptCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        config = {
            pageTitle: 'Pending receipt for scan',
            topActionbar: {
                extra: [
                    {
                        id: 'btnExport',
                        multiselect: false,
                        function: onExport,
                    },
                ],
            },
            listing: [
                {
                    index: 1,
                    url: '/base/pending_receipt_search/',
                    paging: true,
                    scrollBody: true,
                    postData: {
                        from_date: '',
                        to_date: '',
                    },
                    columns: [
                        { name: 'transfer_num', title: 'Receipt' },
                        { name: 'mfg_order_num', title: 'Mfg number' },
                        { name: 'created_on', title: 'Created on' },
                        { name: 'future_date', title: 'Estimated arrival date' },
                        { name: 'source_doc', title: 'External Document Nr' },
                    ],
                },
            ],
        };
        $('#load_btn').on('click', function (event) {
            sparrow.global.set('SEARCH_EVENT', true);
            dtBindFunction();
            config.listing[0].postData = $scope.postData;
            $scope.reloadData(1, config.listing[0]);
        });
        function dtBindFunction() {
            from_date = $('#from_date').val();
            to_date = $('#to_date').val();
            if (from_date == undefined) {
                from_date = '';
            }
            if (to_date == undefined) {
                to_date = '';
            }
            var Dates = $('#dates').text();
            var from_date = '';
            var to_date = '';
            if (Dates != '') {
                var newDates = Dates.split('-');
                from_date = newDates[0].trim();
                to_date = newDates[1].trim();
                var newToDate = to_date.split('/');

                if (parseInt(newToDate[0]) + 1 < 31) {
                    newToDate[0] = (parseInt(newToDate[0]) + 1).toString();
                    to_date = newToDate.join('/').trim();
                }
            }
            var postData = {
                from_date: from_date,
                to_date: to_date,
            };
            $scope.postData = postData;
        }

        function onExport(scope) {
            event.preventDefault();
            dtBindFunction();
            var postData = $scope.postData;
            var url = '/base/pending_receipt_export?from=' + postData['from_date'] + '&to=' + postData['to_date'];
            window.open(url, '_blank');
        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });

    return pendingReceipt;
}

pendingReceiptInit();
