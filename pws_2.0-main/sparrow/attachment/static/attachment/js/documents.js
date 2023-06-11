function documentsInit(data) {
  var documents = {};

  sparrow.registerCtrl(
    "documentsCtrl",
    function (
      $scope,
      $rootScope,
      $route,
      $routeParams,
      $compile,
      DTOptionsBuilder,
      DTColumnBuilder,
      $templateCache,
      $interpolate,
      ModalService,
      $compile
    ) {
      $scope.addViewButtons("");
      $scope.currentPage = 1;
      $scope.pageNumber = 1;
      $scope.searchFilters = {
        search_filter: "",
      };
      $scope.attachments = [];
      $scope.isSearchPerformed = false;
      $scope.ngcolor = sparrow.global.get(sparrow.global.keys.ROW_COLOR);
      var config = {
        pageTitle: "Documents",
        topActionbar: {
          extra: [
            {
              id: "onNewDocument",
              function: onNewDocument,
            },
            {
              id: "onAddLink",
              function: onAddLink,
            },
          ],
        },
      };

      function onNewDocument() {
        var permission = false;
        if (data.permissions["can_add_update"] == true) {
          permission = true;
        }
        if (permission == true) {
          window.location.hash = "#/document/add/0";
        } else {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            10
          );
          return;
        }
      };

      function onAddLink() {
        var permission = false;
        if (data.permissions["can_add_update_link"] == true) {
          permission = true;
        }
        if (permission == true) {
          window.location.hash = "#/document/link/0";
        } else {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            10
          );
          return;
        }
      };

      $scope.addDocument = function (event) {
        window.location.hash = "#/documents/add/";
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

  return documents;
}

documentsInit();
