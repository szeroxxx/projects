function usersInit() {
  var users = {};
  var columns = [
    {
      name: "first_name",
      title: "First Name",
      link: {
        route: "user",
        params: {
          id: "id",
        },
      },
    },
    {
      name: "last_name",
      title: "Last Name",
    },
    {
      name: "email",
      title: "Email",
    },
    {
      name: "user_role_obj",
      title: "Role",
      sort: false,
    },
    {
      name: "is_active",
      title: "Active",
    },
  ];
  sparrow.registerCtrl(
    "usersCtrl",
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
      var page_title = "Users";
      var config = {
        pageTitle: page_title,
        topActionbar: {
          add: {
            url: "/#/accounts/user/",
          },
          edit: {
            url: "/#/accounts/user/",
          },
          delete: {
            url: "/accounts/users_del/",
          },
          extra: [
            {
              id: "btnUserHistory",
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
                  key: "first_name__icontains",
                  name: "First Name",
                  placeholder: "",
                },
                {
                  key: "last_name__icontains",
                  name: "Last Name",
                  placeholder: "",
                },
                {
                  key: "email__icontains",
                  name: "Email",
                  placeholder: "",
                },
                {
                  key: "role__icontains",
                  name: "Role",
                  placeholder: "",
                },
              ],
            },
            url: "/accounts/users_search/",
            crud: true,
            scrollBody: true,
            columns: columns,
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
        window.location.hash =
          "#/auditlog/logs/userprofile/" +
          selectedId +
          "?title=" +
          rowData[0].first_name;
      }

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

  return users;
}

usersInit();
