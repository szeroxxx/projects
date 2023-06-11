function productioncostInit() {
    var productionCost = {};
    sparrow.registerCtrl('productionCostCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        $scope.operation_start_date = false;
        config = {
            pageTitle: 'Operation time',
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
                        create_on: true,
                        operation_start_date: false,
                    },
                    columns: [
                        {
                            name: 'mfg_cost__mfg_order__mfg_order_num',
                            title: 'Mfg number',
                            renderWith: function (data, type, full, meta) {
                                return (
                                    '<a class="link-iframe-item" ng-click="onEditLink(\'/b/iframe_index/#/production/mfg_order/' +
                                    full.mo_id +
                                    "/','Mfg order - " +
                                    data +
                                    "'," +
                                    null +
                                    ', ' +
                                    false +
                                    ', ' +
                                    1 +
                                    ',' +
                                    true +
                                    ')">' +
                                    data +
                                    '</a>'
                                );
                            },
                        },
                        {
                            name: 'mfg_cost__mfg_order__source_doc',
                            title: 'External Document Nr',
                            sort: false,
                        },
                        {
                            name: 'routing_line__operation__name',
                            title: 'Operation (Finished)',
                            sort: false,
                        },
                        {
                            name: 'mfg_cost__mfg_order__running_op',
                            title: 'Operation (Running)',
                            sort: false,
                        },
                        {
                            name: 'mfg_routing__operator__first_name',
                            title: 'Operator name (Finished)',
                            sort: true,
                        },
                        {
                            name: 'running_op_operator',
                            title: 'Operator name (Running)',
                            sort: true,
                        },
                        {
                            name: 'mfg_cost__mfg_order__sales_order__ship_date',
                            title: 'Ship date',
                        },
                        {
                            name: 'mfg_routing__end_time',
                            title: 'Operation end date',
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
                            sort: true,
                        },
                        {
                            name: 'mfg_routing__start_time',
                            title: 'Operation start date',
                            sort: false,
                        },
                        { name: 'panel_quantity', title: 'Panel qty', sort: false },
                        { name: 'mfg_cost__mfg_order__qty', title: 'PCB qty', sort: false },
                        {
                            name: 'total_smd',
                            title: 'Total NOP',
                            sort: false,
                        },
                        {
                            name: 'total_th',
                            title: 'Total TH',
                            sort: false,
                        },
                        { name: 'not_placed_parts', title: 'Not placed', sort: false },
                        { name: 'smd_parts_top_side', title: 'SMD TOP', sort: false },
                        {
                            name: 'smd_parts_bottom_side',
                            title: 'SMD BOTTOM',
                            sort: false,
                        },
                        { name: 'th_parts_top_side', title: 'TH TOP', sort: false },
                        {
                            name: 'th_parts_bottom_side',
                            title: 'TH BOTTOM ',
                            sort: false,
                        },
                        {
                            name: 'th_cut_parts_top_side',
                            title: 'TH_CUT TOP ',
                            sort: false,
                        },
                        {
                            name: 'th_cut_parts_bottom_side',
                            title: 'TH_CUT BOTTOM ',
                            sort: false,
                        },
                        {
                            name: 'th_r_parts_top_side',
                            title: 'TH_R TOP ',
                            sort: false,
                        },
                        {
                            name: 'th_r_parts_bottom_side',
                            title: 'TH_R BOTTOM ',
                            sort: false,
                        },
                        { name: 'bga_top', title: 'BGA TOP ', sort: false },
                        { name: 'bga_bottom', title: 'BGA BOTTOM ', sort: false },
                        { name: 'qfn_top', title: 'QFN TOP ', sort: false },
                        { name: 'qfn_bottom', title: 'QFN BOTTOM ', sort: false },
                        { name: 'finepitch_top', title: 'FinePitch TOP ', sort: false },
                        {
                            name: 'finepitch_bottom',
                            title: 'FinePitch BOTTOM ',
                            sort: false,
                        },
                        { name: 'edge_mount_top', title: 'Edge-mount TOP ', sort: false },
                        {
                            name: 'edge_mount_bottom',
                            title: 'Edge-mount BOTTOM ',
                            sort: false,
                        },
                        { name: 'mixed_top', title: 'Mixed TOP ', sort: false },
                        { name: 'mixed_bottom', title: 'Mixed BOTTOM ', sort: false },
                        { name: 'mechanical_top', title: 'Mechanical TOP ', sort: false },
                        {
                            name: 'mechanical_bottom',
                            title: 'Mechanical BOTTOM ',
                            sort: false,
                        },
                        { name: 'lga_top', title: 'LGA TOP ', sort: false },
                        { name: 'lga_bottom', title: 'LGA BOTTOM ', sort: false },
                        { name: 'th_r_manual_top', title: 'TH_R Manual Top', sort: false },
                        { name: 'th_r_manual_bot', title: 'TH_R Manual Bottom', sort: false },
                        { name: 'smd_manual_top', title: 'SMD Manual Top', sort: false },
                        { name: 'smd_manual_bot', title: ' SMD Manual Bottom', sort: false },
                        {
                            name: 'recordsTotal',
                            title: 'records total',
                            class: 'no-display',
                            renderWith: function (data, type, full, meta) {
                                $scope.$apply(function () {
                                    $scope.records_total = full.recordsTotal;
                                });
                                return '<div class="text"><input class ="total_record" value="' + full.recordsTotal + '" ></div>';
                            },
                        },
                    ],
                },
            ],
        };
        var shift_times = [
            {
                id: 'morning_shift',
                name: 'Morning shift (6:00 – 14:00)',
            },
            {
                id: 'afternoon_shift',
                name: 'Afternoon shift (14:00 – 22:00)',
            },
            {
                id: 'night_shift',
                name: 'Night shift (22:00 – 06:00)',
            },
        ];
        setAutoLookup('id_shift', shift_times, '', false);
        setAutoLookup('id_operation', '/b/lookups/production_cost_operations/', '', true, true, false, null, 10, null, null, null);
        setAutoLookup('id_operator', '/b/lookups/users/', '', true, true, false, null, 10, null, null, null);

        $('#load_btn').on('click', function (event) {
            sparrow.global.set('SEARCH_EVENT', true);
            dtBindFunction();
            config.listing[0].postData = $scope.postData;
            $scope.reloadData(1, config.listing[0]);
        });

        function dtBindFunction() {
            // let op_status = $('#operation_status').find(':selected').val();
            from_date = $('#from_date').val();
            to_date = $('#to_date').val();
            var operation_ids = [];
            var operator_ids = [];
            $('input[name = operation]').each(function (i, obj) {
                operation_ids.push(parseInt($(obj).val()));
            });
            $('input[name = operator]').each(function (i, obj) {
                operator_ids.push(parseInt($(obj).val()));
            });

            shift_timings = $('input[name = shift_time]').val();
            if (shift_timings == undefined) {
                shift_timings = '';
            }
            if (from_date == undefined) {
                from_date = '';
            }
            if (to_date == undefined) {
                to_date = '';
            }
            if (operation_ids == undefined) {
                operation_ids = '';
            }
            if (operator_ids == undefined) {
                operator_ids = '';
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
                operator_ids: operator_ids,
                shift_timings: shift_timings,
                op_status: '',
                create_on: true,
                operation_start_date: false,
            };
            $scope.postData = postData;
        }

        function onExport(scope) {
            event.preventDefault();
            dtBindFunction();
            var postData = $scope.postData;
            var id = postData['operation_ids'];
            var oper_ids = postData['operator_ids'];
            if (id == undefined || id == '') {
                id = 0;
            }
            var recordsTotal = $scope.records_total;
            var start = 0;
            var end = 5000;
            var index = 1;
            while (start < recordsTotal) {
                if (start >= recordsTotal) {
                    break;
                }

                var url =
                    '/base/production_cost_export?from=' +
                    postData['from_date'] +
                    '&to=' +
                    postData['to_date'] +
                    '&id=' +
                    id +
                    '&op_status=' +
                    postData['op_status'] +
                    '&shift=' +
                    postData['shift_timings'] +
                    '&operator_ids=' +
                    oper_ids +
                    '&start=' +
                    start +
                    '&end_range=' +
                    end +
                    '&index=' +
                    index;
                window.open(url, '_blank');

                start += 5000;
                end += 5000;
                index += 1;
            }
        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });

    return productionCost;
}
productioncostInit();
