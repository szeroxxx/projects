function produtiondelayreportInit() {
    var productiondelayreport = {};

    sparrow.registerCtrl('productionDelayCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        var config = {
            pageTitle: 'Production Delay',
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
                    url: '/base/production_delay_search/',
                    postData: {
                        from_date:
                            (moment().startOf('month').toDate().getDay(), 1) +
                            '/' +
                            (moment().startOf('month').toDate().getMonth() + 1) +
                            '/' +
                            moment().startOf('month').toDate().getFullYear(),
                        to_date:
                            (moment().endOf('day').toDate().getDay(), moment().daysInMonth()) +
                            '/' +
                            (moment().endOf('day').toDate().getMonth() + 1) +
                            '/' +
                            moment().endOf('day').toDate().getFullYear(),
                    },
                    scrollBody: true,
                    paging: true,
                    columns: [
                        { name: 'source_doc', title: 'EC number' },
                        { name: 'mfg_order_num', title: 'MO number' },
                        {
                            name: 'status',
                            title: 'MO status',
                            renderWith: function (data, type, full, meta) {
                                if (full.status == 'awaiting') {
                                    return 'Awaiting for customer component';
                                } else {
                                    return full.status;
                                }
                            },
                        },
                        { name: 'sales_order__customer__name', title: 'Customer' },
                        { name: 'sales_order__address_shipping__country__name', title: 'Country' },
                        { name: 'qty', title: 'PCB qty' },
                        { name: 'panel_qty', title: 'Panel qty' },
                        { name: 'number_of_comp', title: 'NOC', sort: false },
                        { name: 'number_of_placements', title: 'NOP', sort: false },
                        { name: 'th_placement_count', title: 'TH', sort: false },
                        { name: 'delivery_day', title: 'Delivery term of PCB' },
                        { name: 'delivery_term_of_assembly', title: 'Delivery term of assembly', sort: false },
                        { name: 'sales_order__ship_date', title: 'Delivery date of assembly' },
                        { name: 'ready_for_production', title: 'Ready for production', sort: false },
                        { name: 'production_start_time', title: 'Start of production' },
                        { name: 'remarks', title: 'Comment', renderWith: onRemarks },
                        { name: 'running_operation', title: 'Last operation' },
                        { name: 'next_operation', title: 'Next operation' },
                    ],
                },
            ],
        };
        function onRemarks(data, type, full, meta) {
            var fix_char = 40;
            data = data == null ? '' : sparrow.stripHtml(data);
            if (data.length >= fix_char) {
                return '<span title="' + data + '">' + data.slice(0, fix_char) + '...</span>';
            }
            return '<span title="' + data + '">' + data + '</span>';
        }

        $('#load_btn').on('click', function (event) {
            sparrow.global.set('SEARCH_EVENT', true);
            dtBindFunction();
            config.listing[0].postData = $scope.postData;
            $scope.reloadData(1, config.listing[0]);
        });

        function dtBindFunction() {
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
            };
            $scope.postData = postData;
        }
        function onExport(scope) {
            // event.preventDefault();
            dtBindFunction();
            var postData = $scope.postData;
            var url = '/base/production_delay_export?from=' + postData['from_date'] + '&to=' + postData['to_date'];
            window.open(url, '_blank');
        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
    return productiondelayreport;
}
produtiondelayreportInit();
