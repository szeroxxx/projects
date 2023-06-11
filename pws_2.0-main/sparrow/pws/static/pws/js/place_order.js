function place_orderInit() {
    var place_order = {};
    sparrow.registerCtrl('place_orderCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        var page_title = 'Place Order';
        var config = {
            pageTitle: page_title,
            topActionbar: {
                // add: {
                //     url: '/#/accounts/user/',
                // },
                // edit: {
                //     url: '/#/accounts/user/',
                // },
                // delete: {
                //     url: '/accounts/users_del/',
                // },

            },
        };

        setAutoLookup("id_company", "/lookups/companies/", "", false, true);
        setAutoLookup("id_layers", "/lookups/layers/", "", false, true);
        setAutoLookup("id_services", "/lookups/services/", "", false, true);
        setAutoLookup("id_operator", "/lookups/operators/", "", false, true);




      //   $scope.saveOrderFlow = function () {
      //   sparrow.postForm(
      //     {
      //       order_flow_mapping:0,
      //     },
      //   $("#frmSaveOrderFlow"),
      //   $scope,
      //     function (data) {
      //         if (data.code == 1) {
      //         window.location.hash = "#/accounts/order_flow/";
      //         $route.reload();
      //         }
      //     }
      //   );
      // };

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });

    return place_order;
}
place_orderInit();
