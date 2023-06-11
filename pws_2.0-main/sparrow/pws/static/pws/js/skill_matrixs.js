function skill_matrixsInit() {
  sparrow.registerCtrl(
    "skill_matrixsCtrl",
    function (
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
      $scope.addViewButtons("");
      var config = {
        pageTitle: "Skill matrix",
        topActionbar: {
            edit: {
              url: "/#/pws/skill_matrix/",
            },
            extra: [
              {
                id: "btnback",
                function: onBack,
              },
            ],
        },
        listing: [
          {
            index: 1,
            search: {
              params:[
                {key: "customer", name:"Customer"},
              ],
            },
            pagging:true,
            scrollBody: true,
            url: "/pws/search_skill_matrix/",
            columns: [
              { name: "name", title: "Customer name",
                renderWith: function (data, type, full, meta) {
                  return (
                    '<span><a title="Click on customer name to add skill matrix" ng-click="onEditOperator(' +
                    full.id +
                    ')">' +
                    data +
                    "</a></span>"
                  );
                },
              },
            ],
          },
        ],
      };
      $scope.onEditOperator = function (id) {
        window.location.href = "#/pws/skill_matrix/" + id + "/";
      };
      function onBack() {
         window.location.href = "#/pws/order_allocations/";
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
}
skill_matrixsInit();
