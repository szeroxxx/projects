function customerLoginValidateModalInit() {


    var customerLoginValidateModal = {};
    sparrow.registerCtrl('customerLoginValidateModalCtrl', function (
        $scope,
        $rootScope,
        $route,
        $routeParams,
        $compile,
        DTOptionsBuilder,
        DTColumnBuilder,
        $templateCache,
        ModalService,
        dataModal
    ) {
        $scope.ValidLogin = function(valid){
            if(valid){
                window.open("/sales/customer_login/" + dataModal.entity_nr + "/" + dataModal.from + "/" + dataModal.ec_user_id + "/" + dataModal.customer_id + "/");

            }

        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, {}, ModalService);
    });
    return customerLoginValidateModal;
}
customerLoginValidateModalInit();
