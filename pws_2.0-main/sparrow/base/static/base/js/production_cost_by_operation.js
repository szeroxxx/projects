function productioncostInit() {
    var productionCostDate = {};
    sparrow.registerCtrl('productionCostWipCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        $scope.operation_start_date = true;
        config = {
            pageTitle: 'Work in progress production cost',
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
                    url: '/base/production_cost_search/',
                    paging: true,
                    scrollBody: true,
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
                        operation_ids: [],
                        op_status: '',
                        create_on: false,
                        operation_start_date: true,
                    },
                    columns: [
                        {
                            name: 'mfg_cost__mfg_order__mfg_order_num',
                            title: 'Mfg number',
                        },
                        { name: 'op_status', title: 'Operation status', sort: false },
                        { name: 'panel_quantity', title: 'Panel qty', sort: false },
                        {
                            name: 'routing_line__operation__name',
                            title: 'Cost line',
                            sort: false,
                        },
                        {
                            name: 'mfg_routing__operation_time',
                            title: 'Estimated time',
                            sort: false,
                        },
                        {
                            name: 'mfg_routing__spent_time',
                            title: 'Spent time',
                            sort: false,
                        },
                        {
                            name: 'mfg_routing__start_time',
                            title: 'Start date',
                            sort: false,
                        },
                        {
                            name: 'pre_machine_cost',
                            title: 'Machine estimated',
                            sort: false,
                        },
                        { name: 'machine_cost', title: 'Machine actual', sort: false },
                        {
                            name: 'pre_labour_cost',
                            title: 'Employee estimated',
                            class: 'employee',
                        },
                        {
                            name: 'labour_cost',
                            title: 'Employee actual',
                            class: 'employee',
                            sort: false,
                        },
                        {
                            name: 'pre_material_cost',
                            title: 'Material estimated',
                            sort: false,
                        },
                        { name: 'material_cost', title: 'Material actual', sort: false },
                        {
                            name: 'pre_workcenter_cost',
                            title: 'Center estimated',
                            class: 'workcenter',
                            sort: false,
                        },
                        {
                            name: 'workcenter_cost',
                            title: 'Center actual',
                            class: 'workcenter',
                            sort: false,
                        },
                        { name: 'pre_total_cost', title: 'Total estimated', sort: false },
                        { name: 'total_cost', title: 'Total actual', sort: false },
                    ],
                },
            ],
        };
        setAutoLookup('id_operation', '/b/lookups/production_cost_operation/', '', true, true, false, null, 10, null, null, null);

        $('#load_btn').on('click', function (event) {
            sparrow.global.set('SEARCH_EVENT', true);
            dtBindFunction();
            config.listing[0].postData = $scope.postData;
            $scope.reloadData(1, config.listing[0]);
        });

        function dtBindFunction() {
            let op_status = $('#operation_status').find(':selected').val();
            from_date = $('#from_date').val();
            to_date = $('#to_date').val();
            var operation_ids = [];
            $('input[name = operation]').each(function (i, obj) {
                operation_ids.push(parseInt($(obj).val()));
            });
            if (from_date == undefined) {
                from_date = '';
            }
            if (to_date == undefined) {
                to_date = '';
            }
            if (operation_ids == undefined) {
                operation_ids = '';
            }
            var Dates = $('#dates').text();
            var from_date = '';
            var to_date = '';
            if (Dates != '') {
                var newDates = Dates.split('-');
                from_date = newDates[0].trim();
                to_date = newDates[1].trim();
                // var newToDate = to_date.split('/');

                // if (parseInt(newToDate[0]) + 1 < 31) {
                //     newToDate[0] = (parseInt(newToDate[0]) + 1).toString();
                //     to_date = newToDate.join('/').trim();
                // }
            }
            var postData = {
                from_date: from_date,
                to_date: to_date,
                operation_ids: operation_ids,
                op_status: op_status,
                create_on: false,
                operation_start_date: true,
            };
            $scope.postData = postData;
        }

        function onExport(scope) {
            event.preventDefault();
            dtBindFunction();
            var postData = $scope.postData;
            var id = postData['operation_ids'];
            if (id == undefined || id == '') {
                id = 0;
            }
            var url =
                '/base/production_cost_by_operation_export?from=' +
                postData['from_date'] +
                '&to=' +
                postData['to_date'] +
                '&id=' +
                id +
                '&op_status=' +
                postData['op_status'] +
                '&op_start_date=' +
                postData['operation_start_date'];
            window.open(url, '_blank');
        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
    return productionCostDate;
}
productioncostInit();
