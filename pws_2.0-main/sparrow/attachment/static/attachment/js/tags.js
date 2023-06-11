function tagsInit() {
    var tags = {};

    sparrow.registerCtrl('tagsCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, $uibModal, DTColumnBuilder, $templateCache, ModalService) {
        // url = '/partners/states_search/';
        title = 'Tags';
        var config = {
            pageTitle: 'Tags',
            topActionbar: {
                add: {
                    url: '/#/attachment/tag/',
                },
                extra: [
                    {
                        id: 'btnEdittag',
                        function: onEditTag,
                        multiselect: false,
                    },
                    {
                        id: 'btntagHistory',
                        function: showLog,
                        multiselect: false,
                    },
                    {
                        id: 'btnDelete',
                        multiselect: true,
                        function: deleteTag,
                    },
                ],
            },
            listing: [
                {
                    index: 1,
                    search: {
                        params: [{ key: 'name__icontains', name: 'Tag' }],
                    },
                    url: '/attachment/tag_search/',
                    crud: true,
                    scrollBody: true,
                    columns: [
                        {
                            name: 'name',
                            title: 'Name',
                            renderWith: function (data, type, full, meta) {
                                return '<a href="#/attachment/tag/' + full.id + '/' + '">' + data + '</a>';
                            },
                        },
                        { name: 'created_on', title: 'Created on' },
                        { name: 'created_by', title: 'Created by' },
                    ],
                },
            ],
        };

        function deleteTag(event) {
            // var selectedIds = $scope.getSelectedIds(1).join([(separator = ',')]);
            // sparrow.post(
            //     '/attachment/check_tag_use/',
            //     {
            //         ids: selectedIds,
            //     },
            //     false,
            //     function (data) {
            //         if (data.code == 1 && data.data == true) {
            //             $scope.msg = 'This tag has been assigned to the documents.Are you sure you want to delete record?';
            //         }
            //     }
            // );
            // setTimeout(function () {
            sparrow.showConfirmDialog(ModalService, 'Are you sure you want to delete record?', 'Delete record', function (confirm) {
                if (!confirm) {
                    return;
                }
                var selectedIds = $scope.getSelectedIds(1).join([(separator = ',')]);
                sparrow.post(
                    '/attachment/tag_del/',
                    {
                        ids: selectedIds,
                    },
                    true,
                    function (data) {
                        if (data.code == 1) {
                            sparrow.showMessage('appMsg', sparrow.MsgType.Success, data.msg, 10);
                            $scope.reloadData(1);
                            return false;
                        }
                        sparrow.showMessage('appMsg', sparrow.MsgType.Error, data.msg, 5);
                        return false;
                    }
                );
            });
            // }, 100);
        }

        function onEditTag(scope) {
            var selectedId = $scope.getSelectedIds(1)[0];
            window.location.hash = '#/attachment/tag/' + selectedId;
        }

        function showLog(scope) {
            var selectedId = $scope.getSelectedIds(1)[0];
            var rowData = $.grep($scope['dtInstance' + 1].DataTable.data(), function (n, i) {
                return n.id == selectedId;
            });
            window.location.hash = '#/auditlog/logs/tag/' + selectedId + '?title=' + rowData[0].name;
        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
        sparrow.setTitle(title);
    });

    return tags;
}

tagsInit();
