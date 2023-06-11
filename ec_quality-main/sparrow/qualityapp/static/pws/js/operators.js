function operatorsInit() {
  sparrow.registerCtrl(
    "operatorsCtrl",
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
        pageTitle: "Operators",
        topActionbar: {
          add: { url: "/#/qualityapp/operator/" },
          edit: { url: "/#/qualityapp/operator/" },
          delete: { url: "/qualityapp/delete_operators/" },
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
            {
              id: "btnviewPI",
              multiselect: false,
              function: onViewPI,
            },
          ],
        },
        listing: [
          {
            index: 1,
            search: {
              params: [
                { key: "username", name: "Operator" },
                { key: "first_name", name: "First Name" },
                { key: "last_name", name: "Last Name" },
                { key: "operator_type", name: "User type" },
                { key: "operator_group", name: "Group" },
                { key: "shift", name: "Today's shift" },
                { key: "permanent_shift", name: "Permanent shift" },
                { key: "email", name: "Email" },
                {
                  key: "is_active",
                  name: "Active",
                  type: "list",
                  options: ["Yes", "No"],
                },
              ],
            },
            url: "/qualityapp/search_operator/",
            crud: true,
            scrollBody: true,
            columns: [
              {
                name: "username",
                title: "Operator name",
                renderWith: function (data, type, full, meta) {
                  return (
                    '<span><a ng-click="onEditOperator(' +
                    full.id +
                    ')">' +
                    data +
                    "</a></span>"
                  );
                },
              },
              { name: "first_name", title: "First name" },
              { name: "last_name", title: "Last name" },
              { name: "email", title: "Email" },
              { name: "user_role", title: "Role", sort: false },
              { name: "operator_group", title: "Group" },
              { name: "is_active", title: "Active" },
              { name: "created_on", title: "Created on" },
              { name: "operator_type", title: "User type" },
              { name: "shift", title: "Today shift" },
              { name: "permanent_shift", title: "Permanent shift" },
              {
                name: "target_efficiency",
                title: "Target efficiency",
              },
              {
                name: "minimum_efficiency",
                title: "Minimum efficiency",
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
          "#/auditlog/logs/operator/" + selectedId + "?title=" + rowData[0].first_name;
        }
        else{
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
        }
      }

      function onExport() {
        if (data.permissions["can_export_operators"] == false) {
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
        var operator_type = "";
        var operator_group = "";
        var shift = "";
        var permanent_shift = "";
        var email = "";
        var is_active = "";

        if (search_parameter) {
          if ("Operator" in search_parameter) {
            var username = search_parameter["Operator"];
          }
          if ("First name" in search_parameter) {
            var first_name = search_parameter["First name"];
          }
          if ("Last name" in search_parameter) {
            var last_name = search_parameter["Last name"];
          }
          if ("User type" in search_parameter) {
            var operator_type = search_parameter["User type"];
          }
          if ("Group" in search_parameter) {
            var operator_group = search_parameter["Group"];
          }
          if ("Today's shift" in search_parameter) {
            var shift = search_parameter["Today's shift"];
          }
          if ("Permanent shift" in search_parameter) {
            var permanent_shift = search_parameter["Permanent shift"];
          }
          if ("Email" in search_parameter) {
            var email = search_parameter["Email"];
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

        sparrow.downloadData("/qualityapp/exports_operators/", {
          ids: selectedIds,
          username: username,
          first_name: first_name,
          last_name: last_name,
          operator_type: operator_type,
          operator_group: operator_group,
          shift: shift,
          permanent_shift: permanent_shift,
          email: email,
          is_active: is_active,
          start: $rootScope.start,
          length: $rootScope.length,
          order_by: order_by_,
        });
      };

      function onAllDataExport() {
        if (data.permissions["can_export_operators"] == false) {
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
        var operator_type = "";
        var operator_group = "";
        var shift = "";
        var permanent_shift = "";
        var email = "";
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
          if ("User type" in search_parameter) {
            var operator_type = search_parameter["User type"];
          }
          if ("Group" in search_parameter) {
            var operator_group = search_parameter["Group"];
          }
          if ("Today's shift" in search_parameter) {
            var shift = search_parameter["Today's shift"];
          }
          if ("Permanent shift" in search_parameter) {
            var permanent_shift = search_parameter["Permanent shift"];
          }
          if ("Email" in search_parameter) {
            var email = search_parameter["Email"];
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

        sparrow.downloadData("/qualityapp/exports_operators/", {
          ids: selectedIds,
          username: username,
          first_name: first_name,
          last_name: last_name,
          operator_type: operator_type,
          operator_group: operator_group,
          shift: shift,
          permanent_shift: permanent_shift,
          email: email,
          is_active: is_active,
          start: 0,
          length: display_data[0].recordsTotal,
          order_by: order_by_,
        });
      };

      $scope.onEditOperator = function (id) {
        window.location.href = '#/qualityapp/operator/' + id + '/';
      };

      function onViewPI() {
        var selectedId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        $("#viewPITitle").text("User PI points");
        $("#viewPIModel").modal("show");
        sparrow.post(
          "/qualityapp/viewpi/",
          {
            id: selectedId,
          },
          false,
          function (data) {
            if (data.nc_count[0] == undefined) {
              rowData[0].doj == "" ?  $("#id_doj").hide() : $("#id_doj").text("DOJ :" + " " + rowData[0].doj);
              $("#id_rejection_jan").text(0);
              $("#id_rejection_feb").text(0);
              $("#id_rejection_mar").text(0);
              $("#id_rejection_apr").text(0);
              $("#id_rejection_may").text(0);
              $("#id_rejection_june").text(0);
              $("#id_rejection_july").text(0);
              $("#id_rejection_aug").text(0);
              $("#id_rejection_sep").text(0);
              $("#id_rejection_oct").text(0);
              $("#id_rejection_nov").text(0);
              $("#id_rejection_dec").text(0);
              $("#id_remark_jan").text(0);
              $("#id_remark_feb").text(0);
              $("#id_remark_mar").text(0);
              $("#id_remark_apr").text(0);
              $("#id_remark_may").text(0);
              $("#id_remark_june").text(0);
              $("#id_remark_july").text(0);
              $("#id_remark_aug").text(0);
              $("#id_remark_sep").text(0);
              $("#id_remark_oct").text(0);
              $("#id_remark_nov").text(0);
              $("#id_remark_dec").text(0);
              $("#id_target_efficiency_jan").text(0);
              $("#id_target_efficiency_feb").text(0);
              $("#id_target_efficiency_mar").text(0);
              $("#id_target_efficiency_apr").text(0);
              $("#id_target_efficiency_may").text(0);
              $("#id_target_efficiency_june").text(0);
              $("#id_target_efficiency_july").text(0);
              $("#id_target_efficiency_aug").text(0);
              $("#id_target_efficiency_sep").text(0);
              $("#id_target_efficiency_oct").text(0);
              $("#id_target_efficiency_nov").text(0);
              $("#id_target_efficiency_dec").text(0);
              $("#id_min_efficiency_jan").text(0);
              $("#id_min_efficiency_feb").text(0);
              $("#id_min_efficiency_mar").text(0);
              $("#id_min_efficiency_apr").text(0);
              $("#id_min_efficiency_may").text(0);
              $("#id_min_efficiency_june").text(0);
              $("#id_min_efficiency_july").text(0);
              $("#id_min_efficiency_aug").text(0);
              $("#id_min_efficiency_sep").text(0);
              $("#id_min_efficiency_oct").text(0);
              $("#id_min_efficiency_nov").text(0);
              $("#id_min_efficiency_dec").text(0);
            } else {
              rowData[0].doj == "" ?  $("#id_doj").hide() : $("#id_doj").text("DOJ :" + " " + rowData[0].doj);
              $("#id_rejection_jan").text(data.nc_count[0].rejection_jan);
              $("#id_rejection_feb").text(data.nc_count[0].rejection_feb);
              $("#id_rejection_mar").text(data.nc_count[0].rejection_mar);
              $("#id_rejection_apr").text(data.nc_count[0].rejection_apr);
              $("#id_rejection_may").text(data.nc_count[0].rejection_may);
              $("#id_rejection_june").text(data.nc_count[0].rejection_june);
              $("#id_rejection_july").text(data.nc_count[0].rejection_july);
              $("#id_rejection_aug").text(data.nc_count[0].rejection_aug);
              $("#id_rejection_sep").text(data.nc_count[0].rejection_sep);
              $("#id_rejection_oct").text(data.nc_count[0].rejection_oct);
              $("#id_rejection_nov").text(data.nc_count[0].rejection_nov);
              $("#id_rejection_dec").text(data.nc_count[0].rejection_dec);
              $("#id_remark_jan").text(data.nc_count[0].remark_jan);
              $("#id_remark_feb").text(data.nc_count[0].remark_feb);
              $("#id_remark_mar").text(data.nc_count[0].remark_mar);
              $("#id_remark_apr").text(data.nc_count[0].remark_apr);
              $("#id_remark_may").text(data.nc_count[0].remark_may);
              $("#id_remark_june").text(data.nc_count[0].remark_june);
              $("#id_remark_july").text(data.nc_count[0].remark_july);
              $("#id_remark_aug").text(data.nc_count[0].remark_aug);
              $("#id_remark_sep").text(data.nc_count[0].remark_sep);
              $("#id_remark_oct").text(data.nc_count[0].remark_oct);
              $("#id_remark_nov").text(data.nc_count[0].remark_nov);
              $("#id_remark_dec").text(data.nc_count[0].remark_dec);
              $("#id_target_efficiency_jan").text(data.efficiency[0].target_efficiency_jan);
              $("#id_target_efficiency_feb").text(data.efficiency[0].target_efficiency_feb);
              $("#id_target_efficiency_mar").text(data.efficiency[0].target_efficiency_mar);
              $("#id_target_efficiency_apr").text(data.efficiency[0].target_efficiency_apr);
              $("#id_target_efficiency_may").text(data.efficiency[0].target_efficiency_may);
              $("#id_target_efficiency_june").text(data.efficiency[0].target_efficiency_june);
              $("#id_target_efficiency_july").text(data.efficiency[0].target_efficiency_july);
              $("#id_target_efficiency_aug").text(data.efficiency[0].target_efficiency_aug);
              $("#id_target_efficiency_sep").text(data.efficiency[0].target_efficiency_sep);
              $("#id_target_efficiency_oct").text(data.efficiency[0].target_efficiency_oct);
              $("#id_target_efficiency_nov").text(data.efficiency[0].target_efficiency_nov);
              $("#id_target_efficiency_dec").text(data.efficiency[0].target_efficiency_dec);
              $("#id_min_efficiency_jan").text(data.efficiency[0].minimum_efficiency_jan);
              $("#id_min_efficiency_feb").text(data.efficiency[0].minimum_efficiency_feb);
              $("#id_min_efficiency_mar").text(data.efficiency[0].minimum_efficiency_mar);
              $("#id_min_efficiency_apr").text(data.efficiency[0].minimum_efficiency_apr);
              $("#id_min_efficiency_may").text(data.efficiency[0].minimum_efficiency_may);
              $("#id_min_efficiency_june").text(data.efficiency[0].minimum_efficiency_june);
              $("#id_min_efficiency_july").text(data.efficiency[0].minimum_efficiency_july);
              $("#id_min_efficiency_aug").text(data.efficiency[0].minimum_efficiency_aug);
              $("#id_min_efficiency_sep").text(data.efficiency[0].minimum_efficiency_sep);
              $("#id_min_efficiency_oct").text(data.efficiency[0].minimum_efficiency_oct);
              $("#id_min_efficiency_nov").text(data.efficiency[0].minimum_efficiency_nov);
              $("#id_min_efficiency_dec").text(data.efficiency[0].minimum_efficiency_dec);
            }
          }
        );
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
operatorsInit();
