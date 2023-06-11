function leaveTypeInit() {
    var leave_type = {};
    sparrow.registerCtrl('leaveCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        var config = {
            pageTitle: 'Leave types',
            topActionbar: {
                extra: [
                    {
                        id: 'btnAddLeaveType',
                        function: showAddLeaveTypeProcess,
                    },
                    {
                        id: 'deleteleavetype',
                        function: deleteLeaveType,
                        multiselect: true,
                    },
                    {
                        id: 'btnEditLeaveType',
                        function: function () {
                            var selectedId = $scope.getSelectedIds(1).join([(separator = ',')]);
                            $scope.oneditLeaveType(selectedId);
                        },
                    },
                ],
            },
            listing: [
                {
                    index: 1,
                    url: '/hrm/leave_type_search/',
                    crud: true,
                    columns: [
                        {
                            name: 'name',
                            title: 'Leave type',
                            renderWith: function (data, type, full) {
                                return '<a style="cursor:pointer;" ng-click="oneditLeaveType(' + full.id + ')">' + data + '</a>';
                            },
                        },
                        {
                            name: 'days',
                            title: 'Default days',
                        },
                    ],
                },
            ],
        };

        var selectedLevelId = 0;

        function showAddLeaveTypeProcess() {
            selectedLevelId = 0;
            $('#myModalLabel').text('Add leave type');
            $('#leaveTypeModel').modal('show');
            $('#id_days').val('');
            $('#id_name-error').hide();
            $('#id_name').val('');
        }

        $scope.oneditLeaveType = function (leaveTypeId) {
            selectedLevelId = leaveTypeId;
            $('#id_name').val('');
            $('#id_days').val('');
            sparrow.post(
                '/hrm/get_leave_type/',
                {
                    id: leaveTypeId,
                },
                false,
                function (data) {
                    $('#id_name').val(data.leave_type.name);
                    $('#id_days').val(data.leave_type.days);
                    $('#myModalLabel').text('Edit leave type');
                    $('#leaveTypeModel').modal('show');
                }
            );
        };

        $scope.saveLeaveType = function (event) {
            event.preventDefault();
            sparrow.postForm(
                {
                    id: selectedLevelId,
                },
                $('#leaveTypeForm'),
                $scope,
                function (data) {
                    if (data.code == 1) {
                        $('#leaveTypeModel').modal('hide');
                        $scope.reloadData(1);
                    }
                }
            );
        };

        function deleteLeaveType(rootScope) {
            sparrow.showConfirmDialog(ModalService, 'Are you sure you want to delete leave type?', 'Delete leave type', function (confirmAction) {
                if (confirmAction) {
                    var selectedIds = $scope.getSelectedIds(1).join([(separator = ',')]);
                    sparrow.post(
                        '/hrm/leave_type_delete/',
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

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });

    return leave_type;
}

leave_type = leaveTypeInit();
