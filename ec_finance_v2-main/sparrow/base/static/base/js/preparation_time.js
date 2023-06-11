function preparationtimereportInit() {
    var preparationtimereport = {};

    sparrow.registerCtrl('preparationTimeCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        var config = {
            pageTitle: 'Preparation Time',
            topActionbar: {
                extra: [
                    {
                        id: 'btnExport',
                        function: onExport,
                    },
                ],
            },

            listing: [
                {
                    index: 1,
                    url: '/base/preparation_time_search/',
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
                        { name: 'mfg_order__mfg_order_num', title: 'MO number' },
                        { name: 'mfg_order__created_on', title: 'Created on' },
                        { name: 'mfg_order__qty', title: 'Qty' },
                        { name: 'number_of_comp', title: 'NOC', sort: false },
                        { name: 'number_of_placements', title: 'NOP', sort: false },
                        { name: 'tech_prep_operator', title: 'Tech prep operator' },
                        { name: 'tech_prep_time', title: 'Tech prep time', sort: false },
                        { name: 'tech_prep_status', title: 'Tech prep status' },
                        { name: 'paste_prep_operator', title: 'Paste data prep operator' },
                        { name: 'paste_prep_time', title: 'Paste data prep time', sort: false },
                        { name: 'paste_prep_status', title: 'Paste data prep status' },
                        { name: 'layout_prep_operator', title: 'Layout prep operator' },
                        { name: 'layout_prep_time', title: 'Layout prep time', sort: false },
                        { name: 'layout_prep_status', title: 'Layout prep status' },
                        { name: 'spi_prep_operator', title: 'SPI prep operator' },
                        { name: 'spi_prep_time', title: 'SPI prep time', sort: false },
                        { name: 'spi_prep_status', title: 'SPI prep status' },
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
            dtBindFunction();
            var postData = $scope.postData;
            var url = '/base/preparation_time_export?from=' + postData['from_date'] + '&to=' + postData['to_date'];
            window.open(url, '_blank');
        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
    return preparationtimereport;
}
preparationtimereportInit();
