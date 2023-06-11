function productioncostv2Init() {
    sparrow.registerCtrl('productionCostV2Ctrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        var config = {
            pageTitle: 'Work in progress production cost v2',

            listing: [
                {
                    index: 1,
                    url: '/base/production_cost_v2_search/',
                    paging: true,
                    scrollBody: true,
                    postData: {
                        month: '',
                        year: '',
                    },
                    columns: [
                        {
                            name: 'mfg_order_num',
                            title: 'Mfg number',
                        },
                        {
                            name: 'operation_name',
                            title: 'Operation name',
                            sort: false,
                        },

                        {
                            name: 'operation_status',
                            title: 'Operation status',
                            sort: false,
                        },
                        {
                            name: 'opeartion_start_time',
                            title: 'Operation start time',
                            sort: false,
                        },
                        {
                            name: 'opeartion_end_time',
                            title: 'Operation end time',
                            sort: false,
                        },
                        {
                            name: 'pre_machine_cost',
                            title: 'Machine estimated',
                            sort: false,
                        },
                        {
                            name: 'machine_cost',
                            title: 'Machine actual',
                            sort: false,
                        },

                        {
                            name: 'pre_labour_cost',
                            title: 'Employee estimated',
                            class: 'employee',
                            sort: false,
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
                            title: 'Workcenter estimated',
                            class: 'workcenter',
                            sort: false,
                        },
                        {
                            name: 'workcenter_cost',
                            title: 'Workcenter actual',
                            class: 'workcenter',
                            sort: false,
                        },
                        { name: 'pre_total_cost', title: 'Total estimated', sort: false },
                        { name: 'total_cost', title: 'Total actual', sort: false },
                    ],
                },
            ],
        };

        $('#id_load_btn').on('click', function (event) {
            sparrow.global.set('SEARCH_EVENT', true);
            date_bind = dtBindFunction();
            if (!date_bind) {
                return false;
            }
            event.preventDefault();
            $('#btnExport').show();
            config.listing[0].postData = $scope.postData;
            $scope.reloadData(1, config.listing[0]);
        });

        function dtBindFunction() {
            var date = $('#datepicker').datepicker('getDate');
            year = date.getFullYear();
            month = date.getMonth() + 1;
            if (isNaN(year) && isNaN(month)) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select month and year', 5);
                return false;
            }
            var postData = {
                year: year,
                month: month,
            };
            $scope.postData = postData;
            return true;
        }
        $scope.onExport = function (event) {
            event.preventDefault();
            dtBindFunction();
            var postData = $scope.postData;
            var url = '/base/production_cost_by_operation_v2_export?&month=' + postData['month'] + '&year=' + postData['year'];
            window.open(url, '_blank');
        };

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
}

productioncostv2Init();
