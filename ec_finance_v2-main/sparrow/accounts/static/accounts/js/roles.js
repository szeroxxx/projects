function rolesInit() {
  var roles = {};

  sparrow.registerCtrl(
    "rolesCtrl",
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
      var config = {
        pageTitle: "Roles",
        topActionbar: {
          add: {
            url: "/#/accounts/role/",
          },
          edit: {
            url: "/#/accounts/role/",
          },
          delete: {
            url: "/accounts/role_del/",
          },
          extra: [
            {
              id: "btnRoleHistory",
              multiselect: false,
              function: showLog,
            },
          ],
        },
        listing: [
          {
            index: 1,
            search: {
              params: [
                {
                  key: "group__name",
                  name: "Role name",
                },
              ],
            },
            url: "/accounts/roles_search/",
            crud: true,
            scrollBody: true,
            columns: [
              {
                name: "group__name",
                title: "Role name",
                link: {
                  route: "role",
                  params: {
                    id: "id",
                  },
                },
              },
              {
                name: "description",
                title: "Description",
              },
            ],
          },
        ],
      };

      function showLog(scope) {
        var selectedId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        if(selectedId){
          window.location.hash =
            "#/auditlog/logs/group/" + selectedId + "?title=" + rowData[0].name;
        }
        else{
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 3);
        }
      }

      Mousetrap.reset()
      Mousetrap.bind('shift+h',showLog)
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

  return roles;
}

rolesInit();
