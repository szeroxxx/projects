function qualificationTypeInit() {
    var qualification_type = {};
    sparrow.registerCtrl(
        'qualificationCtrl',
        function ($scope, $rootScope, $route, $routeParams, $compile, $uibModal, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
            var config = {
                pageTitle: 'Academic qualifications',
                topActionbar: {
                    extra: [
                        {
                            id: 'btnAddQualification',
                            function: AddqualificationType,
                        },
                        {
                            id: 'btnQualificationHistory',
                            function: showLog,
                            multiselect: false,
                        },
                        {
                            id: 'deleteQualificationtype',
                            function: deleteQualification,
                            multiselect: true,
                        },
                        {
                            id: 'btnEditQualificationType',
                            function: function () {
                                var selectedId = $scope.getSelectedIds(1).join([(separator = ',')]);
                                $scope.oneditQualificationType(selectedId);
                            },
                        },
                    ],
                },
                listing: [
                    {
                        index: 1,
                        search: {
                            params: [
                                {
                                    key: 'qualification__icontains',
                                    name: 'Academic qualifications',
                                },
                            ],
                        },
                        url: '/hrm/qualification_type_search/',
                        crud: true,
                        scrollBody: true,
                        columns: [
                            {
                                name: 'qualification',
                                title: 'Academic qualifications',
                                renderWith: function (data, type, full, meta) {
                                    return '<a style="cursor:pointer;" ng-click="oneditQualificationType(' + full.id + ')">' + data + '</a>';
                                },
                            },
                        ],
                    },
                ],
            };

            var selectedqualificationId = 0;

            function AddqualificationType() {
                var templateUrl = '/hrm/qualification_type/0';

                var workcenterOperstorModel = $uibModal.open({
                    templateUrl: templateUrl,
                    controller: 'qualificationtypesCtrl',
                    scope: $scope,
                    size: 'md',
                });
                $scope.qualificationMasterModelTitle = 'Add qualification';
                workcenterOperstorModel.rendered.then(function () {
                    $('#id_name').val();
                });

                workcenterOperstorModel.closed.then(function () {
                    $templateCache.remove(templateUrl);
                });
            }

            $scope.oneditQualificationType = function (qualificatipnTypeId) {
                selectedqualificationId = qualificatipnTypeId;
                var templateUrl = '/hrm/qualification_type/' + selectedqualificationId;
                var workcenterOperstorModel = $uibModal.open({
                    templateUrl: templateUrl,
                    controller: 'qualificationtypesCtrl',
                    scope: $scope,
                    size: 'md',
                    backdrop: false,
                });
                $scope.qualificationMasterModelTitle = 'Edit qualification';

                workcenterOperstorModel.rendered.then(function () {
                    sparrow.post(
                        '/hrm/get_qualification_type/',
                        {
                            id: qualificatipnTypeId,
                        },
                        false,
                        function (data) {
                            $('#id_name').val(data.qualification_type.name);
                            $('#qualificationId').text(data.qualification_type.id);
                        }
                    );
                });

                workcenterOperstorModel.closed.then(function () {
                    $templateCache.remove(templateUrl);
                });
            };

            $scope.saveQualificationType = function (event) {
                event.preventDefault();
                sparrow.postForm(
                    {
                        id: selectedqualificationId,
                    },
                    $('#qualificationTypeForm'),
                    $scope,
                    function (data) {
                        if (data.code == 1) {
                            $('#OperationModel').modal('hide');
                            $scope.reloadData();
                        }
                    }
                );
            };

            function showLog(scope) {
                var selectedId = $scope.getSelectedIds(1)[0];
                var rowData = $.grep($scope['dtInstance1'].DataTable.data(), function (n, i) {
                    return n.id == selectedId;
                });
                window.location.hash = '#/auditlog/logs/academicqualification/' + selectedId + '?title=' + rowData[0].qualification;
            }

            function deleteQualification(rootScope) {
                sparrow.showConfirmDialog(ModalService, 'Are you sure you want to delete qualification type?', 'Delete qualification type', function (confirmAction) {
                    if (confirmAction) {
                        var selectedIds = $scope.getSelectedIds(1).join([(separator = ',')]);
                        sparrow.post(
                            '/hrm/qualification_type_delete/',
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
        }
    );

    return qualification_type;
}

qualification_type = qualificationTypeInit();
