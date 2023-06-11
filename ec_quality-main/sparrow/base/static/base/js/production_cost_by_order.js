function periodicproductioncostInit() {
    var periodicproductioncost = {};

    sparrow.registerCtrl('periodicProductionCostCtrl', function (
        $scope,
        $rootScope,
        $route,
        $routeParams,
        $compile,
        DTOptionsBuilder,
        DTColumnBuilder,
        $templateCache,
        ModalService
    ) {
        var config = {
            pageTitle: 'Production cost by order',
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
                    url: '/base/production_cost_by_order_search/',
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
                        { name: 'mfg_order__finished_order_date', title: 'Finished date' },
                        { name: 'pre_machine_cost__sum', title: 'Machine estimated', sort: false },
                        { name: 'machine_cost__sum', title: 'Machine actual', sort: false },
                        { name: 'pre_labour_cost__sum', title: 'Employee estimated', sort: false },
                        { name: 'labour_cost__sum', title: 'Employee actual', sort: false },
                        { name: 'pre_material_cost__sum', title: 'Material estimated', sort: false },
                        { name: 'material_cost__sum', title: 'Material actual', sort: false },
                        { name: 'pre_workcenter_cost__sum', title: 'Center estimated', sort: false },
                        { name: 'workcenter_cost__sum', title: 'Center actual', sort: false },
                        { name: 'total_estimated_cost', title: 'Total estimated', sort: false },
                        { name: 'total_actual_cost', title: 'Total actual', sort: false },
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
            var url = '/base/production_cost_by_order_export?from=' + postData['from_date'] + '&to=' + postData['to_date'];
            window.open(url, '_blank');
        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
    return periodicproductioncost;
}
periodicproductioncostInit();
