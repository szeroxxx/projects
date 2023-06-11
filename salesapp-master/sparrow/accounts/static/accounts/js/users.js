function usersInit() {
    sparrow.registerCtrl('usersCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        var partner_type = $routeParams.type;

        var config = {
          pageTitle: "Users",
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
              {
                id: "idRoleChange",
                multiselect: false,
                function: onChangeRole,
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
                  { key: "email__icontains", name: "Email", placeholder: "" },
                  { key: "role__icontains", name: "Role", placeholder: "" },
                ],
              },
              url: "/accounts/users_search/",
              crud: true,
              scrollBody: true,
              columns: [
                { name: "first_name", title: "First Name" },
                { name: "last_name", title: "Last Name" },
                { name: "email", title: "Email" },
                { name: "user_role_obj", title: "Role", sort: false },
              ],
            },
          ],
        };

        function showLog(scope) {
            var selectedId = $scope.getSelectedIds(1)[0];
            var rowData = $.grep($scope['dtInstance1'].DataTable.data(), function (n, i) {
                return n.id == selectedId;
            });
            window.location.hash = "#/auditlog/logs/userprofile/" + selectedId + "?title=" + rowData[0].first_name;
        }

        function onChangeRole(scope) {
          $("#ChangeRoleModel").modal("show");
          setAutoLookup("id_change_role", "/b/lookups/group/", "", true);
        }

        $scope.saveRole = function (e) {
          var selectedId = $scope.getSelectedIds(1)[0];

          var role_ms = $("#id_change_role").magicSuggest();
          if (role_ms.getSelection()[0] != undefined) {
            roleCodeId = role_ms.getSelection()[0].id;
          } else {
            roleCodeId = "";
          }

          console.log('>>>>>>>>>>>>>>',roleCodeId);
        //   if (
        //     $scope.defaultSecondaryStatus == null &&
        //     role_ms.getSelection()[0] == undefined
        //   ) {
        //     $("#secondaryStatusModal").modal("hide");
        //     return;
        //   }
          sparrow.post(
            "/accounts/save_user_role/",
            {
              user_id: selectedId,
              role_id: roleCodeId,
            },
            false,
            function (data) {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Success,
                "Saved",
                5
              );
              $scope.reloadData(1);
              $("#ChangeRoleModel").modal("hide");
            }
          );
        };



        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
}

usersInit();