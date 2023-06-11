function nc_detailsInit(data) {
  sparrow.registerCtrl(
    "nc_detailsCtrl",
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
        pageTitle: "NC‎ Details Master",
        topActionbar: {
          delete: {
            url: "/pws/nc_details_delete/",
          },
          extra: [
            {
              id: "btnNCdetailsHistory",
              multiselect: false,
              function: showLog,
            },
            {
              id: "btnAddNew",
              multiselect: false,
              function: onAdd,
            },
            {
              id: "btnEdit",
              multiselect: false,
              function: onEditNCdetail,
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
                { key: "name", name: "Category name" },
                { key: "created_by", name: "Created by" },
                { key: "created_on", name: "Created on", type: "datePicker" },
              ],
            },
            pagging: true,
            crud: true,
            url: "/pws/nc_details_search/",
            columns: [
              {
                name: "name",
                title: "Category name",
              },
              {
                name: "parent_id",
                title: "Related category",
              },
              {
                name: "created_by",
                title: "Created by",
              },
              {
                name: "created_on",
                title: "Created on",
              },
            ],
          },
        ],
      };

      function onExport() {
        if (data.permissions["can_export_nc_details_master"] == false) {
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

        var name = "";
        var created_by = "";
        var created_on = "";

        if (search_parameter) {
          if ("Category name" in search_parameter) {
            var name = search_parameter["Category name"];
          }
          if ("Created by" in search_parameter) {
            var created_by = search_parameter["Created by"];
          }
          if ("Created on" in search_parameter) {
            var created_on = search_parameter["Created on"];
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

        sparrow.downloadData("/pws/exports_nc_details/", {
          ids: selectedIds,
          name: name,
          created_by: created_by,
          created_on: created_on,
          start: $rootScope.start,
          length: $rootScope.length,
          order_by: order_by_,
        });
      };

      function onAllDataExport() {
        if (data.permissions["can_export_nc_details_master"] == false) {
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

        var name = "";
        var created_by = "";
        var created_on = "";

        if (search_parameter) {
          if ("Category name" in search_parameter) {
            var name = search_parameter["Category name"];
          }
          if ("Created by" in search_parameter) {
            var created_by = search_parameter["Created by"];
          }
          if ("Created on" in search_parameter) {
            var created_on = search_parameter["Created on"];
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

        sparrow.downloadData("/pws/exports_nc_details/", {
          ids: selectedIds,
          name: name,
          created_by: created_by,
          created_on: created_on,
          start: 0,
          length: display_data[0].recordsTotal,
          order_by: order_by_,
        });
      };

     $('#addnewcategory').on('shown.bs.modal', function () {
          $('#id_category_name').focus();
      })
      $scope.saveNCdetails = function () {
        if ($("#id_category_name").val() == "") {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "Please enter the data.",
            3
          );
          return;
        }
        sparrow.postForm(
          {
            id: $routeParams.id,
          },
          $("#frmSaveNCdetails"),
          $scope,
          function (data) {
            if (data.code == 1) {
              $("#addnewcategory").modal("hide");
              $scope.reloadData(1);
            }
          }
        );
      };
      function onAdd(scope) {
        if (data.permissions["add_new_nc_detail"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            5
          );
          return;
        } else {
          $("#title").text("New Category");
          var id;
          id = id ? id : 0;
          sparrow.post(
            "/pws/nc_detail/",
            {
              id: id,
            },
            false,
            function (data) {
              $("#nc_detail").html(data);
              $("#addnewcategory").modal("show");
            },
            "html"
          );
        }
      }
      function onEditNCdetail(scope) {
        if (data.permissions["edit_nc_detail"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            5
          );
          return;
        } else {
          var id = $scope.getSelectedIds(1)[0];
          if(id){
              id = id ? id : 0;
              $("#title").text("Update category");
              sparrow.post(
                "/pws/nc_detail/",
                {
                  id: id,
                },
                false,
                function (data) {
                  $("#nc_detail").html(data);
                  $("#addnewcategory").modal("show");
                },
                "html"
              );
          }else{
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 3);
          }
        }
      }
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
            "#/auditlog/logs/nccategory/" +
            selectedId +
            "?title=" +
            rowData[0].name;
        }else{
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 3);
        }
      }

      Mousetrap.reset()
      Mousetrap.bind('shift+a',onAdd)
      Mousetrap.bind('shift+e',onEditNCdetail)
      Mousetrap.bind('shift+h',showLog)
      Mousetrap.bind("shift+x", onExport);
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
nc_detailsInit();
