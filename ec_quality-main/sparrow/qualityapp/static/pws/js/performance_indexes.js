function performance_indexesInit() {
  sparrow.registerCtrl(
    "performanceIndexesCtrl",
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
        pageTitle: "Performance Index(PI)",
        topActionbar: {
          delete: {
            url: "/qualityapp/performance_index_delete/",
          },
          extra: [
            {
              id: "btnEdit",
              multiselect: false,
              function: onEditPerformanceIndex,
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
          ],
        },
        listing: [
          {
            index: 1,
            search: {
              params: [
                { key: "years_of_experience", name: "No. of years" },
                { key: "target_efficiency", name: "Target efficiency" },
                {
                  key: "minimum_efficiency",
                  name: "Minimum efficiency required",
                },
              ],
            },
            pagging: true,
            crud: true,
            scrollBody: true,
            url: "/qualityapp/performance_indexes_search/",
            columns: [
              {
                name: "years_of_experience",
                title: "No. of years",
                renderWith: viewEdit,
              },
              {
                name: "target_efficiency",
                title: "Target efficiency",
              },
              {
                name: "minimum_efficiency",
                title: "Minimum efficiency required",
              },
            ],
          },
        ],
      };
      function viewEdit(data, type, full, meta) {
        return '<span><a ng-click="onEdit(' + full.id + ')">' + data + '</a></span>';
      };
      $scope.onEdit = function (ids) {
        onEditPerformanceIndex(ids);
      }

      function onAdd() {
        if (data.permissions["can_add_performance_index"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            5
          );
          return;
        } else {
          $("#title").text("Set user points");
          var id;
          id = id ? id : 0;
          sparrow.post(
            "/qualityapp/performance_index/",
            {
              id: id,
            },
            false,
            function (data) {
              $("#performance_index").html(data);
              $("#add").modal("show");
            },
            "html"
          );
        }
      };

      function onEditPerformanceIndex(ids) {
        var id_ = ids
        if (data.permissions["can_update_performance_index"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            5
          );
          return;
        } else {
          var id = $scope.getSelectedIds(1)[0];
          if (id_ && id_.length == undefined) {
            $("#title").text("Update user points");
            sparrow.post(
              "/qualityapp/performance_index/",
              {
                id: id_,
              },
              false,
              function (data) {
                $("#performance_index").html(data);
                $("#add").modal("show");
              },
              "html"
            );
          } else {
            if (id) {
              id = id ? id : 0;
              $("#title").text("Update user points");
              sparrow.post(
                "/qualityapp/performance_index/",
                {
                  id: id,
                },
                false,
                function (data) {
                  $("#performance_index").html(data);
                  $("#add").modal("show");
                },
                "html"
              );
            } else {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                "Please select record",
                3
              );
            }
          }
        }
      };

      $scope.savePerformanceIndex = function () {
        var exp_year = $("#hid_year_of_exp").val();
        if (exp_year) {
          $("#id_message").hide();
          $("#id_year_of_exp").css("border-color", "#ccc");
        } else {
          $("#id_message").show();
          $("#id_year_of_exp").css("border-color", "#a94442");
          return;
        }
        sparrow.postForm(
          {
            id: $routeParams.id,
          },
          $("#frmPerformanceIndex"),
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
          if (selectedId) {
              window.location.hash =
                "#/auditlog/logs/performanceindex/" +
                selectedId +
                "?title=" +
                rowData[0].years_of_experience;
          } else {
              sparrow.showMessage(
              "appMsg",
              sparrow.MsgType.Error,
              "Please select record",
              3
              );
          }
      };

      Mousetrap.bind("shift+a", onAdd);
      Mousetrap.bind("shift+e", onEditPerformanceIndex);
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
performance_indexesInit();
