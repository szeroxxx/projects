function customer_usersInit() {
  sparrow.registerCtrl(
    "customer_usersCtrl",
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
        pageTitle: "Customer-Users",
        topActionbar: {
          add: { url: "/#/qualityapp/customer_user/" },
          delete: { url: "/qualityapp/delete_customer_user/" },
          edit: { url: "/#/qualityapp/customer_user/" },
          extra: [
            {
              id: "btnExport",
              function: onExport,
            },
            {
              id: "btnAllDataExport",
              function: onAllDataExport,
            },
            {
              id: "btnHistory",
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
                { key: "username", name: "Username" },
                { key: "first_name", name: "First name" },
                { key: "last_name", name: "Last name" },
                { key: "customer_name", name: "Customer name" },
                { key: "email", name: "Email id" },
                {
                  key: "is_active",
                  name: "Active",
                  type: "list",
                  options: ["Yes", "No"],
                },
                {
                  key: "registration_date",
                  name: "Registration date",
                  type: "datePicker",
                },
              ],
            },
            pagging: true,
            crud: true,
            scrollBody: true,
            url: "/qualityapp/search_customer_user/",
            columns: [
              {
                name: "username",
                title: "Username",
                renderWith: function (data, type, full, meta) {
                  return (
                    '<span><a ng-click="onEditCustomerUser(' +
                    full.id +
                    ')">' +
                    data +
                    "</a></span>"
                  );
                },
              },
              { name: "first_name", title: "First name" },
              { name: "last_name", title: "Last name" },
              { name: "company__name", title: "Customer" },
              { name: "is_active", title: "Active" },
              { name: "email", title: "Email id" },
              { name: "user_role", title: "Role", sort: false },
              { name: "created_on", title: "Created on" },
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
          "#/auditlog/logs/companyuser/" + selectedId + "?title=" + rowData[0].username;
        }
        else{
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
        }
      }

      function onExport() {
        if (data.permissions["can_export_customer_users"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        var selectedIds = $scope.getSelectedIds(1).join([(separator = ",")]);
        var search_parameter = $rootScope.searchParts;
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id;
          }
        );

        var username = "";
        var first_name = "";
        var last_name = "";
        var customer_name = "";
        var email = "";
        var registration_date = "";
        var is_active = "";

        if (search_parameter) {
          if ("Username" in search_parameter) {
            var username = search_parameter["Username"];
          }
          if ("First name" in search_parameter) {
            var first_name = search_parameter["First name"];
          }
          if ("Last name" in search_parameter) {
            var last_name = search_parameter["Last name"];
          }
          if ("Customer name" in search_parameter) {
            var customer_name = search_parameter["Customer name"];
          }
          if ("Email id" in search_parameter) {
            var email = search_parameter["Email id"];
          }
          if ("Registration date" in search_parameter) {
            var registration_date = search_parameter["Registration date"];
          }
          if ("Active" in search_parameter) {
            var is_active = search_parameter["Active"];
          }
        }

        if (!selectedIds) {
          selectedIds = "";
        }

        if(display_data != ""){
          order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }

        sparrow.downloadData("/qualityapp/exports_customer_user/", {
          ids: selectedIds,
          username: username,
          first_name: first_name,
          last_name: last_name,
          customer_name: customer_name,
          email: email,
          registration_date: registration_date,
          is_active: is_active,
          start: $rootScope.start,
          length: $rootScope.length,
          order_by: order_by_,
        });
      };

      function onAllDataExport() {
        if (data.permissions["can_export_customer_users"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        var selectedIds = $scope.getSelectedIds(1).join([(separator = ",")]);
        var search_parameter = $rootScope.searchParts;
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id;
          }
        );

        var username = "";
        var first_name = "";
        var last_name = "";
        var customer_name = "";
        var email = "";
        var registration_date = "";
        var is_active = "";

        if (search_parameter) {
          if ("Username" in search_parameter) {
            var username = search_parameter["Username"];
          }
          if ("First name" in search_parameter) {
            var first_name = search_parameter["First name"];
          }
          if ("Last name" in search_parameter) {
            var last_name = search_parameter["Last name"];
          }
          if ("Customer name" in search_parameter) {
            var customer_name = search_parameter["Customer name"];
          }
          if ("Email id" in search_parameter) {
            var email = search_parameter["Email id"];
          }
          if ("Registration date" in search_parameter) {
            var registration_date = search_parameter["Registration date"];
          }
          if ("Active" in search_parameter) {
            var is_active = search_parameter["Active"];
          }
        }

        if (!selectedIds) {
          selectedIds = "";
        }

        if(display_data != ""){
          order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }

        sparrow.downloadData("/qualityapp/exports_customer_user/", {
          ids: selectedIds,
          username: username,
          first_name: first_name,
          last_name: last_name,
          customer_name: customer_name,
          email: email,
          registration_date: registration_date,
          is_active: is_active,
          start: 0,
          length: display_data[0].recordsTotal,
          order_by: order_by_,
        });
      };

      $scope.onEditCustomerUser = function (id) {
        window.location.href = '#/qualityapp/customer_user/' + id + '/';
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
customer_usersInit();