function customerDashBoardInit(data) {
  var customerDashBoard = {};

  sparrow.registerCtrl(
    "customerDashBoardCtrl",
    function (
      $scope,
      $rootScope,
      Upload,
      $route,
      $routeParams,
      $compile,
      DTOptionsBuilder,
      DTColumnBuilder,
      $templateCache,
      ModalService
    ) {
      $scope.addViewButtons("");
      var config = {
        pageTitle: "Dashboard",
      };
      sparrow.setup(
        $scope,
        $rootScope,
        $route,
        $compile,
        DTOptionsBuilder,
        DTColumnBuilder,
        $templateCache,
        config,
        ModalService
      );
    }
  );

  return customerDashBoard;
}

customerDashBoard = customerDashBoardInit();
