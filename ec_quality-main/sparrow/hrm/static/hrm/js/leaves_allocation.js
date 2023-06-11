function leavesAllocationInit() {
    var leavesAllocation = {};
    sparrow.registerCtrl('leavesAllocationCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        $scope.current_year = new Date().getFullYear();
        var config = {
            pageTitle: 'Leaves allocation',
            topActionbar: {
                delete: {
                    url: '/hrm/leaves_allocation_delete/',
                },
                extra: [
                    {
                        id: 'btnAddLeavesAllocation',
                        function: showAddLeavesTypeAllocation,
                    },
                    {
                        id: 'deleteleaveAllocation',
                        function: deleteLeaveAllocation,
                        multiselect: true,
                    },
                    {
                        id: 'btnEditLeaveAllocation',
                        function: function () {
                            var selectedId = $scope.getSelectedIds(1).join([(separator = ',')]);
                            $scope.oneditLeavesAllocation(selectedId);
                        },
                    },
                    {
                        id: 'btnLeaveAllocationHistory',
                        multiselect: false,
                        function: showLog,
                    },
                ],
            },
            listing: [
                {
                    index: 1,
                    url: '/hrm/leaves_allocation_search/',
                    search: {
                        params: [
                            {
                                key: 'worker__name__icontains',
                                name: 'Employee name',
                            },
                            {
                                key: 'leave_type__name__icontains',
                                name: 'Leave type',
                            },
                            {
                                key: 'allocate_year',
                                name: 'Year',
                            },
                            { key: 'group_by', name: 'Group by', type: 'group_by', options: { worker: 'Employee', allocate_year: 'Year', leave_type: 'Leave type' } },
                        ],
                    },
                    crud: true,
                    columns: [
                        {
                            name: 'worker',
                            title: 'Employee',
                            renderWith: function (data, type, full) {
                                return '<span class="a-link" ng-click="oneditLeavesAllocation(' + full.id + ')">' + data + '</span>';
                            },
                        },
                        {
                            name: 'allocate_year',
                            title: 'Year',
                        },
                        {
                            name: 'leave_type',
                            title: 'Leave type',
                        },
                        {
                            name: 'days',
                            title: 'Days',
                        },
                        {
                            name: 'description',
                            title: 'Description',
                        },
                    ],
                },
            ],
        };

        var leave_allocate = [
            {
                id: $scope.current_year - 1,
                name: $scope.current_year - 1,
            },
            {
                id: $scope.current_year,
                name: $scope.current_year,
            },
            {
                id: $scope.current_year + 1,
                name: $scope.current_year + 1,
            },
            {
                id: $scope.current_year + 2,
                name: $scope.current_year + 2,
            },
            {
                id: $scope.current_year + 3,
                name: $scope.current_year + 3,
            },
        ];

        setAutoLookup('id_allocate_year', leave_allocate, '', true);

        setAutoLookup('id_worker', '/b/lookups/labour/', 'worker', true);

        setAutoLookup('id_leave_type', '/b/lookups/leave_type/', 'id_worker', true);

        var selectedLevelId = 0;

        function showAddLeavesTypeAllocation() {
            clearAllocationForm();

            selectedLevelId = 0;
            $('#myModalLabel').text('Add leave allocation');
            var allocate_year = $('#id_allocate_year').magicSuggest();
            allocate_year.setSelection([
                {
                    name: $scope.current_year,
                    id: $scope.current_year,
                },
            ]);
            $('#leavesAllocationModel').modal('show');
        }

        $scope.oneditLeavesAllocation = function (leavesAllocationId) {
            selectedLevelId = leavesAllocationId;
            sparrow.post(
                '/hrm/leaves_allocation_get/',
                {
                    id: leavesAllocationId,
                },
                false,
                function (data) {
                    var worker = $('#id_worker').magicSuggest();
                    var leave_type = $('#id_leave_type').magicSuggest();
                    worker.setSelection([
                        {
                            name: data.leaves_allocation.worker__name,
                            id: data.leaves_allocation.worker_id,
                        },
                    ]);
                    leave_type.setSelection([
                        {
                            name: data.leaves_allocation.leave_type__name,
                            id: data.leaves_allocation.leave_type_id,
                        },
                    ]);
                    var allocate_year = $('#id_allocate_year').magicSuggest();
                    allocate_year.setSelection([
                        {
                            name: data.leaves_allocation.allocate_year,
                            id: data.leaves_allocation.allocate_year,
                        },
                    ]);
                    $('#id_days').val(Math.round(data.leaves_allocation.days));
                    $('#id_description').val(data.leaves_allocation.description);
                    $('#myModalLabel').text('Edit leave allocation');
                    $('#leavesAllocationModel').modal('show');
                }
            );
        };

        var leave_type_ms = $('#id_leave_type').magicSuggest();
        $(leave_type_ms).on('selectionchange', function (e, m) {
            if (selectedLevelId == 0) {
                leaveTypeId = $('#hid_leave_type').val();
                if (leaveTypeId == undefined) {
                    $('#id_days').val(' ');
                } else {
                    sparrow.post(
                        '/hrm/get_leave_days/',
                        {
                            leave_type: leaveTypeId,
                        },
                        false,
                        function (data) {
                            $('#id_days').val(data.days);
                        }
                    );
                }
            }
        });

        function deleteLeaveAllocation(rootScope) {
            sparrow.showConfirmDialog(ModalService, 'Are you sure you want to delete leave allocation?', 'Delete leave allocation', function (confirmAction) {
                if (confirmAction) {
                    var selectedIds = $scope.getSelectedIds(1).join([(separator = ',')]);
                    sparrow.post(
                        '/hrm/leaves_allocation_delete/',
                        {
                            ids: selectedIds,
                        },
                        true,
                        function (data) {
                            $scope.reloadData(1);
                        }
                    );
                }
            });
        }

        function clearAllocationForm() {
            var worker = $('#id_worker').magicSuggest();
            var leave_type = $('#id_leave_type').magicSuggest();
            worker.clear();
            leave_type.clear();

            $('#id_description').val('');
            $('#myModalLabel').text('');
            $('#id_days').val('');
            $('#id_days').val('');
        }

        $scope.saveUser = function (event) {
            event.preventDefault();
            sparrow.postForm(
                {
                    id: selectedLevelId,
                },
                $('#leavesAllocationForm'),
                $scope,
                function (data) {
                    if (data.code == 1) {
                        $('#leavesAllocationModel').modal('hide');
                        $scope.reloadData(1);
                    }
                }
            );
        };

        function showLog(scope) {
            var selectedId = $scope.getSelectedIds(1);
            var rowData = $.grep($scope['dtInstance1'].DataTable.data(), function (n, i) {
                return n.id == selectedId;
            });
            window.location.hash = '#/auditlog/logs/leaveallocation/' + selectedId + '?title=' + rowData[0].worker;
        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });

    return leavesAllocation;
}
leavesAllocationInit();
