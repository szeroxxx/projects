function workcenterandresourcesInit() {
    var workcenterandresources = {};

    sparrow.registerCtrl(
        'workcenter_and_resources_report',
        function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
            var config = {
                pageTitle: 'Work-center and Resources report',
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
                        url: '/base/workcenters_and_resources_search/',
                        scrollBody: true,
                        paging: true,
                        postData: {
                            workcenter_ids: [],
                        },
                        columns: [
                            { name: 'workcenter__name', title: 'Workcenter Name' },
                            { name: 'attrib_name', title: 'Workcenter attributed cost line' },
                            { name: 'attrib_value', title: 'Workcenter unit cost' },
                            { name: 'attrib_uoc__name', title: 'Workcenter unit' },
                            { name: 'cost_type', title: 'Workcenter cost type' },
                            { name: 'resources_name', title: 'Resource name', sort: false },
                            { name: 'workcenter_line__is_active', title: 'Active' },
                            { name: 'workcenter_line__available_hours', title: 'Available hours', sort: false },
                            { name: 'resource_attribute_cost_line', title: 'Resource attributed cost line', sort: false },
                            { name: 'resource_unit_cost', title: 'Resource unit cost', sort: false },
                            { name: 'resource_unit', title: 'Resource unit', sort: false },
                            { name: 'resource_cost_type', title: 'Resource cost type', sort: false },
                        ],
                    },
                ],
            };
            setAutoLookup('id_workcenter', '/b/lookups/workcenter/', '', true, true, false, null, 20, null, null, null);

            $('#load_btn').on('click', function (event) {
                sparrow.global.set('SEARCH_EVENT', true);
                dtBindFunction();
                config.listing[0].postData = $scope.postData;
                $scope.reloadData(1, config.listing[0]);
            });

            function dtBindFunction() {
                var workcenter_ids = [];
                $('input[name = workcenter]').each(function (i, obj) {
                    workcenter_ids.push(parseInt($(obj).val()));
                });
                if (workcenter_ids == undefined) {
                    workcenter_ids = '';
                }
                var postData = {
                    workcenter_ids: workcenter_ids,
                };
                $scope.postData = postData;
            }
            function onExport(scope) {
                event.preventDefault();
                dtBindFunction();
                var postData = $scope.postData;
                var id = postData['workcenter_ids'];
                if (id == undefined || id == '') {
                    id = 0;
                }
                var url = '/base/workcenters_and_resources_export?workcenter_ids=' + id;

                window.open(url, '_blank');
            }
            sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
        }
    );
    return workcenterandresources;
}
workcenterandresourcesInit();
