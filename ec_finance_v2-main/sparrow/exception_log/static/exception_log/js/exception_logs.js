function exception_logsInit() {
    var exception_logs = {};

    sparrow.registerCtrl('exception_logsCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        var exception_type = window.location.href.split('/').reverse()[1];
        var title = 'Exception logs (' + exception_type + ')';
        $scope.addViewButtons('');
        config = {
            pageTitle: title,
            topActionbar: {
                delete: {
                    url: '/exception_log/delete_exception_log/',
                },
                extra: [
                    {
                        id: 'btnDeleteAllExceptionLogs',
                        function: deleteAllExceptionLogs,
                    },
                ],
            },
            listing: [
                {
                    index: 1,
                    search: {
                        params: [
                            { key: 'class_name', name: 'Class Name' },
                            { key: 'message', name: 'Message' },
                        ],
                    },
                    url: '/exception_log/exception_log_search/',
                    crud: true,
                    scrollBody: true,
                    postData: {
                        exception_type: exception_type,
                    },
                    columns: [
                        { name: 'class_name', title: 'Class Name' },
                        { name: 'message', title: 'Message' },
                        { name: 'traceback', title: 'Traceback' },
                        { name: 'created_on', title: 'Created on', sort: false },
                    ],
                },
            ],
        };

        function deleteAllExceptionLogs() {
            event.preventDefault();
            sparrow.showConfirmDialog(ModalService, 'Are you sure you want to delete all "' + exception_type + '" data?', 'Delete all same type exception data', function (
                confirm
            ) {
                if (confirm) {
                    sparrow.post(
                        '/exception_log/delete_exception_log/',
                        {
                            exception_type: exception_type,
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
    return exception_logs;
}
exception_logsInit();
