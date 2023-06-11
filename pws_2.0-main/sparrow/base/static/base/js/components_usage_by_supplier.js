function componentsUsageBySupplierInit() {
    var componentsUsageBySupplier = {};
    sparrow.registerCtrl(
        'componentsUsageBySupplierCtrl',
        function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
            config = {
                pageTitle: 'Component usage by supplier',

                listing: [
                    {
                        url: '/base/component_usage_by_supplier_search/',
                        paging: true,
                        scrollBody: true,
                        postData: {
                            start_date__date: '',
                            end_date__date: '',
                            worker_id: '',
                        },
                        columns: [
                            {
                                name: 'MPN',
                                title: 'MPN',
                            },
                            {
                                name: 'supplier',
                                title: 'Supplier',
                            },
                            {
                                name: 'quantity',
                                title: 'Quantity',
                            },

                            {
                                name: 'customer',
                                title: 'Customer',
                                sort: false,
                            },
                            {
                                name: 'country',
                                title: 'Country',
                                sort: false,
                            },
                            {
                                name: 'city',
                                title: 'City',
                                sort: false,
                            },
                            {
                                name: 'zipcode',
                                title: 'Zipcode',
                                sort: false,
                            },
                        ],
                        index: 1,
                    },
                ],
            };
            setAutoLookup('id_supplier', '/b/lookups/supplier/', '', true);

            $('#load_btn').on('click', function (event) {
                sparrow.global.set('SEARCH_EVENT', true);
                dtBindFunction();
                config.listing[0].postData = $scope.postData;
                $scope.reloadData(1, config.listing[0]);
                // $('#btnExport').show();
            });

            function dtBindFunction() {
                var id_supplier = $('#hid_supplier').val();
                if (id_supplier == undefined) {
                    id_supplier = '';
                }
                var Dates = $('#dates').text();
                var from_date = '';
                var to_date = '';
                if (Dates != '') {
                    var newDates = Dates.split('-');
                    from_date = newDates[0].trim();
                    to_date = newDates[1].trim();
                }
                var postData = {
                    start_date: from_date,
                    end_date: to_date,
                    id_supplier: id_supplier,
                };
                $scope.postData = postData;
                $('.date_range').text('From ' + $scope.postData.start_date + ' to ' + $scope.postData.end_date);
            }

            $scope.onExport = function (event) {
                event.preventDefault();
                dtBindFunction();
                var postData = $scope.postData;
                var url =
                    '/base/component_usage_by_supplier_export?id_supplier=' +
                    postData['id_supplier'] +
                    '&start_date=' +
                    postData['start_date'] +
                    '&end_date=' +
                    postData['end_date'];
                var totalRecord = $scope.getTotalTableRecords(1);
                var kwargs = {};
                if (totalRecord > 2000) {
                    var msg = 'Maximum 2000 records will be exported?';
                    kwargs.positiveBtnText = 'Ok';
                    kwargs.negativeBtnText = 'Cancel';
                    sparrow.showConfirmDialog(
                        ModalService,
                        msg,
                        'Export component usage by supplier report',
                        function (confirm) {
                            if (confirm) {
                                window.open(url, '_blank');
                            }
                        },
                        kwargs
                    );
                } else {
                    window.open(url, '_blank');
                }
            };
            sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
        }
    );

    return componentsUsageBySupplier;
}

componentsUsageBySupplierInit();
