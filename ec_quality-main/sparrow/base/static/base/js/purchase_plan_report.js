function purchaseplanreportInit() {
    var purchaseplanreport = {};

    sparrow.registerCtrl(
        'purchasePlanReportCtrl',
        function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, $uibModal, DTColumnBuilder, $templateCache, ModalService) {
            console.log(moment().startOf('year').toDate().getMonth() + 1);
            var config = {
                pageTitle: 'Purchase plans',

                listing: [
                    {
                        index: 1,
                        url: '/base/purchase_plan_report_search/',
                        postData: {
                            from_date:
                                (moment().startOf('year').toDate().getDay(), 1) +
                                '/' +
                                (moment().startOf('year').toDate().getMonth() + 1) +
                                '/' +
                                moment().startOf('year').toDate().getFullYear(),
                            to_date:
                                (moment().endOf('year').toDate().getDay(), moment().daysInMonth()) +
                                '/' +
                                (moment().endOf('year').toDate().getMonth() + 1) +
                                '/' +
                                moment().endOf('year').toDate().getFullYear(),
                            purchase_person__icontains: '',
                        },
                        scrollBody: true,
                        columns: [
                            {
                                name: 'purchase_plan_num',
                                title: 'Plan number',
                            },
                            {
                                name: 'purchase_person',
                                title: 'Purchase person',
                            },
                            {
                                name: 'mo_reference',
                                title: 'Plan items',
                            },
                            {
                                name: 'offer_price',
                                title: 'Offered price',
                                sort: false,
                            },
                            {
                                name: 'total_price',
                                title: 'Total price',
                            },
                            {
                                name: 'total_discount_price',
                                title: 'Discounted total',
                            },
                            {
                                name: 'reference',
                                title: 'Reference',
                            },
                            {
                                name: 'status',
                                title: 'Status',

                                sort: false,
                            },
                            {
                                name: 'created_on',
                                title: 'Created on',
                            },
                        ],
                    },
                ],
            };
            setAutoLookup('id_purchase_person', '/b/lookups/users/', '', false);
            $('#load_btn').on('click', function (event) {
                sparrow.global.set('SEARCH_EVENT', true);
                dtBindFunction();
                config.listing[0].postData = $scope.postData;
                $scope.reloadData(1, config.listing[0]);
            });

            function dtBindFunction() {
                var purchase_person = $('#hid_purchase_person').val();
                if (purchase_person == undefined) {
                    purchase_person = '';
                }
                var Dates = $('#dates').text();
                var from_date = '';
                var to_date = '';
                if (Dates != '') {
                    var newDates = Dates.split('-');
                    from_date = newDates[0].trim();
                    to_date = newDates[1].trim();
                }

                $scope.from_date = from_date;
                $scope.to_date = to_date;
                var postData = {
                    from_date: from_date,
                    to_date: to_date,
                    purchase_person__icontains: purchase_person,
                };
                $scope.postData = postData;
            }
            $scope.onExport = function (event) {
                event.preventDefault();
                dtBindFunction();
                var postData = $scope.postData;
                var url =
                    '/base/purchase_plan_report_export?purchase_person_name=' +
                    postData['purchase_person__icontains'] +
                    '&from=' +
                    postData['from_date'] +
                    '&to=' +
                    postData['to_date'];
                window.open(url, '_blank');
            };

            sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
        }
    );
    return purchaseplanreport;
}
purchaseplanreportInit();
