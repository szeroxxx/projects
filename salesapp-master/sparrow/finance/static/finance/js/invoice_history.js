function invoiceHistoryInit() {

    var invoiceHistoryModal = {};
    sparrow.registerCtrl('invoiceHistoryModalCtrl', function (
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
    return invoiceHistoryModal;
}

invoiceHistoryInit();
