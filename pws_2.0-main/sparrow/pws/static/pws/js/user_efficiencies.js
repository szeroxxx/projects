function usersInit() {
  sparrow.registerCtrl(
    "userEfficienciesCtrl",
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
        pageTitle: "User Efficiencies",
        topActionbar: {
          delete: {
            url: "/pws/user_efficiencies_delete/",
          },
          extra: [
            {
              id: "btnEdit",
              multiselect: false,
              function: onEditUserEfficiency,
            },
            {
              id: "btnAddNew",
              multiselect: false,
              function: onAdd,
            },
            {
              id: "btnHistory",
              multiselect: false,
              function: showLog,
            },
            {
              id: "btnExport",
              function: onExport,
            },
            {
              id: "btnAllDataExport",
              function: onAllDataExport,
            },
          ],
        },
        listing: [
          {
            index: 1,
            search: {
              params: [
                { key: "company", name: "Customer" },
                { key: "service", name: "Service" },
                { key: "process", name: "Process" },
                { key: "layer", name: "1/2 layer" },
                { key: "multi_layer", name: "Multi layer" },
              ],
            },
            pagging: true,
            crud: true,
            scrollBody: true,
            url: "/pws/user_efficiencies_search/",
            columns: [
              {
                name: "company__name",
                title: "Customer",
              },
              {
                name: "service__name",
                title: "Service",
              },
              {
                name: "process__name",
                title: "Process",
              },
              {
                name: "layer",
                title: "1/2 Layer",
              },
              {
                name: "multi_layer",
                title: "Multi layer",
              },
            ],
          },
        ],
      };

      function onExport() {
        if (data.permissions["can_export_user_efficiency"] == false) {
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

        var company = "";
        var service = "";
        var process = "";
        var layer = "";
        var multi_layer = "";

        if (search_parameter) {
          if ("Customer" in search_parameter) {
            var company = search_parameter["Customer"];
          }
          if ("Service" in search_parameter) {
            var service = search_parameter["Service"];
          }
          if ("Process" in search_parameter) {
            var process = search_parameter["Process"];
          }
          if ("1/2 layer" in search_parameter) {
            var layer = search_parameter["1/2 layer"];
          }
          if ("Multi layer" in search_parameter) {
            var multi_layer = search_parameter["Multi layer"];
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

        sparrow.downloadData("/pws/exports_user_efficiencies/", {
          ids: selectedIds,
          company: company,
          service: service,
          process: process,
          layer: layer,
          multi_layer: multi_layer,
          start: $rootScope.start,
          length: $rootScope.length,
          order_by: order_by_,
        });
      };

      function onAllDataExport() {
        if (data.permissions["can_export_user_efficiency"] == false) {
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

        var company = "";
        var service = "";
        var process = "";
        var layer = "";
        var multi_layer = "";

        if (search_parameter) {
          if ("Customer" in search_parameter) {
            var company = search_parameter["Customer"];
          }
          if ("Service" in search_parameter) {
            var service = search_parameter["Service"];
          }
          if ("Process" in search_parameter) {
            var process = search_parameter["Process"];
          }
          if ("1/2 layer" in search_parameter) {
            var layer = search_parameter["1/2 layer"];
          }
          if ("Multi layer" in search_parameter) {
            var multi_layer = search_parameter["Multi layer"];
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

        sparrow.downloadData("/pws/exports_user_efficiencies/", {
          ids: selectedIds,
          company: company,
          service: service,
          process: process,
          layer: layer,
          multi_layer: multi_layer,
          start: 0,
          length: display_data[0].recordsTotal,
          order_by: order_by_,
        });
      };

      function onAdd() {
        if(data.permissions["add_new_user_efficiency"] == false){
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "You do not have permission to perform this action" ,5)
          return;
        }
        else{
          $("#title").text("Add New");
          var id;
          id = id ? id : 0;
          sparrow.post(
            "/pws/user_efficiency/",
            {
              id: id,
            },
            false,
            function (data) {
              $("#user_efficiency").html(data);
              $("#add").modal("show");
            },
            "html"
          );
        }
      }

      function onEditUserEfficiency(scope) {
        if(data.permissions["edit_user_efficiency"] == false){
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "You do not have permission to perform this action" ,5)
          return;
        }
        else{
          var id = $scope.getSelectedIds(1)[0];
          if(id){
            id = id ? id : 0;
            $("#title").text("Update user efficiency");
            sparrow.post(
              "/pws/user_efficiency/",
              {
                id: id,
              },
              false,
              function (data) {
                $("#user_efficiency").html(data);
                $("#add").modal("show");
              },
              "html"
            );
          }
          else{
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 3);
          }
        }
      }

      $scope.saveUserEfficiency = function () {
        sparrow.postForm(
          {
            id: $routeParams.id,
          },
          $("#frmUserEfficiency"),
          $scope,
          function (data) {
            if (data.code == 1) {
              $("#add").modal("hide");
              $scope.reloadData(1);
            }
          }
        );
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
          "#/auditlog/logs/efficiency/" +
          selectedId +
          "?title=" +
          rowData[0].company__name;
        }
        else{
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 3);
        }
      }

      Mousetrap.bind('shift+a',onAdd)
      Mousetrap.bind('shift+e',onEditUserEfficiency)
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
usersInit();
