function creditReportModalInit(data) {


    var creditReportModal = {};
    sparrow.registerCtrl('creditReportModalCtrl', function (
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


        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, {}, ModalService);
    });
    return creditReportModal;
}
creditReportModalInit();
